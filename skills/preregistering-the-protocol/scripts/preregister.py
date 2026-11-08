#!/usr/bin/env python3
"""Register a protocol and check its registration, from git history alone.

    preregister.py register <protocol> [--input <path>]... [--task <TASK-id>] [--timestamp-only]
    preregister.py check <protocol> [--outputs <path>]...

register commits the protocol alone (the registration commit), then commits the registration
hash into the protocol (the time-stamp commit). check reports five items, each clear, not
clear or unprovable: registered, timestamp, unaltered, chronology and inputs.

Exit codes: 0 when every item is clear, 1 when an item is not clear or a commit fails,
2 for a usage error, a missing git repository or a lab in the 0.1 layout.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

OLD_LAYOUT_MESSAGE = (
    "this lab uses the 0.1 layout; run science-ultrapowers:initializing-a-research-lab to migrate it"
)
STAMP = b"Registered at commit:"
INPUTS_HEADING = "## Registered inputs"
DEFAULT_OUTPUTS = ("results", "outputs", "figures", "reports", "derived")
ITEMS = ("registered", "timestamp", "unaltered", "chronology", "inputs")
ROLE = "research-project-manager"


class UsageError(Exception):
    """A usage error: exit 2."""


class CommitError(Exception):
    """A git commit that failed, for example through a hook: exit 1."""


class OldLayout(Exception):
    """The lab uses the 0.1 layout: exit 2 with the migration message."""


# ---------------------------------------------------------------- git helpers


def _run(repo, args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True)


def git(repo, *args) -> str:
    """Run git with an argument list and return stdout; raise UsageError with git's message."""
    proc = _run(repo, args)
    if proc.returncode != 0:
        raise UsageError(proc.stderr.decode("utf-8", "replace").strip() or "git failed: " + " ".join(args))
    return proc.stdout.decode("utf-8", "replace")


def git_bytes(repo, *args) -> bytes:
    proc = _run(repo, args)
    if proc.returncode != 0:
        raise UsageError(proc.stderr.decode("utf-8", "replace").strip() or "git failed: " + " ".join(args))
    return proc.stdout


def git_commit(repo, subject, trailer, path):
    """Commit the one path with a subject and a trailer; raise CommitError with git's output."""
    proc = _run(repo, ("commit", "-q", "-m", subject, "-m", trailer, "--", path))
    if proc.returncode != 0:
        out = (proc.stdout + proc.stderr).decode("utf-8", "replace").strip()
        raise CommitError(out or "git commit failed")


def find_repo(cwd) -> Path:
    proc = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True)
    if proc.returncode != 0:
        raise UsageError("not inside a git repository")
    return Path(proc.stdout.decode("utf-8", "replace").strip()).resolve()


def has_head(repo) -> bool:
    return _run(repo, ("rev-parse", "-q", "--verify", "HEAD")).returncode == 0


def is_shallow(repo) -> bool:
    return git(repo, "rev-parse", "--is-shallow-repository").strip() == "true"


def blob_hash(repo, path) -> str:
    return git(repo, "hash-object", "--", path).strip()


def first_commit_touching(repo, path):
    """The commit that added the path, following renames; None when it was never committed."""
    out = git(repo, "log", "--diff-filter=A", "--follow", "--format=%H", "--", path).split()
    return out[-1] if out else None


def registration_commit(repo, path, protocol_id):
    """The commit that registered the protocol: the oldest commit touching the path (renames followed)
    whose 'Preregistration:' trailer names the protocol id. Without such a commit, the commit that
    added the path. Git's copy detection can otherwise trace a protocol copied from the lab's
    template back to the commit that added the template."""
    commits = git(repo, "log", "--follow", "--format=%H", "--", path).split()
    for commit in reversed(commits):
        if trailer(repo, commit, "Preregistration") == protocol_id:
            return commit
    return first_commit_touching(repo, path)


def paths_in_commit(repo, commit) -> list:
    out = git_bytes(repo, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "-z", commit)
    return [p.decode("utf-8", "replace") for p in out.split(b"\0") if p]


def trailer(repo, commit, key):
    out = git(repo, "show", "-s", f"--format=%(trailers:key={key},valueonly)", commit)
    for line in out.splitlines():
        if line.strip():
            return line.strip()
    return None


