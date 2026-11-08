"""init_lab.py --out-of-scope: the folders no role may open, in the brief and in lab.json."""

import json
import tempfile
import unittest
from pathlib import Path

from test_init_fresh import run_script

PROMPT = "*List the folders no role may open.*"
BACKSLASH = chr(92)


class ScopeCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        self.lab = self.proj / "research_lab"

    def run_init(self, *extra, yes=True):
        args = ["--project-root", str(self.proj), "--name", "Scope", *extra]
        if yes:
            args.append("--yes")
        args.append("--json")
        return run_script(args, self.tmp)

    def report(self, *extra, yes=True):
        result = self.run_init(*extra, yes=yes)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return json.loads(result.stdout)

    def brief(self):
        return (self.lab / "00_project_knowledge" / "PROJECT_BRIEF.md").read_text(encoding="utf-8")

    def lab_json(self):
        return json.loads((self.lab / "lab.json").read_text(encoding="utf-8"))

    def section_7(self):
        text = self.brief()
        start = text.index("## 7. Out of scope")
        end = text.index("## 8.")
        return text[start:end]


class TestOutOfScope(ScopeCase):
    def test_folders_go_to_the_brief_as_bullets_and_to_lab_json(self):
        self.report("--out-of-scope", "private_data", "--out-of-scope", "archive/old")
        section = self.section_7()
        self.assertIn("- `private_data`\n", section)
        self.assertIn("- `archive/old`\n", section)
        self.assertNotIn(PROMPT, section)
        self.assertEqual(self.lab_json()["jev"]["blockedPaths"], ["private_data", "archive/old"])

    def test_without_the_flag_the_prompt_stays_and_blocked_paths_are_empty(self):
        self.report()
        self.assertIn(PROMPT, self.section_7())
        self.assertEqual(self.lab_json()["jev"]["blockedPaths"], [])

    def test_folders_are_cleaned_and_deduplicated(self):
        self.report(
            "--out-of-scope", " data" + BACKSLASH + "raw ",
            "--out-of-scope", "./data/raw",
            "--out-of-scope", "other",
        )
        self.assertEqual(self.lab_json()["jev"]["blockedPaths"], ["data/raw", "other"])
        self.assertIn("- `data/raw`\n", self.section_7())

    def test_an_empty_or_multiline_folder_exits_2_before_writing(self):
        for bad in ("", "  ", "a" + chr(10) + "b"):
            result = self.run_init("--out-of-scope", bad)
            self.assertEqual(result.returncode, 2, (bad, result.stderr))
            self.assertIn("--out-of-scope", result.stderr)
            self.assertEqual(list(self.proj.iterdir()), [], repr(bad))

    def test_rerun_merges_folders_into_an_existing_lab_json_but_not_the_brief(self):
        self.report("--out-of-scope", "first")
        brief = self.brief()
        again = self.report("--out-of-scope", "second", "--out-of-scope", "first")
        self.assertEqual(self.lab_json()["jev"]["blockedPaths"], ["first", "second"])
        self.assertIn("research_lab/lab.json", again["append"])
        self.assertEqual(self.brief(), brief)


if __name__ == "__main__":
    unittest.main()
