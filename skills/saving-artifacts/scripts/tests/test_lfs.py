import contextlib
import io
import json
import subprocess
import sys
import tempfile
import os
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts
from _helpers import make_git_lab, make_lab, run_cli, write_file

LAB_JSON = {"lfs": {"thresholdMB": 1, "budgetWarnMB": 2}}
BIG = b"x" * (3 * 1024 * 1024 // 2)
HEADER = [
    "# science-ultrapowers artifact archive: stored copies are byte-exact; one LFS line per file at or above lfs.thresholdMB",
    "archive/** -text",
    "*.jsonl text eol=lf",
]
LFS_TAIL = "filter=lfs diff=lfs merge=lfs -text"


def _has_git_lfs() -> bool:
    try:
        return subprocess.run(["git", "lfs", "version"], capture_output=True).returncode == 0
    except OSError:
        return False


class LfsTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self._tmp.cleanup)
        self.t = Path(self._tmp.name)
        empty = write_file(self.t / "empty-gitconfig", b"")
        patcher = mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(empty), "GIT_CONFIG_NOSYSTEM": "1"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def _store(self, lab_json=LAB_JSON, git=False):
        lab = make_git_lab(self.t, lab_json) if git else make_lab(self.t, lab_json)
        s = artifacts.LabStore(lab)
        return s, s.project_root

    def _save1(self, s, path, **kw):
        kw.setdefault("role", "analyst")
        kw.setdefault("task", "TASK-0001")
        return s.save([path], **kw)[0]

    def _attrs(self, s) -> list[str]:
        return (s.root / ".gitattributes").read_text(encoding="utf-8").splitlines()

    def _git(self, proj, *args) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=proj, capture_output=True, check=True)

    def test_first_save_writes_header(self):
        s, proj = self._store()
        self._save1(s, write_file(proj / "work" / "small.txt", b"0123456789"))
        lines = self._attrs(s)
        self.assertEqual(lines[:3], HEADER)
        self.assertFalse([l for l in lines if "filter=lfs" in l])

    def test_custom_gitattributes_keeps_its_lines_and_gains_the_rules(self):
        s, proj = self._store()
        s.root.mkdir(parents=True, exist_ok=True)
        (s.root / ".gitattributes").write_bytes(b"# mine\n")
        self._save1(s, write_file(proj / "work" / "small.txt", b"0123456789"))
        lines = self._attrs(s)
        self.assertEqual(lines[0], "# mine")
        self.assertEqual(lines.count("archive/** -text"), 1)
        self.assertEqual(lines.count("*.jsonl text eol=lf"), 1)
        after_first = (s.root / ".gitattributes").read_bytes()
        self._save1(s, write_file(proj / "work" / "other.txt", b"abc"))
        self.assertEqual((s.root / ".gitattributes").read_bytes(), after_first)

    def test_custom_gitattributes_still_stores_byte_exact(self):
        s, proj = self._store(git=True)
        self._git(proj, "config", "core.autocrlf", "true")
        s.root.mkdir(parents=True, exist_ok=True)
        (s.root / ".gitattributes").write_bytes(b"# mine\n")
        res = self._save1(s, write_file(proj / "work" / "crlf.md", b"a\r\nb\r\n"))
        shown = self._git(proj, "show", f":research_lab/artifacts/archive/{res['artifact_id']}/v001_crlf.md").stdout
        self.assertEqual(shown, b"a\r\nb\r\n")

    def test_replaced_version_loses_its_lfs_line(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "big.csv", BIG)
        r1 = self._save1(s, f, destination="working")
        aid = r1["artifact_id"]
        write_file(f, BIG + b"y")
        self._save1(s, f, version_of=aid)
        lines = self._attrs(s)
        self.assertIn(f"archive/{aid}/v002_big.csv {LFS_TAIL}", lines)
        self.assertFalse([l for l in lines if "v001_big.csv" in l])
        self.assertEqual(s.lfs_check()["missing_lines"], [])

    def test_large_file_gets_exact_path_line_before_staging(self):
        s, proj = self._store(git=True)
        res = self._save1(s, write_file(proj / "work" / "big.csv", BIG))
        aid = res["artifact_id"]
        self.assertIs(res["lfs"], True)
        self.assertIn(f"archive/{aid}/v001_big.csv {LFS_TAIL}", self._attrs(s))
        stored = f"research_lab/artifacts/archive/{aid}/v001_big.csv"
        attr = self._git(proj, "check-attr", "filter", "--", stored).stdout.decode().strip()
        self.assertTrue(attr.endswith("filter: lfs"), attr)
        staged = self._git(proj, "diff", "--cached", "--name-only").stdout.decode().split()
        self.assertIn("research_lab/artifacts/.gitattributes", staged)
        self.assertIn(stored, staged)

    def test_awkward_name_uses_wildcard_line(self):
        s, proj = self._store(git=True)
        res = self._save1(s, write_file(proj / "work" / "my data [v1].csv", BIG))
        aid = res["artifact_id"]
        lines = self._attrs(s)
        self.assertIn(f"archive/{aid}/v001_* {LFS_TAIL}", lines)
        self.assertFalse([l for l in lines if "my data" in l])
        stored = f"research_lab/artifacts/archive/{aid}/v001_my data [v1].csv"
        attr = self._git(proj, "check-attr", "filter", "--", stored).stdout.decode().strip()
        self.assertTrue(attr.endswith("filter: lfs"), attr)

    def test_default_threshold_eleven_megabyte_csv(self):
        s, proj = self._store(lab_json=None)
        big = self._save1(s, write_file(proj / "work" / "eleven.csv", b"x" * (11 * 1024 * 1024)))
        small = self._save1(s, write_file(proj / "work" / "nine.csv", b"x" * (9 * 1024 * 1024)))
        lines = self._attrs(s)
        self.assertIs(big["lfs"], True)
        self.assertIn(f"archive/{big['artifact_id']}/v001_eleven.csv {LFS_TAIL}", lines)
        self.assertIs(small["lfs"], False)
        self.assertFalse([l for l in lines if small["artifact_id"] in l])

    def test_line_written_once_per_file(self):
        s, proj = self._store()
        r1 = self._save1(s, write_file(proj / "work" / "big.csv", BIG))
        aid = r1["artifact_id"]
        write_file(proj / "work" / "big.csv", BIG + b"y")
        self._save1(s, proj / "work" / "big.csv", version_of=aid)
        lfs_lines = [l for l in self._attrs(s) if "filter=lfs" in l]
        self.assertEqual(
            lfs_lines,
            [f"archive/{aid}/v001_big.csv {LFS_TAIL}", f"archive/{aid}/v002_big.csv {LFS_TAIL}"],
        )
        self.assertIs(s.lfs_line_if_needed(s.lab / r1["storage_path"]), True)
        self.assertEqual([l for l in self._attrs(s) if "filter=lfs" in l], lfs_lines)

    def test_lfs_check_reports_missing_lines(self):
        s, proj = self._store()
        res = self._save1(s, write_file(proj / "work" / "big.csv", BIG))
        aid = res["artifact_id"]
        ga = s.root / ".gitattributes"
        kept = [l for l in self._attrs(s) if "filter=lfs" not in l]
        ga.write_bytes(("\n".join(kept) + "\n").encode("utf-8"))
        self.assertEqual(s.lfs_check()["missing_lines"], [f"archive/{aid}/v001_big.csv"])
        code, out, _ = run_cli(["--lab", str(s.lab), "lfs-check"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["missing_lines"], [f"archive/{aid}/v001_big.csv"])
        s.lfs_line_if_needed(s.lab / res["storage_path"])
        code, out, _ = run_cli(["--lab", str(s.lab), "lfs-check"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["missing_lines"], [])

    def test_lfs_check_ignores_replaced_and_counts_ok_only(self):
        s, proj = self._store()
        r1 = self._save1(s, write_file(proj / "work" / "big.csv", BIG), destination="working")
        aid = r1["artifact_id"]
        second = BIG + b"yy"
        write_file(proj / "work" / "big.csv", second)
        self._save1(s, proj / "work" / "big.csv", version_of=aid, destination="working")
        check = s.lfs_check()
        self.assertEqual(check["missing_lines"], [])
        self.assertEqual(check["total_bytes"], len(second))
        self.assertEqual(s.lfs_total(), len(second))

    def test_budget_warning(self):
        s, proj = self._store()
        err1 = io.StringIO()
        with contextlib.redirect_stderr(err1):
            r1 = self._save1(s, write_file(proj / "work" / "big.csv", BIG))
        self.assertNotIn("warning: LFS total", err1.getvalue())
        write_file(proj / "work" / "big.csv", BIG + b"y")
        err2 = io.StringIO()
        with contextlib.redirect_stderr(err2):
            self._save1(s, proj / "work" / "big.csv", version_of=r1["artifact_id"])
        self.assertIn("warning: LFS total", err2.getvalue())
        self.assertIn("lfs.budgetWarnMB", err2.getvalue())
        self.assertIs(s.lfs_check()["over_budget"], True)

    def test_stored_bytes_are_not_eol_converted(self):
        s, proj = self._store(git=True)
        self._git(proj, "config", "core.autocrlf", "true")
        res = self._save1(s, write_file(proj / "work" / "crlf.md", b"a\r\nb\r\n"))
        shown = self._git(proj, "show", f":research_lab/artifacts/archive/{res['artifact_id']}/v001_crlf.md").stdout
        self.assertEqual(shown, b"a\r\nb\r\n")
        attr = self._git(proj, "check-attr", "eol", "--", "research_lab/artifacts/versions.jsonl").stdout.decode().strip()
        self.assertTrue(attr.endswith("eol: lf"), attr)

    # ---- git-lfs filter state ------------------------------------------

    def _cli_save(self, s, f, *extra):
        return run_cli(["--lab", str(s.lab), "save", str(f), "--role", "r", "--task", "c", *extra])

    def test_save_warns_when_lfs_filter_not_configured(self):
        s, proj = self._store(git=True)
        code, out, err = self._cli_save(s, write_file(proj / "work" / "big.csv", BIG))
        self.assertEqual(code, 0, err)
        aid = json.loads(out)[0]["artifact_id"]
        self.assertIn("git-lfs filter not configured", err)
        self.assertIn("run: git lfs install", err)
        self.assertIn(f"research_lab/artifacts/archive/{aid}/v001_big.csv", err)

    def test_save_does_not_warn_when_lfs_filter_configured(self):
        s, proj = self._store(git=True)
        self._git(proj, "config", "filter.lfs.clean", "git-lfs clean -- %f")
        code, out, err = self._cli_save(s, write_file(proj / "work" / "big.csv", BIG), "--no-stage")
        self.assertEqual(code, 0, err)
        self.assertNotIn("git-lfs filter", err)

    def test_small_file_never_warns(self):
        s, proj = self._store(git=True)
        code, out, err = self._cli_save(s, write_file(proj / "work" / "small.txt", b"0123456789"))
        self.assertEqual(code, 0, err)
        self.assertNotIn("git-lfs filter", err)

    def test_small_save_does_not_probe_the_lfs_filter(self):
        s, proj = self._store(git=True)
        original = artifacts.LabStore.lfs_filter_configured
        with mock.patch.object(
            artifacts.LabStore, "lfs_filter_configured", autospec=True, side_effect=original
        ) as probe:
            self._save1(s, write_file(proj / "work" / "small.txt", b"0123456789"))
        self.assertEqual(probe.call_count, 0)

    def test_lfs_check_reports_filter_state(self):
        s, proj = self._store()
        self._save1(s, write_file(proj / "work" / "big.csv", BIG))
        self.assertIsNone(s.lfs_filter_configured())
        self.assertIsNone(s.lfs_check()["lfs_filter_configured"])
        self.assertEqual(run_cli(["--lab", str(s.lab), "lfs-check"])[0], 0)
        other = self.t / "second"
        other.mkdir()
        g = artifacts.LabStore(make_git_lab(other, LAB_JSON))
        self._save1(g, write_file(g.project_root / "work" / "big.csv", BIG))
        self.assertIs(g.lfs_filter_configured(), False)
        self.assertIs(g.lfs_check()["lfs_filter_configured"], False)
        code, out, err = run_cli(["--lab", str(g.lab), "lfs-check"])
        self.assertEqual(code, 1)
        self.assertIs(json.loads(out)["lfs_filter_configured"], False)
        self.assertIn("git-lfs filter not configured", err)
        self._git(g.project_root, "config", "filter.lfs.clean", "git-lfs clean -- %f")
        self.assertIs(g.lfs_filter_configured(), True)
        code, out, err = run_cli(["--lab", str(g.lab), "lfs-check"])
        self.assertEqual(code, 0, err)
        self.assertIs(json.loads(out)["lfs_filter_configured"], True)

    # ---- folding, equivalent lines, line separators --------------------

    def test_lfs_check_suggests_folding_at_1000_lines(self):
        s, proj = self._store()
        self._save1(s, write_file(proj / "work" / "small.txt", b"0123456789"))
        for count, expect_suggestion in ((1000, True), (999, False)):
            lines = HEADER + [f"archive/a{i:04d}/v001_x.bin {LFS_TAIL}" for i in range(count)]
            (s.root / ".gitattributes").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
            report = s.lfs_check()
            self.assertEqual(report["line_count"], count)
            if expect_suggestion:
                self.assertIn("archive/<aid>/**", report["suggestion"])
            else:
                self.assertIsNone(report["suggestion"])

    def test_equivalent_hand_edited_line_counts(self):
        s, proj = self._store()
        res = self._save1(s, write_file(proj / "work" / "big.csv", BIG))
        aid = res["artifact_id"]
        kept = [l for l in self._attrs(s) if "filter=lfs" not in l]
        kept.append(f"archive/{aid}/v001_big.csv   -text merge=lfs diff=lfs filter=lfs")
        (s.root / ".gitattributes").write_bytes(("\n".join(kept) + "\n").encode("utf-8"))
        before = (s.root / ".gitattributes").read_bytes()
        self.assertEqual(s.lfs_check()["missing_lines"], [])
        self.assertEqual(s.lfs_total(), len(BIG))
        self.assertIs(s.lfs_line_if_needed(s.lab / res["storage_path"]), True)
        self.assertEqual((s.root / ".gitattributes").read_bytes(), before)

    def test_folded_artifact_pattern_covers_its_versions(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "big.csv", BIG)
        res = self._save1(s, f)
        aid = res["artifact_id"]
        kept = [l for l in self._attrs(s) if "filter=lfs" not in l]
        kept.append(f"archive/{aid}/** {LFS_TAIL}")
        (s.root / ".gitattributes").write_bytes(("\n".join(kept) + "\n").encode("utf-8"))
        self.assertEqual(s.lfs_check()["missing_lines"], [])
        self.assertEqual(s.lfs_total(), len(BIG))
        write_file(f, BIG + b"y")
        self._save1(s, f, version_of=aid)
        self.assertEqual([l for l in self._attrs(s) if "filter=lfs" in l], [f"archive/{aid}/** {LFS_TAIL}"])
        self.assertEqual(s.lfs_check()["missing_lines"], [])

    def test_folded_line_survives_working_replacement(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "big.csv", BIG)
        res = self._save1(s, f, destination="working")
        aid = res["artifact_id"]
        kept = [l for l in self._attrs(s) if "filter=lfs" not in l]
        kept.append(f"archive/{aid}/** {LFS_TAIL}")
        (s.root / ".gitattributes").write_bytes(("\n".join(kept) + "\n").encode("utf-8"))
        write_file(f, BIG + b"y")
        self._save1(s, f, version_of=aid)
        self.assertEqual([l for l in self._attrs(s) if "filter=lfs" in l], [f"archive/{aid}/** {LFS_TAIL}"])

    def test_gitattributes_comment_with_line_separator_survives(self):
        s, proj = self._store()
        s.root.mkdir(parents=True, exist_ok=True)
        note = "# note a\u2028b\u2029c"
        text = note + "\nstore/** -text\n*.jsonl text eol=lf\n"
        (s.root / ".gitattributes").write_bytes(text.encode("utf-8"))
        self._save1(s, write_file(proj / "work" / "big.csv", BIG))
        content = (s.root / ".gitattributes").read_text(encoding="utf-8")
        lines = content.split("\n")
        self.assertEqual(lines[0], note)
        self.assertNotIn("b", lines)
        self.assertNotIn("c", lines)

    @unittest.skipUnless(_has_git_lfs(), "git-lfs is not available")
    def test_lfs_pointer_is_what_git_stages(self):
        s, proj = self._store(git=True)
        self._git(proj, "lfs", "install", "--local")
        code, out, err = self._cli_save(s, write_file(proj / "work" / "big.csv", BIG))
        self.assertEqual(code, 0, err)
        aid = json.loads(out)[0]["artifact_id"]
        shown = self._git(proj, "cat-file", "-p", f":research_lab/artifacts/archive/{aid}/v001_big.csv").stdout
        self.assertTrue(shown.startswith(b"version https://git-lfs.github.com/spec/v1"), shown[:60])


if __name__ == "__main__":
    unittest.main()
