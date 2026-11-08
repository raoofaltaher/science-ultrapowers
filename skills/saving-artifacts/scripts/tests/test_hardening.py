"""Review-pass fixes for the artifact store: ledger-derived paths, git absence, LFS hint, row shape, secrets."""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts
from _helpers import make_git_lab, make_lab, run_cli, write_file

SCRIPT = Path(__file__).resolve().parents[1] / "artifacts.py"


class HardeningBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self._tmp.cleanup)
        self.t = Path(self._tmp.name)

    def _store(self, lab_json=None, git=False):
        lab = make_git_lab(self.t, lab_json) if git else make_lab(self.t, lab_json)
        s = artifacts.LabStore(lab)
        return s, s.project_root

    def _save1(self, s, path, **kw):
        kw.setdefault("role", "r")
        kw.setdefault("command", "c")
        return s.save([path], **kw)[0]


class LedgerPathTest(HardeningBase):
    def test_version_of_refuses_ledger_path_escape(self):
        s, proj = self._store()
        f = write_file(proj / "work" / "report.md", "one\n")
        r1 = self._save1(s, f)
        escaped = self.t / "escaped"
        write_file(f, "two\n")
        # Case 1: the artifact id in the ledger climbs out of the store.
        evil = "../../../../escaped"
        arts = s.rows("artifacts")
        arts[0]["id"] = evil
        s.rewrite("artifacts", arts)
        vers = s.rows("versions")
        vers[0]["artifact_id"] = evil
        s.rewrite("versions", vers)
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, f, version_of=evil)
        self.assertIn("names a path outside the store", str(cm.exception))
        self.assertFalse(escaped.exists())
        # Case 2: the store leaf is not a single path component.
        arts = s.rows("artifacts")
        arts[0]["id"] = r1["artifact_id"]
        arts[0]["filename"] = ".."
        s.rewrite("artifacts", arts)
        vers = s.rows("versions")
        vers[0]["artifact_id"] = r1["artifact_id"]
        s.rewrite("versions", vers)
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, f, version_of=r1["artifact_id"])
        self.assertIn("names a path outside the store", str(cm.exception))
        self.assertEqual(len(s.rows("versions")), 1)

    def test_copy_row_outside_the_store_is_refused_by_path(self):
        s, proj = self._store()
        r1 = self._save1(s, write_file(proj / "work" / "report.md", "one\n"))
        write_file(s.lab / "outside.txt", "x\n")
        vers = s.rows("versions")
        vers[0]["storage_path"] = "outside.txt"
        s.rewrite("versions", vers)
        with self.assertRaises(artifacts.StoreError) as cm:
            s.locate(r1["version_id"], stage=False)
        self.assertIn("outside the store", str(cm.exception))

    def test_link_outside_project_is_reported_not_followed(self):
        s, proj = self._store()
        r = s.link([write_file(proj / "data" / "raw.csv", "x\n")], role="r", command="c")[0]
        outside = write_file(self.t / "secret.txt", "secret\n")
        vers = s.rows("versions")
        vers[0]["storage_path"] = "link:../../secret.txt"
        s.rewrite("versions", vers)
        found = s.locate(r["version_id"], stage=False)
        self.assertEqual(found["status"], "outside-project")
        self.assertTrue(outside.is_file())
        self.assertEqual(s.rows("versions")[0]["status"], "ok")
        with self.assertRaises(artifacts.StoreError) as cm:
            s.path(r["version_id"], stage=False)
        self.assertIn("outside-project", str(cm.exception))
        code, out, err = run_cli(["--lab", str(s.lab), "path", r["version_id"], "--no-stage"])
        self.assertEqual(code, 1)
        self.assertIn("outside-project", out)
        # An absolute link that does not exist is reported the same way; one that exists is followed.
        vers = s.rows("versions")
        vers[0]["storage_path"] = "link:" + (self.t / "nowhere.txt").as_posix()
        s.rewrite("versions", vers)
        self.assertEqual(s.locate(r["version_id"], stage=False)["status"], "outside-project")
        vers = s.rows("versions")
        vers[0]["storage_path"] = "link:" + outside.as_posix()
        s.rewrite("versions", vers)
        self.assertEqual(s.locate(r["version_id"], stage=False)["status"], "ok")


    def test_link_row_under_home_expands_tilde(self):
        s, proj = self._store()
        r = s.link([write_file(proj / "data" / "raw.csv", "x\n")], role="r", command="c")[0]
        home = self.t / "home"
        host = write_file(home / "data" / "host.csv", "h\n")
        vers = s.rows("versions")
        vers[0]["storage_path"] = "link:~/data/host.csv"
        s.rewrite("versions", vers)
        with mock.patch.object(artifacts.Path, "home", return_value=home):
            found = s.locate(r["version_id"], stage=False)
            self.assertEqual(found["status"], "ok")
            self.assertEqual(found["path"], host.as_posix())
            self.assertEqual(s.path(r["version_id"], stage=False), host)
            # a home file that is gone is reported outside-project, not followed
            host.unlink()
            self.assertEqual(s.locate(r["version_id"], stage=False)["status"], "outside-project")
        self.assertEqual(s.rows("versions")[0]["storage_path"], "link:~/data/host.csv")