def is_ancestor(repo, older, newer) -> bool:
    proc = _run(repo, ("merge-base", "--is-ancestor", older, newer))
    if proc.returncode in (0, 1):
        return proc.returncode == 0
    raise UsageError(proc.stderr.decode("utf-8", "replace").strip() or "git merge-base failed")


def commits_touching(repo, path) -> list:
    """Every commit on any branch, tag or remote branch, and on HEAD, that touches the path."""
    out = git(repo, "log", "--format=%H", "HEAD", "--branches", "--tags", "--remotes", "--", path)
    return out.split()


def has_uncommitted(repo, path) -> bool:
    out = git_bytes(repo, "status", "--porcelain", "-z", "--untracked-files=all", "--", path)
    return bool(out.strip(b"\0"))


# ------------------------------------------------------------- text helpers


def strip_timestamp(data: bytes) -> bytes:
    """The bytes without the first line that starts with 'Registered at commit:'."""
    lines = data.split(b"\n")
    for i, line in enumerate(lines):
        if line.startswith(STAMP):
            del lines[i]
            break
    return b"\n".join(lines)


def stamp_value(data: bytes):
    """The hash on the 'Registered at commit:' line, or None when the file has no such line."""
    for line in data.split(b"\n"):
        if line.startswith(STAMP):
            return line[len(STAMP):].strip().decode("utf-8", "replace")
    return None


def stamp_bytes(data: bytes, registration: str) -> bytes:
    """Set the 'Registered at commit:' line: replace the first one, or add one after the first line."""
    end = b"\r" if b"\r\n" in data else b""
    new = STAMP + b" " + registration.encode("ascii") + end
    lines = data.split(b"\n")
    for i, line in enumerate(lines):
        if line.startswith(STAMP):
            lines[i] = new
            break
    else:
        lines.insert(1, new)
    return b"\n".join(lines)


def inputs_of(data: bytes) -> list:
    """The (path, blob hash) pairs of the '## Registered inputs' block."""
    found = []
    inside = False
    for line in data.decode("utf-8", "replace").splitlines():
        if line.strip() == INPUTS_HEADING:
            inside = True
        elif inside and line.startswith("#"):
            break
        elif inside and line.startswith("- "):
            parts = line[2:].rstrip().rsplit(" ", 1)
            if len(parts) == 2 and re.fullmatch(r"[0-9a-f]{40,64}", parts[1]):
                found.append((parts[0], parts[1]))
    return found


def is_old_layout(lab: Path) -> bool:
    """True when the lab has the 0.1 layout: no artifacts/archive/, and either the old artifact
    folder or a numbered folder."""
    if (lab / "artifacts" / "archive").is_dir():
        return False
    if (lab / "artifacts" / "store").is_dir():  # legacy
        return True
    try:
        return any(d.is_dir() and re.fullmatch(r"\d\d_.+", d.name) for d in lab.iterdir())
    except OSError:
        return False


def repo_relative(repo: Path, arg) -> str:
    path = Path(arg)
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError:
        raise UsageError(f"{arg} is outside the repository") from None


def find_lab(repo: Path, rel: str):
    for parent in (repo / rel).parents:
        if parent == repo:
            break
        if parent.name == "research_lab":
            return parent
    lab = repo / "research_lab"
    return lab if lab.is_dir() else None


# ------------------------------------------------------------------- register


def _stamp_commit(repo, protocol, pid, registration, task) -> str:
    path = repo / protocol
    committed = path.read_bytes()
    path.write_bytes(stamp_bytes(committed, registration))
    try:
        git_commit(
            repo, f"{task} {ROLE}: time-stamp protocol {pid}",
            f"Preregistration-Timestamp: {registration}", protocol,
        )
    except CommitError as exc:
        path.write_bytes(committed)
        raise CommitError(
            f"registered at {registration}, not time-stamped; fix the cause, "
            f"then run register with --timestamp-only. {exc}"
        ) from None
    return git(repo, "rev-parse", "HEAD").strip()


def find_timestamp_commits(repo, protocol, registration) -> list:
    found = []
    for commit in git(repo, "log", "--follow", "--format=%H", "--", protocol).split():
        if commit == registration:
            continue
        if trailer(repo, commit, "Preregistration-Timestamp") == registration and is_ancestor(
            repo, registration, commit
        ):
            found.append(commit)
    return found


