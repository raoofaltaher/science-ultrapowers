import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts
from _helpers import make_lab, run_cli, write_file


class ResolveTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self._tmp.cleanup)
        self.t = Path(self._tmp.name)
        self.lab = make_lab(self.t)
        self.s = artifacts.LabStore(self.lab)
        self.proj = self.s.project_root
        self.docs = self.proj / "docs"

    def _save(self, name="report.md", text="# report\n", **kw):
        f = write_file(self.proj / "work" / name, text)
        kw.setdefault("role", "paper-author")
        kw.setdefault("command", "pytest")
        return self.s.save([f], **kw)[0]

    def test_resolve_full_version_marker(self):
        r = self._save()
        out = self.s.resolve_markers(f"See {{{{artifact:{r['version_id']}}}}}.", relative_to=self.docs)
        aid = r["artifact_id"]
        self.assertEqual(out, f"See [report.md](../research_lab/artifacts/store/{aid}/v001_report.md).")

    def test_resolve_art_marker_points_at_latest(self):
        r1 = self._save(text="one\n")
        r2 = self._save(text="two\n", version_of=r1["artifact_id"])
        aid = r1["artifact_id"]
        out = self.s.resolve_markers(f"{{{{artifact:art_{aid}}}}}", relative_to=self.docs)
        self.assertEqual(out, f"[report.md](../research_lab/artifacts/store/{aid}/v002_report.md)")
        out1 = self.s.resolve_markers(f"{{{{artifact:{r1['version_id']}}}}}", relative_to=self.docs)
        self.assertEqual(out1, f"[report.md](../research_lab/artifacts/store/{aid}/v001_report.md)")
        self.assertNotEqual(r1["version_id"], r2["version_id"])

    def test_resolve_unique_prefix(self):
        r = self._save()
        full = self.s.resolve_markers(f"{{{{artifact:{r['version_id']}}}}}", relative_to=self.docs)
        short = self.s.resolve_markers(f"{{{{artifact:{r['version_id'][:8]}}}}}", relative_to=self.docs)
        self.assertEqual(short, full)

    def test_resolve_ambiguous_prefix_raises(self):
        r = self._save()
        versions = self.s.rows("versions")
        template = versions[0]
        for vid in ("abcdef0011", "abcdef0022"):
            row = dict(template)
            row["id"] = vid
            row["artifact_id"] = r["artifact_id"]
            row["kind"] = "copy"
            self.s.append("versions", row)
        with self.assertRaises(artifacts.AmbiguousId):
            self.s.resolve_markers("{{artifact:abcdef00}}", relative_to=self.docs)

    def test_resolve_unknown_id_raises(self):
        self._save()
        with self.assertRaises(artifacts.UnknownId):
            self.s.resolve_markers("{{artifact:nope-nope}}", relative_to=self.docs)

    def test_resolve_link_marker(self):
        f = write_file(self.proj / "outputs" / "run.json", '{"a": 1}\n')
        r = self.s.link([f], role="analyst", command="python run.py")[0]
        docs = self.proj / "docs"
        out = self.s.resolve_markers(f"{{{{artifact:{r['version_id']}}}}}", relative_to=docs)
        self.assertEqual(out, "[run.json](../outputs/run.json)")

    def test_resolve_wraps_paths_with_spaces(self):
        r = self._save(name="my report.md")
        out = self.s.resolve_markers(f"{{{{artifact:{r['version_id']}}}}}", relative_to=self.docs)
        aid = r["artifact_id"]
        self.assertEqual(out, f"[my report.md](<../research_lab/artifacts/store/{aid}/v001_my report.md>)")

    def test_resolve_leaves_text_without_markers_unchanged(self):
        text = "no markers {{other}} here"
        self.assertEqual(self.s.resolve_markers(text, relative_to=self.docs), text)

    def test_resolve_several_markers_in_one_text(self):
        r1 = self._save()
        f = write_file(self.proj / "outputs" / "run.json", "{}\n")
        r2 = self.s.link([f], role="analyst", command="python run.py")[0]
        text = f"A {{{{artifact:{r1['version_id']}}}}} and B {{{{artifact:{r2['version_id']}}}}}."
        out = self.s.resolve_markers(text, relative_to=self.docs)
        self.assertNotIn("{{artifact:", out)
        self.assertIn("[report.md](", out)
        self.assertIn("[run.json](../outputs/run.json)", out)

    def test_marker_in_link_destination_becomes_href(self):
        r = self._save()
        aid = r["artifact_id"]
        text = f"See [Figure 2]({{{{artifact:{r['version_id']}}}}}) now\n"
        out = self.s.resolve_markers(text, relative_to=self.docs)
        self.assertEqual(out, f"See [Figure 2](../research_lab/artifacts/store/{aid}/v001_report.md) now\n")
        self.assertNotIn("report.md]", out)

    def test_marker_in_link_destination_keeps_title(self):
        r = self._save()
        aid = r["artifact_id"]
        text = f'[F]({{{{artifact:{r["version_id"]}}}}} "Fig")'
        out = self.s.resolve_markers(text, relative_to=self.docs)
        self.assertEqual(out, f'[F](../research_lab/artifacts/store/{aid}/v001_report.md "Fig")')

    def test_bare_and_destination_markers_in_one_document(self):
        r = self._save()
        aid = r["artifact_id"]
        marker = f"{{{{artifact:{r['version_id']}}}}}"
        out = self.s.resolve_markers(f"{marker} and [t]({marker})", relative_to=self.docs)
        href = f"../research_lab/artifacts/store/{aid}/v001_report.md"
        self.assertEqual(out, f"[report.md]({href}) and [t]({href})")

    def test_destination_href_with_space_is_wrapped(self):
        r = self._save(name="my report.md")
        aid = r["artifact_id"]
        out = self.s.resolve_markers(f"[t]({{{{artifact:{r['version_id']}}}}})", relative_to=self.docs)
        self.assertEqual(out, f"[t](<../research_lab/artifacts/store/{aid}/v001_my report.md>)")

    def test_cli_resolve_prints_to_stdout(self):
        r = self._save()
        note = write_file(self.proj / "docs" / "note.md", f"see {{{{artifact:{r['version_id']}}}}}\n")
        before = note.read_bytes()
        code, out, err = run_cli(["--lab", str(self.lab), "resolve", str(note)])
        self.assertEqual(code, 0, err)
        aid = r["artifact_id"]
        self.assertEqual(out, f"see [report.md](../research_lab/artifacts/store/{aid}/v001_report.md)\n")
        self.assertEqual(note.read_bytes(), before)

    def test_cli_resolve_write_preserves_line_endings(self):
        r = self._save()
        note = write_file(self.proj / "docs" / "note.md", f"line one\r\n{{{{artifact:{r['version_id']}}}}}\r\n")
        code, out, err = run_cli(["--lab", str(self.lab), "resolve", "--write", str(note)])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["markers"], 1)
        data = note.read_bytes()
        self.assertIn(b"\r\n", data)
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
        self.assertIn(b"[report.md](", data)
        self.assertNotIn(b"{{artifact:", data)

    def test_cli_resolve_missing_file(self):
        code, out, err = run_cli(["--lab", str(self.lab), "resolve", str(self.proj / "docs" / "nope.md")])
        self.assertEqual(code, 1)
        self.assertTrue(err.startswith("error:"), err)
        self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
