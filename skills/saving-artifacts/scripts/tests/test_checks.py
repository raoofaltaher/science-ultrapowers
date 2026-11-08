import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts
from _helpers import make_git_lab, make_lab, run_cli, write_file

CHECK_FIELDS = [
    "id", "version_id", "claim", "verdict", "severity", "evidence", "rebuttal",
    "reviewer_role", "status", "resolution", "created_at", "source_ref",
]
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
REVIEWER = "scientific-reviewer"


class ChecksTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self._tmp.cleanup)
        self.t = Path(self._tmp.name)

    def _store(self, git: bool = False):
        lab = make_git_lab(self.t) if git else make_lab(self.t)
        s = artifacts.LabStore(lab)
        return s, s.project_root

    def _save1(self, s, path, **kw):
        kw.setdefault("role", "paper-author")
        kw.setdefault("task", "TASK-0001")
        return s.save([path], **kw)[0]

    def _saved(self, git: bool = False):
        s, proj = self._store(git)
        r = self._save1(s, write_file(proj / "f1.txt", "one"))
        return s, proj, r

    def _add(self, s, ref, **kw):
        kw.setdefault("claim", "F1 matches the ledger")
        kw.setdefault("verdict", "warn")
        kw.setdefault("reviewer_role", REVIEWER)
        return s.finding_add(ref, **kw)

    def test_finding_add_defaults_to_open(self) -> None:
        s, _, r = self._saved()
        row = s.finding_add(
            "art_" + r["artifact_id"],
            claim="F1 matches the ledger",
            verdict="warn",
            reviewer_role=REVIEWER,
        )
        self.assertEqual(row["version_id"], r["version_id"])
        self.assertEqual(row["status"], "open")
        self.assertIsNone(row["resolution"])
        self.assertEqual(list(row), CHECK_FIELDS)
        self.assertEqual(len(s.rows("verification_checks")), 1)

    def test_finding_add_rejects_bad_verdict(self) -> None:
        s, _, r = self._saved()
        with self.assertRaises(artifacts.StoreError) as cm:
            self._add(s, r["version_id"], verdict="great")
        self.assertIn("invalid verdict", str(cm.exception))
        self.assertFalse((s.root / "verification_checks.jsonl").exists())

    def test_finding_add_requires_claim_and_reviewer(self) -> None:
        s, _, r = self._saved()
        with self.assertRaises(artifacts.StoreError):
            self._add(s, r["version_id"], claim="  ")
        with self.assertRaises(artifacts.StoreError):
            self._add(s, r["version_id"], reviewer_role="")
        self.assertEqual(s.rows("verification_checks"), [])

    def test_respond_moves_to_claimed_with_note(self) -> None:
        s, _, r = self._saved()
        c = self._add(s, r["version_id"])
        row = s.respond(c["id"], "re-ran the ledger join")
        self.assertEqual(row["status"], "author-responded")
        self.assertEqual(row["resolution"]["note"], "re-ran the ledger join")
        self.assertRegex(row["resolution"]["at"], ISO_RE)
        self.assertEqual(s.rows("verification_checks")[0]["status"], "author-responded")

    def test_respond_needs_open_or_reopened(self) -> None:
        s, _, r = self._saved()
        c = self._add(s, r["version_id"])
        with self.assertRaises(artifacts.StoreError) as cm:
            s.respond(c["id"], "   ")
        self.assertIn("needs a note", str(cm.exception))
        s.finding_review(c["id"], status="closed", reviewer_role=REVIEWER)
        with self.assertRaises(artifacts.StoreError) as cm:
            s.respond(c["id"], "fixed")
        self.assertIn("only open or re-opened", str(cm.exception))

    def test_finding_review_resolves_and_reflags(self) -> None:
        s, _, r = self._saved()
        c = self._add(s, r["version_id"])
        s.respond(c["id"], "fixed it")
        row = s.finding_review(c["id"], status="re-opened", reviewer_role=REVIEWER, note="still wrong")
        self.assertEqual(row["status"], "re-opened")
        self.assertEqual(row["resolution"]["review"]["by"], REVIEWER)
        self.assertEqual(row["resolution"]["review"]["note"], "still wrong")
        self.assertEqual(row["resolution"]["review"]["status"], "re-opened")
        self.assertRegex(row["resolution"]["review"]["at"], ISO_RE)
        self.assertEqual(row["resolution"]["note"], "fixed it")
        self.assertEqual(s.respond(c["id"], "fixed again")["status"], "author-responded")
        self.assertEqual(
            s.finding_review(c["id"], status="closed", reviewer_role=REVIEWER)["status"], "closed"
        )
        with self.assertRaises(artifacts.StoreError) as cm:
            s.finding_review(c["id"], status="closed", reviewer_role=REVIEWER)
        self.assertIn("already closed", str(cm.exception))
        c2 = self._add(s, r["version_id"])
        with self.assertRaises(artifacts.StoreError):
            s.finding_review(c2["id"], status="open", reviewer_role=REVIEWER)
        with self.assertRaises(artifacts.StoreError):
            s.finding_review(c2["id"], status="closed", reviewer_role="")

    def test_outstanding_filters_like_claude_science(self) -> None:
        s, _, r = self._saved()
        vid = r["version_id"]
        c1 = self._add(s, vid, claim="c1", verdict="warn")
        c2 = self._add(s, vid, claim="c2", verdict="fail")
        s.respond(c2["id"], "tried")
        s.finding_review(c2["id"], status="re-opened", reviewer_role=REVIEWER)
        self._add(s, vid, claim="c3", verdict="pass")
        c4 = self._add(s, vid, claim="c4", verdict="fail")
        s.finding_review(c4["id"], status="closed", reviewer_role=REVIEWER)
        self.assertEqual([c["id"] for c in s.outstanding()], [c1["id"], c2["id"]])
        self.assertEqual(len(s.findings()), 4)

    def test_outstanding_for_artifact_ref_covers_all_versions(self) -> None:
        s, proj, r1 = self._saved()
        r2 = self._save1(s, write_file(proj / "f1.txt", "two"), version_of=r1["artifact_id"])
        a = self._add(s, r1["version_id"], claim="old", verdict="fail")
        b = self._add(s, r2["version_id"], claim="new", verdict="warn")
        want = [a["id"], b["id"]]
        self.assertEqual([c["id"] for c in s.outstanding(r1["artifact_id"])], want)
        self.assertEqual([c["id"] for c in s.outstanding("art_" + r1["artifact_id"])], want)
        self.assertEqual([c["id"] for c in s.outstanding(r2["version_id"])], [b["id"]])
        self.assertEqual([c["id"] for c in s.findings(r1["version_id"])], [a["id"]])

    def _string_resolution_check(self, s, r):
        row = dict.fromkeys(CHECK_FIELDS)
        row.update(
            id="abcdef0099", version_id=r["version_id"], claim="x", verdict="fail",
            reviewer_role=REVIEWER, status="unaddressed", resolution="fixed upstream",
            created_at=artifacts.now_iso(),
        )
        s.append("verification_checks", row)
        return row["id"]

    def test_finding_review_keeps_a_string_resolution_as_the_note(self) -> None:
        s, _, r = self._saved()
        cid = self._string_resolution_check(s, r)
        out = s.finding_review(cid, status="closed", reviewer_role=REVIEWER, note="confirmed")
        self.assertEqual(out["resolution"]["note"], "fixed upstream")
        self.assertEqual(out["resolution"]["review"]["note"], "confirmed")
        self.assertEqual(out["status"], "closed")

    def test_respond_keeps_a_string_resolution(self) -> None:
        s, _, r = self._saved()
        cid = self._string_resolution_check(s, r)
        out = s.respond(cid, "rewrote section 2")
        self.assertEqual(out["resolution"]["note"], "rewrote section 2")
        self.assertEqual(out["resolution"]["earlier_note"], "fixed upstream")
        self.assertEqual(out["status"], "author-responded")

    def test_check_id_prefixes(self) -> None:
        s, _, r = self._saved()
        c = self._add(s, r["version_id"])
        self.assertEqual(s.respond(c["id"][:8], "fixed")["id"], c["id"])
        with self.assertRaises(artifacts.UnknownId) as cm:
            s.respond(c["id"][:3], "x")
        self.assertIn("6 characters", str(cm.exception))
        for suffix in ("11", "22"):
            row = dict.fromkeys(CHECK_FIELDS)
            row.update(
                id="abcdef00" + suffix, version_id=r["version_id"], claim="x", verdict="warn",
                reviewer_role=REVIEWER, status="open", created_at=artifacts.now_iso(),
            )
            s.append("verification_checks", row)
        with self.assertRaises(artifacts.AmbiguousId):
            s.respond("abcdef00", "x")
        with self.assertRaises(artifacts.UnknownId):
            s.respond("ffffff", "x")

    def test_provenance_includes_findings(self) -> None:
        s, proj, r1 = self._saved()
        r2 = self._save1(s, write_file(proj / "f2.txt", "other"))
        c = self._add(s, r1["version_id"])
        self._add(s, r2["version_id"], claim="elsewhere")
        got = s.provenance(r1["version_id"])["findings"]
        self.assertEqual([x["id"] for x in got], [c["id"]])

    def test_finding_add_is_staged(self) -> None:
        s, proj, r = self._saved(git=True)
        self._add(s, r["version_id"])
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], cwd=proj, capture_output=True, text=True, check=True
        ).stdout.split()
        self.assertIn("research_lab/artifacts/verification_checks.jsonl", out)

    def test_cli_findings_commands(self) -> None:
        s, _, r = self._saved()
        lab = str(s.lab)
        code, out, err = run_cli([
            "--lab", lab, "findings", "add", "--version", r["version_id"], "--claim", "F1 ok?",
            "--verdict", "fail", "--reviewer", REVIEWER, "--severity", "high",
            "--evidence", "ledger row 3", "--rebuttal", "none",
        ])
        self.assertEqual(code, 0, err)
        row = json.loads(out)
        self.assertEqual(row["status"], "open")
        self.assertEqual(row["severity"], "high")
        cid = row["id"]
        code, out, err = run_cli(["--lab", lab, "findings", "list"])
        self.assertEqual(code, 0, err)
        self.assertEqual(len(json.loads(out)), 1)
        code, out, err = run_cli(["--lab", lab, "respond", cid, "--note", "fixed"])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["status"], "author-responded")
        code, out, err = run_cli([
            "--lab", lab, "findings", "review", cid, "--status", "closed", "--reviewer", "r",
        ])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["status"], "closed")
        code, out, err = run_cli(["--lab", lab, "findings", "list"])
        self.assertEqual((code, json.loads(out)), (0, []))
        code, out, err = run_cli(["--lab", lab, "findings", "list", "--all"])
        self.assertEqual(code, 0, err)
        self.assertEqual(len(json.loads(out)), 1)
        code, out, err = run_cli(["--lab", lab, "findings", "list", r["artifact_id"], "--all"])
        self.assertEqual(len(json.loads(out)), 1)
        code, out, err = run_cli([
            "--lab", lab, "findings", "add", "--version", r["version_id"], "--claim", "c",
            "--verdict", "bad", "--reviewer", "r",
        ])
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
