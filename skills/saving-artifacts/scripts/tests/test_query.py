import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts
from _helpers import make_git_lab, make_lab, run_cli, write_file

SEARCH_KEYS = [
    "artifact_id", "filename", "latest_version_id", "version_number", "kind",
    "content_type", "size_bytes", "code_description", "created_at", "status",
]


class QueryTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self._tmp.cleanup)
        self.t = Path(self._tmp.name)

    def _store(self):
        lab = make_lab(self.t)
        s = artifacts.LabStore(lab)
        return s, s.project_root

    def _save1(self, s, path, **kw):
        kw.setdefault("role", "paper-author")
        kw.setdefault("task", "TASK-0001")
        return s.save([path], **kw)[0]

    def _link1(self, s, path, **kw):
        kw.setdefault("role", "analyst")
        kw.setdefault("command", "python run.py")
        return s.link([path], **kw)[0]

    # ---- link ----------------------------------------------------------

    def test_link_records_repo_file_without_copying(self):
        s, proj = self._store()
        f = write_file(proj / "outputs" / "run.json", '{"a": 1}\n')
        r = self._link1(s, f)
        self.assertEqual(r["storage_path"], "link:outputs/run.json")
        self.assertIs(r["reused"], False)
        self.assertIs(r["lfs"], False)
        self.assertEqual(r["version_number"], 1)
        v = s.rows("versions")[0]
        self.assertEqual(v["kind"], "link")
        self.assertEqual(v["storage_path"], "link:outputs/run.json")
        self.assertEqual(v["sha256"], hashlib.sha256(f.read_bytes()).hexdigest())
        self.assertEqual(v["size_bytes"], f.stat().st_size)
        self.assertEqual(v["content_type"], "application/json")
        self.assertEqual(v["agent_name"], "analyst")
        self.assertEqual(v["status"], "ok")
        self.assertEqual(s.rows("artifacts")[0]["filename"], "outputs/run.json")
        self.assertFalse(s.archive.exists())

    def test_link_outside_project_is_refused(self):
        s, proj = self._store()
        f = write_file(self.t / "elsewhere" / "run.json", "{}\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._link1(s, f)
        self.assertIn("outside", str(cm.exception))
        self.assertEqual(s.rows("versions"), [])

    def test_link_same_unchanged_path_twice_reuses_version(self):
        s, proj = self._store()
        f = write_file(proj / "outputs" / "run.json", "{}\n")
        r1 = self._link1(s, f)
        n = len(s.rows("versions"))
        r2 = self._link1(s, f)
        self.assertEqual(r2["version_id"], r1["version_id"])
        self.assertIs(r2["reused"], True)
        self.assertEqual(len(s.rows("versions")), n)

    def test_link_changed_file_adds_version_and_marks_old_changed(self):
        s, proj = self._store()
        f = write_file(proj / "outputs" / "run.json", "{}\n")
        r1 = self._link1(s, f)
        write_file(f, '{"b": 2}\n')
        r2 = self._link1(s, f)
        self.assertEqual(r2["version_number"], 2)
        self.assertEqual(r2["artifact_id"], r1["artifact_id"])
        rows = {v["id"]: v for v in s.rows("versions")}
        self.assertEqual(rows[r2["version_id"]]["parent_version_id"], r1["version_id"])
        self.assertEqual(rows[r1["version_id"]]["status"], "changed")
        self.assertEqual(rows[r2["version_id"]]["status"], "ok")
        self.assertEqual(s.rows("artifacts")[0]["latest_version_id"], r2["version_id"])

    # ---- search --------------------------------------------------------

    def test_search_matches_filename_and_description_case_insensitive(self):
        s, proj = self._store()
        self._save1(s, write_file(proj / "work" / "report.md", "r\n"))
        self._save1(s, write_file(proj / "work" / "notes.md", "n\n"), description="Draft REPORT outline")
        self._save1(s, write_file(proj / "work" / "data.csv", "d\n"))
        found = s.search("report")
        self.assertEqual({r["filename"] for r in found}, {"work/report.md", "work/notes.md"})
        for r in found:
            self.assertEqual(list(r), SEARCH_KEYS)
        self.assertEqual(len(s.search("")), 3)

    def test_search_newest_first_by_latest_version(self):
        s, proj = self._store()
        fa = write_file(proj / "work" / "a.md", "1\n")
        ra = self._save1(s, fa)
        self._save1(s, write_file(proj / "work" / "b.md", "b\n"))
        write_file(fa, "2\n")
        self._save1(s, fa, version_of=ra["artifact_id"])
        self.assertEqual([r["filename"] for r in s.search("")], ["work/a.md", "work/b.md"])

    def test_search_hides_intermediate_by_default(self):
        s, proj = self._store()
        self._save1(s, write_file(proj / "work" / "a.md", "a\n"))
        self._save1(s, write_file(proj / "work" / "tmp.md", "t\n"), intermediate=True)
        self.assertEqual([r["filename"] for r in s.search("")], ["work/a.md"])
        self.assertEqual(
            {r["filename"] for r in s.search("", include_intermediate=True)}, {"work/a.md", "work/tmp.md"}
        )

    # ---- path ----------------------------------------------------------

    def test_path_for_copy_link_and_prefixes(self):
        s, proj = self._store()
        r = self._save1(s, write_file(proj / "work" / "report.md", "r\n"))
        stored = (s.lab / r["storage_path"]).resolve()
        vid, aid = r["version_id"], r["artifact_id"]
        for ref in (vid, aid, "art_" + aid, vid[:8]):
            self.assertEqual(s.path(ref).resolve(), stored, ref)
        f = write_file(proj / "outputs" / "run.json", "{}\n")
        lr = self._link1(s, f)
        self.assertEqual(s.path(lr["version_id"]).resolve(), f.resolve())

    def test_path_missing_link_sets_status(self):
        s, proj = self._store()
        f = write_file(proj / "outputs" / "run.json", "{}\n")
        lr = self._link1(s, f)
        f.unlink()
        with self.assertRaises(artifacts.MissingFile) as cm:
            s.path(lr["version_id"])
        self.assertIn("missing", str(cm.exception))
        self.assertEqual(cm.exception.version_id, lr["version_id"])
        self.assertIn("outputs/run.json", cm.exception.path)
        self.assertEqual(s.rows("versions")[0]["status"], "missing")
        write_file(f, "{}\n")
        self.assertEqual(s.path(lr["version_id"]).resolve(), f.resolve())
        self.assertEqual(s.rows("versions")[0]["status"], "ok")

    def test_path_absolute_link_storage(self):
        s, proj = self._store()
        outside = write_file(self.t / "elsewhere" / "data.csv", "a\n")
        base = {
            "folder": None, "is_user_upload": False, "is_ephemeral": False, "superseded_by": None,
            "retention": None, "destination": "snapshot", "created_at": artifacts.now_iso(), "source": "lab",
        }
        s.append("artifacts", {"id": "aaaaaaaa-0001", "filename": "data.csv", "latest_version_id": "vvvvvvvv-0001", **base})
        s.append("versions", {
            "id": "vvvvvvvv-0001", "artifact_id": "aaaaaaaa-0001", "version_number": 1,
            "parent_version_id": None, "kind": "link", "content_type": "text/csv", "size_bytes": 2,
            "sha256": "0" * 64, "storage_path": "link:" + outside.resolve().as_posix(),
            "agent_name": "importer", "producing_command": "import", "producing_session": None,
            "code_description": None, "is_intermediate": False, "is_checkpoint": False,
            "environment": None, "created_at": artifacts.now_iso(), "source": "lab", "status": "ok",
        })
        self.assertEqual(s.path("vvvvvvvv-0001").resolve(), outside.resolve())

    def test_path_of_replaced_version_raises(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "state.json", "{}\n")
        r1 = self._save1(s, f, destination="working")
        write_file(f, '{"a": 1}\n')
        self._save1(s, f, destination="working", version_of=r1["artifact_id"])
        with self.assertRaises(artifacts.StoreError) as cm:
            s.path(r1["version_id"])
        self.assertIn("replaced", str(cm.exception))
        self.assertEqual({v["status"] for v in s.rows("versions")}, {"replaced", "ok"})

    def test_cli_path_missing_prints_status_and_exits_1(self):
        s, proj = self._store()
        f = write_file(proj / "outputs" / "run.json", "{}\n")
        lr = self._link1(s, f)
        lab = str(s.lab)
        code, out, err = run_cli(["--lab", lab, "path", lr["version_id"]])
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version_id"], lr["version_id"])
        self.assertTrue(data["path"].endswith("outputs/run.json"))
        f.unlink()
        code, out, err = run_cli(["--lab", lab, "path", lr["version_id"]])
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertEqual(data["status"], "missing")
        self.assertEqual(data["version_id"], lr["version_id"])
        self.assertIn("path", data)
        self.assertIn("error: missing", err)
        self.assertNotIn("Traceback", err)

    def test_path_reports_lfs_pointer(self):
        s, proj = self._store()
        r = self._save1(s, write_file(proj / "work" / "big.bin", b"z" * 2000))
        stored = s.lab / r["storage_path"]
        stored.write_bytes(b"version https://git-lfs.github.com/spec/v1\noid sha256:" + b"0" * 64 + b"\nsize 2000\n")
        code, out, err = run_cli(["--lab", str(s.lab), "path", r["version_id"]])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["status"], "pointer")
        self.assertIn("git lfs pull", err)
        self.assertNotIn("Traceback", err)
        with self.assertRaises(artifacts.LfsPointer) as cm:
            s.path(r["version_id"])
        self.assertIsInstance(cm.exception, artifacts.StoreError)
        self.assertEqual(cm.exception.version_id, r["version_id"])

    def test_path_with_lfs_like_text_of_recorded_size_is_ok(self):
        s, proj = self._store()
        r = self._save1(s, write_file(proj / "work" / "note.txt", "version https://git-lfs.github.com/spec/v1\nabc\n"))
        code, out, err = run_cli(["--lab", str(s.lab), "path", r["version_id"]])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["status"], "ok")

    def test_cmd_path_resolves_the_reference_once(self):
        s, proj = self._store()
        r = self._save1(s, write_file(proj / "work" / "report.md", "r\n"))
        with mock.patch.object(
            artifacts.LabStore, "_version_row", autospec=True, side_effect=artifacts.LabStore._version_row
        ) as spy:
            code, out, err = run_cli(["--lab", str(s.lab), "path", r["version_id"]])
        self.assertEqual(code, 0, err)
        self.assertEqual(spy.call_count, 1)

    def test_path_stages_a_status_change(self):
        lab = make_git_lab(self.t)
        s = artifacts.LabStore(lab)
        proj = s.project_root
        r = self._save1(s, write_file(proj / "work" / "report.md", "r\n"))
        stored = s.lab / r["storage_path"]
        data = stored.read_bytes()
        stored.unlink()

        def unstaged() -> str:
            return subprocess.run(
                ["git", "diff", "--name-only", "--", "research_lab/artifacts/versions.jsonl"],
                cwd=proj, capture_output=True, text=True, check=True,
            ).stdout.strip()

        code, out, err = run_cli(["--lab", str(s.lab), "path", r["version_id"]])
        self.assertEqual(code, 1)
        self.assertEqual(s.rows("versions")[0]["status"], "missing")
        self.assertEqual(unstaged(), "")
        stored.write_bytes(data)
        code, out, err = run_cli(["--lab", str(s.lab), "path", r["version_id"], "--no-stage"])
        self.assertEqual(code, 0, err)
        self.assertEqual(s.rows("versions")[0]["status"], "ok")
        self.assertIn("versions.jsonl", unstaged())

    # ---- lineage and graph --------------------------------------------

    def test_provenance_lists_inputs_and_findings(self):
        s, proj = self._store()
        ra = self._save1(s, write_file(proj / "work" / "a.csv", "a\n"))
        rr = self._save1(s, write_file(proj / "work" / "report.md", "r\n"), inputs=[ra["version_id"]])
        lin = s.provenance(rr["version_id"])
        self.assertEqual(lin["version"]["id"], rr["version_id"])
        self.assertEqual(lin["artifact"]["filename"], "work/report.md")
        self.assertEqual(
            lin["inputs"],
            [{
                "version_id": ra["version_id"],
                "filename": "work/a.csv",
                "path": (s.lab / ra["storage_path"]).as_posix(),
                "exists": True,
            }],
        )
        self.assertEqual(lin["findings"], [])

    def test_provenance_missing_input_does_not_raise(self):
        s, proj = self._store()
        raw = write_file(proj / "data" / "raw.csv", "x\n")
        rr = self._save1(s, write_file(proj / "work" / "report.md", "r\n"), inputs=["data/raw.csv"])
        raw.unlink()
        lin = s.provenance(rr["version_id"])
        self.assertEqual(len(lin["inputs"]), 1)
        self.assertIs(lin["inputs"][0]["exists"], False)
        self.assertEqual(lin["inputs"][0]["filename"], "data/raw.csv")
        link = [v for v in s.rows("versions") if v["kind"] == "link"][0]
        self.assertEqual(link["status"], "ok")

    def _chain(self, s, proj):
        ra = self._save1(s, write_file(proj / "work" / "a.md", "a\n"))
        rb = self._save1(s, write_file(proj / "work" / "b.md", "b\n"), inputs=[ra["version_id"]])
        rc = self._save1(s, write_file(proj / "work" / "c.md", "c\n"), inputs=[rb["version_id"]])
        return ra, rb, rc

    def test_graph_walks_two_levels(self):
        s, proj = self._store()
        ra, rb, rc = self._chain(s, proj)
        g = s.graph(rc["version_id"])
        self.assertEqual(g["root"], rc["version_id"])
        self.assertEqual(len(g["nodes"]), 3)
        self.assertEqual(g["nodes"][0]["version_id"], rc["version_id"])
        self.assertEqual(
            g["nodes"][0],
            {"version_id": rc["version_id"], "artifact_id": rc["artifact_id"], "filename": "work/c.md", "version_number": 1},
        )
        self.assertEqual(
            g["edges"],
            [
                {"from": rc["version_id"], "to": rb["version_id"], "reference_name": "work/b.md"},
                {"from": rb["version_id"], "to": ra["version_id"], "reference_name": "work/a.md"},
            ],
        )

    def test_graph_handles_dangling_and_cycles(self):
        s, proj = self._store()
        ra, rb, rc = self._chain(s, proj)
        s.append("dependencies", {
            "version_id": ra["version_id"], "depends_on_version_id": "ffffffffffff", "reference_name": "ghost",
        })
        s.append("dependencies", {
            "version_id": ra["version_id"], "depends_on_version_id": rc["version_id"], "reference_name": "c.md",
        })
        g = s.graph(rc["version_id"])
        ids = [n["version_id"] for n in g["nodes"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn(
            {"version_id": "ffffffffffff", "artifact_id": None, "filename": None, "version_number": None},
            g["nodes"],
        )

    # ---- CLI -----------------------------------------------------------

    def test_cli_link_search_provenance_graph_print_json(self):
        s, proj = self._store()
        lab = str(s.lab)
        ra = self._save1(s, write_file(proj / "work" / "a.md", "a\n"))
        write_file(proj / "outputs" / "run.json", "{}\n")
        code, out, err = run_cli([
            "--lab", lab, "link", str(proj / "outputs" / "run.json"),
            "--role", "analyst", "--task", "c", "--inputs", ra["version_id"], "--no-stage",
        ])
        self.assertEqual(code, 0, err)
        linked = json.loads(out)
        self.assertIsInstance(linked, list)
        code, out, err = run_cli(["--lab", lab, "search", "run"])
        self.assertEqual(code, 0, err)
        self.assertIsInstance(json.loads(out), list)
        code, out, err = run_cli(["--lab", lab, "provenance", linked[0]["version_id"]])
        self.assertEqual(code, 0, err)
        self.assertIsInstance(json.loads(out), dict)
        code, out, err = run_cli(["--lab", lab, "graph", linked[0]["version_id"]])
        self.assertEqual(code, 0, err)
        self.assertIsInstance(json.loads(out), dict)


if __name__ == "__main__":
    unittest.main()
