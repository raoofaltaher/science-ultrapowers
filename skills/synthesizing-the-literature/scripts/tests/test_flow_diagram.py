"""Tests of flow_diagram.py: each test runs the script on counts written to a temporary folder."""
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT = str(Path(__file__).resolve().parents[1] / "flow_diagram.py")
XMLNS = "http://www.w3.org/2000/svg"

PRISMA_COUNTS = {
    "identified": {"databases": 250, "registers": 30, "other": 20},
    "duplicates_removed": 50,
    "screened": 250,
    "excluded_screening": 200,
    "sought": 50,
    "not_retrieved": 5,
    "assessed": 45,
    "excluded_assessed": {"Wrong population": 20, "Outcome not reported & no data": 10},
    "included": 15,
}

CONSORT_COUNTS = {
    "assessed": 120,
    "excluded": {"Did not meet the criteria": 14, "Declined to take part": 6},
    "randomized": 100,
    "arms": [
        {"name": "Arm Alpha", "allocated": 50, "received": 48, "lost": 3, "discontinued": 2,
         "analyzed": 42, "excluded_analysis": 1},
        {"name": "Arm Beta", "allocated": 50, "received": 49, "lost": 2, "discontinued": 1,
         "analyzed": 45, "excluded_analysis": 1},
    ],
}


def run(*args):
    """Run the script and return the completed process, with text output."""
    return subprocess.run(
        [sys.executable, SCRIPT, *args], capture_output=True, encoding="utf-8", errors="replace"
    )


class FlowDiagramTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write_counts(self, counts):
        path = self.dir / "counts.json"
        path.write_text(json.dumps(counts), encoding="utf-8")
        return str(path)

    def test_prisma_counts_that_add_up_produce_svg(self):
        out = self.dir / "flow.svg"
        proc = run(self.write_counts(PRISMA_COUNTS), "--style", "prisma2020", "--out", str(out))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        text = out.read_text(encoding="utf-8")
        root = ET.fromstring(text)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertTrue(root.get("viewBox"))
        visible = "".join(root.itertext())
        self.assertIn("Records identified", visible)
        self.assertIn("Studies included", visible)
        self.assertIn("Wrong population", visible)
        self.assertNotIn("http", text.replace(XMLNS, ""))
        self.assertNotIn("<image", text)

    def test_prisma_counts_that_do_not_add_up_exit_1(self):
        counts = dict(PRISMA_COUNTS, screened=240)
        out = self.dir / "flow.svg"
        proc = run(self.write_counts(counts), "--style", "prisma2020", "--out", str(out))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("screened", proc.stderr)
        self.assertFalse(out.exists())

    def test_consort_two_arms(self):
        out = self.dir / "trial.svg"
        proc = run(self.write_counts(CONSORT_COUNTS), "--style", "consort", "--out", str(out))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        text = out.read_text(encoding="utf-8")
        ET.fromstring(text)
        self.assertIn("Arm Alpha", text)
        self.assertIn("Arm Beta", text)
        bad = json.loads(json.dumps(CONSORT_COUNTS))
        bad["arms"][1]["allocated"] = 40
        proc = run(self.write_counts(bad), "--style", "consort", "--out", str(self.dir / "bad.svg"))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("randomized", proc.stderr)

    def test_usage_exit_2(self):
        self.assertEqual(run().returncode, 2)
        proc = run(self.write_counts(PRISMA_COUNTS), "--style", "venn", "--out", str(self.dir / "x.svg"))
        self.assertEqual(proc.returncode, 2)
        proc = run(str(self.dir / "missing.json"), "--style", "consort", "--out", str(self.dir / "x.svg"))
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
