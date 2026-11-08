"""init_lab.py column additions: Basis on the findings log and Input checksums on the register."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from test_init_fresh import FreshFolderCase, run_script

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "lab_0_1"

OLD_FINDINGS = """# Findings log

Free text above the table stays as it is.

| FND-id (finding) | Statement | Type | Evidence | Status | Recorded | Verified | Scope and caveats |
|---|---|---|---|---|---|---|---|
| FND-0001 | The measured value is 3 | measured | EVR-0001 | verified | 2026-01-03 | 2026-01-04 | a caveat |
| FND-0002 | A second statement | measured | EVR-0001 | tentative | 2026-01-03 |  | none |
"""
NEW_FINDINGS = """# Findings log

Free text above the table stays as it is.

| FND-id (finding) | Statement | Type | Basis | Evidence | Status | Recorded | Verified | Scope and caveats |
|---|---|---|---|---|---|---|---|---|
| FND-0001 | The measured value is 3 | measured | exploratory | EVR-0001 | verified | 2026-01-03 | 2026-01-04 | a caveat |
| FND-0002 | A second statement | measured | exploratory | EVR-0001 | tentative | 2026-01-03 |  | none |
"""
OLD_REGISTER = """# Experiment register

| EXP-id (experiment) | Preregistration | Hypothesis | Code and config | Seeds and partitions | Environment | Status | Outputs | Deviations | Findings |
|---|---|---|---|---|---|---|---|---|---|
| EXP-0001 | experiments/preregistrations/p1.md | HYP-0001 | run.py | seed 1 | env one | completed |  |  | FND-0001 |
"""
NEW_REGISTER = """# Experiment register