class GitMissingTest(HardeningBase):
    def test_missing_git_is_a_warning_not_a_crash(self):
        lab = make_lab(self.t)
        proj = lab.parent
        f = write_file(proj / "work" / "report.md", "r\n")
        empty = self.t / "emptybin"
        empty.mkdir()
        env = dict(os.environ)
        env["PATH"] = str(empty)
        done = subprocess.run(
            [sys.executable, str(SCRIPT), "--lab", str(lab), "save", str(f), "--role", "r", "--command", "c"],
            capture_output=True, env=env, text=True, encoding="utf-8",
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("warning: git not found; nothing staged", done.stderr)
        self.assertNotIn("Traceback", done.stderr)
        self.assertEqual(len(json.loads(done.stdout)), 1)


class LfsInstallHintTest(HardeningBase):
    def _tracked_store(self):
        s, proj = self._store({"lfs": {"thresholdMB": 0.000001, "budgetWarnMB": 800}}, git=True)
        return s, proj

    def test_lfs_warning_says_to_install_git_lfs_when_it_is_missing(self):
        s, proj = self._tracked_store()
        f = write_file(proj / "work" / "big.bin", b"0123456789")
        real = artifacts.LabStore._git

        def fake(self, args, cwd):
            if args[:2] == ["lfs", "version"]:
                return subprocess.CompletedProcess(["git", *args], 1, "", "git: 'lfs' is not a git command")
            return real(self, args, cwd)

        err = io.StringIO()
        with mock.patch.object(artifacts.LabStore, "_git", fake), \
                mock.patch.object(artifacts.LabStore, "lfs_filter_configured", return_value=False), \
                contextlib.redirect_stderr(err):
            self._save1(s, f)
        self.assertIn("install git-lfs, then run: git lfs install", err.getvalue())

    def test_lfs_warning_keeps_the_short_hint_when_git_lfs_is_installed(self):
        s, proj = self._tracked_store()
        f = write_file(proj / "work" / "big.bin", b"0123456789")
        real = artifacts.LabStore._git

        def fake(self, args, cwd):
            if args[:2] == ["lfs", "version"]:
                return subprocess.CompletedProcess(["git", *args], 0, "git-lfs/3.0", "")
            return real(self, args, cwd)

        err = io.StringIO()
        with mock.patch.object(artifacts.LabStore, "_git", fake), \
                mock.patch.object(artifacts.LabStore, "lfs_filter_configured", return_value=False), \
                contextlib.redirect_stderr(err):
            self._save1(s, f)
        self.assertIn("run: git lfs install", err.getvalue())
        self.assertNotIn("install git-lfs, then", err.getvalue())


class InputsHelpTest(HardeningBase):
    def test_inputs_help_says_to_put_it_after_the_files_or_repeat_it(self):
        for sub in ("save", "link"):
            code, out, err = run_cli([sub, "--help"])
            self.assertEqual(code, 0)
            flat = " ".join(out.split())
            self.assertIn("put --inputs after the files, or repeat it", flat)


class RowShapeTest(HardeningBase):
    def test_non_object_ledger_row_is_a_store_error(self):
        s, proj = self._store()
        s.root.mkdir(parents=True, exist_ok=True)
        (s.root / "artifacts.jsonl").write_text('{"id": "a"}\n[1, 2]\n', encoding="utf-8")
        with self.assertRaises(artifacts.StoreError) as cm:
            s.rows("artifacts")
        self.assertEqual(str(cm.exception), "artifacts.jsonl line 2: not a artifacts row")

    def test_row_without_its_key_is_a_store_error(self):
        s, proj = self._store()
        s.root.mkdir(parents=True, exist_ok=True)
        (s.root / "dependencies.jsonl").write_text('{"version_id": "v"}\n', encoding="utf-8")
        with self.assertRaises(artifacts.StoreError) as cm:
            s.rows("dependencies")
        self.assertIn("dependencies.jsonl line 1: not a dependencies row", str(cm.exception))
        (s.root / "versions.jsonl").write_text('{"artifact_id": "a"}\n', encoding="utf-8")
        with self.assertRaises(artifacts.StoreError):
            s.rows("versions")
        (s.root / "verification_checks.jsonl").write_text('"text"\n', encoding="utf-8")
        with self.assertRaises(artifacts.StoreError):
            s.rows("verification_checks")

    def test_cli_reports_a_bad_row_without_a_traceback(self):
        s, proj = self._store()
        s.root.mkdir(parents=True, exist_ok=True)
        (s.root / "artifacts.jsonl").write_text("[1]\n", encoding="utf-8")
        code, out, err = run_cli(["--lab", str(s.lab), "search"])
        self.assertEqual(code, 1)
        self.assertIn("not a artifacts row", err)
        self.assertNotIn("Traceback", err)


class SecretRefusalTest(HardeningBase):
    def _assert_refused(self, s, rel_path, **kw):
        f = write_file(s.project_root / rel_path, "KEY=1\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            self._save1(s, f, **kw)
        self.assertEqual(
            str(cm.exception),
            f"{rel_path} looks like a secret or ignored file; pass --force to save it anyway",
        )
        self.assertFalse((s.root / "versions.jsonl").exists())
        return f

    def test_secret_names_and_special_folders_are_refused(self):
        s, proj = self._store()
        for rel in (".env", ".env.local", "keys/server.pem", "keys/id_rsa", ".claude/settings.json",
                    ".venv-lab-skills/lib/x.py", ".git/hooks/pre-commit"):
            self._assert_refused(s, rel)

    def test_link_refuses_a_secret_too(self):
        s, proj = self._store()
        f = write_file(proj / ".env", "KEY=1\n")
        with self.assertRaises(artifacts.StoreError) as cm:
            s.link([f], role="r", command="c")
        self.assertIn("looks like a secret or ignored file; pass --force to save it anyway", str(cm.exception))
        self.assertFalse((s.root / "versions.jsonl").exists())

    def test_git_ignored_file_is_refused_and_force_overrides(self):
        s, proj = self._store(git=True)
        write_file(proj / ".gitignore", "scratch/\n")
        f = self._assert_refused(s, "scratch/out.csv")
        res = self._save1(s, f, force=True)
        self.assertEqual(res["version_number"], 1)
        self.assertEqual(s.rows("artifacts")[0]["filename"], "scratch/out.csv")

    def test_force_overrides_a_name_match_in_save_and_link(self):
        s, proj = self._store()
        f = write_file(proj / ".env", "KEY=1\n")
        self.assertEqual(self._save1(s, f, force=True)["version_number"], 1)
        g = write_file(proj / "keys" / "id_x", "k\n")
        self.assertEqual(s.link([g], role="r", command="c", force=True)[0]["version_number"], 1)

    def test_cli_refusal_exits_1_and_force_flag_works(self):
        s, proj = self._store()
        f = write_file(proj / ".env", "KEY=1\n")
        code, out, err = run_cli(["--lab", str(s.lab), "save", str(f), "--role", "r", "--command", "c", "--no-stage"])
        self.assertEqual(code, 1)
        self.assertIn("error: .env looks like a secret or ignored file; pass --force to save it anyway", err)
        code, out, err = run_cli(
            ["--lab", str(s.lab), "save", str(f), "--role", "r", "--command", "c", "--no-stage", "--force"]
        )
        self.assertEqual(code, 0, err)

    def test_an_ordinary_file_is_not_refused(self):
        s, proj = self._store(git=True)
        res = self._save1(s, write_file(proj / "work" / "environment.md", "e\n"))
        self.assertEqual(res["version_number"], 1)


if __name__ == "__main__":
    unittest.main()
