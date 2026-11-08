"""Tests for the profile step: profile files, the diff against plugin agents, the skill classes."""

import contextlib
import dataclasses
import io
import json
import re
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fixture_db  # noqa: E402
import migrate_claude_science as mcs  # noqa: E402

STUB_AGENT = (
    "---\n"
    "name: lab-project-manager\n"
    'description: "Stub agent."\n'
    "model: inherit\n"
    "skills:\n"
    "  - science-ultrapowers:running-the-lab\n"
    "  - science-ultrapowers:verifying-evidence-by-doi\n"
    "---\n"
    "\n"
    "You are the project manager of the lab.\n"
    "You keep the gates.\n"
    "\n"
    "## When to invoke\n"
    "\n"
    "- Not part of the first paragraph.\n"
)


def tree_snapshot(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(Path(root).rglob("*")) if p.is_file()
    }


def groups(section):
    """Class heading -> list of backticked names under it, from one PROFILE_DIFF section."""
    result, current = {}, None
    for number, line in enumerate(section.split("\n")):
        if line.startswith(("### ", "#### ")):
            current = line.lstrip("#").strip()
            result[current] = []
        elif line.startswith("## ") and number > 0:
            break
        elif current is not None and line.startswith("- "):
            result[current].append(line[2:].strip())
    return result


class ProfileTestCase(unittest.TestCase):
    def setUp(self):
        # No process tool is ever run by a test: the running-program check finds none.
        self.enterContext(mock.patch.object(mcs, "_run_tool", return_value=None))
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        self.lab = self.tmp / "research_lab"

        self.plugin = self.tmp / "plugin"
        (self.plugin / "agents").mkdir(parents=True)
        self.agent_file = self.plugin / "agents" / "lab-project-manager.md"
        self.agent_file.write_text(STUB_AGENT, encoding="utf-8", newline="\n")
        for name in ("running-the-lab", "verifying-evidence-by-doi", "peer-review"):
            (self.plugin / "skills" / name).mkdir(parents=True)
        (self.plugin / "skills" / "peer-review" / "PROVENANCE.md").write_text("vendored\n", encoding="utf-8")

        self.synced = self.tmp / "synced"
        (self.synced / "org-fixture-0001" / "deep-research").mkdir(parents=True)

        self.info = fixture_db.build_fixture(self.tmp / "data")
        self.conn = None

    def connect(self, edit=None):
        if edit:
            conn = sqlite3.connect(str(self.info.db_path))
            try:
                edit(conn)
                conn.commit()
            finally:
                conn.close()
        copy_dir = self.tmp / "copy"
        copy_dir.mkdir()
        self.conn = mcs.open_ro(mcs.copy_db(self.info.org_dir, copy_dir))
        self.addCleanup(self.conn.close)
        return self.conn

    def classifier(self):
        return mcs.SkillClassifier(self.plugin / "skills", self.info.data_dir, self.synced)

    def export(self, **kwargs):
        conn = self.conn or self.connect()
        return mcs.export_profiles(conn, self.plugin / "agents", self.lab, self.classifier(), **kwargs)

    def diff_text(self):
        return (self.lab / "migration" / "PROFILE_DIFF.md").read_text(encoding="utf-8")

    def section(self, heading_start):
        text = self.diff_text()
        start = text.index(heading_start)
        end = text.find("\n## ", start + 1)
        return text[start:] if end < 0 else text[start:end]


class ClassifierTest(ProfileTestCase):
    def test_classes_in_order(self):
        c = self.classifier()
        self.assertEqual(c.classify("running-the-lab"), "lab")
        self.assertEqual(c.classify("doi-verified-evidence"), "lab")
        self.assertEqual(c.classify("peer-review"), "vendored")
        self.assertEqual(c.classify("pdf-explore"), "bundled")
        self.assertEqual(c.classify("skill-creator"), "bundled")
        self.assertEqual(c.classify("deep-research"), "account")
        self.assertEqual(c.classify("pdf"), "account")
        self.assertEqual(c.classify("theme-factory"), "example")
        self.assertEqual(c.classify("no-such-skill"), "unknown")

    def test_plugin_name_maps_old_names(self):
        c = self.classifier()
        self.assertEqual(c.plugin_name("doi-verified-evidence"), "verifying-evidence-by-doi")
        self.assertEqual(c.plugin_name("jev-decisions"), "deciding-with-jev")
        self.assertEqual(c.plugin_name("running-the-lab"), "running-the-lab")
        self.assertEqual(c.plugin_name("peer-review"), "peer-review")
        self.assertIsNone(c.plugin_name("pdf-explore"))

    def test_runtime_skill_folders_count_as_bundled(self):
        (self.info.data_dir / "runtime" / "0.0.0-fixture" / "skills" / "new-bundled-skill").mkdir(parents=True)
        self.assertEqual(self.classifier().classify("new-bundled-skill"), "bundled")

    def test_missing_synced_dir_is_fine(self):
        c = mcs.SkillClassifier(self.plugin / "skills", None, self.tmp / "nope")
        self.assertEqual(c.classify("deep-research"), "unknown")
        self.assertEqual(c.classify("docx"), "account")


