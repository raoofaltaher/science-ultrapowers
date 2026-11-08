"""init_lab.py refreshes a stale lab section in an existing instructions file (a 0.1 lab's CLAUDE.md)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

from test_init_existing import make_existing_lab
from test_init_fresh import BEGIN, END, FreshFolderCase, run_script

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import init_lab  # noqa: E402

OLD_SECTION = (
    f"{BEGIN}\n# Research lab (old)\n\n- Gates: G0 question, G1 evidence.\n- Scratch files go only in "
    "`research_lab/.scratch/`.\n{END}\n"
).replace("{END}", END)
HEAD = "# My project\n\nKeep it small.\n\n"
TAIL = "\n## After the lab\n\nMy own notes stay.\n"
REWRITE = "rewrite CLAUDE.md: the lab section between the markers -> the current template"


class ClaudeSectionCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.proj = Path(self._tmp.name) / "proj"
        self.proj.mkdir()
        make_existing_lab(self.proj)
        (self.proj / ".claude" / "CLAUDE.md").unlink()

    def init(self, yes=True):
        args = ["--project-root", str(self.proj), "--name", "Existing", "--short-name", "ex", "--json"]
        if yes:
            args.append("--yes")
        result = run_script(args, self.proj.parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_stale_section_is_planned_as_a_rewrite_and_nothing_is_written_without_yes(self):
        (self.proj / "CLAUDE.md").write_text(HEAD + OLD_SECTION + TAIL, encoding="utf-8")
        report = self.init(yes=False)
        self.assertIn(REWRITE, report["migration"])
        self.assertNotIn("CLAUDE.md", report["skip"])
        self.assertEqual((self.proj / "CLAUDE.md").read_text(encoding="utf-8"), HEAD + OLD_SECTION + TAIL)

    def test_stale_section_is_replaced_and_the_rest_of_the_file_is_untouched(self):
        (self.proj / "CLAUDE.md").write_text(HEAD + OLD_SECTION + TAIL, encoding="utf-8")
        report = self.init()
        self.assertIn(REWRITE, report["migration"])
        text = (self.proj / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith(HEAD))
        self.assertTrue(text.endswith(TAIL))
        self.assertEqual(text.count(BEGIN), 1)
        self.assertEqual(text.count(END), 1)
        self.assertNotIn(".scratch", text)
        self.assertNotIn("G0", text)
        self.assertIn("research_lab/.working/", text)
        self.assertIn("Stages: Question, Literature, Preregistration", text)
        self.assertIn("Research lab (ex)", text)

    def test_second_run_plans_nothing_for_the_section(self):
        (self.proj / "CLAUDE.md").write_text(HEAD + OLD_SECTION + TAIL, encoding="utf-8")
        self.init()
        report = self.init(yes=False)
        self.assertNotIn(REWRITE, report["migration"])
        self.assertIn("CLAUDE.md", report["skip"])

    def test_crlf_file_keeps_crlf(self):
        raw = (HEAD + OLD_SECTION + TAIL).replace("\n", "\r\n").encode("utf-8")
        (self.proj / "CLAUDE.md").write_bytes(raw)
        self.init()
        data = (self.proj / "CLAUDE.md").read_bytes()
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
        self.assertIn(b"research_lab/.working/", data)

    def test_a_file_that_is_not_utf8_is_left_byte_identical_with_a_warning(self):
        raw = (HEAD + OLD_SECTION + TAIL).encode("utf-8") + b"\x93quoted\x94 in Windows-1252\n"
        (self.proj / "CLAUDE.md").write_bytes(raw)
        report = self.init()
        self.assertEqual((self.proj / "CLAUDE.md").read_bytes(), raw)
        self.assertIn("CLAUDE.md is not UTF-8; the lab section was not refreshed", report["warn"])
        self.assertNotIn(REWRITE, report["migration"])
        self.assertTrue((self.proj / "research_lab" / "lab.json").is_file(), "the other items are still written")
        self.assertTrue((self.proj / "research_lab" / "findings" / "KEY_RESULTS.md").is_file())

    def test_section_without_end_marker_is_left_alone_with_a_warning(self):
        (self.proj / "CLAUDE.md").write_text(HEAD + BEGIN + "\n# half a section\n" + TAIL, encoding="utf-8")
        report = self.init()
        self.assertNotIn(REWRITE, report["migration"])
        self.assertTrue(any("end marker" in w for w in report["warn"]), report["warn"])
        self.assertEqual((self.proj / "CLAUDE.md").read_text(encoding="utf-8"), HEAD + BEGIN + "\n# half a section\n" + TAIL)


class ShortNameCase(FreshFolderCase):
    def rerun(self, *extra, yes=False):
        args = ["--project-root", str(self.proj), *extra, "--json"]
        if yes:
            args.append("--yes")
        result = run_script(args, self.tmp)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_rerun_with_another_name_keeps_the_recorded_short_name(self):
        self.rerun("--name", "Demo study", "--short-name", "mp", yes=True)
        before = (self.proj / "CLAUDE.md").read_bytes()
        self.assertIn(b"# Research lab (mp)", before)
        report = self.rerun("--name", "My Project")
        self.assertNotIn(REWRITE, report["migration"])
        self.assertIn("CLAUDE.md", report["skip"])
        self.rerun("--name", "My Project", yes=True)
        self.assertEqual((self.proj / "CLAUDE.md").read_bytes(), before)
        self.assertEqual(self.lab_json()["shortName"], "mp")

    def test_name_defaults_to_the_recorded_name_and_is_required_without_one(self):
        result = run_script(["--project-root", str(self.proj), "--json"], self.tmp)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--name", result.stderr)
        self.rerun("--name", "Demo study", "--short-name", "mp", yes=True)
        report = self.rerun()
        self.assertEqual(report["migration"], [])
        self.assertIn("CLAUDE.md", report["skip"])

    def test_an_explicit_short_name_still_wins(self):
        self.rerun("--name", "Demo study", "--short-name", "mp", yes=True)
        report = self.rerun("--name", "Demo study", "--short-name", "other")
        self.assertIn(REWRITE, report["migration"])

    def test_the_section_names_the_markers_as_the_place_init_writes(self):
        self.rerun("--name", "Demo study", yes=True)
        lines = (self.proj / "CLAUDE.md").read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], BEGIN)
        self.assertEqual(
            lines[1], "<!-- init regenerates the text between these markers; keep your own notes outside them -->"
        )


if __name__ == "__main__":
    unittest.main()
