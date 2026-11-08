"""setup_lab_env.ps1: the default project root outside a repository, and the pinned package versions."""

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SCRIPT = SKILL / "scripts" / "setup_lab_env.ps1"
SHELLS = [name for name in ("powershell", "pwsh") if shutil.which(name)]
PIN = re.compile(r"^[A-Za-z0-9_.-]+==\d+(\.\d+)*$")


def package_list() -> list[str]:
    text = SCRIPT.read_text(encoding="utf-8")
    block = re.search(r"\$pkgs\s*=\s*@\((.*?)\)\s*\r?\n", text, re.DOTALL)
    assert block, "the $pkgs list was not found"
    return re.findall(r"'([^']+)'", block.group(1))


class TestDefaultRoot(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.folder = Path(self._tmp.name)
        inside = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=self.folder, capture_output=True, text=True
        ) if shutil.which("git") else None
        if inside is None or inside.returncode == 0:
            self.skipTest("needs git, and a temp folder that is not inside a repository")

    def run_shell(self, shell: str):
        return subprocess.run(
            [shell, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT), "-DryRun"],
            cwd=self.folder,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
        )

    def test_a_folder_that_is_not_a_repository_does_not_stop_the_script(self):
        if not SHELLS:
            self.skipTest("no PowerShell on PATH")
        for shell in SHELLS:
            with self.subTest(shell=shell):
                result = self.run_shell(shell)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("Dry run: nothing was changed.", result.stdout)
                self.assertIn(str(self.folder.resolve()).lower(), result.stdout.lower())


class TestPins(unittest.TestCase):
    def test_every_package_in_the_environment_is_pinned(self):
        packages = package_list()
        self.assertEqual(len(packages), 14, packages)
        for item in packages:
            self.assertRegex(item, PIN)

    def test_a_dated_comment_records_where_the_pins_come_from(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertRegex(text, r"# Pins checked against PyPI on \d{4}-\d{2}-\d{2}")

    def test_the_optuna_server_is_pinned(self):
        catalogue = json.loads((SKILL / "connectors.json").read_text(encoding="utf-8"))
        entry = next(e for e in catalogue if e["id"] == "optuna")
        self.assertRegex(entry["args"][0], r"^optuna-mcp==\d+(\.\d+)*$")
        self.assertEqual(entry["args"][1], "--storage")


if __name__ == "__main__":
    unittest.main()
