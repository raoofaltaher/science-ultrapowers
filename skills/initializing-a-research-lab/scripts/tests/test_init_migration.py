"""init_lab.py on a lab in the 0.1 layout: the shown plan, the renames, the header and token rewrites."""

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_init_fresh import GIT_IDENTITY, HAVE_GIT, run_script

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import init_lab  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "lab_0_1"
OLD_FOLDERS = [  # legacy
    "00_project_knowledge",  # legacy
    "01_reference_registry",  # legacy
    "02_findings_ledger",  # legacy
    "03_experiments",  # legacy
    "04_reviews",  # legacy
    "05_access_requests",  # legacy
    "06_decisions",  # legacy
    "07_project_management",  # legacy
    "08_decision_log",  # legacy
    "09_skill_vetting",  # legacy
]
NEW_ROLES = [
    "academic-paper-author",
    "academic-reviewer",
    "academic-supervisor",
    "citation-reference-auditor",
    "data-evaluation-researcher",
    "decision-systems-specialist",
    "documentation-writer",
    "findings-records-curator",
    "lab-experiments-lead",
    "literature-researcher",
    "methods-innovation-researcher",
    "research-engineer",
    "research-project-manager",
    "scientific-peer-reviewer",
]
EXPECTED_PLAN = [
    "rename research_lab/00_project_knowledge -> research_lab/project",  # legacy
    "rename research_lab/01_reference_registry -> research_lab/literature",  # legacy
    "rename research_lab/02_findings_ledger -> research_lab/findings",  # legacy
    "rename research_lab/03_experiments -> research_lab/experiments",  # legacy
    "rename research_lab/04_reviews -> research_lab/reviews",  # legacy
    "rename research_lab/05_access_requests -> research_lab/requests",  # legacy
    "rename research_lab/06_decisions -> research_lab/decisions",  # legacy
    "rename research_lab/07_project_management -> research_lab/planning",  # legacy
    "rename research_lab/08_decision_log -> research_lab/automation",  # legacy
    "rename research_lab/09_skill_vetting -> research_lab/tool_vetting",  # legacy
    "rename research_lab/artifacts/store -> research_lab/artifacts/archive",  # legacy
    "rename research_lab/.scratch -> research_lab/.working",  # legacy
    "rename research_lab/literature/REGISTRY.csv -> research_lab/literature/SOURCES.csv",  # legacy
    "rename research_lab/literature/evidence_cards -> research_lab/literature/evidence_records",  # legacy
    "rename research_lab/literature/audits -> research_lab/literature/search_logs",  # legacy
    "rename research_lab/findings/FINDINGS.md -> research_lab/findings/FINDINGS_LOG.md",  # legacy
    "rename research_lab/findings/CANONICAL_NUMBERS.md -> research_lab/findings/KEY_RESULTS.md",  # legacy
    "rename research_lab/experiments/protocols -> research_lab/experiments/preregistrations",  # legacy
    "rename research_lab/decisions/DECISIONS.md -> research_lab/decisions/DECISION_LOG.md",  # legacy
    "rename research_lab/planning/TASK_BOARD.md -> research_lab/planning/WORK_PLAN.md",  # legacy
    "rename research_lab/migration/WHERE_WE_LEFT_OFF.md -> research_lab/migration/HANDOVER_SUMMARY.md",  # legacy
    "rename research_lab/templates/H_CARD.md -> research_lab/templates/HYPOTHESIS_RECORD.md",  # legacy
    "rename research_lab/templates/EVIDENCE_CARD.md -> research_lab/templates/EVIDENCE_RECORD.md",  # legacy
    "rename research_lab/templates/SESSION_KICKOFF.md -> research_lab/templates/SESSION_OPENING.md",  # legacy
    "rename research_lab/decisions/lab_meetings/2026-01-05_kickoff.md -> research_lab/decisions/lab_meetings/2026-01-05_opening.md",  # legacy
    "header research_lab/findings/FINDINGS_LOG.md: F-id -> FND-id (finding)",  # legacy
    "header research_lab/findings/FINDINGS_LOG.md: Scope / caveats -> Scope and caveats",  # legacy
    "header research_lab/findings/FINDINGS_LOG.md: (none) -> Basis",
    "header research_lab/findings/KEY_RESULTS.md: F-id -> FND-id (finding)",  # legacy
    "header research_lab/literature/SOURCES.csv: ref_id -> source_id",  # legacy
    "header research_lab/literature/SOURCES.csv: lab_status -> status",  # legacy
    "header research_lab/literature/SOURCES.csv: tier -> source_class",  # legacy
    "header research_lab/literature/SOURCES.csv: verify_status -> doi_status",  # legacy
    "header research_lab/literature/SOURCES.csv: evidence_cards -> evidence_records",  # legacy
    "header research_lab/experiments/EXPERIMENT_REGISTER.md: Experiment id -> EXP-id (experiment)",  # legacy
    "header research_lab/experiments/EXPERIMENT_REGISTER.md: Protocol -> Preregistration",  # legacy
    "header research_lab/experiments/EXPERIMENT_REGISTER.md: Code / config -> Code and config",  # legacy
    "header research_lab/experiments/EXPERIMENT_REGISTER.md: Seeds / splits (where applicable) -> Seeds and partitions",  # legacy
    "header research_lab/experiments/EXPERIMENT_REGISTER.md: (none) -> Input checksums",
    "header research_lab/reviews/REVIEW_LOG.md: RV-id -> REV-id (review)",  # legacy
    "header research_lab/reviews/REVIEW_LOG.md: Artifact (path / version) -> Artifact",  # legacy
    "header research_lab/reviews/REVIEW_LOG.md: Gate -> Stage",  # legacy
    "header research_lab/reviews/REVIEW_LOG.md: Reviewer role -> Reviewer",  # legacy
    "header research_lab/reviews/REVIEW_LOG.md: Verdict -> Outcome",  # legacy
    "header research_lab/requests/ACCESS_REQUESTS.md: REQ-id -> REQ-id (request)",
    "header research_lab/requests/ACCESS_REQUESTS.md: DOI / identifier -> DOI or identifier",
    "header research_lab/requests/ACCESS_REQUESTS.md: Requested by / date -> Requested by and date",
    "header research_lab/decisions/DECISION_LOG.md: D-id -> DEC-id (decision)",  # legacy
    "header research_lab/decisions/DECISION_LOG.md: Evidence ids -> Evidence",  # legacy
    "header research_lab/decisions/DECISION_LOG.md: (none) -> Date",
    "header research_lab/decisions/DECISION_LOG.md: (none) -> Stage",
    "header research_lab/planning/WORK_PLAN.md: Task -> TASK-id (task)",  # legacy
    "header research_lab/planning/WORK_PLAN.md: Gate -> Stage",  # legacy
    "header research_lab/planning/RISK_REGISTER.md: R-id -> RSK-id (risk)",  # legacy
    "rewrite research_lab/findings/FINDINGS_LOG.md: Basis, 2 rows: (empty) -> exploratory",
    "rewrite research_lab/literature/SOURCES.csv: status, 1 rows: ADMITTED -> citable",  # legacy
    "rewrite research_lab/literature/SOURCES.csv: status, 1 rows: PENDING_FULLTEXT -> awaiting full text",  # legacy
    "rewrite research_lab/literature/SOURCES.csv: source_class, 1 rows: A -> peer-reviewed matched doi",  # legacy
    "rewrite research_lab/literature/SOURCES.csv: source_class, 1 rows: C -> not peer-reviewed",  # legacy
    "rewrite research_lab/literature/SOURCES.csv: doi_status, 1 rows: VERIFIED -> matched",  # legacy
    "rewrite research_lab/literature/SOURCES.csv: doi_status, 1 rows: NO_DOI -> no doi",  # legacy
    "rewrite research_lab/reviews/REVIEW_LOG.md: Stage, 1 rows: G1 -> Literature",  # legacy
    "rewrite research_lab/requests/ACCESS_REQUESTS.md: Type, 1 rows: FULLTEXT -> full-text request",  # legacy
    "rewrite research_lab/requests/ACCESS_REQUESTS.md: Priority, 1 rows: P1 -> blocks a stage",  # legacy
    "rewrite research_lab/requests/ACCESS_REQUESTS.md: Status, 1 rows: OPEN -> open",  # legacy
    "rewrite research_lab/planning/WORK_PLAN.md: Stage, 1 rows: G1 -> Literature",  # legacy
    "rewrite research_lab/memory/project/a-pitfall.md: evidence, 1 rows: evidence -> basis",  # legacy
    "rewrite research_lab/memory/project/a-pitfall.md: type, 1 rows: gotcha -> pitfall",  # legacy
    "rewrite research_lab/memory/project/another-pitfall.md: evidence, 1 rows: evidence -> basis",  # legacy
    "rewrite research_lab/memory/project/another-pitfall.md: type, 1 rows: gotcha -> pitfall",  # legacy
    "rewrite research_lab/lab.json: jev.blockedPaths, 1 rows: jev.blockedPaths -> scope.restrictedFolders",  # legacy
    "rewrite research_lab/lab.json: roles, 1 rows: citation-auditor -> citation-reference-auditor",  # legacy
    "rewrite research_lab/lab.json: roles, 1 rows: experiments-lead -> lab-experiments-lead",  # legacy
    "rewrite research_lab/lab.json: roles, 1 rows: findings-curator -> findings-records-curator",  # legacy
    "rewrite research_lab/lab.json: roles, 1 rows: lab-project-manager -> research-project-manager",  # legacy
    "rewrite research_lab/lab.json: roles, 1 rows: methods-researcher -> methods-innovation-researcher",  # legacy
    "rewrite research_lab/lab.json: roles, 1 rows: paper-author -> academic-paper-author",  # legacy
    "rewrite research_lab/lab.json: roles, 1 rows: scientific-reviewer -> scientific-peer-reviewer",  # legacy
    "rewrite research_lab/lab.json: idPrefixes, 1 rows: absent -> added",
    "rewrite research_lab/artifacts/.gitattributes: patterns, 2 lines: store/ -> archive/",  # legacy
    # The fixture's task board keeps the 0.1 text above its table, so init refreshes that text (test_init_refresh.py).
    "refresh research_lab/planning/WORK_PLAN.md: the 0.1 text above the table -> the current text",
]


