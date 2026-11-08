"""Tests of preregister.py: each test runs the script on a fresh temporary git repository."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = str(Path(__file__).resolve().parents[1] / "preregister.py")
PROTOCOL = "research_lab/experiments/preregistrations/EXP-0001.md"
PROTOCOL_TEXT = "# EXP-0001 preregistration\n\n1. Hypothesis: the effect is positive.\n2. Design: two arms.\n"
OLD_LAYOUT_MESSAGE = (
    "this lab uses the 0.1 layout; run science-ultrapowers:initializing-a-research-lab to migrate it\n"
)


def git(repo, *args, check=True):
    """Run git in the repository and return stdout as text."""
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, encoding="utf-8", errors="replace"
    )
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {proc.stderr}")
    return proc.stdout


def write(repo, rel, text):
    path = Path(repo) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def commit_all(repo, message, *paths):
    git(repo, "add", "--", *paths)
    git(repo, "commit", "-q", "-m", message, "--", *paths)
    return git(repo, "rev-parse", "HEAD").strip()


def make_repo(tmp, name="repo"):
    """A git repository with one baseline commit: README.md and data/raw/fixture.csv."""
    repo = Path(tmp) / name
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "Test Researcher")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "commit.gpgsign", "false")
    git(repo, "config", "core.autocrlf", "false")
    write(repo, "README.md", "baseline\n")
    write(repo, "data/raw/fixture.csv", "a,b\n1,2\n")
    commit_all(repo, "baseline", "README.md", "data/raw/fixture.csv")
    return repo


def run(repo, *args, env=None):
    return subprocess.run(
        [sys.executable, SCRIPT, *args], cwd=str(repo), capture_output=True, encoding="utf-8",
        errors="replace", env=env,
    )


def register(repo, *args):
    proc = run(repo, "register", PROTOCOL, *args)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads(proc.stdout)


def check(repo, *args, protocol=PROTOCOL):
    proc = run(repo, "check", protocol, *args)
    return proc.returncode, json.loads(proc.stdout)


def register_by_hand(repo):
    """The registration commit without the time stamp, as a researcher could make it."""
    write(repo, PROTOCOL, PROTOCOL_TEXT)
    git(repo, "add", "--", PROTOCOL)
    git(
        repo, "commit", "-q", "-m", "TASK-0001 research-project-manager: register protocol EXP-0001",
        "-m", "Preregistration: EXP-0001", "--", PROTOCOL,
    )
    return git(repo, "rev-parse", "HEAD").strip()


class PreregisterTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = self._tmp.name
        self.repo = make_repo(self.tmp)

    def test_register_makes_two_commits_with_trailers(self):
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        result = register(self.repo, "--input", "data/raw/fixture.csv", "--task", "TASK-0001")
        timestamp_commit, registration_commit = git(self.repo, "log", "-2", "--format=%H").split()
        self.assertEqual(result["registration_commit"], registration_commit)
        self.assertEqual(result["timestamp_commit"], timestamp_commit)
        self.assertEqual(result["protocol"], PROTOCOL)
        self.assertEqual(result["protocol_id"], "EXP-0001")
        blob = git(self.repo, "hash-object", "data/raw/fixture.csv").strip()
        self.assertEqual(result["inputs"], [{"path": "data/raw/fixture.csv", "blob": blob}])
        registration_message = git(self.repo, "log", "-1", "--format=%B", registration_commit)
        self.assertIn("TASK-0001 research-project-manager: register protocol EXP-0001", registration_message)
        self.assertIn("Preregistration: EXP-0001", registration_message)
        timestamp_message = git(self.repo, "log", "-1", "--format=%B", timestamp_commit)
        self.assertIn("TASK-0001 research-project-manager: time-stamp protocol EXP-0001", timestamp_message)
        self.assertIn(f"Preregistration-Timestamp: {registration_commit}", timestamp_message)
        text = (self.repo / PROTOCOL).read_text(encoding="utf-8")
        self.assertIn(f"Registered at commit: {registration_commit}", text)
        self.assertIn("## Registered inputs", text)
        self.assertIn(f"- data/raw/fixture.csv {blob}", text)
        for commit in (registration_commit, timestamp_commit):
            changed = git(self.repo, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).split()
            self.assertEqual(changed, [PROTOCOL])

    def test_register_refuses_tracked_protocol(self):
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        commit_all(self.repo, "add protocol", PROTOCOL)
        before = git(self.repo, "log", "--format=%H")
        proc = run(self.repo, "register", PROTOCOL)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("error", json.loads(proc.stdout))
        self.assertEqual(git(self.repo, "log", "--format=%H"), before)

    def test_register_leaves_other_staged_changes_alone(self):
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        write(self.repo, "other.txt", "staged by the researcher\n")
        git(self.repo, "add", "--", "other.txt")
        register(self.repo)
        self.assertEqual(git(self.repo, "diff", "--cached", "--name-only").split(), ["other.txt"])
        for commit in git(self.repo, "log", "-2", "--format=%H").split():
            changed = git(self.repo, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).split()
            self.assertNotIn("other.txt", changed)

    def test_register_path_with_spaces(self):
        name = "research_lab/experiments/preregistrations/EXP 0002 ü.md"
        write(self.repo, name, "# EXP 0002 preregistration\n\nPlan.\n")
        proc = run(self.repo, "register", name)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        code, report = check(self.repo, protocol=name)
        self.assertEqual(code, 0, report)
        self.assertTrue(report["ok"])

    def test_register_timestamp_only_completes_an_untimestamped_registration(self):
        registration = register_by_hand(self.repo)
        proc = run(self.repo, "register", PROTOCOL, "--timestamp-only", "--task", "TASK-0001")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["registration_commit"], registration)
        head = git(self.repo, "rev-parse", "HEAD").strip()
        self.assertEqual(result["timestamp_commit"], head)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD~1").strip(), registration)
        message = git(self.repo, "log", "-1", "--format=%B")
        self.assertIn(f"Preregistration-Timestamp: {registration}", message)
        code, report = check(self.repo)
        self.assertEqual(code, 0, report)

    def test_check_is_clear_after_a_clean_registration(self):
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        register(self.repo, "--input", "data/raw/fixture.csv")
        write(self.repo, "results/EXP-0001/metrics.txt", "f1=0.8\n")
        commit_all(self.repo, "run EXP-0001", "results/EXP-0001/metrics.txt")
        code, report = check(self.repo, "--outputs", "results")
        self.assertEqual(code, 0, report)
        self.assertTrue(report["ok"])
        self.assertEqual(
            sorted(report["checks"]), ["chronology", "inputs", "registered", "timestamp", "unaltered"]
        )
        for name, item in report["checks"].items():
            self.assertEqual(item["status"], "clear", (name, item))

    def test_check_registered_is_not_clear_when_never_committed(self):
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        code, report = check(self.repo)
        self.assertEqual(code, 1)
        self.assertFalse(report["ok"])
        self.assertEqual(report["checks"]["registered"]["status"], "not clear")

    def test_check_timestamp_is_not_clear_when_hash_wrong(self):
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        register(self.repo)
        path = self.repo / PROTOCOL
        lines = path.read_text(encoding="utf-8").split("\n")
        lines = ["Registered at commit: " + "0" * 40 if x.startswith("Registered at commit:") else x for x in lines]
        path.write_bytes("\n".join(lines).encode("utf-8"))
        commit_all(self.repo, "edit the stamp", PROTOCOL)
        code, report = check(self.repo)
        self.assertEqual(code, 1)
        self.assertEqual(report["checks"]["timestamp"]["status"], "not clear")

    def test_check_unaltered_is_not_clear_when_edited_after_registration(self):
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        register(self.repo)
        path = self.repo / PROTOCOL
        path.write_bytes(path.read_bytes().replace(b"two arms", b"three arms"))
        commit_all(self.repo, "edit the design", PROTOCOL)
        code, report = check(self.repo)
        self.assertEqual(code, 1)
        self.assertEqual(report["checks"]["unaltered"]["status"], "not clear")
        self.assertEqual(report["checks"]["registered"]["status"], "clear")

    def test_check_unaltered_is_not_clear_on_uncommitted_edit(self):
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        register(self.repo)
        path = self.repo / PROTOCOL
        path.write_bytes(path.read_bytes() + b"3. An added step.\n")
        code, report = check(self.repo)
        self.assertEqual(code, 1)
        self.assertEqual(report["checks"]["unaltered"]["status"], "not clear")

    def test_check_chronology_is_not_clear_when_output_predates_registration(self):
        write(self.repo, "results/EXP-0001/x.txt", "an early output\n")
        commit_all(self.repo, "early output", "results/EXP-0001/x.txt")
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        register(self.repo)
        code, report = check(self.repo, "--outputs", "results")
        self.assertEqual(code, 1)
        self.assertEqual(report["checks"]["chronology"]["status"], "not clear")

    def test_check_parallel_branch_output_is_unprovable(self):
        baseline = git(self.repo, "rev-parse", "HEAD").strip()
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        register(self.repo)
        git(self.repo, "checkout", "-q", "-b", "side", baseline)
        write(self.repo, "results/EXP-0001/y.txt", "an output on a parallel branch\n")
        commit_all(self.repo, "output on the side branch", "results/EXP-0001/y.txt")
        git(self.repo, "checkout", "-q", "main")
        code, report = check(self.repo, "--outputs", "results")
        self.assertEqual(code, 1)
        self.assertFalse(report["ok"])
        self.assertEqual(report["checks"]["chronology"]["status"], "unprovable")

    def test_check_inputs_is_not_clear_when_input_changed(self):
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        register(self.repo, "--input", "data/raw/fixture.csv")
        write(self.repo, "data/raw/fixture.csv", "a,b\n1,3\n")
        code, report = check(self.repo)
        self.assertEqual(code, 1)
        self.assertEqual(report["checks"]["inputs"]["status"], "not clear")

    def test_check_reports_untimestamped_registration(self):
        register_by_hand(self.repo)
        code, report = check(self.repo)
        self.assertEqual(code, 1)
        self.assertFalse(report["ok"])
        self.assertEqual(report["checks"]["registered"]["status"], "clear")
        self.assertEqual(report["checks"]["timestamp"]["status"], "not clear")
        self.assertEqual(report["checks"]["timestamp"]["detail"], "registered, not time-stamped")

    def test_check_shallow_history_fails_closed(self):
        write(self.repo, PROTOCOL, PROTOCOL_TEXT)
        register(self.repo)
        clone = Path(self.tmp) / "clone"
        subprocess.run(
            ["git", "clone", "-q", "--depth", "1", self.repo.as_uri(), str(clone)],
            check=True, capture_output=True,
        )
        code, report = check(clone)
        self.assertEqual(code, 1)
        self.assertFalse(report["ok"])
        self.assertEqual(report["checks"]["registered"]["status"], "not clear")
        self.assertIn("shallow", report["checks"]["registered"]["detail"])

    def test_exit_2_outside_git(self):
        outside = Path(self.tmp) / "plain"
        outside.mkdir()
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(Path(self.tmp)))
        write(outside, PROTOCOL, PROTOCOL_TEXT)
        for args in (("register", PROTOCOL), ("check", PROTOCOL)):
            proc = run(outside, *args, env=env)
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)

    def test_exit_2_on_the_0_1_layout(self):
        old = "research_lab/03_experiments/protocols/EXP-0001.md"
        write(self.repo, old, PROTOCOL_TEXT)
        before = git(self.repo, "log", "--format=%H")
        for args in (("register", old), ("check", old)):
            proc = run(self.repo, *args)
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertEqual(proc.stderr, OLD_LAYOUT_MESSAGE)
        self.assertEqual(git(self.repo, "log", "--format=%H"), before)


if __name__ == "__main__":
    unittest.main()
