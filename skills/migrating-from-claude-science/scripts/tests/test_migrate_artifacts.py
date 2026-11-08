"""Tests for the artifact step: versions, links, dependencies, checks, LFS lines, idempotence."""

import dataclasses
import errno
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fixture_db  # noqa: E402
import migrate_claude_science as mcs  # noqa: E402

INIT_LAB = Path(__file__).resolve().parents[3] / "initializing-a-research-lab" / "scripts" / "init_lab.py"
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
MB = 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def scaffold(project_root, *extra):
    result = subprocess.run(
        [sys.executable, str(INIT_LAB), "--project-root", str(project_root),
         "--name", "Fixture Study", "--yes", *extra],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise AssertionError("init_lab failed: " + result.stdout + result.stderr)


def tree_snapshot(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(Path(root).rglob("*")) if p.is_file()
    }


class ArtifactTestCase(unittest.TestCase):
    lfs_threshold_mb = None

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        self.info = fixture_db.build_fixture(self.tmp / "data")
        self.proj = self.info.root
        extra = []
        if self.lfs_threshold_mb is not None:
            extra = ["--lfs-threshold-mb", str(self.lfs_threshold_mb)]
        scaffold(self.proj, *extra)
        self.lab = self.proj / "research_lab"
        self.module = mcs.load_artifacts()
        self.ids = self.info.versions
        self.aids = self.info.artifacts

    def edit_db(self, edit):
        conn = sqlite3.connect(str(self.info.db_path))
        try:
            edit(conn)
            conn.commit()
        finally:
            conn.close()

    def export(self, *, write=True, org_dir=None):
        copy_dir = Path(tempfile.mkdtemp(dir=self.tmp))
        conn = mcs.open_ro(mcs.copy_db(self.info.org_dir, copy_dir))
        try:
            project = mcs.pick_project(conn, self.info.project_id)
            store = self.module.LabStore(self.lab)
            lines = []
            report = mcs.export_artifacts(
                conn, project, org_dir or self.info.org_dir, store, lines, write=write
            )
        finally:
            conn.close()
        self.lines = lines
        self.store = store
        return report

    def rows(self, ledger):
        return self.module.LabStore(self.lab).rows(ledger)

    def version(self, key):
        return next(r for r in self.rows("versions") if r["id"] == self.ids[key])

    def stored(self, key):
        return self.lab / self.version(key)["storage_path"]


class HelpersTest(unittest.TestCase):
    def test_ms_to_iso(self):
        self.assertEqual(mcs.ms_to_iso(1760000000123), "2025-10-09T08:53:20.123Z")
        self.assertEqual(mcs.ms_to_iso(1760000000000), "2025-10-09T08:53:20.000Z")
        self.assertIsNone(mcs.ms_to_iso(None))

    def test_ms_to_iso_matches_the_store_format(self):
        self.assertRegex(mcs.ms_to_iso(fixture_db.T0), ISO_RE)
        self.assertRegex(mcs.load_artifacts().now_iso(), ISO_RE)


class ExportArtifactsTest(ArtifactTestCase):
    def test_copy_versions_land_in_the_archive_with_kept_ids(self):
        report = self.export()
        a1 = self.aids["a1"]
        v1, v2 = self.version("a1v1"), self.version("a1v2")
        self.assertEqual(v1["storage_path"], "artifacts/archive/" + a1 + "/v001_results.csv")
        self.assertEqual(v2["storage_path"], "artifacts/archive/" + a1 + "/v002_results.csv")
        for key, row in (("a1v1", v1), ("a1v2", v2)):
            stored = self.lab / row["storage_path"]
            self.assertEqual(stored.read_bytes(), self.info.files[key].read_bytes())
            self.assertEqual(row["sha256"], sha(stored.read_bytes()))
            self.assertEqual((row["kind"], row["status"], row["source"]), ("copy", "ok", "claude-science"))
        self.assertEqual(report.versions_copied, 2)
        self.assertEqual({r["id"] for r in self.rows("versions")}, set(self.ids.values()))

    def test_windows_illegal_filename_is_sanitised(self):
        self.edit_db(lambda c: c.execute(
            "UPDATE artifacts SET filename = ? WHERE id = ?", ("results 12:30?.csv", self.aids["a1"])))
        self.export()
        for key in ("a1v1", "a1v2"):
            row = self.version(key)
            stored = self.lab / row["storage_path"]
            leaf = Path(row["storage_path"]).name
            self.assertNotIn(":", leaf)
            self.assertNotIn("?", leaf)
            self.assertEqual(row["status"], "ok")
            self.assertEqual(stored.stat().st_size, self.info.files[key].stat().st_size)
            self.assertEqual(stored.read_bytes(), self.info.files[key].read_bytes())

    def test_filename_leaf_sanitiser(self):
        self.assertEqual(mcs.safe_leaf('a<b>c:d"e/f\\g|h?i*j'), "a_b_c_d_e_f_g_h_i_j")
        self.assertEqual(mcs.safe_leaf("x\x00y\x1fz"), "x_y_z")
        self.assertEqual(mcs.safe_leaf("name. . "), "name")
        self.assertEqual(mcs.safe_leaf("..."), "file")
        self.assertEqual(mcs.safe_leaf(""), "file")

    def test_missing_source_file_is_a_missing_row_and_report_line(self):
        report = self.export()
        row = self.version("a2v1")
        self.assertEqual((row["kind"], row["status"]), ("copy", "missing"))
        checksum = self.edit_checksum("a2v1")
        self.assertEqual(row["sha256"], checksum)
        self.assertEqual(row["storage_path"], "artifacts/archive/" + self.aids["a2"] + "/v001_notes.md")
        self.assertFalse((self.lab / row["storage_path"]).exists())
        self.assertEqual(report.versions_missing, 2)  # a2v1 and the absent host file a4v1
        line = next(l for l in self.lines if l.startswith("missing: " + self.ids["a2v1"] + " "))
        self.assertIn("notes.md", line)

    def patched_copyfile(self, error):
        """shutil.copyfile that raises `error` for the copy into the store of a1v2, else copies."""
        real = shutil.copyfile

        def copyfile(src, dst, *args, **kwargs):
            if str(dst).endswith("v002_results.csv"):
                raise error
            return real(src, dst, *args, **kwargs)

        return mock.patch.object(shutil, "copyfile", side_effect=copyfile)

    def test_path_too_long_is_a_missing_row_and_a_report_line_not_a_failure(self):
        error = OSError(errno.ENAMETOOLONG, "File name too long")
        with self.patched_copyfile(error):
            report = self.export()
        row = self.version("a1v2")
        self.assertEqual((row["kind"], row["status"]), ("copy", "missing"))
        self.assertEqual(row["sha256"], self.edit_checksum("a1v2"))
        self.assertFalse(self.stored("a1v2").exists())
        self.assertEqual(self.version("a1v1")["status"], "ok")
        self.assertEqual(self.stored("a1v1").read_bytes(), self.info.files["a1v1"].read_bytes())
        self.assertEqual(
            (report.versions_copied, report.versions_linked, report.versions_missing), (1, 1, 3))
        self.assertEqual(
            report.versions_copied + report.versions_linked + report.versions_missing, report.source_versions)
        expected = (
            "path too long: " + self.ids["a1v2"] + " " + row["storage_path"]
            + r" (enable long paths: HKLM\SYSTEM\CurrentControlSet\Control\FileSystem"
            " LongPathsEnabled=1, then re-run)"
        )
        self.assertIn(expected, self.lines)
        self.assertFalse([l for l in self.lines if l.startswith("missing: " + self.ids["a1v2"])])

    def test_path_too_long_is_told_from_other_copy_errors(self):
        long_dest = Path("x") / ("d" * 260)
        self.assertTrue(mcs._path_too_long(OSError(errno.ENAMETOOLONG, "long"), Path("short")))
        self.assertTrue(mcs._path_too_long(FileNotFoundError(errno.ENOENT, "gone"), long_dest))
        self.assertFalse(mcs._path_too_long(FileNotFoundError(errno.ENOENT, "gone"), Path("short")))
        self.assertFalse(mcs._path_too_long(PermissionError(errno.EACCES, "denied"), long_dest))
        if sys.platform == "win32":
            for code in (3, 206):
                self.assertTrue(mcs._path_too_long(OSError(0, "x", None, code), Path("short")))
            self.assertFalse(mcs._path_too_long(OSError(0, "x", None, 5), Path("short")))
        with self.patched_copyfile(PermissionError(errno.EACCES, "denied")):
            with self.assertRaises(mcs.MigrationError):
                self.export()

    def edit_checksum(self, key):
        conn = sqlite3.connect(str(self.info.db_path))
        try:
            return conn.execute(
                "SELECT checksum FROM artifact_versions WHERE id = ?", (self.ids[key],)
            ).fetchone()[0]
        finally:
            conn.close()

    def test_host_link_inside_project_becomes_relative_link(self):
        report = self.export()
        row = self.version("a3v1")
        self.assertEqual((row["kind"], row["status"]), ("link", "ok"))
        self.assertEqual(row["storage_path"], "link:host/data.csv")
        self.assertEqual(row["sha256"], sha(self.info.files["a3v1"].read_bytes()))
        self.assertEqual(report.versions_linked, 1)
        self.assertEqual(report.versions_changed, 0)

    def link_outside(self, home):
        """Point a3v1 at a file under tmp/elsewhere and export with `home` as the home folder."""
        outside = self.tmp / "elsewhere" / "data" / "outside.csv"
        outside.parent.mkdir(parents=True)
        outside.write_bytes(b"a,b\n")
        self.edit_db(lambda c: c.execute(
            "UPDATE artifact_versions SET storage_path = ?, checksum = ? WHERE id = ?",
            ("~/" + outside.as_posix(), sha(b"a,b\n"), self.ids["a3v1"]),
        ))
        with mock.patch.object(Path, "home", return_value=home):
            self.export()
        return outside

    def test_host_link_outside_project_and_home_is_an_absolute_link_with_a_line(self):
        outside = self.link_outside(self.tmp / "somebody-else")
        row = self.version("a3v1")
        self.assertEqual(row["storage_path"], "link:" + outside.as_posix())
        self.assertEqual(row["status"], "ok")
        self.assertIn("absolute link path recorded: " + self.ids["a3v1"], self.lines)

    def test_host_link_under_the_home_folder_is_tilde_relative(self):
        self.link_outside(self.tmp / "elsewhere")
        row = self.version("a3v1")
        self.assertEqual(row["storage_path"], "link:~/data/outside.csv")
        self.assertEqual(row["status"], "ok")
        self.assertFalse([l for l in self.lines if l.startswith("absolute link path recorded")])

    def test_host_link_inside_the_project_stays_project_relative_even_under_home(self):
        with mock.patch.object(Path, "home", return_value=self.tmp):
            self.export()
        self.assertEqual(self.version("a3v1")["storage_path"], "link:host/data.csv")

    def test_missing_lines_give_the_recorded_sha256(self):
        self.export()
        for key in ("a2v1", "a4v1"):
            line = next(l for l in self.lines if l.startswith("missing: " + self.ids[key] + " "))
            self.assertTrue(
                line.endswith(" (recorded sha256 " + self.edit_checksum(key) + ")"), line)
        self.edit_db(lambda c: c.execute(
            "UPDATE artifact_versions SET checksum = '' WHERE id = ?", (self.ids["a2v1"],)))
        shutil.rmtree(self.lab / "artifacts" / "archive")
        for name in ("versions", "artifacts", "dependencies", "verification_checks"):
            self.module.LabStore(self.lab).rewrite(name, [])
        self.export()
        line = next(l for l in self.lines if l.startswith("missing: " + self.ids["a2v1"] + " "))
        self.assertTrue(line.endswith(" (no sha256 recorded)"), line)

    def test_host_link_missing_is_missing_row(self):
        self.export()
        row = self.version("a4v1")
        self.assertEqual((row["kind"], row["status"]), ("link", "missing"))
        self.assertEqual(row["storage_path"], "link:host/absent.csv")
        self.assertEqual(row["sha256"], self.edit_checksum("a4v1"))
        line = next(l for l in self.lines if l.startswith("missing: " + self.ids["a4v1"] + " "))
        self.assertIn("absent.csv", line)

    @unittest.skipUnless(os.name == "nt", "needs a drive letter that is not mounted")
    def test_host_link_on_an_unmounted_drive_is_missing_not_a_traceback(self):
        letter = next(c for c in "QRSTUVWXYZ" if not os.path.exists(c + ":\\"))
        self.edit_db(lambda c: c.execute(
            "UPDATE artifact_versions SET storage_path = ? WHERE id = ?",
            ("~/" + letter + ":/AU/Code/outputs/x.csv", self.ids["a3v1"]),
        ))
        report = self.export()
        row = self.version("a3v1")
        self.assertEqual((row["kind"], row["status"]), ("link", "missing"))
        self.assertEqual(row["storage_path"], "link:" + letter + ":/AU/Code/outputs/x.csv")
        self.assertEqual(report.versions_missing, 3)

    def test_changed_host_file_is_changed_row_with_both_hashes(self):
        old = self.edit_checksum("a3v1")
        new_bytes = b"id,value\n1,99\n"
        self.info.files["a3v1"].write_bytes(new_bytes)
        report = self.export()
        row = self.version("a3v1")
        self.assertEqual((row["kind"], row["status"]), ("link", "changed"))
        self.assertEqual(row["sha256"], sha(new_bytes))
        self.assertEqual((report.versions_changed, report.versions_linked), (1, 1))
        line = next(l for l in self.lines if l.startswith("changed: " + self.ids["a3v1"] + " "))
        self.assertTrue(line.endswith(": claude-science " + old + " now " + sha(new_bytes)), line)

    def test_changed_copy_is_changed_row(self):
        self.info.files["a1v1"].write_bytes(b"split,score\ndev,0.99\n")
        report = self.export()
        row = self.version("a1v1")
        self.assertEqual((row["kind"], row["status"]), ("copy", "changed"))
        self.assertEqual(row["sha256"], sha(b"split,score\ndev,0.99\n"))
        self.assertEqual((report.versions_changed, report.versions_copied), (1, 2))
        self.assertTrue(any(l.startswith("changed: " + self.ids["a1v1"] + " ") for l in self.lines))

    def test_dependency_edge_and_check_imported(self):
        report = self.export()
        deps = self.rows("dependencies")
        self.assertEqual(deps, [{
            "version_id": self.ids["a1v2"], "depends_on_version_id": self.ids["a3v1"],
            "reference_name": "data.csv",
        }])
        checks = self.rows("verification_checks")
        self.assertEqual(len(checks), 1)
        check = checks[0]
        self.assertEqual(check["id"], "00000000-0000-4000-8000-000000000d11")
        self.assertEqual(check["version_id"], self.ids["a1v2"])
        self.assertEqual((check["verdict"], check["severity"], check["status"]), ("warn", "minor", "open"))
        self.assertEqual(check["claim"], "The table mixes dev and test numbers.")
        self.assertEqual(check["evidence"], "Row 3 cites the test split.")
        self.assertIsNone(check["rebuttal"])
        self.assertIsNone(check["resolution"])
        self.assertEqual(check["reviewer_role"], "literature-researcher")
        self.assertRegex(check["created_at"], ISO_RE)
        self.assertEqual((report.dependencies, report.dependencies_outside, report.checks), (1, 0, 1))

    def test_checks_scoped_by_root_frame_are_imported_without_version(self):
        def edit(conn):
            for check_id, frame in (
                ("00000000-0000-4000-8000-000000000d21", self.info.frames["root"]),
                ("00000000-0000-4000-8000-000000000d22", self.info.frames["other_lit"]),
            ):
                conn.execute(
                    "INSERT INTO verification_checks (id, root_frame_id, artifact_version_id, claim,"
                    " verdict, severity, evidence, reviewer_frame_id, source_ref, status, created_at)"
                    " VALUES (?, ?, NULL, 'A claim with no artifact.', 'fail', 'major', 'e', NULL,"
                    " 'ptr-" + check_id[-2:] + "', 'open', ?)",
                    (check_id, frame, fixture_db.T0 + 5),
                )

        self.edit_db(edit)
        report = self.export()
        checks = {r["id"]: r for r in self.rows("verification_checks")}
        self.assertEqual(
            set(checks),
            {"00000000-0000-4000-8000-000000000d11", "00000000-0000-4000-8000-000000000d21"},
        )
        loose = checks["00000000-0000-4000-8000-000000000d21"]
        self.assertIsNone(loose["version_id"])
        self.assertEqual(loose["source_ref"], "ptr-21")
        self.assertEqual(loose["reviewer_role"], "reviewer")
        self.assertEqual(checks["00000000-0000-4000-8000-000000000d11"]["source_ref"], "fixture-ref")
        self.assertEqual((report.checks, report.source_checks), (2, 2))

    def test_empty_checksum_is_ok_not_changed(self):
        self.edit_db(lambda c: (
            c.execute("UPDATE artifact_versions SET checksum = '' WHERE id = ?", (self.ids["a3v1"],)),
            c.execute("UPDATE artifact_versions SET checksum = '' WHERE id = ?", (self.ids["a1v1"],)),
        ))
        report = self.export()
        for key in ("a3v1", "a1v1"):
            row = self.version(key)
            self.assertEqual(row["status"], "ok")
            self.assertEqual(row["sha256"], sha(self.info.files[key].read_bytes()))
            self.assertIn("no checksum recorded: " + self.ids[key], self.lines)
        self.assertEqual(report.versions_changed, 0)
        self.assertEqual((report.versions_copied, report.versions_linked), (2, 1))

    def test_unresolved_reviewer_frame_becomes_reviewer(self):
        self.edit_db(lambda c: c.execute(
            "UPDATE verification_checks SET reviewer_frame_id = NULL"))
        self.export()
        self.assertEqual(self.rows("verification_checks")[0]["reviewer_role"], "reviewer")

    def test_reviewer_frame_that_does_not_resolve_becomes_reviewer(self):
        self.edit_db(lambda c: c.execute(
            "UPDATE verification_checks SET reviewer_frame_id = ?",
            ("00000000-0000-4000-8000-0000000fffff",)))
        self.export()
        self.assertEqual(self.rows("verification_checks")[0]["reviewer_role"], "reviewer")

    def test_reviewer_frame_without_an_agent_name_becomes_reviewer(self):
        self.edit_db(lambda c: c.execute(
            "UPDATE frames SET agent_name = '  ' WHERE id = ?", (self.info.frames["lit"],)))
        self.export()
        self.assertEqual(self.rows("verification_checks")[0]["reviewer_role"], "reviewer")
        conn = sqlite3.connect(":memory:")
        try:
            conn.execute("CREATE TABLE frames (id TEXT, agent_name TEXT)")
            conn.execute("INSERT INTO frames VALUES ('f-null', NULL)")
            conn.execute("INSERT INTO frames VALUES ('f-ok', 'LIT_RESEARCHER')")
            self.assertIsNone(mcs._frame_role(conn, {}, "f-null"))
            self.assertIsNone(mcs._frame_role(conn, {}, "f-missing"))
            self.assertEqual(mcs._frame_role(conn, {}, "f-ok"), "literature-researcher")
        finally:
            conn.close()

    def test_dependency_outside_the_project_is_counted_not_written(self):
        outside_version = "00000000-0000-4000-8000-000000000b99"

        def edit(conn):
            conn.execute(
                "INSERT INTO artifacts (id, project_id, root_frame_id, frame_id, filename, created_at,"
                " latest_version_id, is_user_upload, is_ephemeral, sort_order)"
                " VALUES (?, ?, ?, ?, 'foreign.csv', ?, ?, 0, 0, 0)",
                ("00000000-0000-4000-8000-000000000a99", self.info.other_project_id,
                 self.info.frames["other_lit"], self.info.frames["other_lit"], fixture_db.T0,
                 outside_version),
            )
            conn.execute(
                "INSERT INTO artifact_versions (id, artifact_id, version_number, content_type, size_bytes,"
                " checksum, storage_path, created_at, is_intermediate)"
                " VALUES (?, ?, 1, 'text/csv', 1, 'x', 'proj_other\\x\\v1_foreign.csv', ?, 0)",
                (outside_version, "00000000-0000-4000-8000-000000000a99", fixture_db.T0),
            )
            conn.execute(
                "INSERT INTO artifact_dependencies (id, artifact_version_id, depends_on_version_id,"
                " reference_name, created_at) VALUES (?, ?, ?, 'foreign.csv', ?)",
                ("00000000-0000-4000-8000-000000000d99", self.ids["a1v1"], outside_version, fixture_db.T0),
            )

        self.edit_db(edit)
        report = self.export()
        self.assertEqual((report.dependencies, report.dependencies_outside), (1, 1))
        self.assertEqual(len(self.rows("dependencies")), 1)
        self.assertEqual(len(self.rows("versions")), 5)
        self.assertEqual(len(self.rows("artifacts")), 4)

    def test_producing_command_from_execution_log(self):
        self.export()
        self.assertEqual(self.version("a1v2")["producing_command"], "print('hi')")
        for key in ("a1v1", "a2v1", "a3v1", "a4v1"):
            self.assertIsNone(self.version(key)["producing_command"])

    def test_artifact_rows(self):
        self.export()
        artifacts = {r["id"]: r for r in self.rows("artifacts")}
        self.assertEqual(list(artifacts), [self.aids[k] for k in ("a1", "a2", "a3", "a4")])
        a1 = artifacts[self.aids["a1"]]
        self.assertEqual(a1, {
            "id": self.aids["a1"], "filename": "results.csv", "latest_version_id": self.ids["a1v2"],
            "folder": "Results", "is_user_upload": False, "is_ephemeral": False,
            "superseded_by": None, "retention": None, "destination": "milestone",
            "created_at": mcs.ms_to_iso(fixture_db.T0), "source": "claude-science",
        })
        self.assertIsNone(artifacts[self.aids["a2"]]["folder"])

    def test_version_row_fields(self):
        self.edit_db(lambda c: c.execute(
            "UPDATE artifact_versions SET environment_snapshot = ?, is_checkpoint = 1, is_intermediate = 1"
            " WHERE id = ?", ('{"python": "3.12"}', self.ids["a1v1"])))
        self.export()
        v2 = self.version("a1v2")
        self.assertEqual(v2["parent_version_id"], self.ids["a1v1"])
        self.assertEqual(v2["agent_name"], "literature-researcher")
        self.assertEqual(v2["producing_session"], self.info.frames["lit"])
        self.assertEqual(v2["code_description"], "Builds the results table")
        self.assertEqual((v2["is_intermediate"], v2["is_checkpoint"]), (False, False))
        self.assertEqual((v2["destination"], v2["environment"]), ("milestone", None))
        self.assertEqual((v2["version_number"], v2["content_type"]), (2, "text/csv"))
        self.assertEqual(v2["created_at"], mcs.ms_to_iso(fixture_db.T0 + 100))
        v1 = self.version("a1v1")
        self.assertEqual((v1["is_intermediate"], v1["is_checkpoint"]), (True, True))
        self.assertEqual(v1["environment"], '{"python": "3.12"}')
        self.assertIsNone(v1["parent_version_id"])

    def test_gitattributes_rules_exist_without_any_large_file(self):
        (self.lab / "artifacts" / ".gitattributes").unlink()
        self.export()
        text = (self.lab / "artifacts" / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("archive/** -text", text)
        self.assertIn("*.jsonl text eol=lf", text)
        self.assertNotIn("filter=lfs", text)

    def test_rerun_is_idempotent(self):
        self.export()
        first = tree_snapshot(self.lab)
        report = self.export()
        self.assertEqual(report.already_present, 5)
        self.assertEqual(
            (report.versions_copied, report.versions_linked, report.versions_missing,
             report.artifacts, report.dependencies, report.checks), (0, 0, 0, 0, 0, 0))
        self.assertEqual(first, tree_snapshot(self.lab))
        attributes = (self.lab / "artifacts" / ".gitattributes").read_text(encoding="utf-8").split("\n")
        self.assertEqual(len(attributes), len(set(attributes)))

    def test_counts_reconcile(self):
        report = self.export()
        self.assertEqual(report.artifacts, 4)
        self.assertEqual(report.versions_copied + report.versions_linked + report.versions_missing, 5)
        self.assertEqual(
            (report.versions_copied, report.versions_linked, report.versions_missing), (2, 1, 2))
        self.assertEqual((report.source_versions, report.source_checks), (5, 1))
        self.assertEqual(report.already_present, 0)

    def test_dry_run_writes_nothing(self):
        (self.lab / "artifacts" / ".gitattributes").unlink()
        before = tree_snapshot(self.proj)
        dry = self.export(write=False)
        dry_lines = list(self.lines)
        self.assertEqual(before, tree_snapshot(self.proj))
        self.assertFalse((self.lab / "artifacts" / ".gitattributes").exists())
        real = self.export()
        self.assertEqual(dataclasses.asdict(dry), dataclasses.asdict(real))
        self.assertEqual(dry_lines, self.lines)
        self.assertEqual(dry.versions_copied, 2)

    def test_dry_run_decides_changed_by_the_file(self):
        self.info.files["a3v1"].write_bytes(b"different\n")
        dry = self.export(write=False)
        self.assertEqual(dry.versions_changed, 1)
        self.assertEqual(self.rows("versions"), [])


class ReviewerFindingWordsTest(unittest.TestCase):
    """The reviewer-finding status of an imported check is written in the new words; the old words are read."""

    def test_new_words_for_the_old_statuses(self):
        for old, new in (("unaddressed", "open"), ("claimed", "author-responded"), ("resolved", "closed")):
            self.assertEqual(mcs.finding_status(old), new)

    def test_new_words_pass_through_and_unknown_words_are_kept(self):
        for word in ("open", "author-responded", "re-opened", "closed"):
            self.assertEqual(mcs.finding_status(word), word)
        self.assertEqual(mcs.finding_status("something-else"), "something-else")
        self.assertIsNone(mcs.finding_status(None))


class ArchiveFieldNamesTest(ArtifactTestCase):
    def test_rows_use_the_archive_field_names(self):
        other = self.tmp / "other"
        other.mkdir()
        scaffold(other)
        store = self.module.LabStore(other / "research_lab")
        (other / "a.txt").write_text("one", encoding="utf-8")
        (other / "b.txt").write_text("two", encoding="utf-8")
        saved = store.save(
            [other / "a.txt"], role="academic-paper-author", command="python a.py", stage=False)[0]
        linked = store.link(
            [other / "b.txt"], role="academic-paper-author", command="python b.py",
            inputs=[saved["version_id"]], stage=False)[0]
        store.check_add(saved["version_id"], claim="c", verdict="warn",
                        reviewer_role="scientific-peer-reviewer", stage=False)

        self.export()
        ours = {name: self.rows(name) for name in ("artifacts", "versions", "dependencies", "verification_checks")}
        theirs = {name: store.rows(name) for name in ours}
        for name in ours:
            self.assertTrue(ours[name], name)
        self.assertEqual(list(ours["artifacts"][0]), list(theirs["artifacts"][0]))
        copy_keys = list(next(r for r in theirs["versions"] if r["kind"] == "copy"))
        link_keys = list(next(r for r in theirs["versions"] if r["kind"] == "link"))
        self.assertEqual(copy_keys, link_keys)
        for row in ours["versions"]:
            self.assertEqual(list(row), copy_keys)
        self.assertEqual(list(ours["dependencies"][0]), list(theirs["dependencies"][0]))
        store_keys = list(theirs["verification_checks"][0])  # `check add` may or may not write source_ref
        self.assertEqual(
            list(ours["verification_checks"][0]),
            store_keys if "source_ref" in store_keys else store_keys + ["source_ref"],
        )
        self.assertEqual(linked["version_number"], 1)


class LargeCopyTest(ArtifactTestCase):
    lfs_threshold_mb = 1

    def big_a1v1(self):
        data = (b"0123456789abcdef" * 1024) * 96  # 1.5 MB
        self.info.files["a1v1"].write_bytes(data)
        self.edit_db(lambda c: c.execute(
            "UPDATE artifact_versions SET checksum = ?, size_bytes = ? WHERE id = ?",
            (sha(data), len(data), self.ids["a1v1"])))
        return data

    def test_lfs_line_for_large_copied_version(self):
        data = self.big_a1v1()
        self.assertEqual(len(data), 3 * MB // 2)
        report = self.export()
        self.assertEqual(self.version("a1v1")["status"], "ok")
        text = (self.lab / "artifacts" / ".gitattributes").read_text(encoding="utf-8")
        line = "archive/" + self.aids["a1"] + "/v001_results.csv filter=lfs diff=lfs merge=lfs -text"
        self.assertEqual(text.split("\n").count(line), 1)
        self.assertEqual(text.count("filter=lfs"), 1)
        self.assertIn("archive/** -text", text)
        self.assertEqual(report.versions_copied, 2)
        self.assertEqual(self.store.lfs_check()["missing_lines"], [])

    def test_budget_warning_when_the_lfs_total_passes_the_budget(self):
        self.big_a1v1()
        config = json.loads((self.lab / "lab.json").read_text(encoding="utf-8"))
        config["lfs"]["budgetWarnMB"] = 1
        (self.lab / "lab.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        self.export()
        warning = [l for l in self.lines if "(LFS) total" in l]
        self.assertEqual(len(warning), 1, self.lines)
        self.assertIn("1.5 MB", warning[0])
        self.assertIn("budgetWarnMB", warning[0])

    def test_no_budget_warning_under_the_budget(self):
        self.big_a1v1()
        self.export()
        self.assertEqual([l for l in self.lines if "(LFS) total" in l], [])


if __name__ == "__main__":
    unittest.main()
