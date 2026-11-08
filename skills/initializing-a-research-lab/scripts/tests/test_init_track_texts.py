"""init_lab.py --track: every research_lab/ path the shared texts name is in each track's minimal lab."""

import json
import re
import sys
import unittest
from pathlib import Path

from test_init_fresh import FreshFolderCase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import init_lab  # noqa: E402

SKILLS = Path(__file__).resolve().parents[3]
SHARED_TEXTS = (
    SKILLS / "initializing-a-research-lab" / "templates" / "CLAUDE_SECTION.md",
    SKILLS / "holding-lab-meetings" / "SKILL.md",
    SKILLS / "requesting-reference-access" / "SKILL.md",
)
GUARD = "where the lab has"
PATH = re.compile(r"research_lab/[A-Za-z0-9_./-]*")
PLACEHOLDERS = ("YYYY", "xxxx", "*", "<")


def named_paths() -> list:
    """(text, line number, path) for each research_lab/ path on a line without the guard phrase.

    A path that ends in a placeholder (a dated note, a glob) stands for its folder."""
    found = []
    for text in SHARED_TEXTS:
        for number, line in enumerate(text.read_text(encoding="utf-8").splitlines(), start=1):
            if GUARD in line:
                continue
            for match in PATH.finditer(line):
                path = match.group(0).rstrip(".,:;")
                last = path.rsplit("/", 1)[-1]
                if any(mark in last for mark in PLACEHOLDERS):
                    path = path.rsplit("/", 1)[0] + "/"
                found.append((text.name, number, path))
    return found


def held(path: str, created: set) -> bool:
    if path in created:
        return True
    folder = path.rstrip("/") + "/"
    return any(rel.startswith(folder) for rel in created)


class TestTrackTexts(FreshFolderCase):
    def test_the_texts_name_paths(self):
        paths = {path for _, _, path in named_paths()}
        for path in (
            "research_lab/requests/ACCESS_REQUESTS.md",
            "research_lab/planning/WORK_PLAN.md",
            "research_lab/decisions/lab_meetings/",
            "research_lab/templates/",
        ):
            self.assertIn(path, paths)

    def test_each_track_holds_every_path_the_shared_texts_name(self):
        wanted = named_paths()
        for track in init_lab.TRACKS:
            result = self.init("--track", track, yes=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            created = set(json.loads(result.stdout)["create"])
            missing = [f"{name}:{number} {path}" for name, number, path in wanted if not held(path, created)]
            self.assertEqual(missing, [], f"track {track} lacks paths its shared texts name")

    def test_the_shared_set_holds_the_request_plan_and_meeting_files(self):
        for track, files in init_lab.TRACK_FILES.items():
            for rel in (
                "research_lab/requests/README.md",
                "research_lab/requests/ACCESS_REQUESTS.md",
                "research_lab/planning/WORK_PLAN.md",
                "research_lab/templates/TASK_REPORT.md",
                "research_lab/templates/SESSION_OPENING.md",
                "research_lab/templates/SESSION_CLOSE.md",
                "research_lab/templates/LAB_MEETING.md",
            ):
                self.assertIn(rel, files, track)


if __name__ == "__main__":
    unittest.main()