def cmd_register(repo, protocol, inputs, task, timestamp_only) -> dict:
    pid = Path(protocol).stem
    path = repo / protocol
    if not path.is_file():
        raise UsageError(f"{protocol} is not a file")
    if not has_head(repo):
        raise UsageError("the repository has no commits yet; commit a baseline first")
    if timestamp_only:
        if inputs:
            raise UsageError("inputs are recorded at registration; do not combine --input with --timestamp-only")
        registration = registration_commit(repo, protocol, pid)
        if registration is None or trailer(repo, registration, "Preregistration") != pid:
            raise UsageError(
                "the first commit of the protocol is not a registration commit "
                f"(no 'Preregistration: {pid}' trailer)"
            )
        if find_timestamp_commits(repo, protocol, registration):
            raise UsageError("the protocol is already time-stamped")
        if has_uncommitted(repo, protocol):
            raise UsageError("the protocol has uncommitted edits; commit or discard them first")
        timestamp = _stamp_commit(repo, protocol, pid, registration, task)
        registered = inputs_of(git_bytes(repo, "cat-file", "blob", f"{registration}:{protocol}"))
        return _register_result(protocol, pid, registration, timestamp, registered)
    if git(repo, "log", "-1", "--format=%H", "--", protocol).strip():
        raise UsageError(
            "the protocol is already committed; a registration is the first commit of the file. "
            "Register a new protocol file for a new confirmatory test"
        )
    entries = []
    for arg in inputs:
        rel = repo_relative(repo, arg)
        if not (repo / rel).is_file():
            raise UsageError(f"{arg} is not a file")
        entries.append((rel, blob_hash(repo, rel)))
    original = path.read_bytes()
    data = original
    if entries:
        nl = b"\r\n" if b"\r\n" in data else b"\n"
        if not data.endswith(b"\n"):
            data += nl
        data += nl + INPUTS_HEADING.encode() + nl + nl
        data += b"".join(f"- {p} {b}".encode("utf-8") + nl for p, b in entries)
        path.write_bytes(data)
    try:
        git(repo, "add", "--", protocol)
        git_commit(repo, f"{task} {ROLE}: register protocol {pid}", f"Preregistration: {pid}", protocol)
    except (CommitError, UsageError):
        _run(repo, ("reset", "-q", "--", protocol))
        path.write_bytes(original)
        raise
    registration = git(repo, "rev-parse", "HEAD").strip()
    timestamp = _stamp_commit(repo, protocol, pid, registration, task)
    return _register_result(protocol, pid, registration, timestamp, entries)


def _register_result(protocol, pid, registration, timestamp, entries) -> dict:
    return {
        "protocol": protocol,
        "protocol_id": pid,
        "registration_commit": registration,
        "timestamp_commit": timestamp,
        "inputs": [{"path": p, "blob": b} for p, b in entries],
    }


# ---------------------------------------------------------------------- check


def item(status, detail) -> dict:
    return {"status": status, "detail": detail}


def _blocked(registered, reason) -> dict:
    checks = {"registered": registered}
    for name in ITEMS[1:]:
        checks[name] = item("unprovable", reason)
    return checks


def _check_chronology(repo, outputs, registration, skip) -> dict:
    if not outputs:
        outputs = [p for p in DEFAULT_OUTPUTS if (repo / p).exists() or commits_touching(repo, p)]
    not_clear, unprovable, seen = [], [], set()
    for out in outputs:
        for commit in commits_touching(repo, out):
            if commit in seen or commit == registration or commit in skip:
                continue
            seen.add(commit)
            if is_ancestor(repo, commit, registration):
                not_clear.append(f"{out} at {commit[:10]}")
            elif not is_ancestor(repo, registration, commit):
                unprovable.append(f"{out} at {commit[:10]}")
        if has_uncommitted(repo, out):
            unprovable.append(f"{out} has uncommitted files")
    if not_clear:
        return item("not clear", "output committed before the registration: " + "; ".join(not_clear))
    if unprovable:
        return item("unprovable", "order against the registration cannot be proved: " + "; ".join(unprovable))
    if not seen:
        return item("clear", "no output committed yet")
    return item("clear", f"{len(seen)} output commit(s), all after the registration")