def tree_bytes(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def git(args, cwd):
    env = dict(os.environ)
    env.update(GIT_IDENTITY)
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", env=env)


class MigrationCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.proj = self.tmp / "proj"
        shutil.copytree(FIXTURE, self.proj)
        self.lab = self.proj / "research_lab"

    def init(self, *extra, yes=True, as_json=True):
        args = ["--project-root", str(self.proj), "--name", "Fixture study", *extra]
        if yes:
            args.append("--yes")
        if as_json:
            args.append("--json")
        return run_script(args, self.tmp, GIT_IDENTITY)

    def report(self, *extra, yes=True):
        result = self.init(*extra, yes=yes)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def read(self, rel: str) -> str:
        return (self.lab / rel).read_bytes().decode("utf-8")

    def original(self, rel: str) -> str:
        return (FIXTURE / "research_lab" / rel).read_bytes().decode("utf-8")

    def test_old_layout_is_detected_and_planned(self):
        self.assertEqual(init_lab.detect_old_layout(self.proj), OLD_FOLDERS)
        before = tree_bytes(self.proj)
        report = self.report(yes=False)
        self.assertEqual(report["migration"], EXPECTED_PLAN)
        self.assertEqual(tree_bytes(self.proj), before, "a dry run writes nothing")
        text = self.init(yes=False, as_json=False).stdout
        shown = text.splitlines()
        for line in EXPECTED_PLAN:
            self.assertIn(line, shown)
        self.assertNotIn("create research_lab/findings/FINDINGS_LOG.md", shown)
        self.assertIn("create research_lab/literature/citation_audits/.gitkeep", shown)

    @unittest.skipUnless(HAVE_GIT, "git is not installed")
    def test_migration_applies_with_git_mv_when_tracked(self):
        self.assertEqual(git(["init", "-b", "main"], self.proj).returncode, 0)
        self.assertEqual(git(["add", "-A"], self.proj).returncode, 0)
        self.assertEqual(git(["commit", "-m", "fixture"], self.proj).returncode, 0)
        self.report()
        status = git(["status", "--porcelain"], self.proj).stdout.splitlines()
        moved = [l for l in status if "research_lab/findings/FINDINGS_LOG.md" in l]
        self.assertEqual(len(moved), 1, status)
        self.assertTrue(moved[0].startswith("R"), moved[0])
        self.assertIn("research_lab/02_findings_ledger/FINDINGS.md", moved[0])  # legacy
        self.assertFalse([l for l in status if l.startswith(" D") or l.startswith("D ")], status)

    def test_migration_rewrites_headers_and_tokens_only(self):
        self.report()
        self.assertEqual(
            self.read("findings/FINDINGS_LOG.md"),
            self.original("02_findings_ledger/FINDINGS.md")  # legacy
            .replace("| F-id |", "| FND-id (finding) |")  # legacy
            .replace("| Scope / caveats |", "| Scope and caveats |")  # legacy
            .replace("| Type | Evidence |", "| Type | Basis | Evidence |")
            .replace("|---|---|---|---|---|---|---|---|\n", "|---|---|---|---|---|---|---|---|---|\n")
            .replace("| measured | EC-0001 |", "| measured | exploratory | EC-0001 |"),  # legacy
        )
        self.assertEqual(
            self.read("findings/KEY_RESULTS.md"),
            self.original("02_findings_ledger/CANONICAL_NUMBERS.md").replace("| F-id |", "| FND-id (finding) |"),  # legacy
        )
        old_head = "ref_id,lab_status,tier,doi,other_id,first_author,year,title,venue,local_file,verify_status,verified_on,retraction_status,evidence_cards,notes"  # legacy
        new_head = "source_id,status,source_class,doi,other_id,first_author,year,title,venue,local_file,doi_status,verified_on,retraction_status,evidence_records,notes"
        self.assertEqual(
            self.read("literature/SOURCES.csv"),
            self.original("01_reference_registry/REGISTRY.csv")  # legacy
            .replace(old_head, new_head)
            .replace(",ADMITTED,", ",citable,")
            .replace(",PENDING_FULLTEXT,", ",awaiting full text,")
            .replace(",citable,A,", ",citable,peer-reviewed matched doi,")
            .replace(",awaiting full text,C,", ",awaiting full text,not peer-reviewed,")
            .replace(",VERIFIED,", ",matched,")
            .replace(",NO_DOI,", ",no doi,"),
        )
        self.assertIn('"Doe, J.",2020,"A title, with a comma"', self.read("literature/SOURCES.csv"))
        self.assertEqual(
            self.read("reviews/REVIEW_LOG.md"),
            self.original("04_reviews/REVIEW_LOG.md")  # legacy
            .replace("| RV-id |", "| REV-id (review) |")  # legacy
            .replace("| Artifact (path / version) |", "| Artifact |")
            .replace("| Gate |", "| Stage |")  # legacy
            .replace("| Reviewer role |", "| Reviewer |")
            .replace("| Verdict |", "| Outcome |")
            .replace("| G1 |", "| Literature |"),  # legacy
        )
        self.assertEqual(
            self.read("requests/ACCESS_REQUESTS.md"),
            self.original("05_access_requests/ACCESS_REQUESTS.md")  # legacy
            .replace("| REQ-id |", "| REQ-id (request) |")
            .replace("| DOI / identifier |", "| DOI or identifier |")
            .replace("| Requested by / date |", "| Requested by and date |")
            .replace("| FULLTEXT |", "| full-text request |")  # legacy
            .replace("| P1 |", "| blocks a stage |")  # legacy
            .replace("| OPEN |", "| open |"),
        )
        self.assertEqual(
            self.read("decisions/DECISION_LOG.md"),
            self.original("06_decisions/DECISIONS.md")  # legacy
            .replace("| D-id |", "| DEC-id (decision) | Date | Stage |")  # legacy
            .replace("| Evidence ids |", "| Evidence |")  # legacy
            .replace("|---|---|---|---|---|---|---|\n", "|---|---|---|---|---|---|---|---|---|\n")
            .replace("| D-01 |", "| D-01 |  |  |"),  # legacy
        )
        self.assertIn("| D-01 |", self.read("decisions/DECISION_LOG.md"))  # legacy
        self.assertIn("| F-0001 |", self.read("findings/FINDINGS_LOG.md"))  # legacy
        self.assertIn("superseded by F-0003", self.read("findings/FINDINGS_LOG.md"))  # legacy
        self.assertEqual(
            self.read("planning/WORK_PLAN.md"),
            self.original("07_project_management/TASK_BOARD.md")  # legacy
            .replace("# Task board\n", "# Work plan\n", 1)  # legacy
            .replace("| Task |", "| TASK-id (task) |")  # legacy
            .replace("| Gate |", "| Stage |")  # legacy
            .replace("| G1 |", "| Literature |"),  # legacy
        )
        self.assertEqual(
            self.read("planning/RISK_REGISTER.md"),
            self.original("07_project_management/RISK_REGISTER.md").replace("| R-id |", "| RSK-id (risk) |"),  # legacy
        )
        self.assertEqual(
            self.read("experiments/EXPERIMENT_REGISTER.md"),
            self.original("03_experiments/EXPERIMENT_REGISTER.md")  # legacy
            .replace("| Experiment id |", "| EXP-id (experiment) |")  # legacy
            .replace("| Protocol |", "| Preregistration |")  # legacy
            .replace("| Code / config |", "| Code and config |")  # legacy
            .replace("| Seeds / splits (where applicable) |", "| Seeds and partitions |")  # legacy
            .replace("| Environment | Status |", "| Environment | Input checksums | Status |")
            .replace("|---|---|---|---|---|---|---|---|---|---|\n", "|---|---|---|---|---|---|---|---|---|---|---|\n")
            .replace("| env one | planned |", "| env one |  | planned |"),
        )
        for name in ("a-pitfall", "another-pitfall"):
            entry = self.read(f"memory/project/{name}.md")
            self.assertIn("  basis: ", entry)
            self.assertIn("  type: pitfall\n", entry)
            self.assertNotIn("  evidence:", entry)  # legacy
            self.assertNotIn("gotcha", entry)  # legacy
            self.assertIn("\nevidence: this line is body text, not a key\n", entry)  # legacy
        self.assertEqual(
            self.read("memory/project/a-pitfall.md"),
            self.original("memory/project/a-pitfall.md")
            .replace("  type: gotcha\n", "  type: pitfall\n")  # legacy
            .replace("  evidence: observed\n", "  basis: observed\n"),  # legacy
        )
        for rel in (
            "literature/evidence_records/EC-0001.md",  # legacy
            "decisions/lab_meetings/2026-01-05_opening.md",
            "migration/HANDOVER_SUMMARY.md",
            "templates/SESSION_OPENING.md",
            "templates/HYPOTHESIS_RECORD.md",
            "templates/EVIDENCE_RECORD.md",
        ):
            self.assertTrue((self.lab / rel).is_file(), rel)
        self.assertEqual(self.read("artifacts/archive/artifacts.jsonl"), self.original("artifacts/store/artifacts.jsonl"))  # legacy
        self.assertTrue((self.lab / ".working" / ".gitkeep").is_file())
        self.assertEqual(init_lab.detect_old_layout(self.proj), [])
        self.assertFalse((self.lab / "02_findings_ledger").exists())  # legacy

    def test_migrated_decision_log_and_request_queue_carry_the_template_headers(self):
        def header(text: str) -> str:
            return next(line for line in text.splitlines() if line.startswith("|"))

        self.report()
        templates = init_lab.TEMPLATE_ROOT / "research_lab"
        for rel in ("decisions/DECISION_LOG.md", "requests/ACCESS_REQUESTS.md"):
            template = (templates / rel).read_text(encoding="utf-8")
            self.assertEqual(header(self.read(rel)), header(template), rel)
        # The old rows keep their cells; the added Date and Stage cells are empty.
        self.assertIn("| D-01 |  |  | context text |", self.read("decisions/DECISION_LOG.md"))  # legacy

    def run_in_process(self, *extra):
        """init_lab.main in this process (so a rename can be patched): (exit code, the parsed JSON report)."""
        argv = ["--project-root", str(self.proj), "--name", "Fixture study", "--yes", "--json", *extra]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = init_lab.main(argv)
        return code, json.loads(out.getvalue())

    def test_a_failed_rename_is_a_warning_and_a_second_run_finishes_the_migration(self):
        real_rename = os.rename

        def locked(src, dst, *args, **kwargs):
            if Path(src).name == "03_experiments":  # legacy
                raise PermissionError(13, "The process cannot access the file because it is being used")
            return real_rename(src, dst, *args, **kwargs)

        with mock.patch.object(os, "rename", locked):
            code, report = self.run_in_process()
        self.assertEqual(code, 0)
        warnings = [w for w in report["warn"] if w.startswith("rename failed for research_lab/03_experiments: ")]  # legacy
        self.assertEqual(len(warnings), 1, report["warn"])
        self.assertTrue(warnings[0].endswith("; close the file and run init again"), warnings[0])
        self.assertTrue((self.lab / "03_experiments").is_dir())  # legacy
        self.assertFalse((self.lab / "experiments").exists(), "nothing is created inside a folder whose rename failed")
        for old, new in (("01_reference_registry", "literature"), ("04_reviews", "reviews"), ("06_decisions", "decisions")):  # legacy
            self.assertTrue((self.lab / new).is_dir(), new)
            self.assertFalse((self.lab / old).exists(), old)
        self.assertEqual(init_lab.detect_old_layout(self.proj), ["03_experiments"])  # legacy
        code, report = self.run_in_process()
        self.assertEqual(code, 0)
        self.assertEqual([w for w in report["warn"] if "rename failed" in w], [])
        self.assertEqual(init_lab.detect_old_layout(self.proj), [])
        self.assertTrue((self.lab / "experiments" / "EXPERIMENT_REGISTER.md").is_file())
        self.assertTrue((self.lab / "experiments" / "preregistrations").is_dir())
        self.assertIn("| EXP-id (experiment) |", self.read("experiments/EXPERIMENT_REGISTER.md"))

    def test_a_failed_table_rewrite_is_a_warning_and_the_other_items_are_written(self):
        real_write = init_lab._write_text

        def locked(path, text):
            if Path(path).name == "FINDINGS_LOG.md":
                raise PermissionError(13, "The process cannot access the file because it is being used")
            return real_write(path, text)

        with mock.patch.object(init_lab, "_write_text", locked):
            code, report = self.run_in_process()
        self.assertEqual(code, 0)
        warnings = [w for w in report["warn"] if w.startswith("rewrite failed for research_lab/findings/FINDINGS_LOG.md: ")]
        self.assertEqual(len(warnings), 1, report["warn"])
        self.assertTrue(warnings[0].endswith("; the file is unchanged: close it and edit it by hand"), warnings[0])
        done = [line for line in report["migration"] if line.startswith(("header", "rewrite")) and "FINDINGS_LOG.md" in line]
        self.assertEqual(done, [], "a failed rewrite is not reported as done")
        self.assertIn("| F-id |", self.read("findings/FINDINGS_LOG.md"))  # legacy
        self.assertNotIn("| FND-id (finding) |", self.read("findings/FINDINGS_LOG.md"))
        self.assertIn("| REQ-id (request) |", self.read("requests/ACCESS_REQUESTS.md"))

    def test_gitattributes_patterns_move_to_archive(self):
        self.report()
        lines = self.read("artifacts/.gitattributes").splitlines()
        self.assertIn("archive/** -text", lines)
        self.assertIn("archive/art-1/** -diff", lines)
        self.assertFalse([l for l in lines if l.startswith("store/")], lines)  # legacy
        self.assertIn("*.jsonl text eol=lf", lines)
        self.assertEqual(lines.count("archive/** -text"), 1)

    def test_migration_refuses_existing_target(self):
        (self.lab / "findings").mkdir()
        (self.lab / "findings" / "NOTES.md").write_text("hand made\n", encoding="utf-8")
        before = (self.lab / "02_findings_ledger" / "FINDINGS.md").read_bytes()  # legacy
        result = self.init(as_json=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("unexpected layout", result.stdout)
        self.assertIn("research_lab/02_findings_ledger", result.stdout)  # legacy
        self.assertEqual((self.lab / "02_findings_ledger" / "FINDINGS.md").read_bytes(), before)  # legacy
        self.assertFalse((self.lab / "findings" / "FINDINGS_LOG.md").read_bytes().startswith(b"| F-id"))  # legacy
        self.assertTrue((self.lab / "literature").is_dir())
        self.assertFalse((self.lab / "01_reference_registry").exists())  # legacy

    def test_migration_is_idempotent(self):
        first = self.report()
        self.assertTrue(first["migration"])
        after_first = tree_bytes(self.proj)
        second = self.report()
        self.assertEqual(second["migration"], [])
        self.assertEqual(init_lab.detect_old_layout(self.proj), [])
        self.assertEqual(tree_bytes(self.proj), after_first)
        self.assertEqual(self.report(yes=False)["migration"], [])

    def test_lab_json_keys_migrate(self):
        self.report()
        data = json.loads(self.read("lab.json"))
        self.assertEqual(data["scope"]["restrictedFolders"], ["data/private"])
        self.assertNotIn("jev", data)
        self.assertEqual(sorted(data["roles"]), NEW_ROLES)
        self.assertTrue(all(data["roles"].values()))
        template = json.loads((init_lab.TEMPLATE_ROOT / "lab.json").read_text(encoding="utf-8"))
        self.assertEqual(data["idPrefixes"], template["idPrefixes"])
        self.assertEqual(data["pluginVersion"], init_lab.plugin_version())

    def test_hand_copies_of_old_role_ids_are_reported(self):
        (self.proj / ".claude" / "agents").mkdir(parents=True)
        (self.proj / ".claude" / "agents" / "lab-project-manager.md").write_text("mine\n", encoding="utf-8")  # legacy
        report = self.report(yes=False)
        self.assertIn(".claude/agents/lab-project-manager.md", report["duplicates"])  # legacy


if __name__ == "__main__":
    unittest.main()