class ExportProfilesTest(ProfileTestCase):
    def test_profile_file_written_with_skills(self):
        report = self.export()
        self.assertEqual(report.profiles, 2)
        text = (self.lab / "migration" / "profiles" / "LAB_PROJECT_MANAGER.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\ndisplay_name: Lab Project Manager\n"))
        self.assertIn(
            'skill_names: ["doi-verified-evidence", "peer-review", "pdf-explore", "deep-research", '
            '"theme-factory", "no-such-skill"]\n',
            text,
        )
        self.assertIn("```\nYou are the project manager of the lab.\nYou keep the task board.\n```", text)
        operon = (self.lab / "migration" / "profiles" / "OPERON.md").read_text(encoding="utf-8")
        self.assertIn("skill_names: []\n", operon)
        self.assertIn("You are the main agent.", operon)

    def test_odd_skill_names_keep_the_frontmatter_and_the_diff_intact(self):
        names = ["a]b", "c,d", "e`f"]

        def edit(conn):
            conn.execute(
                "UPDATE user_agents SET skill_names = ? WHERE name = 'OPERON'", (json.dumps(names),))

        self.connect(edit)
        self.export()
        text = (self.lab / "migration" / "profiles" / "OPERON.md").read_text(encoding="utf-8")
        line = next(l for l in text.split("\n") if l.startswith("skill_names:"))
        self.assertEqual(line, 'skill_names: ["a]b", "c,d", "e`f"]')
        self.assertEqual(json.loads(line[len("skill_names:"):]), names)
        unmatched = self.diff_text()
        unmatched = unmatched[unmatched.index("\n## Unmatched") + 1:]
        found = groups(unmatched)
        self.assertEqual(found["unknown"], ["`a]b`", "`c,d`", "``e`f``"])

    def test_renamed_skill_line_reads_old_arrow_new(self):
        def edit(conn):
            conn.execute(
                "UPDATE user_agents SET skill_names = ? WHERE name = 'OPERON'",
                (json.dumps(["findings-ledger"]),),
            )

        self.connect(edit)
        self.export()
        self.assertIn("- `findings-ledger` -> `recording-findings`", self.diff_text())

    def test_diff_matches_profile_to_agent(self):
        report = self.export()
        self.assertEqual((report.matched, report.unmatched), (1, 1))
        section = self.section("## `LAB_PROJECT_MANAGER` -> `lab-project-manager.md`")
        self.assertIn("```diff", section)
        self.assertIn("--- claude-science/LAB_PROJECT_MANAGER", section)
        self.assertIn("+++ agents/lab-project-manager.md", section)
        self.assertIn("\n-You keep the task board.", section)
        self.assertIn("\n+You keep the gates.", section)
        self.assertNotIn("Not part of the first paragraph", section)
        listed = " ".join(" ".join(v) for v in groups(section).values())
        self.assertNotIn("doi-verified-evidence", listed)
        self.assertNotIn("verifying-evidence-by-doi", listed)
        self.assertIn("decides nothing by itself", self.diff_text())

    def test_unmatched_profile_listed(self):
        self.export()
        text = self.diff_text()
        self.assertIn("\n## Unmatched", text)
        unmatched = text[text.index("\n## Unmatched"):]
        self.assertIn("OPERON", unmatched)
        self.assertNotIn("LAB_PROJECT_MANAGER", unmatched)

    def test_missing_skills_classified(self):
        self.export()
        found = groups(self.section("## `LAB_PROJECT_MANAGER` -> `lab-project-manager.md`"))
        by_class = {key.split(" ")[0]: value for key, value in found.items()}
        self.assertEqual(set(by_class), {"vendored", "bundled", "account", "example", "unknown"})
        self.assertEqual(by_class["vendored"], ["`peer-review`"])
        self.assertEqual(by_class["bundled"], ["`pdf-explore`"])
        self.assertEqual(by_class["account"], ["`deep-research`"])
        self.assertEqual(by_class["example"], ["`theme-factory`"])
        self.assertEqual(by_class["unknown"], ["`no-such-skill`"])
        headings = list(found)
        self.assertIn("bundled (Claude Science only; not portable)", headings)
        self.assertIn("account (reachable in Claude Code through the claude.ai sign-in)", headings)

    def test_unmatched_profile_skills_are_classified_too(self):
        def edit(conn):
            conn.execute(
                "UPDATE user_agents SET skill_names = ? WHERE name = 'OPERON'",
                (json.dumps(["findings-ledger", "pdf-explore"]),),
            )

        self.connect(edit)
        self.export()
        text = self.diff_text()
        found = groups(text[text.index("\n## Unmatched") + 1:])
        by_class = {key.split(" ")[0]: value for key, value in found.items()}
        self.assertIn("`recording-findings`", " ".join(by_class.get("lab", [])))
        self.assertEqual(by_class["bundled"], ["`pdf-explore`"])

    def test_bad_skill_names_json_gives_a_report_line(self):
        def edit(conn):
            conn.execute("UPDATE user_agents SET skill_names = 'not json' WHERE name = 'OPERON'")

        self.connect(edit)
        report = self.export()
        self.assertTrue(any("OPERON" in line and "skill_names" in line for line in report.lines), report.lines)
        text = (self.lab / "migration" / "profiles" / "OPERON.md").read_text(encoding="utf-8")
        self.assertIn("skill_names: []\n", text)

    def test_profile_names_that_sanitise_alike_do_not_overwrite_each_other(self):
        def edit(conn):
            conn.execute("UPDATE user_agents SET name = 'Xy', display_name = 'First' WHERE name = 'OPERON'")
            conn.execute(
                "UPDATE user_agents SET name = 'xy', display_name = 'Second' WHERE name = 'LAB_PROJECT_MANAGER'")
            conn.execute(
                "INSERT INTO user_agents (id, user_id, name, display_name, description, system_prompt,"
                " skill_names, created_at, updated_at) VALUES (?, ?, 'XY', 'Third', 'd', 'Third prompt',"
                " '[]', 1, 1)", (fixture_db._uid(0x599), fixture_db.USER_ID))

        self.connect(edit)
        report = self.export()
        self.assertEqual(report.profiles, 3)
        folder = self.lab / "migration" / "profiles"
        self.assertEqual(sorted(p.name for p in folder.glob("*.md")), ["XY.md", "Xy_2.md", "xy_3.md"])
        for leaf, display in (("XY.md", "Third"), ("Xy_2.md", "First"), ("xy_3.md", "Second")):
            text = (folder / leaf).read_text(encoding="utf-8")
            self.assertIn("display_name: " + display + "\n", text)

    def test_profile_file_names_keep_underscores_and_clash_with_an_underscore_number(self):
        self.assertEqual(mcs._profile_file_name("LIT RESEARCHER"), "LIT_RESEARCHER")
        self.assertEqual(mcs._profile_file_name("a!!b"), "a__b")
        self.assertEqual(mcs._profile_file_name("Keep_this-name.v2"), "Keep_this-name.v2")

        def edit(conn):
            conn.execute("UPDATE user_agents SET name = 'LIT_RESEARCHER' WHERE name = 'OPERON'")
            conn.execute("UPDATE user_agents SET name = 'lit_researcher' WHERE name = 'LAB_PROJECT_MANAGER'")

        self.connect(edit)
        self.export()
        folder = self.lab / "migration" / "profiles"
        self.assertEqual(
            sorted(p.name for p in folder.glob("*.md")), ["LIT_RESEARCHER.md", "lit_researcher_2.md"])
        self.assertIn("display_name: Operon\n", (folder / "LIT_RESEARCHER.md").read_text(encoding="utf-8"))
        self.assertIn(
            "display_name: Lab Project Manager\n", (folder / "lit_researcher_2.md").read_text(encoding="utf-8"))

    def test_no_agent_file_is_changed(self):
        before = tree_snapshot(self.plugin)
        self.export()
        self.assertEqual(before, tree_snapshot(self.plugin))
        self.assertEqual(self.agent_file.read_bytes(), STUB_AGENT.encode("utf-8"))

    def test_dry_run_writes_nothing(self):
        dry = self.export(write=False)
        self.assertFalse(self.lab.exists())
        real = self.export()
        self.assertEqual(dataclasses.asdict(dry), dataclasses.asdict(real))

    def test_unsafe_profile_name_stays_inside_the_folder(self):
        def edit(conn):
            conn.execute("UPDATE user_agents SET name = '../evil' WHERE name = 'OPERON'")

        self.connect(edit)
        report = self.export()
        self.assertFalse((self.lab / "migration" / "evil.md").exists())
        self.assertEqual(len(list((self.lab / "migration" / "profiles").glob("*.md"))), 1)
        self.assertEqual(report.invalid_ids, 1)
        self.assertIn("invalid id skipped: user_agents '../evil'", report.lines)


class CliStepTest(ProfileTestCase):
    def test_cli_runs_the_profile_step(self):
        self.lab.mkdir()
        (self.lab / "lab.json").write_text("{}\n", encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = mcs.main([
                "--data-dir", str(self.info.data_dir), "--config-home", str(self.tmp / "nohome"),
                "--synced-skills-dir", str(self.synced),
                "--project", "proj_fix", "--lab", str(self.lab), "--dry-run",
            ])
        self.assertEqual(code, 0, err.getvalue())
        self.assertIn("| profiles | 2 | 2 | 0 | 0 |", out.getvalue())
        written = {p.relative_to(self.lab).as_posix() for p in self.lab.rglob("*") if p.is_file()}
        self.assertEqual(written, {"lab.json", "migration/MIGRATION_REPORT.md"})


if __name__ == "__main__":
    unittest.main()
