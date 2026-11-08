"""init_lab.py refreshes the 0.1 template text that migration left in a lab: only text that is still exactly the
0.1 text, and above a record's table only the preamble."""

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from test_init_fresh import run_script

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import init_lab  # noqa: E402

TESTS = Path(__file__).resolve().parent
OLD_TEMPLATES = TESTS / "fixtures" / "templates_0_1"
OLD_LAB_JSON = TESTS / "fixtures" / "lab_0_1" / "research_lab" / "lab.json"

NAME = "Coral Study"
DESCRIPTION = "Thermal tolerance in corals."
SETUP_DATE = "2026-01-15"
SETUP_VERSION = "0.1.1"
FINDINGS = "research_lab/findings/FINDINGS_LOG.md"
OLD_FINDINGS = "research_lab/02_findings_ledger/FINDINGS.md"
OPENING = "research_lab/templates/SESSION_OPENING.md"
OLD_OPENING = "research_lab/templates/SESSION_KICKOFF.md"
README = "research_lab/README.md"
LISTED = [
    OPENING,
    "research_lab/templates/TASK_REPORT.md",
    README,
    "research_lab/findings/README.md",
    FINDINGS,
]
ADDED_ROW = "| F-0001 | Bleaching began at 31 C | measured | EC-0001 | tentative | 2026-01-16 |  | one tank only |\n"
RETIRED_WORDS = ("Session kickoff", "F-id", "CANONICAL_NUMBERS", "01_reference_registry")  # legacy


def old_destination(rel):
    """The 0.1 path of a 0.2 destination, through the same rename tables migration uses."""
    renames = [(f"research_lab/{old}", f"research_lab/{new}") for old, new in init_lab.OLD_FOLDERS.items()]
    renames += [(f"research_lab/{old}", f"research_lab/{new}") for old, new in init_lab.OTHER_FOLDER_RENAMES]
    renames += [(f"research_lab/{old}", f"research_lab/{new}") for old, new in init_lab.INNER_RENAMES]
    return init_lab._before_renames(rel, renames)


def lf(raw):
    return raw.decode("utf-8").replace("\r\n", "\n")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def current_text(rel):
    return init_lab.read_template(init_lab.template_files()[rel], {})


