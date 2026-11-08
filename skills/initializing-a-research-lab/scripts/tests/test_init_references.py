"""init_lab.py and a project that tracks its references/ folder in git: the ignore line for it is never added."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_init_fresh import GIT_IDENTITY, run_script


def git(args, cwd):
    env = {**os.environ, **GIT_IDENTITY}
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", env=env, check=True)


class ReferencesIgnoreCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.proj = self.tmp / "proj"
        self.proj.mkdir()

    def init(self, yes):
        args = ["--project-root", str(self.proj), "--name", "Tracked refs", "--json"]
        if yes:
            args.append("--yes")
        result = run_script(args, self.tmp)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_a_project_that_tracks_references_keeps_them_tracked(self):
        git(["init", "-q"], self.proj)
        (self.proj / "references").mkdir()
        (self.proj / "references" / "Doe_2020_paper.pdf").write_bytes(b"%PDF-1.4 stub")
        (self.proj / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
        git(["add", "-A"], self.proj)
        git(["commit", "-q", "-m", "references tracked"], self.proj)
        plan = self.init(yes=False)
        self.assertIn(".gitignore", plan["append"], "the other template lines are still added")
        report = self.init(yes=True)
        text = (self.proj / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("/research_lab/.working/", text)
        self.assertNotIn("references", text, text)
        self.assertTrue(any("references/ is tracked" in w for w in report["warn"]), report["warn"])
        second = self.init(yes=False)
        self.assertIn(".gitignore", second["skip"])
        self.assertNotIn("references", (self.proj / ".gitignore").read_text(encoding="utf-8"))

    def test_a_project_without_tracked_references_gets_the_line(self):
        (self.proj / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
        self.init(yes=True)
        self.assertIn("/references/", (self.proj / ".gitignore").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
