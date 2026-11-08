import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts
from artifacts import LabStore, find_lab, now_iso, sha256_file
from _helpers import make_lab, write_file


def tmpdir():
    return tempfile.TemporaryDirectory(ignore_cleanup_errors=True)


class StoreBasicsTest(unittest.TestCase):
    def test_defaults_without_lab_json(self):
        with tmpdir() as t:
            s = LabStore(make_lab(t))
            self.assertEqual(s.threshold_bytes, 10 * 1024 * 1024)
            self.assertEqual(s.budget_warn_bytes, 800 * 1024 * 1024)

    def test_lab_json_overrides(self):
        with tmpdir() as t:
            s = LabStore(make_lab(t, {"lfs": {"thresholdMB": 1, "budgetWarnMB": 2}}))
            self.assertEqual(s.threshold_bytes, 1048576)
            self.assertEqual(s.budget_warn_bytes, 2097152)

    def test_lab_json_other_keys_are_kept(self):
        with tmpdir() as t:
            s = LabStore(make_lab(t, {"name": "x", "memory": {"indexBudget": 150}}))
            self.assertEqual(s.config["name"], "x")
            self.assertEqual(s.config["memory"]["indexBudget"], 150)
            self.assertEqual(s.config["lfs"]["thresholdMB"], 10)

    def test_invalid_lab_json_raises_store_error(self):
        with tmpdir() as t:
            lab = make_lab(t)
            (lab / "lab.json").write_text("{not json", encoding="utf-8")
            with self.assertRaises(artifacts.StoreError) as cm:
                LabStore(lab)
            self.assertIn("lab.json", str(cm.exception))

    def test_lab_path_is_resolved(self):
        with tmpdir() as t:
            s = LabStore(make_lab(t))
            self.assertEqual(s.lab, make_lab(t).resolve())
            self.assertEqual(s.project_root, s.lab.parent)
            self.assertEqual(s.root, s.lab / "artifacts")
            self.assertEqual(s.store, s.root / "store")

    def test_append_and_rows_roundtrip(self):
        with tmpdir() as t:
            s = LabStore(make_lab(t))
            s.append("artifacts", {"id": "a"})
            s.append("artifacts", {"id": "b"})
            self.assertEqual(s.rows("artifacts"), [{"id": "a"}, {"id": "b"}])
            data = (s.root / "artifacts.jsonl").read_bytes()
            self.assertTrue(data.endswith(b"\n"))
            self.assertNotIn(b"\r", data)

    def test_append_is_atomic(self):
        with tmpdir() as t:
            s = LabStore(make_lab(t))
            s.append("artifacts", {"id": "a"})
            self.assertEqual(list(s.root.glob("*.tmp")), [])

    def test_rows_of_missing_ledger_is_empty(self):
        with tmpdir() as t:
            s = LabStore(make_lab(t))
            self.assertEqual(s.rows("versions"), [])

    def test_rows_reports_corrupt_line(self):
        with tmpdir() as t:
            s = LabStore(make_lab(t))
            s.root.mkdir(parents=True, exist_ok=True)
            (s.root / "versions.jsonl").write_text('{"id": "a"}\n{broken\n', encoding="utf-8")
            with self.assertRaises(artifacts.StoreError) as cm:
                s.rows("versions")
            self.assertIn("versions.jsonl", str(cm.exception))
            self.assertIn("line 2", str(cm.exception))

    def test_rows_survive_unicode_line_separators(self):
        with tmpdir() as t:
            s = LabStore(make_lab(t))
            proj = s.project_root
            desc = "a b c\u0085d\x0ce\x1cf"
            s.save([write_file(proj / "work" / "one.md", "1\n")], role="r", command="c", description=desc)
            self.assertEqual(s.rows("versions")[0]["code_description"], desc)
            s.save([write_file(proj / "work" / "two.md", "2\n")], role="r", command="c")
            self.assertEqual(len(s.rows("versions")), 2)
            self.assertEqual(s.rows("versions")[0]["code_description"], desc)
            self.assertEqual([r["filename"] for r in s.search("a b")], ["work/one.md"])
            first = s.rows("versions")[0]["id"]
            s.check_add(first, claim="c", verdict="pass", reviewer_role="r", evidence="x\u0085y")
            self.assertEqual(s.rows("verification_checks")[0]["evidence"], "x\u0085y")

    def test_unknown_ledger_raises_store_error(self):
        with tmpdir() as t:
            s = LabStore(make_lab(t))
            with self.assertRaises(artifacts.StoreError):
                s.append("nope", {})
            with self.assertRaises(artifacts.StoreError):
                s.rows("nope")

    def test_find_lab_walks_up(self):
        for marker in ("file", "dir"):
            with tmpdir() as t:
                lab = make_lab(t)
                if marker == "file":
                    (lab / "lab.json").write_text("{}", encoding="utf-8")
                else:
                    (lab / "artifacts").mkdir()
                deep = Path(t) / "proj" / "sub" / "dir"
                deep.mkdir(parents=True)
                self.assertEqual(find_lab(deep), lab.resolve())
                self.assertEqual(find_lab(Path(t) / "proj" / "research_lab"), lab.resolve())

    def test_find_lab_accepts_a_bare_research_lab(self):
        with tmpdir() as t:
            lab = make_lab(t)
            proj = Path(t) / "proj"
            (lab / "03_experiments").mkdir()
            (proj / "sub").mkdir()
            self.assertEqual(find_lab(lab), lab.resolve())
            self.assertEqual(find_lab(lab / "03_experiments"), lab.resolve())
            self.assertEqual(find_lab(proj / "sub"), lab.resolve())

    def test_find_lab_raises_lab_not_found(self):
        with tmpdir() as t:
            with self.assertRaises(artifacts.LabNotFound) as cm:
                find_lab(Path(t))
            self.assertIn("research_lab", str(cm.exception))

    def test_sha256_file_matches_hashlib(self):
        with tmpdir() as t:
            p = Path(t) / "a.bin"
            p.write_bytes(b"abc")
            self.assertEqual(sha256_file(p), hashlib.sha256(b"abc").hexdigest())
            big = Path(t) / "big.bin"
            big.write_bytes(b"x" * (3 * 1024 * 1024))
            self.assertEqual(sha256_file(big), hashlib.sha256(b"x" * (3 * 1024 * 1024)).hexdigest())

    def test_error_hierarchy(self):
        for cls in (artifacts.LabNotFound, artifacts.AmbiguousId, artifacts.UnknownId):
            self.assertTrue(issubclass(cls, artifacts.StoreError))
        self.assertTrue(issubclass(artifacts.StoreError, Exception))

    def test_now_iso_format(self):
        self.assertRegex(now_iso(), r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


if __name__ == "__main__":
    unittest.main()