def tree_bytes(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def build_old_lab(proj: Path):
    """A lab as science-ultrapowers 0.1.1 left it: the 0.1 templates, a rendered README and a lab.json."""
    shutil.copytree(OLD_TEMPLATES, proj)
    text = lf((OLD_TEMPLATES / README).read_bytes())
    for key, value in (
        ("NAME", NAME),
        ("DESCRIPTION_SENTENCE", init_lab.description_sentence(DESCRIPTION)),
        ("DATE", SETUP_DATE),
        ("PLUGIN_VERSION", SETUP_VERSION),
    ):
        text = text.replace("{{" + key + "}}", value)
    (proj / README).write_bytes(text.encode("utf-8"))
    data = json.loads(OLD_LAB_JSON.read_text(encoding="utf-8"))
    data["name"] = NAME
    data["description"] = DESCRIPTION
    (proj / "research_lab" / "lab.json").write_bytes((json.dumps(data, indent=2) + "\n").encode("utf-8"))
    with open(proj / OLD_FINDINGS, "ab") as handle:
        handle.write(ADDED_ROW.encode("utf-8"))


class RefreshCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.proj = self.tmp / "proj"
        build_old_lab(self.proj)

    def init(self, yes=True):
        args = ["--project-root", str(self.proj), "--json"]
        if yes:
            args.append("--yes")
        result = run_script(args, self.tmp)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def read(self, rel):
        return (self.proj / rel).read_bytes().decode("utf-8")

    def write(self, rel, text):
        (self.proj / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.proj / rel).write_bytes(text.encode("utf-8"))

    def refresh_lines(self, report):
        return [line for line in report["migration"] if line.startswith("refresh ")]

    def refreshed(self, report):
        return [line.split(" ", 1)[1].split(":", 1)[0] for line in self.refresh_lines(report)]


class TestKeys(unittest.TestCase):
    def test_the_table_agrees_with_the_fixture(self):
        self.assertTrue(init_lab.OLD_TEMPLATE_KEYS)
        for rel, (kind, key) in init_lab.OLD_TEMPLATE_KEYS.items():
            self.assertIn(kind, ("whole", "preamble"), rel)
            old = OLD_TEMPLATES / old_destination(rel)
            self.assertTrue(old.is_file(), f"{rel}: no 0.1 file at {old_destination(rel)}")
            text = lf(old.read_bytes())
            if kind == "preamble":
                preamble = init_lab.preamble_of(text)
                self.assertIsNotNone(preamble, rel)
                text = preamble
            self.assertEqual(digest(text), key, rel)

    def test_the_table_holds_only_files_init_writes_and_never_the_researchers_documents(self):
        files = init_lab.template_files()
        for rel in init_lab.OLD_TEMPLATE_KEYS:
            self.assertIn(rel, files)
            self.assertNotEqual(rel, "research_lab/project/PROJECT_BRIEF.md")
            self.assertNotEqual(rel, init_lab.LAB_JSON_REL)
            self.assertFalse(rel.endswith((".csv", ".json", ".jsonl", ".gitkeep")), rel)
            self.assertFalse(rel.startswith("research_lab/migration/"), rel)
            self.assertNotIn("lab_meetings/", rel)
        for rel in LISTED:
            self.assertIn(rel, init_lab.OLD_TEMPLATE_KEYS)

    def test_a_refreshed_file_never_matches_the_table_again(self):
        for rel, (kind, key) in init_lab.OLD_TEMPLATE_KEYS.items():
            text = current_text(rel)
            if rel == README:
                continue  # the README carries the lab's name and dates; the placeholders differ
            if kind == "preamble":
                text = init_lab.preamble_of(text)
            self.assertNotEqual(digest(text), key, rel)

    def test_preamble_of_stops_at_the_first_table_line(self):
        self.assertEqual(init_lab.preamble_of("# T\n\ntext\n\n| a | b |\n|---|---|\n"), "# T\n\ntext\n\n")
        self.assertEqual(init_lab.preamble_of("# T\r\n  | a |\r\n"), "# T\n")
        self.assertEqual(init_lab.preamble_of("| a |\n"), "")
        self.assertIsNone(init_lab.preamble_of("# T\n\nno table here\n"))


class TestDryRun(RefreshCase):
    def test_lists_the_refresh_lines_and_writes_nothing(self):
        before = tree_bytes(self.proj)
        report = self.init(yes=False)
        self.assertEqual(tree_bytes(self.proj), before)
        lines = report["migration"]
        for rel in LISTED:
            self.assertEqual(len([l for l in lines if l.startswith(f"refresh {rel}:")]), 1, (rel, lines))
        self.assertIn(
            f"refresh {FINDINGS}: the 0.1 text above the table -> the current text", lines
        )
        self.assertIn(f"refresh {OPENING}: the 0.1 template -> the current template", lines)
        self.assertNotIn("migration_refresh", report)
        refresh_at = [i for i, l in enumerate(lines) if l.startswith("refresh ")]
        other_at = [i for i, l in enumerate(lines) if not l.startswith("refresh ")]
        self.assertGreater(min(refresh_at), max(other_at), "the refresh lines come after the other migration lines")


class TestApply(RefreshCase):
    def test_the_session_template_is_the_current_one(self):
        report = self.init()
        current = init_lab.SKILLS_ROOT / "holding-lab-meetings" / "templates" / "SESSION_OPENING.md"
        self.assertEqual((self.proj / OPENING).read_bytes(), lf(current.read_bytes()).encode("utf-8"))
        self.assertIn(OPENING, self.refreshed(report))

    def test_no_retired_word_is_left_in_a_refreshed_file(self):
        report = self.init()
        refreshed = self.refreshed(report)
        for rel in LISTED:
            self.assertIn(rel, refreshed)
        for rel in refreshed:
            text = self.read(rel)
            for word in RETIRED_WORDS:
                self.assertNotIn(word, text, f"{rel} still holds {word!r}")

    def test_the_readme_keeps_the_name_the_setup_date_and_the_version(self):
        self.init()
        text = self.read(README)
        self.assertTrue(text.startswith(f"# {NAME} research lab\n"), text[:60])
        self.assertIn(f"works on {NAME}: {DESCRIPTION} It indexes", text)
        self.assertIn(f"Set up {SETUP_DATE} by science-ultrapowers {SETUP_VERSION}.", text)
        self.assertNotIn("{{", text)

    def test_the_findings_log_gets_the_current_preamble_and_keeps_its_table(self):
        old_rest = lf((OLD_TEMPLATES / old_destination(FINDINGS)).read_bytes())
        old_rest = old_rest[len(init_lab.preamble_of(old_rest)):] + ADDED_ROW
        spec = next(s for s in init_lab.TABLES if f"research_lab/{s.path}" == FINDINGS)
        migrated_table = init_lab.transform_table(old_rest, spec)[0]
        self.init()
        text = self.read(FINDINGS)
        preamble = init_lab.preamble_of(current_text(FINDINGS))
        self.assertTrue(text.startswith(preamble))
        self.assertEqual(text[len(preamble):], migrated_table)
        self.assertIn("| F-0001 | Bleaching began at 31 C | measured | exploratory | EC-0001 |", text)

    def test_a_second_run_plans_and_changes_nothing(self):
        self.init()
        after = tree_bytes(self.proj)
        plan = self.init(yes=False)
        self.assertEqual(self.refresh_lines(plan), [])
        again = self.init()
        self.assertEqual(self.refresh_lines(again), [])
        self.assertEqual(tree_bytes(self.proj), after)

    def test_a_template_the_researcher_edited_is_kept_and_reported(self):
        edited = lf((OLD_TEMPLATES / "research_lab/templates/H_CARD.md").read_bytes()) + "My own extra line.\n"
        self.write("research_lab/templates/H_CARD.md", edited)
        report = self.init()
        rel = "research_lab/templates/HYPOTHESIS_RECORD.md"
        self.assertEqual(self.read(rel), edited)
        self.assertNotIn(rel, self.refreshed(report))
        message = (
            f"{rel} was edited after setup and was kept; it may still use 0.1 names: "
            "compare it with the current template"
        )
        self.assertIn(message, report["warn"])
        self.assertEqual(len([w for w in report["warn"] if "was edited after setup" in w]), 1, report["warn"])

    def test_the_notebook_and_the_memory_index_grow_by_design_and_are_kept_without_a_warning(self):
        notebook = "research_lab/02_findings_ledger/LAB_NOTEBOOK.md"  # legacy
        index = "research_lab/memory/MEMORY.md"
        grown = {}
        for rel in (notebook, index):
            grown[rel] = lf((OLD_TEMPLATES / rel).read_bytes()) + "\n## 2026-02-01\n\nAn entry the lab wrote.\n"
            self.write(rel, grown[rel])
        report = self.init()
        self.assertEqual(self.read("research_lab/findings/LAB_NOTEBOOK.md"), grown[notebook])
        self.assertEqual(self.read(index), grown[index])
        edited = [w for w in report["warn"] if "was edited after setup" in w]
        self.assertFalse([w for w in edited if "LAB_NOTEBOOK.md" in w or "MEMORY.md" in w], edited)

    def test_a_crlf_file_stays_crlf(self):
        old = lf((OLD_TEMPLATES / OLD_OPENING).read_bytes())
        (self.proj / OLD_OPENING).write_bytes(old.replace("\n", "\r\n").encode("utf-8"))
        report = self.init()
        self.assertIn(OPENING, self.refreshed(report))
        raw = (self.proj / OPENING).read_bytes()
        self.assertEqual(raw, current_text(OPENING).replace("\n", "\r\n").encode("utf-8"))
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

    def test_a_crlf_record_keeps_crlf_and_its_rows(self):
        old = lf((OLD_TEMPLATES / old_destination(FINDINGS)).read_bytes()) + ADDED_ROW
        self.write(OLD_FINDINGS, old.replace("\n", "\r\n"))
        self.init()
        raw = (self.proj / FINDINGS).read_bytes()
        self.assertTrue(raw.startswith(init_lab.preamble_of(current_text(FINDINGS)).replace("\n", "\r\n").encode("utf-8")))
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))


