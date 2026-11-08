"""init_lab.py --track: the minimal lab for one track, the union of tracks and a re-run on a full or minimal lab."""

import json
import sys
import unittest
from pathlib import Path

from test_init_fresh import FreshFolderCase, run_script

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import init_lab  # noqa: E402

TRACKS = ("idea", "literature", "review", "writing", "dissemination")
EVERY_TRACK = [
    "research_lab/literature/README.md",
    "research_lab/literature/SOURCES.csv",
    "research_lab/literature/EXCEPTIONS.md",
    "research_lab/literature/evidence_records/.gitkeep",
    "research_lab/literature/search_logs/.gitkeep",
    "research_lab/literature/citation_audits/.gitkeep",
    "research_lab/reviews/README.md",
    "research_lab/reviews/REVIEW_LOG.md",
    "research_lab/reviews/reports/.gitkeep",
    "research_lab/artifacts/archive/.gitkeep",
    "research_lab/memory/MEMORY.md",
    "research_lab/memory/README.md",
    "research_lab/memory/project/.gitkeep",
    "research_lab/memory/artifact/.gitkeep",
    "research_lab/README.md",
    "research_lab/project/README.md",
    "research_lab/project/PROJECT_BRIEF.md",
    "research_lab/decisions/README.md",
    "research_lab/decisions/DECISION_LOG.md",
    "research_lab/decisions/lab_meetings/.gitkeep",
    "research_lab/requests/README.md",
    "research_lab/requests/ACCESS_REQUESTS.md",
    "research_lab/planning/WORK_PLAN.md",
    "research_lab/.working/.gitkeep",
    "research_lab/templates/TASK_REPORT.md",
    "research_lab/templates/SESSION_OPENING.md",
    "research_lab/templates/SESSION_CLOSE.md",
    "research_lab/templates/LAB_MEETING.md",
    "research_lab/lab.json",
]


def tree_bytes(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


class TestTrack(FreshFolderCase):
    def test_track_review_plans_only_the_minimal_set(self):
        result = self.init("--track", "review", yes=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        lab_files = sorted(p for p in plan["create"] if p.startswith("research_lab/"))
        self.assertEqual(lab_files, sorted(init_lab.TRACK_FILES["review"] + [init_lab.GITATTRIBUTES_REL]))
        for rel in EVERY_TRACK:
            self.assertIn(rel, lab_files)
        for rel in (
            "research_lab/templates/REFEREE_REPORT.md",
            "research_lab/templates/CITATION_AUDIT.md",
            "research_lab/templates/RESPONSE_MATRIX.md",
            "research_lab/templates/ADVERSARIAL_REVIEW.md",
        ):
            self.assertIn(rel, lab_files)
        self.assertFalse(
            [
                p
                for p in lab_files
                if p.startswith(("research_lab/experiments/", "research_lab/planning/"))
                and p != "research_lab/planning/WORK_PLAN.md"
            ]
        )
        self.assertEqual(plan["tracks"], ["review"])
        self.assertEqual(sorted(init_lab.TRACK_FILES), sorted(TRACKS))
        templates = init_lab.template_files()
        for track, files in init_lab.TRACK_FILES.items():
            for rel in EVERY_TRACK:
                self.assertIn(rel, files, track)
            for rel in files:
                self.assertIn(rel, templates, f"{track}: {rel} is not a template file")
        self.assertIn("research_lab/project/PROJECT_BRIEF.md", init_lab.TRACK_FILES["idea"])
        self.assertIn("research_lab/templates/SYNTHESIS_MATRIX.md", init_lab.TRACK_FILES["literature"])
        self.assertIn("research_lab/planning/WORK_PLAN.md", init_lab.TRACK_FILES["writing"])
        self.assertIn("research_lab/findings/FINDINGS_LOG.md", init_lab.TRACK_FILES["dissemination"])

    def test_track_review_applies_and_sets_tracks(self):
        result = self.init("--track", "review")
        self.assertEqual(result.returncode, 0, result.stderr)
        lab = self.proj / "research_lab"
        for rel in init_lab.TRACK_FILES["review"]:
            self.assertTrue((self.proj / rel).is_file(), rel)
        self.assertFalse((lab / "experiments").exists())
        self.assertEqual(sorted(x.name for x in (lab / "planning").iterdir()), ["WORK_PLAN.md"])
        data = self.lab_json()
        self.assertEqual(data["tracks"], ["review"])
        self.assertEqual(
            data["preregistration"],
            {"registrationTrailer": "Preregistration", "timestampTrailer": "Preregistration-Timestamp"},
        )
        self.assertEqual(len(data["roles"]), 14)

    def test_track_on_full_lab_adds_only_the_track(self):
        self.assertEqual(self.init().returncode, 0)
        before = tree_bytes(self.proj)
        before.pop("research_lab/lab.json")
        result = self.init("--track", "literature")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["create"], [])
        after = tree_bytes(self.proj)
        after.pop("research_lab/lab.json")
        self.assertEqual(after, before)
        self.assertEqual(self.lab_json()["tracks"], ["literature"])

    def test_two_tracks_union(self):
        result = self.init("--track", "review", "--track", "literature", yes=False)
        plan = json.loads(result.stdout)
        lab_files = {p for p in plan["create"] if p.startswith("research_lab/")}
        want = set(init_lab.TRACK_FILES["review"]) | set(init_lab.TRACK_FILES["literature"])
        self.assertEqual(lab_files, want | {init_lab.GITATTRIBUTES_REL})
        self.assertEqual(plan["tracks"], ["review", "literature"])
        self.assertEqual(self.init("--track", "review").returncode, 0)
        self.assertEqual(self.init("--track", "literature").returncode, 0)
        self.assertEqual(self.lab_json()["tracks"], ["review", "literature"])
        self.assertEqual(self.init("--track", "review").returncode, 0)
        self.assertEqual(self.lab_json()["tracks"], ["review", "literature"])
        for rel in init_lab.TRACK_FILES["literature"]:
            self.assertTrue((self.proj / rel).is_file(), rel)

    def test_full_init_after_minimal_shows_plan(self):
        self.assertEqual(self.init("--track", "review").returncode, 0)
        before = tree_bytes(self.proj)
        result = self.init(yes=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        for rel in (
            "research_lab/experiments/EXPERIMENT_REGISTER.md",
            "research_lab/planning/ROADMAP_STATUS.md",
            "research_lab/findings/FINDINGS_LOG.md",
        ):
            self.assertIn(rel, plan["create"])
        self.assertEqual(tree_bytes(self.proj), before)
        self.assertEqual(self.init().returncode, 0)
        self.assertEqual(self.lab_json()["tracks"], ["review"], "nothing is promoted silently")
        self.assertTrue((self.proj / "research_lab" / "experiments" / "EXPERIMENT_REGISTER.md").is_file())

    def test_unknown_track_is_usage_error(self):
        result = run_script(["--project-root", str(self.proj), "--name", "Demo", "--track", "poster"], self.tmp)
        self.assertEqual(result.returncode, 2)
        for name in TRACKS:
            self.assertIn(name, result.stderr)
        self.assertEqual(list(self.proj.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
