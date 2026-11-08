"""init_lab.py on a project that already has a lab, instructions files and duplicate agents and skills."""

import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_init_fresh import BEGIN, END, RECORD_FOLDERS, run_script

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import init_lab  # noqa: E402

FINDINGS = "# Findings\n\n| id | claim |\n|----|-------|\n| F-0001 | a recorded claim |\n"
CARD = "my own evidence card\n"
DOT_CLAUDE = "# Project rules\n\nKeep it small.\n"
DUPLICATES = [
    ".claude/agents/citation-auditor.md",
    ".claude/skills/doi-verified-evidence",
    ".claude/skills/peer-review",
]


def make_existing_lab(root: Path) -> None:
    lab = root / "research_lab"
    for folder in RECORD_FOLDERS:
        (lab / folder).mkdir(parents=True)
    (lab / "02_findings_ledger" / "FINDINGS.md").write_text(FINDINGS, encoding="utf-8")
    (lab / "templates").mkdir()
    (lab / "templates" / "EVIDENCE_CARD.md").write_text(CARD, encoding="utf-8")
    claude = root / ".claude"
    (claude / "agents").mkdir(parents=True)
    (claude / "CLAUDE.md").write_text(DOT_CLAUDE, encoding="utf-8")
    (claude / "agents" / "citation-auditor.md").write_text("my agent\n", encoding="utf-8")
    for skill in ("doi-verified-evidence", "peer-review"):
        (claude / "skills" / skill).mkdir(parents=True)
        (claude / "skills" / skill / "SKILL.md").write_text(f"my {skill}\n", encoding="utf-8")


def tree_bytes(root: Path, prefix: str) -> dict:
    base = root / prefix
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(base.rglob("*")) if p.is_file()}


class ExistingCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        make_existing_lab(self.proj)

    def init(self, *extra, yes=True):
        args = ["--project-root", str(self.proj), "--name", "Existing", *extra]
        if yes:
            args.append("--yes")
        args.append("--json")
        return run_script(args, self.tmp)

    def report(self, *extra, yes=True):
        result = self.init(*extra, yes=yes)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return json.loads(result.stdout)


