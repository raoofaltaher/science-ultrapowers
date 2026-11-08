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
        kw.setdefault("command", "pytest")
        return s.save([path], **kw)[0]

    def _saved(self, git: bool = False):
        s, proj = self._store(git)
        r = self._save1(s, write_file(proj / "f1.txt", "one"))
        return s, proj, r

    def _add(self, s, ref, **kw):
        kw.setdefault("claim", "F1 matches the ledger")
        kw.setdefault("verdict", "warn")
        kw.setdefault("reviewer_role", REVIEWER)
        return s.check_add(ref, **kw)

    def test_check_add_defaults_to_open(self) -> None:
        s, _, r = self._saved()
        row = s.check_add(
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

    def test_check_add_rejects_bad_verdict(self) -> None:
        s, _, r = self._saved()
        with self.assertRaises(artifacts.StoreError) as cm:
            self._add(s, r["version_id"], verdict="great")
        self.assertIn("invalid verdict", str(cm.exception))
        self.assertFalse((s.root / "verification_checks.jsonl").exists())

    def test_check_add_requires_claim_and_reviewer(self) -> None:
        s, _, r = self._saved()
        with self.assertRaises(artifacts.StoreError):
            self._add(s, r["version_id"], claim="  ")
        with self.assertRaises(artifacts.StoreError):
            self._add(s, r["version_id"], reviewer_role="")
        self.assertEqual(s.rows("verification_checks"), [])

    def test_mark_addressed_moves_to_claimed_with_note(self) -> None:
        s, _, r = self._saved()
        c = self._add(s, r["version_id"])
        row = s.mark_addressed(c["id"], "re-ran the ledger join")
        self.assertEqual(row["status"], "claimed")
        self.assertEqual(row["resolution"]["note"], "re-ran the ledger join")
        self.assertRegex(row["resolution"]["at"], ISO_RE)
        self.assertEqual(s.rows("verification_checks")[0]["status"], "claimed")

    def test_mark_addressed_needs_open_or_unaddressed(self) -> None:
        s, _, r = self._saved()
        c = self._add(s, r["version_id"])
        with self.assertRaises(artifacts.StoreError) as cm:
            s.mark_addressed(c["id"], "   ")
        self.assertIn("needs a note", str(cm.exception))
        s.check_review(c["id"], status="resolved", reviewer_role=REVIEWER)
        with self.assertRaises(artifacts.StoreError) as cm:
            s.mark_addressed(c["id"], "fixed")
        self.assertIn("only open or unaddressed", str(cm.exception))

    def test_check_review_resolves_and_reflags(self) -> None:
        s, _, r = self._saved()
        c = self._add(s, r["version_id"])
        s.mark_addressed(c["id"], "fixed it")
        row = s.check_review(c["id"], status="unaddressed", reviewer_role=REVIEWER, note="still wrong")
        self.assertEqual(row["status"], "unaddressed")
        self.assertEqual(row["resolution"]["review"]["by"], REVIEWER)
        self.assertEqual(row["resolution"]["review"]["note"], "still wrong")
        self.assertEqual(row["resolution"]["review"]["status"], "unaddressed")
        self.assertRegex(row["resolution"]["review"]["at"], ISO_RE)
        self.assertEqual(row["resolution"]["note"], "fixed it")
        self.assertEqual(s.mark_addressed(c["id"], "fixed again")["status"], "claimed")
        self.assertEqual(
            s.check_review(c["id"], status="resolved", reviewer_role=REVIEWER)["status"], "resolved"
        )
        with self.assertRaises(artifacts.StoreError) as cm:
            s.check_review(c["id"], status="resolved", reviewer_role=REVIEWER)
        self.assertIn("already resolved", str(cm.exception))
        c2 = self._add(s, r["version_id"])
        with self.assertRaises(artifacts.StoreError):
            s.check_review(c2["id"], status="open", reviewer_role=REVIEWER)
        with self.assertRaises(artifacts.StoreError):
            s.check_review(c2["id"], status="resolved", reviewer_role="")

    def test_outstanding_filters_like_claude_science(self) -> None:
        s, _, r = self._saved()
        vid = r["version_id"]
        c1 = self._add(s, vid, claim="c1", verdict="warn")
        c2 = self._add(s, vid, claim="c2", verdict="fail")
        s.mark_addressed(c2["id"], "tried")
        s.check_review(c2["id"], status="unaddressed", reviewer_role=REVIEWER)
        self._add(s, vid, claim="c3", verdict="pass")
        c4 = self._add(s, vid, claim="c4", verdict="fail")
        s.check_review(c4["id"], status="resolved", reviewer_role=REVIEWER)
        self.assertEqual([c["id"] for c in s.outstanding()], [c1["id"], c2["id"]])
        self.assertEqual(len(s.checks()), 4)

    def test_outstanding_for_artifact_ref_covers_all_versions(self) -> None:
        s, proj, r1 = self._saved()
        r2 = self._save1(s, write_file(proj / "f1.txt", "two"), version_of=r1["artifact_id"])
        a = self._add(s, r1["version_id"], claim="old", verdict="fail")
        b = self._add(s, r2["version_id"], claim="new", verdict="warn")
        want = [a["id"], b["id"]]
        self.assertEqual([c["id"] for c in s.outstanding(r1["artifact_id"])], want)
        self.assertEqual([c["id"] for c in s.outstanding("art_" + r1["artifact_id"])], want)
        self.assertEqual([c["id"] for c in s.outstanding(r2["version_id"])], [b["id"]])
        self.assertEqual([c["id"] for c in s.checks(r1["version_id"])], [a["id"]])

    def _string_resolution_check(self, s, r):
        row = dict.fromkeys(CHECK_FIELDS)
        row.update(
            id="abcdef0099", version_id=r["version_id"], claim="x", verdict="fail",
            reviewer_role=REVIEWER, status="unaddressed", resolution="fixed upstream",
            created_at=artifacts.now_iso(),
        )
        s.append("verification_checks", row)
        return row["id"]

    def test_check_review_keeps_a_string_resolution_as_the_note(self) -> None:
        s, _, r = self._saved()
        cid = self._string_resolution_check(s, r)
        out = s.check_review(cid, status="resolved", reviewer_role=REVIEWER, note="confirmed")
        self.assertEqual(out["resolution"]["note"], "fixed upstream")
        self.assertEqual(out["resolution"]["review"]["note"], "confirmed")
        self.assertEqual(out["status"], "resolved")

    def test_mark_addressed_keeps_a_string_resolution(self) -> None:
        s, _, r = self._saved()
        cid = self._string_resolution_check(s, r)
        out = s.mark_addressed(cid, "rewrote section 2")
        self.assertEqual(out["resolution"]["note"], "rewrote section 2")
        self.assertEqual(out["resolution"]["earlier_note"], "fixed upstream")
        self.assertEqual(out["status"], "claimed")

    def test_check_id_prefixes(self) -> None:
        s, _, r = self._saved()
        c = self._add(s, r["version_id"])
        self.assertEqual(s.mark_addressed(c["id"][:8], "fixed")["id"], c["id"])
        with self.assertRaises(artifacts.UnknownId) as cm:
            s.mark_addressed(c["id"][:3], "x")
        self.assertIn("6 characters", str(cm.exception))
        for suffix in ("11", "22"):
            row = dict.fromkeys(CHECK_FIELDS)
            row.update(
                id="abcdef00" + suffix, version_id=r["version_id"], claim="x", verdict="warn",
                reviewer_role=REVIEWER, status="open", created_at=artifacts.now_iso(),
            )
            s.append("verification_checks", row)
        with self.assertRaises(artifacts.AmbiguousId):
            s.mark_addressed("abcdef00", "x")
        with self.assertRaises(artifacts.UnknownId):
            s.mark_addressed("ffffff", "x")

    def test_lineage_includes_checks(self) -> None:
        s, proj, r1 = self._saved()
        r2 = self._save1(s, write_file(proj / "f2.txt", "other"))
        c = self._add(s, r1["version_id"])
        self._add(s, r2["version_id"], claim="elsewhere")
        got = s.lineage(r1["version_id"])["checks"]
        self.assertEqual([x["id"] for x in got], [c["id"]])

    def test_check_add_is_staged(self) -> None:
        s, proj, r = self._saved(git=True)
        self._add(s, r["version_id"])
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], cwd=proj, capture_output=True, text=True, check=True
        ).stdout.split()
        self.assertIn("research_lab/artifacts/verification_checks.jsonl", out)

    def test_cli_check_commands(self) -> None:
        s, _, r = self._saved()
        lab = str(s.lab)
        code, out, err = run_cli([
            "--lab", lab, "check", "add", "--version", r["version_id"], "--claim", "F1 ok?",
            "--verdict", "fail", "--reviewer", REVIEWER, "--severity", "high",
            "--evidence", "ledger row 3", "--rebuttal", "none",
        ])
        self.assertEqual(code, 0, err)
        row = json.loads(out)
        self.assertEqual(row["status"], "open")
        self.assertEqual(row["severity"], "high")
        cid = row["id"]
        code, out, err = run_cli(["--lab", lab, "check", "list"])
        self.assertEqual(code, 0, err)
        self.assertEqual(len(json.loads(out)), 1)
        code, out, err = run_cli(["--lab", lab, "mark-addressed", cid, "--note", "fixed"])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["status"], "claimed")
        code, out, err = run_cli([
            "--lab", lab, "check", "review", cid, "--status", "resolved", "--reviewer", "r",
        ])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["status"], "resolved")
        code, out, err = run_cli(["--lab", lab, "check", "list"])
        self.assertEqual((code, json.loads(out)), (0, []))
        code, out, err = run_cli(["--lab", lab, "check", "list", "--all"])
        self.assertEqual(code, 0, err)
        self.assertEqual(len(json.loads(out)), 1)
        code, out, err = run_cli(["--lab", lab, "check", "list", r["artifact_id"], "--all"])
        self.assertEqual(len(json.loads(out)), 1)
        code, out, err = run_cli([
            "--lab", lab, "check", "add", "--version", r["version_id"], "--claim", "c",
            "--verdict", "bad", "--reviewer", "r",
        ])
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
