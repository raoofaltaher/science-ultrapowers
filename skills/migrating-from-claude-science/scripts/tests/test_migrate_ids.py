"""Tests for the id rule (M1): an id taken from the database is checked before a path or
frontmatter uses it; a row with a bad id is skipped, counted and named in a warning line."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fixture_db  # noqa: E402
import migrate_claude_science as mcs  # noqa: E402
from test_migrate_report import ReportTestCase, scaffold, tree_snapshot  # noqa: E402

REPO = Path(__file__).resolve().parents[4]
HOSTILE = "../../../../zz_outside"


def warning(table, value):
    return "invalid id skipped: " + table + " " + repr(value)[:40]


class IdTestCase(ReportTestCase):
    def open_conn(self):
        copy_dir = Path(tempfile.mkdtemp())  # outside self.tmp, which the tests compare
        self.addCleanup(shutil.rmtree, copy_dir, True)
        conn = mcs.open_ro(mcs.copy_db(self.info.org_dir, copy_dir))
        self.addCleanup(conn.close)
        return conn

    def project_of(self, conn):
        return mcs.pick_project(conn, "proj_fix")

    def artifact_ids_of(self, conn):
        return {r[0] for r in conn.execute("SELECT id FROM artifacts WHERE project_id = 'proj_fix'")}

    def outside_the_lab(self):
        """Every file under the temporary folder that is not inside the lab, with its bytes."""
        lab = self.lab.relative_to(self.tmp).as_posix() + "/"
        return {k: v for k, v in tree_snapshot(self.tmp).items() if not k.startswith(lab)}

    def export_memories(self, conn):
        return mcs.export_memories(conn, self.project_of(conn), self.artifact_ids_of(conn), self.lab)

    def rename_artifact(self, conn, old, new):
        conn.execute("UPDATE artifacts SET id = ? WHERE id = ?", (new, old))
        conn.execute("UPDATE artifact_versions SET artifact_id = ? WHERE artifact_id = ?", (new, old))
        conn.execute("UPDATE memories SET subject_artifact_id = ? WHERE subject_artifact_id = ?", (new, old))

    def rename_version(self, conn, old, new):
        conn.execute("UPDATE artifact_versions SET id = ? WHERE id = ?", (new, old))


class IdRuleTest(unittest.TestCase):
    def test_the_rule_accepts_ids_and_names_only(self):
        for good in ("proj_fix", "a-B_9", "00000000-0000-4000-8000-000000000a01"):
            self.assertTrue(mcs._valid_id(good), good)
        for bad in ("../../x", "a/b", "..", "", None, "a\n", "a b", "a.b", "é", 7, "a\\b"):
            self.assertFalse(mcs._valid_id(bad), repr(bad))

    def test_the_skip_line_names_the_table_and_a_short_repr(self):
        self.assertEqual(mcs._invalid_id_line("memories", "a/b"), "invalid id skipped: memories 'a/b'")
        line = mcs._invalid_id_line("artifacts", "x" * 90 + "/")
        self.assertEqual(line, "invalid id skipped: artifacts " + repr("x" * 90 + "/")[:40])

    def test_containment_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "memory"
            folder.mkdir()
            self.assertTrue(mcs._inside(folder / "project" / "a.md", folder))
            self.assertFalse(mcs._inside(folder / ".." / "x.md", folder))
            self.assertFalse(mcs._inside(folder, folder / "project"))


class MemoryIdTest(IdTestCase):
    def test_memory_rows_with_bad_ids_are_skipped_and_counted(self):
        def edit(conn):
            for key, bad in (("m1", "../../x"), ("m2", "a/b"), ("m3", "..")):
                conn.execute("UPDATE memories SET id = ? WHERE id = ?", (bad, self.info.memories[key]))

        self.build(edit=edit)
        before = self.outside_the_lab()
        report = self.export_memories(self.open_conn())
        self.assertEqual(report.invalid_ids, 3)
        for bad in ("../../x", "a/b", ".."):
            self.assertIn(warning("memories", bad), report.lines)
        self.assertEqual(self.outside_the_lab(), before)
        index = (self.lab / "memory" / "MEMORY.md").read_text(encoding="utf-8")
        self.assertNotIn("../../x", index)
        self.assertFalse((self.lab / "migration" / "PROFILE_MEMORIES.md").exists())
        self.assertFalse((self.lab / "migration" / "SUPERSEDED_MEMORIES.md").exists())
        self.assertFalse((self.lab / "x").exists())

    def test_a_memory_scoped_to_an_artifact_with_a_path_id_never_leaves_the_memory_folder(self):
        self.build(edit=lambda conn: self.rename_artifact(conn, self.info.artifacts["a1"], HOSTILE))
        before = self.outside_the_lab()
        report = self.export_memories(self.open_conn())
        self.assertEqual(report.invalid_ids, 1)
        self.assertEqual(report.artifact, 0)
        self.assertIn(warning("memories", HOSTILE), report.lines)
        self.assertFalse((self.tmp / "zz_outside").exists())
        self.assertEqual(self.outside_the_lab(), before)
        self.assertEqual(list((self.lab / "memory").glob("artifact/*/*")), [])

    def test_a_frame_id_with_a_path_is_never_written_to_frontmatter(self):
        def edit(conn):
            conn.execute("UPDATE memories SET subject_project_id = NULL, subject_frame_id = ? WHERE id = ?",
                         (HOSTILE, self.info.memories["m1"]))

        self.build(edit=edit)
        report = self.export_memories(self.open_conn())
        self.assertEqual(report.invalid_ids, 1)
        self.assertIn(warning("memories", HOSTILE), report.lines)
        everything = "".join(p.read_text(encoding="utf-8") for p in (self.lab / "memory").rglob("*.md"))
        self.assertNotIn("zz_outside", everything)

    def test_a_memory_file_that_exists_is_already_present_and_is_never_overwritten(self):
        self.build()
        conn = self.open_conn()
        body = conn.execute(
            "SELECT body FROM memories WHERE id = ?", (self.info.memories["m1"],)).fetchone()[0]
        target = self.lab / "memory" / "project" / (mcs.slugify(mcs.first_sentence(body)) + ".md")
        baseline = self.export_memories(conn)
        self.assertTrue(target.is_file())
        # A second lab with the same rows, where the file appears after the slug was chosen.
        second = self.proj.parent / "proj2"
        second.mkdir()
        scaffold(second)
        lab2 = second / "research_lab"
        real = mcs._entry_text

        def racing(slug, description, kind, entity, evidence, learned_by, date, note, memory_id, body_text):
            if memory_id == self.info.memories["m1"]:
                path = lab2 / "memory" / "project" / (slug + ".md")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("PRE-EXISTING\n", encoding="utf-8")
            return real(slug, description, kind, entity, evidence, learned_by, date, note, memory_id, body_text)

        with mock.patch.object(mcs, "_entry_text", racing):
            report = mcs.export_memories(conn, self.project_of(conn), self.artifact_ids_of(conn), lab2)
        written = lab2 / "memory" / "project" / target.name
        self.assertEqual(written.read_text(encoding="utf-8"), "PRE-EXISTING\n")
        self.assertEqual(report.project, baseline.project - 1)
        self.assertEqual(report.already_present, baseline.already_present + 1)
        index = (lab2 / "memory" / "MEMORY.md").read_text(encoding="utf-8")
        self.assertNotIn("project/" + target.name, index)
        mapping = json.loads((lab2 / "migration" / "memory-map.json").read_text(encoding="utf-8"))
        self.assertNotIn(self.info.memories["m1"], mapping)


class ArtifactIdTest(IdTestCase):
    def export(self, conn):
        store = mcs.load_artifacts().LabStore(self.lab)
        lines = []
        report = mcs.export_artifacts(conn, self.project_of(conn), self.info.org_dir, store, lines)
        return report, lines, store

    def test_an_artifact_with_a_path_id_is_skipped_with_its_versions(self):
        self.build(edit=lambda conn: self.rename_artifact(conn, self.info.artifacts["a2"], "a/b"))
        before = self.outside_the_lab()
        report, lines, store = self.export(self.open_conn())
        self.assertIn(warning("artifacts", "a/b"), lines)
        self.assertEqual(report.invalid_artifacts, 1)
        self.assertEqual(report.versions_invalid, 1)
        self.assertEqual(report.source_versions, 5)
        self.assertNotIn("a/b", {r["id"] for r in store.rows("artifacts")})
        self.assertEqual(report.artifacts, 3)
        self.assertEqual(self.outside_the_lab(), before)

    def test_an_artifact_id_that_climbs_out_copies_nothing_outside_the_archive(self):
        self.build(edit=lambda conn: self.rename_artifact(conn, self.info.artifacts["a1"], HOSTILE))
        before = self.outside_the_lab()
        report, lines, store = self.export(self.open_conn())
        self.assertFalse((self.tmp / "zz_outside").exists())
        self.assertEqual((report.versions_copied, report.versions_invalid, report.source_versions), (0, 2, 5))
        self.assertEqual(self.outside_the_lab(), before)
        self.assertIn(warning("artifacts", HOSTILE), lines)

    def test_a_version_with_a_bad_id_is_skipped_and_counted(self):
        self.build(edit=lambda conn: self.rename_version(conn, self.info.versions["a1v2"], ".."))
        before = self.outside_the_lab()
        report, lines, store = self.export(self.open_conn())
        self.assertIn(warning("artifact_versions", ".."), lines)
        self.assertEqual(report.versions_invalid, 1)
        self.assertEqual(report.source_versions, 5)
        self.assertEqual(
            {r["id"] for r in store.rows("versions")},
            set(self.info.versions.values()) - {self.info.versions["a1v2"]},
        )
        self.assertEqual(self.outside_the_lab(), before)
        self.assertFalse((self.lab / "artifacts" / "archive" / self.info.artifacts["a1"] / "v002_results.csv").exists())

    def test_a_check_with_a_bad_id_is_skipped_and_counted(self):
        self.build(edit=lambda conn: conn.execute(
            "UPDATE verification_checks SET id = 'x/y' WHERE id = ?", (fixture_db._uid(0xD11),)))
        report, lines, store = self.export(self.open_conn())
        self.assertIn(warning("verification_checks", "x/y"), lines)
        self.assertEqual((report.checks, report.invalid_checks, report.source_checks), (0, 1, 1))
        self.assertEqual(store.rows("verification_checks"), [])

    def test_dry_run_counts_the_same_skips_and_writes_nothing(self):
        self.build(edit=lambda conn: self.rename_version(conn, self.info.versions["a1v2"], ".."))
        conn = self.open_conn()
        store = mcs.load_artifacts().LabStore(self.lab)
        lines = []
        report = mcs.export_artifacts(conn, self.project_of(conn), self.info.org_dir, store, lines, write=False)
        self.assertEqual(report.versions_invalid, 1)
        self.assertIn(warning("artifact_versions", ".."), lines)
        self.assertFalse(any((self.lab / "artifacts" / "archive").rglob("v0*")))


class TranscriptAndProfileIdTest(IdTestCase):
    def test_a_root_frame_with_a_path_id_writes_no_transcript(self):
        def edit(conn):
            old = self.info.frames["root"]
            for sql in (
                "UPDATE frames SET id = ? WHERE id = ?",
                "UPDATE frames SET root_frame_id = ? WHERE root_frame_id = ?",
                "UPDATE frames SET parent_frame_id = ? WHERE parent_frame_id = ?",
                "UPDATE frame_messages SET frame_id = ? WHERE frame_id = ?",
            ):
                conn.execute(sql, ("../../x", old))

        self.build(edit=edit)
        before = self.outside_the_lab()
        conn = self.open_conn()
        report = mcs.write_transcripts(conn, self.project_of(conn), self.lab, 10 ** 9, enabled=True)
        self.assertEqual((report.files, report.invalid_ids), (0, 1))
        self.assertIn(warning("frames", "../../x"), report.lines)
        self.assertEqual(self.outside_the_lab(), before)
        self.assertFalse((self.lab / "x").exists())
        self.assertEqual(list((self.lab / "migration" / "transcripts").glob("*")), [])

    def test_profiles_with_bad_names_are_skipped_and_counted(self):
        def edit(conn):
            conn.execute("UPDATE user_agents SET name = '../evil' WHERE name = 'OPERON'")
            conn.execute("UPDATE user_agents SET name = 'a/b' WHERE name = 'LAB_PROJECT_MANAGER'")

        self.build(edit=edit)
        conn = self.open_conn()
        classifier = mcs.SkillClassifier(REPO / "skills", self.info.data_dir, self.tmp / "synced")
        report = mcs.export_profiles(conn, REPO / "agents", self.lab, classifier)
        self.assertEqual((report.profiles, report.invalid_ids), (2, 2))
        self.assertIn(warning("user_agents", "../evil"), report.lines)
        self.assertIn(warning("user_agents", "a/b"), report.lines)
        self.assertEqual(list((self.lab / "migration" / "profiles").glob("*")), [])
        self.assertNotIn("evil", (self.lab / "migration" / "PROFILE_DIFF.md").read_text(encoding="utf-8"))


class CliIdTest(IdTestCase):
    def test_a_run_over_hostile_ids_stays_inside_the_lab(self):
        def edit(conn):
            self.rename_artifact(conn, self.info.artifacts["a1"], HOSTILE)
            self.rename_version(conn, self.info.versions["a3v1"], "a/b")
            conn.execute("UPDATE memories SET id = '..' WHERE id = ?", (self.info.memories["m1"],))
            conn.execute("UPDATE user_agents SET name = '../evil' WHERE name = 'OPERON'")
            conn.execute("UPDATE verification_checks SET id = 'x/y'")

        self.build(edit=edit)
        before = self.outside_the_lab()
        self.run_ok("--transcripts")
        self.assertEqual(self.outside_the_lab(), before)
        self.assertFalse((self.tmp / "zz_outside").exists())
        self.assertFalse((self.lab / "x").exists())
        self.assertIn("invalid id", self.report_row("memories")[4])
        self.assertIn("invalid id", self.report_row("profiles")[4])
        self.assertIn("invalid id", self.report_row("artifacts")[4])
        self.assertIn("invalid id", self.report_row("versions")[4])
        self.assertIn("invalid id", self.report_row("reviewer findings")[4])


if __name__ == "__main__":
    unittest.main()
