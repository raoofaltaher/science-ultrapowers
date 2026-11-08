import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts
from _helpers import make_lab, write_file

SCRIPT = Path(__file__).resolve().parents[1] / "artifacts.py"
DESCRIPTION = "α-band power ≤ 3 → μ"


class CliSubprocessTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self._tmp.cleanup)
        self.t = Path(self._tmp.name)
        self.env = dict(os.environ)
        self.env.pop("PYTHONIOENCODING", None)
        self.env.pop("PYTHONUTF8", None)

    def _run(self, lab, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--lab", str(lab), *args],
            capture_output=True,
            env=self.env,
        )

    def test_non_ascii_text_survives_a_pipe(self):
        lab = make_lab(self.t)
        proj = lab.parent
        f = write_file(proj / "work" / "report.md", "r\n")
        saved = self._run(lab, "save", str(f), "--role", "r", "--command", "c",
                          "--description", DESCRIPTION, "--no-stage")
        self.assertEqual(saved.returncode, 0, saved.stderr.decode("utf-8", "replace"))
        version_id = json.loads(saved.stdout.decode("utf-8"))[0]["version_id"]

        found = self._run(lab, "search", "power")
        self.assertEqual(found.returncode, 0, found.stderr.decode("utf-8", "replace"))
        self.assertIn(DESCRIPTION, found.stdout.decode("utf-8"))
        self.assertNotIn("Traceback", found.stderr.decode("utf-8", "replace"))

        doc = write_file(proj / "docs" / "doc.md", f"Δ result {{{{artifact:{version_id}}}}}\n")
        resolved = self._run(lab, "resolve", str(doc))
        self.assertEqual(resolved.returncode, 0, resolved.stderr.decode("utf-8", "replace"))
        text = resolved.stdout.decode("utf-8")
        self.assertIn("Δ result", text)
        self.assertIn("](", text)


if __name__ == "__main__":
    unittest.main()
