"""init_lab.py installs the scholarly output style once and says so when it is already there."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from test_init_fresh import run_script

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import init_lab  # noqa: E402

STYLE_REL = ".claude/output-styles/scholarly-explanatory.md"
SETTING_LINE = '"outputStyle": "Scholarly Explanatory"'
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "lab_0_1"


class OutputStyleCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.proj = self.tmp / "proj"
        self.proj.mkdir()

    def init(self, *extra, yes=True):
        args = ["--project-root", str(self.proj), "--name", "Style study", *extra]
        if yes:
            args.append("--yes")
        result = run_script(args, self.tmp)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_source_has_the_style_frontmatter(self):
        text = init_lab.OUTPUT_STYLE_SOURCE.read_text(encoding="utf-8")
        head = text.split("---")[1]
        self.assertIn("name: Scholarly Explanatory", head)
        self.assertIn("keep-coding-instructions: true", head)
        self.assertIn(
            "description: Give research-grade explanations in plain, disciplined scholarly English while you complete research tasks",
            head,
        )

    def test_output_style_installed_and_skipped(self):
        dry = self.init(yes=False)
        self.assertIn(f"output-style {STYLE_REL}: create", dry.splitlines())
        self.assertFalse((self.proj / STYLE_REL).exists(), "a dry run writes nothing")
        first = self.init()
        self.assertIn(f"output-style {STYLE_REL}: create", first.splitlines())
        self.assertIn(SETTING_LINE, [line.strip() for line in first.splitlines()])
        installed = (self.proj / STYLE_REL).read_bytes()
        source = init_lab.OUTPUT_STYLE_SOURCE.read_bytes().decode("utf-8").replace("\r\n", "\n")
        self.assertEqual(installed.decode("utf-8"), source)
        second = self.init()
        self.assertIn(f"output-style {STYLE_REL}: skip", second.splitlines())
        self.assertNotIn(SETTING_LINE, second)
        self.assertEqual((self.proj / STYLE_REL).read_bytes(), installed)

    def test_an_existing_style_file_is_never_overwritten(self):
        target = self.proj / STYLE_REL
        target.parent.mkdir(parents=True)
        target.write_text("my own style\n", encoding="utf-8")
        out = self.init()
        self.assertIn(f"output-style {STYLE_REL}: skip", out.splitlines())
        self.assertEqual(target.read_text(encoding="utf-8"), "my own style\n")

    def test_migrated_lab_gets_the_style_too(self):
        shutil.copytree(FIXTURE, self.proj, dirs_exist_ok=True)
        out = self.init()
        self.assertIn(f"output-style {STYLE_REL}: create", out.splitlines())
        self.assertTrue((self.proj / STYLE_REL).is_file())


if __name__ == "__main__":
    unittest.main()
