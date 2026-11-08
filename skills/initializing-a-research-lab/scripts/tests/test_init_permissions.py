"""init_lab.py --permissions: opt-in project permission rules for the literature domains."""

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_init_fresh import GIT_IDENTITY, HAVE_GIT, run_script

TEMPLATE = Path(__file__).resolve().parents[2] / "templates" / "permissions.json"
HOSTS = [
    "aclanthology.org",
    "api.crossref.org",
    "api.openalex.org",
    "api.semanticscholar.org",
    "arxiv.org",
    "doi.org",
    "jmlr.org",
    "openaccess.thecvf.com",
    "openalex.org",
    "openreview.net",
    "proceedings.mlr.press",
    "proceedings.neurips.cc",
    "pubmed.ncbi.nlm.nih.gov",
    "www.biorxiv.org",
    "www.medrxiv.org",
    "www.ncbi.nlm.nih.gov",
    "www.semanticscholar.org",
]
RULE_RE = re.compile(r"^WebFetch\(domain:[a-z0-9.-]+\)$")
RULES = [f"WebFetch(domain:{host})" for host in HOSTS]
NL = chr(10)


class PermissionsCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        self.settings = self.proj / ".claude" / "settings.json"

    def run_init(self, *extra, yes=True, as_json=True):
        args = ["--project-root", str(self.proj), "--name", "Perm", *extra]
        if yes:
            args.append("--yes")
        if as_json:
            args.append("--json")
        return run_script(args, self.tmp)

    def report(self, *extra, yes=True):
        result = self.run_init(*extra, yes=yes)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return json.loads(result.stdout)

    def lab_json(self):
        return json.loads((self.proj / "research_lab" / "lab.json").read_text(encoding="utf-8"))


