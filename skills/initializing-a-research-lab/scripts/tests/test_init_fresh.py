"""init_lab.py on a fresh folder: the plan, the dry run, the apply and the re-run."""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "init_lab.py"
HAVE_GIT = shutil.which("git") is not None
GIT_IDENTITY = {
    "GIT_AUTHOR_NAME": "Lab Test",
    "GIT_AUTHOR_EMAIL": "lab@example.invalid",
    "GIT_COMMITTER_NAME": "Lab Test",
    "GIT_COMMITTER_EMAIL": "lab@example.invalid",
    # Ignore the machine's git configuration (signing, hooks, templates) so the tests are hermetic.
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}
BEGIN = "<!-- science-ultrapowers:begin -->"
END = "<!-- science-ultrapowers:end -->"
RECORD_FOLDERS = [
    "project",
    "literature",
    "findings",
    "experiments",
    "reviews",
    "requests",
    "decisions",
    "planning",
    "automation",
    "tool_vetting",
]


def run_script(args, cwd, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def snapshot(root: Path):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))


class FreshFolderCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.proj = self.tmp / "proj"
        self.proj.mkdir()

    def init(self, *extra, yes=True, as_json=True, cwd=None, env_extra=None, root=True):
        args = []
        if root:
            args += ["--project-root", str(self.proj)]
        args += ["--name", "Demo study"]
        args += list(extra)
        if yes:
            args.append("--yes")
        if as_json:
            args.append("--json")
        return run_script(args, cwd or self.tmp, env_extra)

    def lab_json(self):
        return json.loads((self.proj / "research_lab" / "lab.json").read_text(encoding="utf-8"))