def cmd_check(repo, protocol, outputs) -> dict:
    if not has_head(repo):
        raise UsageError("the repository has no commits yet")
    if is_shallow(repo):
        checks = _blocked(
            item("not clear", "shallow clone: the history is incomplete, so no registration can be proved"),
            "shallow clone",
        )
        return _report(protocol, checks)
    registration = registration_commit(repo, protocol, Path(protocol).stem)
    if registration is None:
        return _report(protocol, _blocked(item("not clear", "no commit holds the protocol"), "no registration commit"))
    changed = paths_in_commit(repo, registration)
    if len(changed) == 1:
        reg_path = changed[0]
        registered = item("clear", f"commit {registration[:10]} holds the protocol alone")
    else:
        registered = item("not clear", "the registration commit also holds: " + ", ".join(changed[:5]))
        reg_path = protocol if protocol in changed else None
    if reg_path is None:
        return _report(protocol, _blocked(registered, "registration commit unknown"))
    checks = {"registered": registered}

    stamps = find_timestamp_commits(repo, protocol, registration)
    head = _run(repo, ("cat-file", "blob", f"HEAD:{protocol}"))
    head_data = head.stdout if head.returncode == 0 else None
    work_path = repo / protocol
    work_data = work_path.read_bytes() if work_path.is_file() else None
    if not stamps:
        checks["timestamp"] = item("not clear", "registered, not time-stamped")
    elif head_data is None:
        checks["timestamp"] = item("not clear", "the protocol is missing at the branch head")
    else:
        values = {stamp_value(head_data), stamp_value(work_data) if work_data is not None else None}
        if values == {registration}:
            checks["timestamp"] = item("clear", f"time-stamped by commit {stamps[0][:10]}")
        else:
            checks["timestamp"] = item(
                "not clear", "the 'Registered at commit:' line is missing or does not name the registration commit"
            )

    registered_data = git_bytes(repo, "cat-file", "blob", f"{registration}:{reg_path}")
    baseline = strip_timestamp(registered_data)
    if head_data is None or work_data is None:
        checks["unaltered"] = item("not clear", "the protocol file is missing")
    elif strip_timestamp(head_data) != baseline:
        checks["unaltered"] = item("not clear", "the protocol at the branch head differs from the registered version")
    elif strip_timestamp(work_data) != baseline:
        checks["unaltered"] = item("not clear", "the protocol has uncommitted edits")
    else:
        checks["unaltered"] = item("clear", "the protocol equals the registered version")

    checks["chronology"] = _check_chronology(repo, outputs, registration, set(stamps))

    recorded = inputs_of(registered_data)
    if not recorded:
        checks["inputs"] = item("clear", "no inputs registered")
    else:
        bad = []
        for rel, blob in recorded:
            file = repo / rel
            try:
                inside = file.resolve().is_relative_to(repo)
            except OSError:
                inside = False
            if not inside or not file.is_file():
                bad.append(f"{rel} is missing")
            elif blob_hash(repo, rel) != blob:
                bad.append(f"{rel} changed")
        if bad:
            checks["inputs"] = item("not clear", "; ".join(bad))
        else:
            checks["inputs"] = item("clear", f"{len(recorded)} input checksum(s) match")
    return _report(protocol, checks)


def _report(protocol, checks) -> dict:
    return {
        "protocol": protocol,
        "ok": all(c["status"] == "clear" for c in checks.values()),
        "checks": checks,
    }


# ----------------------------------------------------------------------- main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="preregister.py", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    reg = sub.add_parser("register", help="commit the protocol, then time-stamp it")
    reg.add_argument("protocol")
    reg.add_argument("--input", action="append", default=[], help="an input file to checksum (repeatable)")
    reg.add_argument("--task", default="lab", help="the TASK-id for the commit subjects")
    reg.add_argument("--timestamp-only", action="store_true", help="time-stamp an existing registration commit")
    chk = sub.add_parser("check", help="report the five items of the registration check")
    chk.add_argument("protocol")
    chk.add_argument("--outputs", action="append", default=[], help="an output path (repeatable)")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo = find_repo(Path.cwd())
        protocol = repo_relative(repo, args.protocol)
        lab = find_lab(repo, protocol)
        if lab is not None and is_old_layout(lab):
            raise OldLayout(OLD_LAYOUT_MESSAGE)
        if args.command == "register":
            result = cmd_register(repo, protocol, args.input, args.task, args.timestamp_only)
            code = 0
        else:
            outputs = [repo_relative(repo, p) for p in args.outputs]
            result = cmd_check(repo, protocol, outputs)
            code = 0 if result["ok"] else 1
    except OldLayout as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except UsageError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    except CommitError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