class TestNewLayout(RefreshCase):
    def test_a_lab_migrated_before_the_fix_is_refreshed_by_a_rerun(self):
        self.init()
        self.write(OPENING, lf((OLD_TEMPLATES / OLD_OPENING).read_bytes()))
        plan = self.init(yes=False)
        self.assertEqual(self.refresh_lines(plan), [f"refresh {OPENING}: the 0.1 template -> the current template"])
        report = self.init()
        self.assertEqual(self.refresh_lines(report), [f"refresh {OPENING}: the 0.1 template -> the current template"])
        self.assertFalse([w for w in report["warn"] if "was edited after setup" in w], report["warn"])
        self.assertEqual(self.read(OPENING), current_text(OPENING))

    def test_old_preamble_over_a_table_keeps_every_row_byte_for_byte(self):
        self.init()
        table = self.read(FINDINGS)
        table = table[len(init_lab.preamble_of(table)):]
        old_preamble = init_lab.preamble_of(lf((OLD_TEMPLATES / old_destination(FINDINGS)).read_bytes()))
        self.write(FINDINGS, old_preamble + table)
        report = self.init()
        self.assertEqual(self.refreshed(report), [FINDINGS])
        self.assertEqual(self.read(FINDINGS), init_lab.preamble_of(current_text(FINDINGS)) + table)

    def test_a_file_that_does_not_match_is_skipped_silently(self):
        self.init()
        self.write(OPENING, self.read(OPENING) + "My note.\n")
        report = self.init()
        self.assertEqual(self.refresh_lines(report), [])
        self.assertFalse([w for w in report["warn"] if "was edited after setup" in w], report["warn"])
        self.assertTrue(self.read(OPENING).endswith("My note.\n"))

    def test_the_researchers_documents_are_never_touched(self):
        self.write("research_lab/00_project_knowledge/PROJECT_BRIEF.md", "# My brief\n\nRetired words F-id here.\n")  # legacy
        meeting = "research_lab/06_decisions/lab_meetings/2026-01-05_kickoff.md"  # legacy
        self.write(meeting, "# Session kickoff\n\nNotes with F-id.\n")  # legacy
        self.init()
        self.assertEqual(self.read("research_lab/project/PROJECT_BRIEF.md"), "# My brief\n\nRetired words F-id here.\n")  # legacy
        self.assertEqual(
            self.read("research_lab/decisions/lab_meetings/2026-01-05_opening.md"),  # legacy
            "# Session kickoff\n\nNotes with F-id.\n",  # legacy
        )


class TestReadmeKey(RefreshCase):
    def test_a_readme_whose_first_line_changed_is_kept(self):
        text = self.read(README).replace(f"# {NAME} research lab", f"# {NAME} lab", 1)
        self.write(README, text)
        report = self.init()
        self.assertNotIn(README, self.refreshed(report))
        self.assertEqual(self.read(README), text)
        self.assertTrue([w for w in report["warn"] if w.startswith(f"{README} was edited after setup")], report["warn"])

    def test_a_readme_that_names_another_lab_is_kept(self):
        text = self.read(README).replace(NAME, "Other Name")
        self.write(README, text)
        report = self.init()
        self.assertNotIn(README, self.refreshed(report))
        self.assertEqual(self.read(README), text)


if __name__ == "__main__":
    unittest.main()