class TestFreshFolder(FreshFolderCase):
    def test_dry_run_writes_nothing_and_lists_files(self):
        before = snapshot(self.proj)
        result = self.init(yes=False, as_json=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.proj), before)
        plan = json.loads(result.stdout)
        for item in (
            "research_lab/lab.json",
            "research_lab/artifacts/.gitattributes",
            "research_lab/memory/MEMORY.md",
            "research_lab/templates/TASK_REPORT.md",
            "CLAUDE.md",
        ):
            self.assertIn(item, plan["create"])
        self.assertIn(".gitignore", plan["append"])
        self.assertIn("references/", plan["create"])
        self.assertEqual(plan["connectors"], {})
        self.assertEqual(plan["duplicates"], [])
        self.assertNotIn("\\", plan["projectRoot"])

    def test_dry_run_prints_the_readable_lines_and_the_closing_sentence(self):
        before = snapshot(self.proj)
        result = self.init("--connectors", "pubmed", yes=False, as_json=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.proj), before)
        lines = result.stdout.splitlines()
        self.assertIn("create research_lab/lab.json", lines)
        self.assertIn("create .mcp.json", lines)
        self.assertIn("append .gitignore", lines)
        self.assertEqual(lines[-1], "Dry run: nothing written. Re-run with --yes to apply.")
        self.assertFalse([l for l in lines if l.startswith("written:")], lines)
        self.assertFalse(result.stdout.lstrip().startswith("{"))

    def test_dry_run_prints_the_warnings_too(self):
        (self.proj / ".claude" / "agents").mkdir(parents=True)
        (self.proj / ".claude" / "agents" / "citation-reference-auditor.md").write_text("mine", encoding="utf-8")
        lines = self.init(yes=False, as_json=False).stdout.splitlines()
        self.assertTrue(any(l.startswith("warn same names as the plugin's agents or skills") for l in lines), lines)

    def test_dry_run_lines_match_the_applied_report_lines(self):
        dry = self.init(yes=False, as_json=False).stdout.splitlines()
        real = self.init(as_json=False).stdout.splitlines()
        verbs = ("create ", "append ", "skip ")
        planned = [l for l in dry if l.startswith(verbs)]
        applied = [l for l in real if l.startswith(verbs)]
        self.assertEqual(planned, applied)

    def test_apply_creates_layout(self):
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        lab = self.proj / "research_lab"
        for folder in RECORD_FOLDERS:
            self.assertTrue((lab / folder).is_dir(), folder)
        self.assertEqual(len(list((lab / "templates").iterdir())), 12)
        self.assertTrue((lab / "artifacts" / "archive").is_dir())
        self.assertTrue((lab / "memory" / "project").is_dir())
        self.assertTrue((lab / "memory" / "artifact").is_dir())
        self.assertTrue((lab / ".working" / ".gitkeep").is_file())
        self.assertTrue((lab / "memory" / "MEMORY.md").is_file())
        self.assertTrue((lab / "memory" / "README.md").is_file())
        self.assertFalse((lab / "memory" / "entry.md").exists())
        for name in ("LAB_MEETING.md", "SESSION_OPENING.md", "SESSION_CLOSE.md"):
            self.assertTrue((lab / "templates" / name).is_file(), name)
        self.assertTrue((self.proj / "references").is_dir())
        data = self.lab_json()
        self.assertEqual(data["name"], "Demo study")
        self.assertEqual(data["shortName"], "demo-study")
        self.assertEqual(data["lfs"]["thresholdMB"], 10)
        self.assertEqual(data["memory"]["indexBudget"], 150)
        self.assertEqual(len(data["roles"]), 14)
        self.assertTrue(all(v is True for v in data["roles"].values()))
        self.assertIsNone(data["claudeScience"])
        claude = (self.proj / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(claude.count(BEGIN), 1)
        self.assertEqual(claude.count(END), 1)
        self.assertIn("@research_lab/project/PROJECT_BRIEF.md", claude)
        ignore = (self.proj / ".gitignore").read_text(encoding="utf-8").splitlines()
        for line in ("/research_lab/.working/", "/.venv-lab-skills/", "/references/"):
            self.assertIn(line, ignore)
        attrs = (lab / "artifacts" / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertTrue(attrs[0].startswith("# science-ultrapowers artifact archive"))
        self.assertIn("archive/** -text", attrs)
        self.assertIn("*.jsonl text eol=lf", attrs)
        report = json.loads(result.stdout)
        self.assertIn("research_lab/lab.json", report["written"])
        self.assertNotIn("references/", report["written"])

    def test_lab_json_memory_keeps_only_the_index_budget(self):
        self.assertEqual(self.init().returncode, 0)
        data = self.lab_json()
        self.assertEqual(data["memory"], {"indexBudget": 150})
        self.assertEqual(len(data["roles"]), 14)

    def test_text_report_without_json(self):
        result = self.init(as_json=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertIn("create research_lab/lab.json", lines)
        self.assertIn("append .gitignore", lines)
        self.assertRegex(lines[-1], r"^written: \d+ files$")

    def test_rerun_skips_everything(self):
        first = self.init()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = {p: (self.proj / p).read_bytes() for p in snapshot(self.proj) if (self.proj / p).is_file()}
        second = self.init()
        self.assertEqual(second.returncode, 0, second.stderr)
        report = json.loads(second.stdout)
        self.assertEqual(report["create"], [])
        self.assertEqual(report["append"], [])
        self.assertEqual(report["written"], [])
        self.assertIn("research_lab/lab.json", report["skip"])
        self.assertIn("CLAUDE.md", report["skip"])
        self.assertIn(".gitignore", report["skip"])
        self.assertIn("references/", report["skip"])
        self.assertIn("research_lab/artifacts/.gitattributes", report["skip"])
        after = {p: (self.proj / p).read_bytes() for p in snapshot(self.proj) if (self.proj / p).is_file()}
        self.assertEqual(before, after)

    def test_placeholders_substituted(self):
        result = self.init("--description", "A study of things")
        self.assertEqual(result.returncode, 0, result.stderr)
        brief = self.proj / "research_lab" / "project" / "PROJECT_BRIEF.md"
        self.assertEqual(brief.read_text(encoding="utf-8").splitlines()[0], "# Demo study project brief")
        for path in self.proj.rglob("*"):
            if path.is_file():
                self.assertNotIn("{{", path.read_text(encoding="utf-8"), path.as_posix())
        data = self.lab_json()
        self.assertRegex(data["scaffoldedAt"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertNotEqual(data["pluginVersion"], "")
        self.assertEqual(data["description"], "A study of things")

    def readme_sentence(self):
        text = (self.proj / "research_lab" / "README.md").read_text(encoding="utf-8")
        return next(line for line in text.splitlines() if line.startswith("This folder is the record"))

    def test_readme_first_sentence_without_a_description(self):
        self.assertEqual(self.init().returncode, 0)
        sentence = self.readme_sentence()
        self.assertTrue(
            sentence.startswith("This folder is the record of the research lab that works on Demo study. It indexes"),
            sentence,
        )
        self.assertNotIn(": .", sentence)

    def test_readme_first_sentence_with_a_description(self):
        self.assertEqual(self.init("--description", "A study of things.").returncode, 0)
        sentence = self.readme_sentence()
        self.assertTrue(
            sentence.startswith("This folder is the record of the research lab that works on Demo study: A study of things. It indexes"),
            sentence,
        )
        self.assertNotIn("..", sentence)

    @unittest.skipUnless(HAVE_GIT, "git is not installed")
    def test_project_root_defaults_to_git_toplevel_from_subdir(self):
        subprocess.run(["git", "init", "-q", str(self.proj)], check=True, capture_output=True)
        sub = self.proj / "src"
        sub.mkdir()
        result = self.init(cwd=sub, root=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.proj / "research_lab" / "lab.json").is_file())
        self.assertFalse((sub / "research_lab").exists())

    def test_project_root_defaults_to_cwd_outside_git(self):
        result = self.init(cwd=self.proj, root=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.proj / "research_lab" / "lab.json").is_file())

    def test_project_root_that_is_not_a_directory_exits_2(self):
        missing = self.tmp / "missing"
        result = run_script(["--project-root", str(missing), "--name", "X", "--yes"], self.tmp)
        self.assertEqual(result.returncode, 2)
        self.assertNotEqual(result.stderr.strip(), "")
        self.assertFalse(missing.exists())

    def test_no_backslashes_in_written_json(self):
        result = self.init("--description", "plain")
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in self.proj.rglob("*.json"):
            self.assertNotIn("\\", path.read_text(encoding="utf-8"), path.as_posix())
        self.assertNotIn("\\", json.loads(result.stdout)["projectRoot"])

    def test_lfs_threshold_flag(self):
        result = self.init("--lfs-threshold-mb", "25")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.lab_json()["lfs"]["thresholdMB"], 25)

    def test_lfs_threshold_must_be_positive(self):
        result = self.init("--lfs-threshold-mb", "0")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.proj / "research_lab").exists())

    def test_description_with_quotes_keeps_lab_json_valid(self):
        result = self.init("--description", 'a "quoted" word')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.lab_json()["description"], 'a "quoted" word')

    def test_files_are_lf_and_templates_stay_empty(self):
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in self.proj.rglob("*"):
            if path.is_file():
                self.assertNotIn(b"\r", path.read_bytes(), path.as_posix())
        jev = self.proj / "research_lab" / "automation" / "JEV_CALLS.jsonl"
        self.assertEqual(jev.read_bytes(), b"")

    def test_existing_files_are_never_overwritten(self):
        lab = self.proj / "research_lab"
        (lab / "decisions").mkdir(parents=True)
        mine = lab / "decisions" / "DECISION_LOG.md"
        mine.write_text("my own decisions\n", encoding="utf-8")
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(mine.read_text(encoding="utf-8"), "my own decisions\n")
        self.assertIn("research_lab/decisions/DECISION_LOG.md", json.loads(result.stdout)["skip"])

    def test_existing_claude_md_gets_the_section_appended(self):
        claude = self.proj / "CLAUDE.md"
        claude.write_bytes(b"# Mine\n")
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CLAUDE.md", json.loads(result.stdout)["append"])
        text = claude.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# Mine\n\n" + BEGIN))
        self.assertEqual(text.count(BEGIN), 1)
        self.assertEqual(text.count(END), 1)
        before = claude.read_bytes()
        again = self.init()
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(claude.read_bytes(), before)

    def test_crlf_claude_md_stays_crlf(self):
        claude = self.proj / "CLAUDE.md"
        claude.write_bytes(b"# Mine\r\nline\r\n")
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        raw = claude.read_bytes()
        self.assertTrue(raw.startswith(b"# Mine\r\nline\r\n\r\n"))
        self.assertIn(BEGIN.encode("utf-8"), raw)
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"))
        again = self.init()
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(claude.read_bytes(), raw)

    def test_existing_gitignore_gets_only_missing_lines(self):
        ignore = self.proj / ".gitignore"
        ignore.write_bytes(b"node_modules/\nreferences/")
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            ignore.read_text(encoding="utf-8").splitlines(),
            ["node_modules/", "references/", "/research_lab/.working/", "/.venv-lab-skills/"],
        )

    def test_unanchored_existing_line_counts_as_present(self):
        ignore = self.proj / ".gitignore"
        ignore.write_bytes(b"research_lab/.working/\n")
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = ignore.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines.count("research_lab/.working/"), 1)
        self.assertNotIn("/research_lab/.working/", lines)
        self.assertIn("/references/", lines)

    @unittest.skipUnless(HAVE_GIT, "git is not installed")
    def test_nested_references_folder_is_not_ignored(self):
        subprocess.run(["git", "init", "-q", str(self.proj)], check=True, capture_output=True, env={**os.environ, **GIT_IDENTITY})
        nested = self.proj / "paper" / "references"
        nested.mkdir(parents=True)
        (nested / "refs.bib").write_text("@misc{a}", encoding="utf-8")
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)

        def ignored(path):
            return subprocess.run(
                ["git", "check-ignore", "-q", path], cwd=self.proj, capture_output=True, env={**os.environ, **GIT_IDENTITY}
            ).returncode

        self.assertEqual(ignored("paper/references/refs.bib"), 1)
        self.assertEqual(ignored("references/x.pdf"), 0)

    def test_existing_archive_gitattributes_gets_missing_rules(self):
        store = self.proj / "research_lab" / "artifacts"
        store.mkdir(parents=True)
        (store / ".gitattributes").write_text("archive/** -text\n", encoding="utf-8")
        plan = json.loads(self.init(yes=False).stdout)
        self.assertIn("research_lab/artifacts/.gitattributes", plan["append"])
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = (store / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "archive/** -text")
        self.assertIn("*.jsonl text eol=lf", lines)

    def test_unreadable_existing_lab_json_is_a_warning_not_a_crash(self):
        lab = self.proj / "research_lab"
        lab.mkdir()
        (lab / "lab.json").write_text("{not json", encoding="utf-8")
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(any("lab.json" in w for w in report["warn"]), report["warn"])
        self.assertEqual((lab / "lab.json").read_text(encoding="utf-8"), "{not json")

    @unittest.skipUnless(HAVE_GIT, "git is not installed")
    def test_git_init_commits_the_scaffold(self):
        result = self.init("--git-init", env_extra=GIT_IDENTITY)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.proj / ".git").exists())
        log = subprocess.run(
            ["git", "log", "--oneline"], cwd=self.proj, capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(len(log.stdout.splitlines()), 1, log.stdout + log.stderr)
        files = subprocess.run(
            ["git", "ls-files"], cwd=self.proj, capture_output=True, text=True, encoding="utf-8"
        ).stdout.splitlines()
        self.assertIn("research_lab/lab.json", files)
        self.assertIn("CLAUDE.md", files)
        self.assertFalse([f for f in files if f.startswith("research_lab/.working/")], files)
        self.assertFalse([f for f in files if f.startswith("references/")], files)

    def tracked(self):
        return subprocess.run(
            ["git", "ls-files"], cwd=self.proj, capture_output=True, text=True, encoding="utf-8"
        ).stdout.splitlines()

    @unittest.skipUnless(HAVE_GIT, "git is not installed")
    def test_git_init_commits_the_gitignore_it_created(self):
        self.assertEqual(self.init("--git-init", env_extra=GIT_IDENTITY).returncode, 0)
        files = self.tracked()
        self.assertIn(".gitignore", files)
        self.assertIn("research_lab/lab.json", files)

    @unittest.skipUnless(HAVE_GIT, "git is not installed")
    def test_git_init_leaves_appended_files_for_your_human_partner(self):
        secret = "Bearer not-a-real-token"
        (self.proj / ".mcp.json").write_text(
            json.dumps({"mcpServers": {"mine": {"type": "http", "url": "https://example.invalid/mcp", "headers": {"Authorization": secret}}}})
            + "\n",
            encoding="utf-8",
        )
        (self.proj / "CLAUDE.md").write_text("# Mine\n", encoding="utf-8")
        (self.proj / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
        result = self.init("--git-init", "--connectors", "pubmed", env_extra=GIT_IDENTITY)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        for rel in (".mcp.json", "CLAUDE.md", ".gitignore"):
            self.assertIn(rel, report["append"])
        files = self.tracked()
        self.assertIn("research_lab/lab.json", files)
        for rel in (".mcp.json", "CLAUDE.md", ".gitignore"):
            self.assertNotIn(rel, files)
            self.assertIn(f"review and commit {rel} yourself", " | ".join(report["warn"]))
        shown = subprocess.run(
            ["git", "show", "--stat", "-p", "HEAD"], cwd=self.proj, capture_output=True, text=True, encoding="utf-8"
        ).stdout
        self.assertNotIn(secret, shown)
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=self.proj, capture_output=True, text=True, encoding="utf-8"
        ).stdout
        self.assertIn("?? .mcp.json", status)

    @unittest.skipUnless(HAVE_GIT, "git is not installed")
    def test_git_init_on_an_existing_repository_warns_and_leaves_history(self):
        subprocess.run(["git", "init", "-q", str(self.proj)], check=True, capture_output=True)
        plan = json.loads(self.init("--git-init", yes=False).stdout)
        self.assertNotIn(".git/", plan["create"])
        self.assertTrue(any("already a git repository" in w for w in plan["warn"]), plan["warn"])
        result = self.init("--git-init", env_extra=GIT_IDENTITY)
        self.assertEqual(result.returncode, 0, result.stderr)
        log = subprocess.run(
            ["git", "log", "--oneline"], cwd=self.proj, capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(log.stdout.strip(), "")

    @unittest.skipUnless(HAVE_GIT, "git is not installed")
    def test_git_commit_failure_is_a_warning(self):
        env = dict(GIT_IDENTITY)
        # An unusable identity makes the commit fail without touching the real git configuration.
        env["GIT_AUTHOR_NAME"] = ""
        env["GIT_COMMITTER_NAME"] = ""
        env["GIT_CONFIG_GLOBAL"] = os.devnull
        env["GIT_CONFIG_SYSTEM"] = os.devnull
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        result = self.init("--git-init", env_extra=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertTrue((self.proj / "research_lab" / "lab.json").is_file())
        report = json.loads(result.stdout)
        self.assertTrue(any(re.search(r"git (init|add|commit) failed", w) for w in report["warn"]), report["warn"])


if __name__ == "__main__":
    unittest.main()