class TestPermissions(PermissionsCase):
    def test_template_holds_the_agreed_hosts_sorted(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertTrue(text.endswith("}\n"))
        self.assertEqual(json.loads(text), {"permissions": {"allow": RULES}})
        self.assertEqual(RULES, sorted(RULES))

    def test_permissions_writes_webfetch_allows_when_absent(self):
        report = self.report("--permissions", "--allow-domain", "ieeexplore.ieee.org")
        data = json.loads(self.settings.read_text(encoding="utf-8"))
        allow = data["permissions"]["allow"]
        for rule in RULES:
            self.assertIn(rule, allow)
        self.assertIn("WebFetch(domain:ieeexplore.ieee.org)", allow)
        self.assertEqual(len(allow), len(RULES) + 1)
        for rule in allow:
            self.assertRegex(rule, RULE_RE)
            self.assertFalse(rule.startswith("Bash("))
        self.assertEqual(list(data), ["permissions"])
        raw = self.settings.read_text(encoding="utf-8")
        self.assertTrue(raw.endswith("\n"))
        self.assertTrue(raw.splitlines()[1].startswith('  "permissions"'))
        self.assertNotIn("\r", raw)
        self.assertIn(".claude/settings.json", report["create"])
        self.assertEqual(
            report["permissions"], {"file": ".claude/settings.json", "action": "create", "rules": allow}
        )

    def test_permissions_skips_existing_settings(self):
        self.settings.parent.mkdir()
        raw = b'{"theme": "x"}'
        self.settings.write_bytes(raw)
        plan = self.report("--permissions", yes=False)
        self.assertEqual(plan["permissions"]["action"], "skip")
        self.assertEqual(plan["permissions"]["rules"], RULES)
        self.assertIn(".claude/settings.json exists; merge the rules by hand", plan["skip"])
        self.assertNotIn(".claude/settings.json", plan["create"])
        report = self.report("--permissions")
        self.assertEqual(self.settings.read_bytes(), raw)
        self.assertEqual(report["permissions"]["action"], "skip")
        self.assertIn(".claude/settings.json exists; merge the rules by hand", report["skip"])
        text = self.run_init("--permissions", as_json=False).stdout
        lines = text.splitlines()
        at = lines.index("rules to merge into .claude/settings.json:")
        end = next(i for i, l in enumerate(lines) if l.startswith("written: "))
        self.assertEqual(json.loads(NL.join(lines[at + 1 : end])), {"permissions": {"allow": RULES}})
        self.assertRegex(lines[-1], r"^written: \d+ files$")
        dry = self.run_init("--permissions", yes=False, as_json=False).stdout.splitlines()
        at = dry.index("rules to merge into .claude/settings.json:")
        end = dry.index("Dry run: nothing written. Re-run with --yes to apply.")
        self.assertEqual(json.loads(NL.join(dry[at + 1 : end])), {"permissions": {"allow": RULES}})

    def test_invalid_existing_settings_are_left_alone_too(self):
        self.settings.parent.mkdir()
        raw = b'{"permissions": {"allow": [],}}'
        self.settings.write_bytes(raw)
        report = self.report("--permissions")
        self.assertEqual(self.settings.read_bytes(), raw)
        self.assertEqual(report["permissions"]["action"], "skip")

    def test_no_permissions_flag_writes_no_settings(self):
        report = self.report()
        self.assertFalse((self.proj / ".claude").exists())
        self.assertFalse(report["permissions"])
        self.assertFalse(self.lab_json()["permissions"]["written"])
        plan = self.report(yes=False)
        self.assertNotIn(".claude/settings.json", plan["create"] + plan["skip"] + plan["append"])

    def test_permission_rules_are_sorted_and_unique(self):
        report = self.report(
            "--permissions", "--allow-domain", "doi.org", "--allow-domain", "DOI.org",
            "--allow-domain", "aaa.example.org", "--allow-domain", "zzz.example.org",
        )
        allow = json.loads(self.settings.read_text(encoding="utf-8"))["permissions"]["allow"]
        self.assertEqual(allow, sorted(set(allow)))
        self.assertEqual(allow.count("WebFetch(domain:doi.org)"), 1)
        self.assertEqual(len(allow), len(RULES) + 2)
        self.assertEqual(allow[0], "WebFetch(domain:aaa.example.org)")
        self.assertEqual(allow[-1], "WebFetch(domain:zzz.example.org)")
        self.assertEqual(report["permissions"]["rules"], allow)

    def test_bad_domain_exits_2(self):
        for bad in ("evil.com/x", "no_dots", "-a.com", "a b.com", "http://x.org", "localhost", "a..b.com"):
            for yes in (True, False):
                result = self.run_init("--permissions", f"--allow-domain={bad}", yes=yes)
                self.assertEqual(result.returncode, 2, (bad, result.stderr))
                self.assertIn(bad, result.stderr)
                self.assertEqual(list(self.proj.iterdir()), [], bad)

    def test_allow_domain_with_a_trailing_newline_is_stored_stripped(self):
        report = self.report("--permissions", "--allow-domain", "ieeexplore.ieee.org" + NL, "--allow-domain", " Doi.org " + NL)
        allow = json.loads(self.settings.read_text(encoding="utf-8"))["permissions"]["allow"]
        self.assertIn("WebFetch(domain:ieeexplore.ieee.org)", allow)
        self.assertEqual(len(allow), len(RULES) + 1)
        for rule in allow:
            self.assertRegex(rule, RULE_RE)
            self.assertNotIn(NL, rule)
        self.assertEqual(report["permissions"]["rules"], allow)

    def test_allow_domain_with_an_inner_newline_exits_2(self):
        result = self.run_init("--permissions", "--allow-domain", "a.org" + NL + "b.org")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(list(self.proj.iterdir()), [])

    def test_allow_domain_without_permissions_exits_2(self):
        result = self.run_init("--allow-domain", "doi.org")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--allow-domain needs --permissions", result.stderr)
        self.assertEqual(list(self.proj.iterdir()), [])

    def test_lab_json_records_written_permissions(self):
        self.report("--permissions")
        self.assertTrue(self.lab_json()["permissions"]["written"])

    def test_lab_json_stays_false_when_settings_already_exist(self):
        self.settings.parent.mkdir()
        self.settings.write_bytes(b"{}")
        self.report("--permissions")
        self.assertFalse(self.lab_json()["permissions"]["written"])

    def test_no_bash_rule_is_ever_written(self):
        self.report("--permissions", "--allow-domain", "bash.example.org")
        text = self.settings.read_text(encoding="utf-8")
        self.assertNotIn("Bash(", text)
        self.assertNotIn("\\", text)

    @unittest.skipUnless(HAVE_GIT, "git is not installed")
    def test_git_init_commits_only_what_init_wrote_outside_research_lab(self):
        (self.proj / ".claude" / "agents").mkdir(parents=True)
        (self.proj / ".claude" / "settings.local.json").write_text("{}", encoding="utf-8")
        (self.proj / ".claude" / "agents" / "x.md").write_text("mine", encoding="utf-8")
        args = ["--project-root", str(self.proj), "--name", "Perm", "--git-init", "--permissions", "--yes", "--json"]
        result = run_script(args, self.tmp, GIT_IDENTITY)
        self.assertEqual(result.returncode, 0, result.stderr)
        files = subprocess.run(
            ["git", "ls-files"], cwd=self.proj, capture_output=True, text=True, encoding="utf-8"
        ).stdout.splitlines()
        self.assertIn(".claude/settings.json", files)
        self.assertIn("research_lab/lab.json", files)
        self.assertNotIn(".claude/settings.local.json", files)
        self.assertNotIn(".claude/agents/x.md", files)
        self.assertFalse([f for f in files if f.startswith("research_lab/.scratch/")], files)


if __name__ == "__main__":
    unittest.main()
