"""Offline tests for jev_ask.py: every test runs the script as a subprocess in a temp
project, never reaches the network and never needs a real API key."""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = str(Path(__file__).resolve().parents[1] / "jev_ask.py")
KEY_MESSAGE = "error: TYPESAFE_API_KEY is not set; decide as a specialist"
REQUEST = {"state": "x", "questions": {"q": {"type": "choice", "instructions": "pick",
                                              "criteria": {"a": "first", "b": "second"}}}}


class JevAskOfflineTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(os.path.realpath(self._tmp.name))

    def make_project(self, blocked=None):
        """A temp project with research_lab/08_decision_log/ and, if given, a lab.json."""
        (self.root / "research_lab" / "08_decision_log").mkdir(parents=True)
        if blocked is not None:
            (self.root / "research_lab" / "lab.json").write_text(
                json.dumps({"jev": {"blockedPaths": blocked}}), encoding="utf-8")
        return self.root

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def run_script(self, args, cwd=None, key=None):
        env = dict(os.environ)
        env.pop("TYPESAFE_API_KEY", None)
        if key is not None:
            env["TYPESAFE_API_KEY"] = key
        return subprocess.run([sys.executable, SCRIPT] + [str(a) for a in args],
                              cwd=str(cwd or self.root), env=env, capture_output=True,
                              text=True, encoding="utf-8", timeout=60)

    def test_missing_key_exits_2_and_logs_nothing(self):
        self.make_project()
        req = self.write("req.json", json.dumps(REQUEST))
        r = self.run_script(["--request", req, "--role", "x", "--purpose", "y"])
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(KEY_MESSAGE, r.stderr)
        self.assertFalse((self.root / "research_lab" / "08_decision_log" / "JEV_CALLS.jsonl").exists())

    def test_policy_check_redacts_personal_data(self):
        f = self.write("note.txt", "contact jane.doe@example.org or +90 532 123 45 67 / 905321234567")
        r = self.run_script(["--policy-check", f])
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertIs(out["blocked"], False)
        self.assertNotIn("@", out["redacted"])
        self.assertIsNone(re.search(r"\d{9,}", out["redacted"]))

    def test_policy_check_blocks_a_blocked_folder_mention(self):
        self.make_project(blocked=["grant_application/"])
        f = self.write("note.txt", "see grant_application/budget.xlsx for the numbers")
        r = self.run_script(["--policy-check", f])
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertIs(out["blocked"], True)
        self.assertTrue(any("grant_application" in x for x in out["reasons"]), out["reasons"])

    def test_policy_check_blocks_a_file_inside_a_blocked_folder(self):
        self.make_project(blocked=["grant_application/"])
        f = self.write("grant_application/notes.txt", "harmless text")
        r = self.run_script(["--policy-check", f])
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertIs(out["blocked"], True)
        self.assertTrue(any("grant_application" in x for x in out["reasons"]), out["reasons"])

    def test_lab_is_found_from_a_nested_working_directory(self):
        self.make_project(blocked=["grant_application/"])
        deep = self.root / "src" / "deep"
        deep.mkdir(parents=True)
        f = self.write("note.txt", "see grant_application/budget.xlsx")
        r = self.run_script(["--policy-check", f], cwd=deep)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIs(json.loads(r.stdout)["blocked"], True)

    def test_no_lab_refuses_a_call(self):
        # a fresh temp dir with no research_lab/ at or above it
        req = self.write("req.json", json.dumps(REQUEST))
        r = self.run_script(["--request", req, "--role", "x", "--purpose", "y"], key="dummy")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("no research_lab/ at or above", r.stderr)

    def test_request_mentioning_a_blocked_folder_exits_2_without_a_traceback(self):
        # The policy check runs before any network call, so a dummy key never leaves the process.
        self.make_project(blocked=["data/private"])
        req = self.write("req.json", json.dumps({"state": "see data/private/notes.csv",
                                                  "questions": REQUEST["questions"]}))
        r = self.run_script(["--request", req, "--role", "x", "--purpose", "y"], key="dummy-not-a-key")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("error: Jev payload blocked by lab data policy: mentions blocked folder data/private",
                      r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertFalse((self.root / "research_lab" / "08_decision_log" / "JEV_CALLS.jsonl").exists())

    def test_unreadable_lab_json_blocks_the_policy_check(self):
        self.make_project()
        (self.root / "research_lab" / "lab.json").write_text("{not json", encoding="utf-8")
        f = self.write("note.txt", "see data/private/x.csv")
        r = self.run_script(["--policy-check", f])
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertIs(out["blocked"], True)
        self.assertTrue(any("lab.json is unreadable" in x for x in out["reasons"]), out["reasons"])

    def test_unreadable_lab_json_refuses_a_call_and_sends_nothing(self):
        self.make_project()
        (self.root / "research_lab" / "lab.json").write_text("{not json", encoding="utf-8")
        req = self.write("req.json", json.dumps(REQUEST))
        r = self.run_script(["--request", req, "--role", "x", "--purpose", "y"], key="dummy-not-a-key")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("lab.json is unreadable", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertFalse((self.root / "research_lab" / "08_decision_log" / "JEV_CALLS.jsonl").exists())

    def test_blocked_paths_that_are_not_a_list_block(self):
        self.make_project(blocked="data/private")
        f = self.write("note.txt", "nothing sensitive")
        out = json.loads(self.run_script(["--policy-check", f]).stdout)
        self.assertIs(out["blocked"], True)
        self.assertTrue(any("blockedPaths" in x for x in out["reasons"]), out["reasons"])

    def test_lab_json_without_a_jev_section_blocks_nothing(self):
        self.make_project()
        (self.root / "research_lab" / "lab.json").write_text(json.dumps({"name": "x"}), encoding="utf-8")
        f = self.write("note.txt", "see data/private/x.csv")
        out = json.loads(self.run_script(["--policy-check", f]).stdout)
        self.assertIs(out["blocked"], False)

    def test_policy_check_of_a_missing_file_is_a_clean_error(self):
        r = self.run_script(["--policy-check", self.root / "missing.txt"])
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("error: cannot read", r.stderr)
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
