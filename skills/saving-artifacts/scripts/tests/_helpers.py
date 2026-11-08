"""Shared helpers for the artifact-store tests."""
import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import artifacts


def make_lab(tmp, lab_json: dict | None = None) -> Path:
    """Create <tmp>/proj/research_lab (optionally with lab.json); return it unresolved."""
    lab = Path(tmp) / "proj" / "research_lab"
    lab.mkdir(parents=True, exist_ok=True)
    if lab_json is not None:
        (lab / "lab.json").write_text(json.dumps(lab_json), encoding="utf-8")
    return lab


def make_git_lab(tmp, lab_json: dict | None = None) -> Path:
    """make_lab, then initialise a git repository in <tmp>/proj."""
    lab = make_lab(tmp, lab_json)
    proj = Path(tmp) / "proj"
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "test@example.com"],
        ["git", "config", "user.name", "test"],
        ["git", "config", "core.autocrlf", "false"],
    ):
        subprocess.run(cmd, cwd=proj, check=True, capture_output=True)
    return lab


def write_file(path, data: bytes | str) -> Path:
    """Write bytes exactly (str is encoded as utf-8, no newline translation)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    path.write_bytes(data)
    return path


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    """Call artifacts.main(argv); return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = artifacts.main(argv)
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()