class TestExistingProject(ExistingCase):
    def test_existing_files_are_skipped_and_untouched(self):
        findings = self.proj / "research_lab" / "02_findings_ledger" / "FINDINGS.md"
        card = self.proj / "research_lab" / "templates" / "EVIDENCE_CARD.md"
        before = (findings.read_bytes(), card.read_bytes())
        report = self.report()
        self.assertEqual((findings.read_bytes(), card.read_bytes()), before)
        self.assertIn("research_lab/02_findings_ledger/FINDINGS.md", report["skip"])
        self.assertIn("research_lab/templates/EVIDENCE_CARD.md", report["skip"])
        self.assertNotIn("research_lab/02_findings_ledger/FINDINGS.md", report["create"])

    def test_missing_pieces_are_created(self):
        report = self.report()
        lab = self.proj / "research_lab"
        self.assertTrue((lab / "artifacts" / "store").is_dir())
        self.assertTrue((lab / "artifacts" / ".gitattributes").is_file())
        self.assertTrue((lab / "memory" / "MEMORY.md").is_file())
        self.assertTrue((lab / "lab.json").is_file())
        self.assertTrue((lab / ".scratch" / ".gitkeep").is_file())
        self.assertEqual(len(list((lab / "templates").iterdir())), 12)
        self.assertIn("research_lab/lab.json", report["create"])

    def test_section_goes_to_dot_claude_when_it_is_the_only_instructions_file(self):
        report = self.report()
        self.assertFalse((self.proj / "CLAUDE.md").exists())
        self.assertIn(".claude/CLAUDE.md", report["append"])
        self.assertNotIn("CLAUDE.md", report["create"])
        text = (self.proj / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith(DOT_CLAUDE + "\n" + BEGIN))
        self.assertEqual(text.count(BEGIN), 1)
        self.assertEqual(text.count(END), 1)
        self.assertIn("@../research_lab/00_project_knowledge/PROJECT_BRIEF.md", text)
        self.assertIn("@../research_lab/memory/MEMORY.md", text)
        self.assertNotIn("@research_lab/", text)

    def test_root_claude_md_preferred_when_present(self):
        (self.proj / "CLAUDE.md").write_text("# Root\n", encoding="utf-8")
        dot_before = (self.proj / ".claude" / "CLAUDE.md").read_bytes()
        report = self.report()
        self.assertIn("CLAUDE.md", report["append"])
        self.assertNotIn(".claude/CLAUDE.md", report["append"])
        root = (self.proj / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(root.count(BEGIN), 1)
        self.assertIn("@research_lab/00_project_knowledge/PROJECT_BRIEF.md", root)
        self.assertNotIn("@../", root)
        self.assertEqual((self.proj / ".claude" / "CLAUDE.md").read_bytes(), dot_before)

    def test_duplicates_are_reported_not_touched(self):
        before = tree_bytes(self.proj, ".claude/agents") | tree_bytes(self.proj, ".claude/skills")
        plan = json.loads(self.init(yes=False).stdout)
        self.assertEqual(plan["duplicates"], DUPLICATES)
        report = self.report()
        self.assertEqual(report["duplicates"], DUPLICATES)
        after = tree_bytes(self.proj, ".claude/agents") | tree_bytes(self.proj, ".claude/skills")
        self.assertEqual(before, after)
        lines = [w for w in report["warn"] if w.startswith("same names as the plugin's agents or skills were left in place; check each for local changes and remove it by hand: ")]
        self.assertEqual(len(lines), 1, report["warn"])
        for name in DUPLICATES:
            self.assertIn(name, lines[0])

    def test_no_duplicates_means_no_duplicates_warning(self):
        fresh = self.tmp / "fresh"
        fresh.mkdir()
        result = run_script(["--project-root", str(fresh), "--name", "X", "--json"], self.tmp)
        plan = json.loads(result.stdout)
        self.assertEqual(plan["duplicates"], [])
        self.assertFalse([w for w in plan["warn"] if w.startswith(("duplicates", "same names"))])

    def test_readonly_claude_md_is_a_warning(self):
        target = self.proj / ".claude" / "CLAUDE.md"
        os.chmod(target, stat.S_IREAD)
        self.addCleanup(os.chmod, target, stat.S_IWRITE | stat.S_IREAD)
        before = target.read_bytes()
        report = self.report()
        self.assertEqual(target.read_bytes(), before)
        self.assertTrue(any(".claude/CLAUDE.md" in w for w in report["warn"]), report["warn"])
        self.assertNotIn(".claude/CLAUDE.md", report["append"])
        self.assertTrue((self.proj / "research_lab" / "lab.json").is_file())

    def test_marker_in_dot_claude_stops_a_second_section(self):
        first = self.report()
        self.assertIn(".claude/CLAUDE.md", first["append"])
        root = self.proj / "CLAUDE.md"
        root.write_text("# Root\n", encoding="utf-8")
        second = self.report()
        self.assertEqual(root.read_text(encoding="utf-8"), "# Root\n")
        self.assertNotIn(BEGIN, root.read_text(encoding="utf-8"))
        self.assertIn(".claude/CLAUDE.md", second["skip"])
        self.assertNotIn("CLAUDE.md", second["append"])
        self.assertNotIn("CLAUDE.md", second["create"])

    def test_marker_in_root_stops_a_section_in_dot_claude(self):
        (self.proj / "CLAUDE.md").write_text("# Root\n\n" + BEGIN + "\nmine\n" + END + "\n", encoding="utf-8")
        dot_before = (self.proj / ".claude" / "CLAUDE.md").read_bytes()
        report = self.report()
        self.assertIn("CLAUDE.md", report["skip"])
        self.assertNotIn(".claude/CLAUDE.md", report["append"])
        self.assertNotIn("CLAUDE.md", report["append"])
        self.assertEqual((self.proj / ".claude" / "CLAUDE.md").read_bytes(), dot_before)

    def test_symlinked_claude_md_is_a_warning(self):
        outside = self.tmp / "outside.md"
        outside.write_text("# Shared instructions\n", encoding="utf-8")
        link = self.proj / "CLAUDE.md"
        try:
            os.symlink(outside, link)
        except (OSError, NotImplementedError):
            self.skipTest("cannot create symlinks here")
        report = self.report()
        self.assertEqual(outside.read_text(encoding="utf-8"), "# Shared instructions\n")
        self.assertTrue(link.is_symlink())
        warns = [w for w in report["warn"] if "CLAUDE.md" in w and "symlink" in w]
        self.assertEqual(len(warns), 1, report["warn"])
        self.assertIn(str(outside.name), warns[0])
        self.assertIn("by hand", warns[0])
        self.assertNotIn("CLAUDE.md", report["append"])
        self.assertTrue((self.proj / "research_lab" / "lab.json").is_file())

    def test_symlink_is_never_written_through_even_where_symlinks_are_unavailable(self):
        # The real-symlink test above is skipped on machines that cannot create links; this one stands in.
        (self.proj / "CLAUDE.md").write_text("# Root\n", encoding="utf-8")
        opts = init_lab.Options(name="Existing")
        with mock.patch.object(init_lab, "is_symlink", lambda path: path.name == "CLAUDE.md"), mock.patch.object(
            init_lab, "symlink_target", lambda path: "../shared/CLAUDE.md"
        ):
            plan = init_lab.build_plan(self.proj, opts)
            report = init_lab.apply_plan(plan, self.proj, opts)
        self.assertEqual((self.proj / "CLAUDE.md").read_text(encoding="utf-8"), "# Root\n")
        self.assertNotIn("CLAUDE.md", report["append"])
        warns = [w for w in report["warn"] if w.startswith("CLAUDE.md is a symlink")]
        self.assertEqual(len(warns), 1, report["warn"])
        self.assertIn("../shared/CLAUDE.md", warns[0])
        self.assertIn("by hand", warns[0])

    def test_missing_plugin_source_is_a_warning_not_a_create(self):
        opts = init_lab.Options(name="Existing")
        copied = {"research_lab/memory/GHOST.md": "no-such-skill/templates/GHOST.md"}
        with mock.patch.object(init_lab, "COPIED_FILES", copied):
            plan = init_lab.build_plan(self.proj, opts)
        self.assertNotIn("research_lab/memory/GHOST.md", plan.create)
        self.assertNotIn("research_lab/memory/GHOST.md", plan.skip)
        warns = [w for w in plan.warn if w.startswith("plugin file missing: ")]
        self.assertEqual(len(warns), 1, plan.warn)
        self.assertEqual(
            warns[0],
            "plugin file missing: skills/no-such-skill/templates/GHOST.md; "
            "research_lab/memory/GHOST.md was not planned",
        )

    def test_symlinked_mcp_json_is_never_written_through(self):
        (self.proj / ".mcp.json").write_text('{"mcpServers": {}}\n', encoding="utf-8")
        opts = init_lab.Options(name="Existing", connectors=["pubmed"])
        with mock.patch.object(init_lab, "is_symlink", lambda path: path.name == ".mcp.json"), mock.patch.object(
            init_lab, "symlink_target", lambda path: "../shared/mcp.json"
        ):
            plan = init_lab.build_plan(self.proj, opts)
            report = init_lab.apply_plan(plan, self.proj, opts)
        self.assertEqual((self.proj / ".mcp.json").read_text(encoding="utf-8"), '{"mcpServers": {}}\n')
        self.assertNotIn(".mcp.json", plan.append + plan.create)
        self.assertEqual(plan.connectors, {})
        self.assertEqual(plan.configured_connectors, [])
        warns = [w for w in report["warn"] if w.startswith(".mcp.json is a symlink")]
        self.assertEqual(len(warns), 1, report["warn"])
        self.assertEqual(
            warns[0], ".mcp.json is a symlink to ../shared/mcp.json; it was not written through: add the servers by hand"
        )

    def test_symlinked_gitignore_is_never_written_through(self):
        (self.proj / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
        opts = init_lab.Options(name="Existing")
        with mock.patch.object(init_lab, "is_symlink", lambda path: path.name == ".gitignore"), mock.patch.object(
            init_lab, "symlink_target", lambda path: "../shared/gitignore"
        ):
            plan = init_lab.build_plan(self.proj, opts)
            report = init_lab.apply_plan(plan, self.proj, opts)
        self.assertEqual((self.proj / ".gitignore").read_text(encoding="utf-8"), "node_modules/\n")
        self.assertNotIn(".gitignore", plan.append + plan.create)
        warns = [w for w in report["warn"] if w.startswith(".gitignore is a symlink")]
        self.assertEqual(len(warns), 1, report["warn"])
        self.assertEqual(
            warns[0], ".gitignore is a symlink to ../shared/gitignore; it was not written through: add the lines by hand"
        )

    def test_existing_lab_rerun_is_all_skip(self):
        self.report()
        again = self.report()
        self.assertEqual(again["create"], [])
        self.assertEqual(again["append"], [])
        self.assertEqual(again["written"], [])
        self.assertIn(".claude/CLAUDE.md", again["skip"])


if __name__ == "__main__":
    unittest.main()