| EXP-id (experiment) | Preregistration | Hypothesis | Code and config | Seeds and partitions | Environment | Input checksums | Status | Outputs | Deviations | Findings |
|---|---|---|---|---|---|---|---|---|---|---|
| EXP-0001 | experiments/preregistrations/p1.md | HYP-0001 | run.py | seed 1 | env one |  | completed |  |  | FND-0001 |
"""
FINDINGS = "research_lab/findings/FINDINGS_LOG.md"
REGISTER = "research_lab/experiments/EXPERIMENT_REGISTER.md"
DECISIONS = "research_lab/decisions/DECISION_LOG.md"
REVIEWS = "research_lab/reviews/REVIEW_LOG.md"


def tree_bytes(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


class ColumnCase(FreshFolderCase):
    def setUp(self):
        super().setUp()
        self.assertEqual(self.init().returncode, 0)  # a lab with the new layout
        self.write(FINDINGS, OLD_FINDINGS)
        self.write(REGISTER, OLD_REGISTER)

    def write(self, rel, text):
        (self.proj / rel).write_bytes(text.encode("utf-8"))

    def read(self, rel):
        return (self.proj / rel).read_bytes().decode("utf-8")

    def report(self, yes=True):
        result = self.init(yes=yes)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)


class TestColumns(ColumnCase):
    def test_findings_log_gains_basis_and_old_rows_get_exploratory(self):
        report = self.report()
        self.assertEqual(self.read(FINDINGS), NEW_FINDINGS)
        self.assertIn(f"header {FINDINGS}: (none) -> Basis", report["migration"])
        self.assertIn(f"rewrite {FINDINGS}: Basis, 2 rows: (empty) -> exploratory", report["migration"])

    def test_register_gains_input_checksums(self):
        report = self.report()
        self.assertEqual(self.read(REGISTER), NEW_REGISTER)
        self.assertIn(f"header {REGISTER}: (none) -> Input checksums", report["migration"])
        self.assertEqual([l for l in report["migration"] if l.startswith("rewrite") and REGISTER in l], [])

    def test_column_additions_are_idempotent(self):
        self.assertTrue(self.report()["migration"])
        after_first = tree_bytes(self.proj)
        plan = self.report(yes=False)
        self.assertEqual([l for l in plan["migration"] if l.startswith(("header", "rewrite"))], [])
        second = self.report()
        self.assertEqual(second["migration"], [])
        self.assertEqual(tree_bytes(self.proj), after_first)

    def test_column_additions_listed_in_plan(self):
        before = tree_bytes(self.proj)
        lines = self.init(yes=False, as_json=False).stdout.splitlines()
        self.assertEqual(tree_bytes(self.proj), before, "a dry run writes nothing")
        self.assertIn(f"header {FINDINGS}: (none) -> Basis", lines)
        self.assertIn(f"rewrite {FINDINGS}: Basis, 2 rows: (empty) -> exploratory", lines)
        self.assertIn(f"header {REGISTER}: (none) -> Input checksums", lines)
        kinds = {l.split(" ", 1)[0] for l in lines if l.startswith(("rename ", "header ", "rewrite "))}
        self.assertEqual(kinds, {"header", "rewrite"})

    def test_column_additions_leave_other_records_alone(self):
        decisions = (
            "# Decision log\n\n"
            "| DEC-id (decision) | Date | Stage | Decision | Rationale | Evidence | Approver |\n"
            "|---|---|---|---|---|---|---|\n"
            "| DEC-0001 | 2026-01-03 | Question | go | because | FND-0001 | the researcher |\n"
        )
        reviews = (
            "# Review log\n\n"
            "| REV-id (review) | Stage | Artifact | Reviewer | Outcome | Date | Report |\n"
            "|---|---|---|---|---|---|---|\n"
            "| REV-0001 | Literature | notes | reviewer | approved | 2026-01-03 | reports/REV-0001.md |\n"
        )
        self.write(DECISIONS, decisions)
        self.write(REVIEWS, reviews)
        others = ("research_lab/findings/KEY_RESULTS.md", "research_lab/literature/SOURCES.csv")
        before = {rel: (self.proj / rel).read_bytes() for rel in others}
        self.report()
        self.assertEqual(self.read(DECISIONS), decisions)
        self.assertEqual(self.read(REVIEWS), reviews)
        for rel, raw in before.items():
            self.assertEqual((self.proj / rel).read_bytes(), raw, rel)

    def test_column_addition_skips_a_table_without_its_anchor_column(self):
        odd = OLD_FINDINGS.replace(" Type |", "").replace("| measured ", "")
        self.assertNotIn("Type", odd)
        self.write(FINDINGS, odd)
        report = self.report()
        self.assertEqual(self.read(FINDINGS), odd)
        self.assertEqual([l for l in report["migration"] if FINDINGS in l], [])
        warns = [w for w in report["warn"] if "FINDINGS_LOG.md" in w]
        self.assertEqual(len(warns), 1, report["warn"])
        self.assertIn("Type", warns[0])
        self.assertIn("Basis", warns[0])
        self.assertEqual(self.read(REGISTER), NEW_REGISTER, "the other table is still done")


class TestColumnsOfAZeroOneLab(unittest.TestCase):
    def test_column_additions_follow_the_renames_of_a_0_1_lab(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            shutil.copytree(FIXTURE, proj)
            result = run_script(["--project-root", str(proj), "--name", "Fixture study", "--yes", "--json"], Path(tmp))
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            findings = (proj / FINDINGS).read_text(encoding="utf-8")
            head = [l for l in findings.splitlines() if l.startswith("| FND-id")][0]
            self.assertEqual(
                head,
                "| FND-id (finding) | Statement | Type | Basis | Evidence | Status | Recorded | Verified | Scope and caveats |",
            )
            rows = [l for l in findings.splitlines() if l.startswith("| F-")]  # legacy
            self.assertEqual(len(rows), 2)
            for row in rows:
                self.assertEqual(row.split("|")[4].strip(), "exploratory", row)
            register = (proj / REGISTER).read_text(encoding="utf-8")
            self.assertIn("| Environment | Input checksums | Status |", register)
            row = [l for l in register.splitlines() if l.startswith("| EXP-001")][0]
            self.assertEqual([c.strip() for c in row.split("|")][6:8], ["env one", ""])
            self.assertFalse((proj / "research_lab" / "02_findings_ledger").exists())  # legacy
            self.assertIn(f"header {FINDINGS}: (none) -> Basis", report["migration"])
            self.assertIn(f"header {REGISTER}: (none) -> Input checksums", report["migration"])


if __name__ == "__main__":
    unittest.main()
