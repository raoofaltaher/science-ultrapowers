import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts
from _helpers import make_git_lab, make_lab, run_cli, write_file

ARTIFACT_FIELDS = [
    "id", "filename", "latest_version_id", "folder", "is_user_upload", "is_ephemeral",
    "superseded_by", "retention", "destination", "created_at", "source",
]
VERSION_FIELDS = [
    "id", "artifact_id", "version_number", "parent_version_id", "kind", "content_type",
    "size_bytes", "sha256", "storage_path", "agent_name", "producing_command",
    "producing_session", "code_description", "is_intermediate", "is_checkpoint", "destination",
    "environment", "created_at", "source", "status",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class SaveTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self._tmp.cleanup)
        self.t = Path(self._tmp.name)

    def _store(self, lab_json=None, git=False):
        lab = make_git_lab(self.t, lab_json) if git else make_lab(self.t, lab_json)
        s = artifacts.LabStore(lab)
        return s, s.project_root

    def _save1(self, s, path, **kw):
        kw.setdefault("role", "paper-author")
        kw.setdefault("command", "pytest")
        return s.save([path], **kw)[0]

    def test_save_new_file_creates_artifact_and_version(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "report.md", "# hello\n")
        res = s.save([f], role="paper-author", command="pytest")
        self.assertEqual(len(res), 1)
        r = res[0]
        self.assertEqual(sorted(r), sorted(["artifact_id", "version_id", "version_number", "storage_path", "lfs"]))
        self.assertIs(r["lfs"], False)
        arts, vers = s.rows("artifacts"), s.rows("versions")
        self.assertEqual(len(arts), 1)
        self.assertEqual(len(vers), 1)
        a, v = arts[0], vers[0]
        self.assertEqual(list(a), ARTIFACT_FIELDS)
        self.assertEqual(list(v), VERSION_FIELDS)
        self.assertEqual(a["filename"], "work/report.md")
        self.assertEqual(a["destination"], "snapshot")
        self.assertEqual(a["source"], "lab")
        self.assertEqual(a["latest_version_id"], v["id"])
        self.assertEqual(v["artifact_id"], a["id"])
        self.assertEqual(v["version_number"], 1)
        self.assertIsNone(v["parent_version_id"])
        self.assertEqual(v["kind"], "copy")
        self.assertEqual(v["content_type"], "text/markdown")
        self.assertEqual(v["sha256"], _sha(f.read_bytes()))
        self.assertEqual(v["storage_path"], f"artifacts/store/{a['id']}/v001_report.md")
        self.assertEqual(v["agent_name"], "paper-author")
        self.assertEqual(v["producing_command"], "pytest")
        self.assertEqual(v["status"], "ok")
        self.assertEqual(r["storage_path"], v["storage_path"])
        self.assertEqual((s.lab / v["storage_path"]).read_bytes(), f.read_bytes())

    def test_same_basename_in_two_folders_are_two_artifacts(self):
        s, proj = self._store()
        r1 = self._save1(s, write_file(proj / "a" / "report.md", "one\n"))
        r2 = self._save1(s, write_file(proj / "b" / "report.md", "two\n"))
        self.assertNotEqual(r1["artifact_id"], r2["artifact_id"])
        self.assertEqual([a["filename"] for a in s.rows("artifacts")], ["a/report.md", "b/report.md"])
        self.assertTrue(r1["storage_path"].endswith("/v001_report.md"))
        self.assertTrue(r2["storage_path"].endswith("/v001_report.md"))
        self.assertEqual([r["filename"] for r in s.search("b/report")], ["b/report.md"])
        # the same path again is the same artifact: refused without --version-of, a new version with it
        again = write_file(proj / "a" / "report.md", "uno\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, again)
        self.assertEqual(
            str(cm.exception),
            f"artifact a/report.md exists ({r1['artifact_id']}); pass --version-of {r1['artifact_id']} "
            "for a new state of the same file",
        )
        r3 = self._save1(s, again, version_of="a/report.md")
        self.assertEqual(r3["artifact_id"], r1["artifact_id"])
        self.assertEqual(r3["version_number"], 2)

    def test_save_second_version_chains(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "report.md", "one\n")
        r1 = self._save1(s, f)
        write_file(f, "two\n")
        r2 = self._save1(s, f, version_of=r1["artifact_id"])
        self.assertEqual(r2["version_number"], 2)
        self.assertEqual(r2["artifact_id"], r1["artifact_id"])
        v2 = [v for v in s.rows("versions") if v["id"] == r2["version_id"]][0]
        self.assertEqual(v2["parent_version_id"], r1["version_id"])
        self.assertEqual(s.rows("artifacts")[0]["latest_version_id"], r2["version_id"])
        d = s.store / r1["artifact_id"]
        self.assertTrue((d / "v001_report.md").is_file())
        self.assertTrue((d / "v002_report.md").is_file())

    def test_save_new_version_from_other_filename_keeps_artifact_name(self):
        s, proj = self._store()
        r1 = self._save1(s, write_file(proj / "work" / "report.md", "one\n"))
        other = write_file(proj / "work" / "report_final.md", "two\n")
        r2 = self._save1(s, other, version_of=r1["artifact_id"])
        self.assertEqual(r2["storage_path"], f"artifacts/store/{r1['artifact_id']}/v002_report.md")
        self.assertTrue((s.store / r1["artifact_id"] / "v002_report.md").is_file())
        self.assertEqual(s.rows("artifacts")[0]["filename"], "work/report.md")

    def test_save_same_filename_without_version_of_is_refused(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "report.md", "one\n")
        self._save1(s, f)
        write_file(f, "two\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, f)
        self.assertIn("--version-of", str(cm.exception))
        self.assertEqual(len(s.rows("artifacts")), 1)
        self.assertEqual(len(s.rows("versions")), 1)

    def test_save_identical_bytes_is_refused(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "report.md", "one\n")
        r1 = self._save1(s, f)
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, f, version_of=r1["artifact_id"])
        self.assertIn("identical", str(cm.exception))
        self.assertEqual(len(s.rows("versions")), 1)

    def test_version_of_accepts_version_id_and_prefix(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "report.md", "one\n")
        r1 = self._save1(s, f)
        write_file(f, "two\n")
        r2 = self._save1(s, f, version_of=r1["version_id"])
        self.assertEqual(r2["artifact_id"], r1["artifact_id"])
        self.assertEqual(r2["version_number"], 2)
        write_file(f, "three\n")
        r3 = self._save1(s, f, version_of=r1["version_id"][:8])
        self.assertEqual(r3["artifact_id"], r1["artifact_id"])
        self.assertEqual(r3["version_number"], 3)

    def test_save_records_inputs_as_edges(self):
        s, proj = self._store()
        ra = self._save1(s, write_file(proj / "work" / "a.csv", "a,b\n1,2\n"))
        write_file(proj / "data" / "raw.csv", "x\n1\n")
        rr = self._save1(s, write_file(proj / "work" / "report.md", "r\n"), inputs=[ra["version_id"], "data/raw.csv"])
        edges = [e for e in s.rows("dependencies") if e["version_id"] == rr["version_id"]]
        self.assertEqual(len(edges), 2)
        by_dep = {e["depends_on_version_id"]: e for e in edges}
        self.assertEqual(by_dep[ra["version_id"]]["reference_name"], "work/a.csv")
        links = [v for v in s.rows("versions") if v["kind"] == "link"]
        self.assertEqual(len(links), 1)
        self.assertIn(links[0]["id"], by_dep)
        link_art = [a for a in s.rows("artifacts") if a["id"] == links[0]["artifact_id"]][0]
        self.assertEqual(link_art["filename"], "data/raw.csv")

    def test_save_input_path_reuses_existing_link(self):
        s, proj = self._store()
        write_file(proj / "data" / "raw.csv", "x\n1\n")
        r1 = self._save1(s, write_file(proj / "work" / "one.md", "1\n"), inputs=["data/raw.csv"])
        r2 = self._save1(s, write_file(proj / "work" / "two.md", "2\n"), inputs=["data/raw.csv"])
        links = [v for v in s.rows("versions") if v["kind"] == "link"]
        self.assertEqual(len(links), 1)
        edges = s.rows("dependencies")
        self.assertEqual(len(edges), 2)
        self.assertEqual({e["version_id"] for e in edges}, {r1["version_id"], r2["version_id"]})
        self.assertEqual({e["depends_on_version_id"] for e in edges}, {links[0]["id"]})

    def test_save_refuses_version_of_a_link(self):
        s, proj = self._store()
        link = s.link([write_file(proj / "outputs" / "run.json", "{}\n")], role="r", command="c")[0]
        other = write_file(proj / "work" / "other.json", "{ }\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, other, version_of=link["artifact_id"])
        self.assertIn("linked file", str(cm.exception))

    def test_copy_and_link_names_do_not_collide(self):
        s, proj = self._store()
        s.link([write_file(proj / "notes.md", "top\n")], role="r", command="c")
        r = self._save1(s, write_file(proj / "work" / "notes.md", "work\n"))
        arts = s.rows("artifacts")
        self.assertEqual(len(arts), 2)
        copies = [v for v in s.rows("versions") if v["kind"] == "copy"]
        self.assertEqual([v["artifact_id"] for v in copies], [r["artifact_id"]])

    def test_git_add_failure_is_a_warning(self):
        s, proj = self._store(git=True)
        lock = proj / ".git" / "index.lock"
        lock.write_bytes(b"")
        try:
            f = write_file(proj / "work" / "report.md", "r\n")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                r = self._save1(s, f)
            self.assertTrue((s.lab / r["storage_path"]).is_file())
            self.assertIn("warning: git add failed", err.getvalue())
        finally:
            if lock.exists():
                lock.unlink()

    def test_save_records_id_inputs(self):
        s, proj = self._store()
        ra = self._save1(s, write_file(proj / "work" / "a.csv", "a\n"))
        rb = self._save1(s, write_file(proj / "work" / "b.csv", "b\n"))
        rr = self._save1(
            s, write_file(proj / "work" / "report.md", "r\n"),
            inputs=[ra["version_id"], "art_" + rb["artifact_id"], ra["version_id"]],
        )
        edges = [e for e in s.rows("dependencies")]
        self.assertEqual(len(edges), 2)
        for e in edges:
            self.assertEqual(list(e), ["version_id", "depends_on_version_id", "reference_name"])
        self.assertEqual(
            [(e["version_id"], e["depends_on_version_id"], e["reference_name"]) for e in edges],
            [(rr["version_id"], ra["version_id"], "work/a.csv"), (rr["version_id"], rb["version_id"], "work/b.csv")],
        )

    def test_unknown_input_writes_nothing(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "report.md", "r\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, f, inputs=["no-such-id-123"])
        self.assertIn("unknown input", str(cm.exception))
        self.assertFalse(s.store.exists())
        for ledger in artifacts.LEDGERS:
            self.assertFalse((s.root / f"{ledger}.jsonl").exists())

    def test_save_outside_project_root_is_refused(self):
        s, proj = self._store()
        f = write_file(self.t / "elsewhere" / "report.md", "r\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, f)
        self.assertIn("outside", str(cm.exception))
        self.assertFalse(s.store.exists())

    def test_save_requires_existing_files(self):
        s, proj = self._store()
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, proj / "work" / "missing.md")
        self.assertIn("not a file", str(cm.exception))
        (proj / "work").mkdir(parents=True, exist_ok=True)
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, proj / "work")
        self.assertIn("not a file", str(cm.exception))

    def test_relative_paths_resolve_against_project_root(self):
        s, proj = self._store()
        write_file(proj / "work" / "report.md", "r\n")
        res = s.save(["work/report.md"], role="r", command="c")
        self.assertEqual(len(res), 1)
        self.assertEqual(s.rows("artifacts")[0]["filename"], "work/report.md")

    def test_working_data_replaces_previous_bytes(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "state.json", "{}\n")
        r1 = self._save1(s, f, destination="working_data")
        write_file(f, '{"a": 1}\n')
        r2 = self._save1(s, f, destination="working_data", version_of=r1["artifact_id"])
        d = s.store / r1["artifact_id"]
        self.assertFalse((d / "v001_state.json").exists())
        self.assertTrue((d / "v002_state.json").is_file())
        status = {v["id"]: v["status"] for v in s.rows("versions")}
        self.assertEqual(status[r1["version_id"]], "replaced")
        self.assertEqual(status[r2["version_id"]], "ok")
        self.assertEqual(s.rows("artifacts")[0]["destination"], "working_data")

    def _changed(self, f, text):
        write_file(f, text)
        return f

    def test_working_data_is_sticky(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "state.json", "{}\n")
        r1 = self._save1(s, f, destination="working_data")
        r2 = self._save1(s, self._changed(f, '{"a": 1}\n'), version_of=r1["artifact_id"])
        d = s.store / r1["artifact_id"]
        self.assertFalse((d / "v001_state.json").exists())
        self.assertTrue((d / "v002_state.json").is_file())
        status = {v["id"]: v["status"] for v in s.rows("versions")}
        self.assertEqual(status[r1["version_id"]], "replaced")
        v2 = [v for v in s.rows("versions") if v["id"] == r2["version_id"]][0]
        self.assertEqual(v2["destination"], "working_data")
        self.assertEqual(s.rows("artifacts")[0]["destination"], "working_data")

    def test_explicit_working_data_never_deletes_snapshots(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "report.md", "one\n")
        r1 = self._save1(s, f)
        aid = r1["artifact_id"]
        for text in ("two\n", "three\n"):
            self._save1(s, self._changed(f, text), version_of=aid)
        r4 = self._save1(s, self._changed(f, "four\n"), version_of=aid, destination="working_data")
        d = s.store / aid
        for n in (1, 2, 3):
            self.assertTrue((d / f"v{n:03d}_report.md").is_file())
        self.assertEqual([v["status"] for v in s.rows("versions")], ["ok"] * 4)
        r5 = self._save1(s, self._changed(f, "five\n"), version_of=aid, destination="working_data")
        status = {v["version_number"]: v["status"] for v in s.rows("versions")}
        self.assertEqual(status, {1: "ok", 2: "ok", 3: "ok", 4: "replaced", 5: "ok"})
        self.assertFalse((d / "v004_report.md").exists())
        for n in (1, 2, 3, 5):
            self.assertTrue((d / f"v{n:03d}_report.md").is_file())
        self.assertEqual(s.rows("artifacts")[0]["destination"], "snapshot")
        self.assertEqual(r4["version_number"], 4)
        self.assertEqual(r5["version_number"], 5)

    def test_snapshot_milestone_in_working_data_artifact_is_kept(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "state.json", "{}\n")
        r1 = self._save1(s, f, destination="working_data")
        aid = r1["artifact_id"]
        self._save1(s, self._changed(f, '{"a": 1}\n'), version_of=aid, destination="snapshot")
        self._save1(s, self._changed(f, '{"a": 2}\n'), version_of=aid)
        status = {v["version_number"]: v["status"] for v in s.rows("versions")}
        self.assertEqual(status, {1: "replaced", 2: "ok", 3: "ok"})
        d = s.store / aid
        self.assertTrue((d / "v002_state.json").is_file())
        self.assertFalse((d / "v001_state.json").exists())

    def test_invalid_destination_is_refused(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "state.json", "{}\n")
        with self.assertRaises(artifacts.StoreError):
            self._save1(s, f, destination="elsewhere")
        self.assertFalse(s.store.exists())

    def test_replacement_marks_ledger_before_unlinking(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "state.json", "{}\n")
        r1 = self._save1(s, f, destination="working_data")
        self._changed(f, '{"a": 1}\n')
        with mock.patch.object(artifacts.Path, "unlink", side_effect=OSError("locked")):
            with self.assertRaises(OSError):
                self._save1(s, f, version_of=r1["artifact_id"])
        status = {v["id"]: v["status"] for v in s.rows("versions")}
        self.assertEqual(status[r1["version_id"]], "replaced")

    def test_dependency_without_artifact_is_store_error(self):
        s, proj = self._store()
        ghost = {name: None for name in VERSION_FIELDS}
        ghost.update({
            "id": "ghostversion0001", "artifact_id": "ghostartifact0001", "version_number": 1,
            "kind": "copy", "content_type": "text/plain", "size_bytes": 1, "sha256": "0" * 64,
            "storage_path": "artifacts/store/ghostartifact0001/v001_x.txt", "agent_name": "r",
            "producing_command": "c", "is_intermediate": False, "is_checkpoint": False,
            "destination": "snapshot", "created_at": artifacts.now_iso(), "source": "lab", "status": "ok",
        })
        s.append("versions", ghost)
        f = write_file(proj / "work" / "report.md", "r\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, f, inputs=["ghostversion0001"])
        self.assertIn("has no artifact row", str(cm.exception))

    def test_unknown_input_after_a_path_input_writes_nothing(self):
        s, proj = self._store()
        write_file(proj / "data" / "raw.csv", "x\n1\n")
        f = write_file(proj / "work" / "new.md", "n\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, f, inputs=["data/raw.csv", "nosuchid123"])
        self.assertIn("unknown input", str(cm.exception))
        self.assertFalse((s.root / "versions.jsonl").exists())
        self.assertFalse((s.root / "artifacts.jsonl").exists())

    def test_directory_input_says_not_a_file(self):
        s, proj = self._store()
        write_file(proj / "data" / "raw.csv", "x\n1\n")
        f = write_file(proj / "work" / "new.md", "n\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, f, inputs=["data"])
        self.assertIn("not a file", str(cm.exception))
        self.assertFalse((s.root / "versions.jsonl").exists())

    def test_replacement_never_deletes_outside_the_store(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "state.json", "{}\n")
        r1 = self._save1(s, f, destination="working_data")
        outside = write_file(s.lab / "outside.txt", "precious\n")
        rows = s.rows("versions")
        rows[0]["storage_path"] = "outside.txt"
        s.rewrite("versions", rows)
        before = s.rows("versions")
        self._changed(f, '{"a": 1}\n')
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, f, version_of=r1["artifact_id"])
        self.assertIn("outside the store", str(cm.exception))
        self.assertTrue(outside.is_file())
        self.assertEqual(s.rows("versions"), before)

    def test_save_marks_checkpoint_and_intermediate(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "report.md", "r\n")
        self._save1(s, f, checkpoint=True, intermediate=True, description="a note", environment="py3.11")
        v = s.rows("versions")[0]
        self.assertIs(v["is_checkpoint"], True)
        self.assertIs(v["is_intermediate"], True)
        self.assertEqual(v["code_description"], "a note")
        self.assertEqual(v["environment"], "py3.11")

    def test_csv_content_type_is_text_csv(self):
        s, proj = self._store()
        self._save1(s, write_file(proj / "work" / "a.csv", "a\n1\n"))
        self.assertEqual(s.rows("versions")[0]["content_type"], "text/csv")

    def test_save_two_files_in_one_call(self):
        s, proj = self._store()
        f1 = write_file(proj / "work" / "a.md", "a\n")
        f2 = write_file(proj / "work" / "b.md", "b\n")
        res = s.save([f1, f2], role="r", command="c")
        self.assertEqual(len(res), 2)
        self.assertNotEqual(res[0]["artifact_id"], res[1]["artifact_id"])
        names = {a["id"]: a["filename"] for a in s.rows("artifacts")}
        self.assertEqual([names[r["artifact_id"]] for r in res], ["work/a.md", "work/b.md"])

    def _cached(self, proj):
        p = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=proj, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout.split()

    def test_save_stages_written_files(self):
        s, proj = self._store(git=True)
        f = write_file(proj / "work" / "report.md", "r\n")
        r = self._save1(s, f)
        staged = self._cached(proj)
        self.assertIn(f"research_lab/artifacts/store/{r['artifact_id']}/v001_report.md", staged)
        self.assertIn("research_lab/artifacts/artifacts.jsonl", staged)
        self.assertIn("research_lab/artifacts/versions.jsonl", staged)

    def test_working_data_replacement_is_staged(self):
        s, proj = self._store(git=True)
        f = write_file(proj / "work" / "state.json", "{}\n")
        r1 = self._save1(s, f, destination="working_data")
        write_file(f, '{"a": 1}\n')
        self._save1(s, f, destination="working_data", version_of=r1["artifact_id"])
        p = subprocess.run(
            ["git", "ls-files", "research_lab/artifacts/store"], cwd=proj, capture_output=True, text=True
        )
        listed = p.stdout.split()
        self.assertIn(f"research_lab/artifacts/store/{r1['artifact_id']}/v002_state.json", listed)
        self.assertNotIn(f"research_lab/artifacts/store/{r1['artifact_id']}/v001_state.json", listed)
        self._cached(proj)

    def test_resolve_id_forms(self):
        s, proj = self._store()
        r = self._save1(s, write_file(proj / "work" / "report.md", "r\n"))
        vid, aid = r["version_id"], r["artifact_id"]
        self.assertEqual(s.resolve_id(vid), ("version", vid))
        self.assertEqual(s.resolve_id(aid), ("artifact", aid))
        self.assertEqual(s.resolve_id("art_" + aid), ("artifact", aid))
        self.assertEqual(s.resolve_id(vid[:8]), ("version", vid))
        with self.assertRaises(artifacts.UnknownId):
            s.resolve_id("nope")
        with self.assertRaises(artifacts.UnknownId) as cm:
            s.resolve_id(vid[:3])
        self.assertIn("6 characters", str(cm.exception))
        base = {
            "folder": None, "is_user_upload": False, "is_ephemeral": False, "superseded_by": None,
            "retention": None, "destination": "snapshot", "created_at": artifacts.now_iso(), "source": "lab",
        }
        s.append("artifacts", {"id": "abcdef0011", "filename": "x", "latest_version_id": None, **base})
        s.append("artifacts", {"id": "abcdef0022", "filename": "y", "latest_version_id": None, **base})
        with self.assertRaises(artifacts.AmbiguousId):
            s.resolve_id("abcdef00")

    def test_invalid_threshold_is_store_error(self):
        lab = make_lab(self.t, {"lfs": {"thresholdMB": "big"}})
        with self.assertRaises(artifacts.StoreError) as cm:
            artifacts.LabStore(lab)
        self.assertIn("thresholdMB", str(cm.exception))

    def test_cli_save_prints_json(self):
        lab = make_lab(self.t)
        f = write_file(lab.parent / "work" / "report.md", "r\n")
        code, out, err = run_cli(
            ["--lab", str(lab), "save", str(f), "--role", "r", "--command", "c", "--no-stage"]
        )
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["version_number"], 1)

    def test_cli_error_has_no_traceback(self):
        lab = make_lab(self.t)
        code, out, err = run_cli(
            ["--lab", str(lab), "save", str(lab.parent / "nope.md"), "--role", "r", "--command", "c"]
        )
        self.assertEqual(code, 1)
        self.assertTrue(err.startswith("error:"), err)
        self.assertNotIn("Traceback", err)
        code, out, err = run_cli(
            ["--lab", str(self.t / "nowhere"), "save", "x", "--role", "r", "--command", "c"]
        )
        self.assertEqual(code, 1)
        self.assertIn("lab directory not found", err)

    def test_lab_flag_at_project_root_is_refused(self):
        lab = make_lab(self.t)
        proj = lab.parent
        f = write_file(proj / "work" / "report.md", "r\n")
        code, out, err = run_cli(
            ["--lab", str(proj), "save", str(f), "--role", "r", "--command", "c", "--no-stage"]
        )
        self.assertEqual(code, 1)
        self.assertIn("not a research_lab", err)
        self.assertIn("did you mean", err)
        self.assertFalse((proj / "artifacts").exists())

    def test_os_error_is_reported_without_traceback(self):
        lab = make_lab(self.t)
        f = write_file(lab.parent / "work" / "report.md", "r\n")
        boom = PermissionError(13, "Permission denied", "versions.jsonl")
        with mock.patch.object(artifacts.os, "replace", side_effect=boom):
            code, out, err = run_cli(
                ["--lab", str(lab), "save", str(f), "--role", "r", "--command", "c", "--no-stage"]
            )
        self.assertEqual(code, 1)
        self.assertTrue(err.startswith("error: Permission denied"), err)
        self.assertNotIn("Traceback", err)

    def test_two_files_with_one_name_in_one_call_are_two_artifacts(self):
        s, proj = self._store()
        f1 = write_file(proj / "a" / "report.md", "one\n")
        f2 = write_file(proj / "b" / "report.md", "two\n")
        res = s.save([f1, f2], role="r", command="c")
        self.assertEqual(len(res), 2)
        self.assertNotEqual(res[0]["artifact_id"], res[1]["artifact_id"])
        self.assertEqual([a["filename"] for a in s.rows("artifacts")], ["a/report.md", "b/report.md"])

    def test_one_path_twice_in_one_call_is_refused(self):
        s, proj = self._store()
        f1 = write_file(proj / "a" / "report.md", "one\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            s.save([f1, f1], role="r", command="c")
        self.assertIn("a/report.md is named twice in this call", str(cm.exception))
        self.assertEqual(s.rows("versions"), [])

    def test_cli_directory_input_relative_to_cwd_says_not_a_file(self):
        lab = make_lab(self.t)
        proj = lab.parent
        (proj / "work" / "sub").mkdir(parents=True)
        write_file(proj / "work" / "new.md", "n\n")
        with contextlib.chdir(proj / "work"):
            code, out, err = run_cli(
                ["--lab", str(lab), "save", "new.md", "--inputs", "sub", "--role", "r", "--command", "c", "--no-stage"]
            )
        self.assertEqual(code, 1)
        self.assertIn("not a file", err)

    def test_docstring_lists_inputs_last(self):
        doc = artifacts.__doc__
        for start in ("python artifacts.py save", "python artifacts.py link"):
            block = doc[doc.index(start):].split("\n\n")[0]
            options = block.replace("\n", " ").split(" [")
            self.assertTrue(options[-1].startswith("--inputs ID_OR_PATH ...]"), block)
        self.assertIn("--inputs takes one or more values; put it after the files or repeat it.", doc)

    def test_symlink_out_of_the_project_is_refused(self):
        s, proj = self._store()
        outside = write_file(self.t / "outside.md", "secret\n")
        (proj / "work").mkdir(parents=True)
        link = proj / "work" / "escape.md"
        try:
            os.symlink(outside, link)
        except (OSError, NotImplementedError):
            self.skipTest("no symlink privilege")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, link)
        self.assertIn("outside the project root", str(cm.exception))
        other = write_file(proj / "work" / "other.md", "o\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, other, inputs=[str(link)])
        self.assertIn("outside the project root", str(cm.exception))

    @unittest.skipUnless(sys.platform == "win32", "directory junctions are a Windows feature")
    def test_junction_out_of_the_project_is_refused(self):
        # A junction needs no symlink privilege, so this runs where the symlink test skips.
        import _winapi

        s, proj = self._store()
        outside_dir = self.t / "outside"
        write_file(outside_dir / "secret.md", "secret\n")
        (proj / "work").mkdir(parents=True)
        junction = proj / "work" / "escape"
        _winapi.CreateJunction(str(outside_dir), str(junction))
        self.addCleanup(os.rmdir, junction)
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, junction / "secret.md")
        self.assertIn("outside the project root", str(cm.exception))
        other = write_file(proj / "work" / "other.md", "o\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, other, inputs=[str(junction / "secret.md")])
        self.assertIn("outside the project root", str(cm.exception))
        self.assertFalse((s.root / "versions.jsonl").exists())

    def test_repeated_inputs_flag_keeps_every_input(self):
        s, proj = self._store()
        lab = str(s.lab)
        ids = []
        for name in ("a.csv", "b.csv"):
            f = write_file(proj / "data" / name, name + "\n")
            ids.append(s.link([f], role="r", command="c")[0]["version_id"])
        target = write_file(proj / "work" / "report.md", "r\n")
        code, out, err = run_cli([
            "--lab", lab, "save", str(target), "--role", "r", "--command", "c", "--no-stage",
            "--inputs", ids[0], "--inputs", ids[1],
        ])
        self.assertEqual(code, 0, err)
        vid = json.loads(out)[0]["version_id"]
        edges = [e["depends_on_version_id"] for e in s.rows("dependencies") if e["version_id"] == vid]
        self.assertEqual(sorted(edges), sorted(ids))

    def test_link_writes_the_artifact_row_first(self):
        s, proj = self._store()
        f = write_file(proj / "outputs" / "run.json", "{}\n")
        calls: list[str] = []
        real_append, real_rewrite = artifacts.LabStore.append, artifacts.LabStore.rewrite

        def spy_append(self, ledger, row):
            calls.append(ledger)
            return real_append(self, ledger, row)

        def spy_rewrite(self, ledger, rows):
            calls.append(ledger)
            return real_rewrite(self, ledger, rows)

        with mock.patch.object(artifacts.LabStore, "append", autospec=True, side_effect=spy_append), \
                mock.patch.object(artifacts.LabStore, "rewrite", autospec=True, side_effect=spy_rewrite):
            s.link([f], role="r", command="c")
        self.assertEqual(calls[0], "artifacts")
        self.assertIn("versions", calls)

    def test_comma_separated_inputs_get_a_hint(self):
        s, proj = self._store()
        ids = [
            s.link([write_file(proj / "data" / name, name + "\n")], role="r", command="c")[0]["version_id"]
            for name in ("a.csv", "b.csv")
        ]
        before = s.rows("versions")
        target = write_file(proj / "work" / "report.md", "r\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, target, inputs=[",".join(ids)])
        self.assertIn("not commas", str(cm.exception))
        self.assertEqual(s.rows("versions"), before)
        self.assertEqual(len(before), 2)


if __name__ == "__main__":
    unittest.main()
