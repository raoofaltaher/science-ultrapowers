#!/usr/bin/env python3
"""Project-local artifact archive for a research lab.

A versioned artifact archive committed to git: the workspace is working space, every
save is a full-copy version, inputs become dependency edges, and reviewer findings
attach to versions. Copies at or above lfs.thresholdMB are tracked with Git Large File Storage (LFS).

Usage:
    python artifacts.py [--lab PATH] <subcommand> ...

    python artifacts.py save FILES... --role R --task TASK_ID [--session S] [--version-of ID]
        [--checkpoint] [--intermediate] [--destination {milestone,working}]
        [--description T] [--environment T] [--no-stage] [--force] [--inputs ID_OR_PATH ...]

    python artifacts.py link PATHS... --role R --task TASK_ID [--session S]
        [--description T] [--no-stage] [--force] [--inputs ID_OR_PATH ...]

    --inputs takes one or more values; put it after the files or repeat it.
    --force saves a file that looks like a secret (.env*, *.pem, id_*, under .git/, .claude/,
    .venv-lab-skills/) or that git ignores.

    python artifacts.py search [TEXT] [--include-intermediate]
    python artifacts.py path REF [--no-stage]
    python artifacts.py provenance REF
    python artifacts.py graph REF
    python artifacts.py lfs-check

    python artifacts.py findings add --version REF --claim C --verdict VERDICT
        --reviewer R [--severity S] [--evidence E] [--rebuttal T] [--no-stage]
    python artifacts.py findings list [REF] [--all]
    python artifacts.py findings review FINDING_ID --status {closed,re-opened} --reviewer R
        [--note N] [--no-stage]
    python artifacts.py respond FINDING_ID --note N [--no-stage]

    python artifacts.py resolve FILE [--write]

A lab that still has the 0.1 layout (any of its ten numbered folders, or the old artifact
folder without artifacts/archive/) exits 2 and names the migration.
"""
from __future__ import annotations

import argparse
import copy
import fnmatch
import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath

DEFAULT_CONFIG = {"lfs": {"thresholdMB": 10, "budgetWarnMB": 800}}
TABLES = ("artifacts", "versions", "dependencies", "verification_checks")
FINDING_VERDICTS = ("pass", "warn", "fail", "inconclusive")
OUTSTANDING_VERDICTS = FINDING_VERDICTS[1:3]
FINDING_STATUSES = ("open", "author-responded", "re-opened", "closed")
REVIEW_STATUSES = ("closed", "re-opened")
DESTINATIONS = ("milestone", "working")
FINDING_STATUS_LEGACY = {"claimed": "author-responded", "unaddressed": "re-opened", "resolved": "closed"}  # legacy
DESTINATION_LEGACY = {"snapshot": "milestone", "working_data": "working"}  # legacy
OLD_LAYOUT_MESSAGE = (
    "this lab uses the 0.1 layout; run science-ultrapowers:initializing-a-research-lab to migrate it"
)
OLD_STORE_PREFIX = "artifacts/store/"  # legacy
ARCHIVE_PREFIX = "artifacts/archive/"
REQUIRED_KEYS = {
    "artifacts": ("id",),
    "versions": ("id",),
    "dependencies": ("version_id", "depends_on_version_id"),
    "verification_checks": ("id",),
}

GITATTRIBUTES_HEADER = (
    "# science-ultrapowers artifact archive: stored copies are byte-exact; "
    "one LFS line per file at or above lfs.thresholdMB",
    "archive/** -text",
    "*.jsonl text eol=lf",
)
SECRET_NAME_PATTERNS = (".env*", "*.pem", "id_*")
SECRET_FOLDERS = (".git", ".claude", ".venv-lab-skills")
LFS_ATTRIBUTES = "filter=lfs diff=lfs merge=lfs -text"
_LFS_ATTRIBUTE_SET = frozenset(LFS_ATTRIBUTES.split())
MARKER_RE = re.compile(r"\{\{artifact:([A-Za-z0-9_-]+)\}\}")

_MIME = mimetypes.MimeTypes()
_MIME.add_type("text/markdown", ".md")


class StoreError(Exception):
    """Any failure the CLI reports as `error: <message>`."""


class LabNotFound(StoreError):
    pass


class OldLayout(StoreError):
    """The lab still has the 0.1 layout; the CLI prints the message as is and exits 2."""


class AmbiguousId(StoreError):
    pass


class UnknownId(StoreError):
    pass


class MissingFile(StoreError):
    """A version's bytes are gone from disk; carries the version id and the POSIX path."""

    def __init__(self, message: str, version_id: str, path: str) -> None:
        super().__init__(message)
        self.version_id = version_id
        self.path = path


class LfsPointer(StoreError):
    """A stored copy holds a Git LFS pointer, not the file; carries the version id and the POSIX path."""

    def __init__(self, message: str, version_id: str, path: str) -> None:
        super().__init__(message)
        self.version_id = version_id
        self.path = path


LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def finding_status(status):
    """The current word for a reviewer-finding status; a legacy word is read as its new word."""
    return FINDING_STATUS_LEGACY.get(status, status)


def destination_word(destination):
    """The current word for a destination; a legacy word is read as its new word."""
    return DESTINATION_LEGACY.get(destination, destination)


def report_finding(row: dict) -> dict:
    """A copy of a reviewer-finding row with every status in the current words."""
    out = dict(row)
    out["status"] = finding_status(row.get("status"))
    resolution = out.get("resolution")
    if isinstance(resolution, dict) and isinstance(resolution.get("review"), dict):
        review = dict(resolution["review"])
        review["status"] = finding_status(review.get("status"))
        out["resolution"] = {**resolution, "review": review}
    return out


# The ten numbered folders of the 0.1 layout; any one of them directly under research_lab/ makes the
# lab old (the criterion of init's detect_old_layout). A numbered folder of the researcher's own does not.
OLD_NUMBERED_FOLDERS = (  # legacy
    "00_project_knowledge", "01_reference_registry", "02_findings_ledger", "03_experiments",  # legacy
    "04_reviews", "05_access_requests", "06_decisions", "07_project_management",  # legacy
    "08_decision_log", "09_skill_vetting",  # legacy
)


def is_old_layout(lab: Path) -> bool:
    """True when the lab has the 0.1 layout: any of the ten numbered folders exists under it, or the
    old artifact folder exists and artifacts/archive/ does not."""
    if (lab / "artifacts" / "store").is_dir() and not (lab / "artifacts" / "archive").is_dir():  # legacy
        return True
    return any((lab / name).is_dir() for name in OLD_NUMBERED_FOLDERS)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_lab(start: Path) -> Path:
    """Walk up from `start` to the first research_lab/ directory (or the start inside one)."""
    start = Path(start).resolve()
    for d in [start, *start.parents]:
        if d.name == "research_lab" and d.is_dir():
            return d
        if (d / "research_lab").is_dir():
            return (d / "research_lab").resolve()
    raise LabNotFound(f"no research_lab/ at or above {start}")


def _merge(base: dict, over: dict) -> dict:
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value
    return base


class LabStore:
    def __init__(self, lab: Path) -> None:
        self.lab = Path(lab).resolve()
        self.project_root = self.lab.parent
        if is_old_layout(self.lab):
            raise OldLayout(OLD_LAYOUT_MESSAGE)
        self.root = self.lab / "artifacts"
        self.archive = self.root / "archive"
        self.config = copy.deepcopy(DEFAULT_CONFIG)
        lab_json = self.lab / "lab.json"
        if lab_json.is_file():
            try:
                loaded = json.loads(lab_json.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise StoreError(f"cannot read {lab_json}: {exc}") from exc
            if not isinstance(loaded, dict):
                raise StoreError(f"cannot read {lab_json}: top level must be an object")
            _merge(self.config, loaded)
        self.threshold_bytes = self._megabytes(lab_json, "thresholdMB")
        self.budget_warn_bytes = self._megabytes(lab_json, "budgetWarnMB")

    def _megabytes(self, lab_json: Path, key: str) -> int:
        lfs = self.config.get("lfs")
        value = lfs.get(key) if isinstance(lfs, dict) else None
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise StoreError(f"invalid lfs.{key} in {lab_json}: {value!r}")
        return int(value * 1024 * 1024)

    def _table_path(self, table: str) -> Path:
        if table not in TABLES:
            raise StoreError(f"unknown table: {table}")
        return self.root / f"{table}.jsonl"

    def rows(self, table: str) -> list[dict]:
        path = self._table_path(table)
        if not path.is_file():
            return []
        out: list[dict] = []
        for n, line in self._numbered_lines(path):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise StoreError(f"{path.name} line {n}: {exc.msg}") from exc
            if not isinstance(row, dict) or not all(key in row for key in REQUIRED_KEYS[table]):
                raise StoreError(f"{path.name} line {n}: not a {table} row")
            out.append(row)
        return out

    @staticmethod
    def _numbered_lines(path: Path) -> list[tuple[int, str]]:
        """(line number, text) of each non-empty table line. Only a line feed separates lines:
        str.splitlines would also split on U+2028, U+0085 and friends, which
        json.dumps(ensure_ascii=False) leaves raw inside strings."""
        text = path.read_text(encoding="utf-8")
        found: list[tuple[int, str]] = []
        for n, line in enumerate(text.split("\n"), start=1):
            line = line[:-1] if line.endswith("\r") else line
            if line.strip():
                found.append((n, line))
        return found

    def _write_lines(self, path: Path, lines: list[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("".join(line + "\n" for line in lines))
        os.replace(tmp, path)

    def append(self, table: str, row: dict) -> None:
        path = self._table_path(table)
        lines: list[str] = []
        if path.is_file():
            lines = [line for _, line in self._numbered_lines(path)]
        lines.append(json.dumps(row, ensure_ascii=False))
        self._write_lines(path, lines)

    def rewrite(self, table: str, rows: list[dict]) -> None:
        path = self._table_path(table)
        self._write_lines(path, [json.dumps(r, ensure_ascii=False) for r in rows])

    # ---- lookups -------------------------------------------------------

    def _copy_path(self, row: dict) -> Path:
        """Where a copy's bytes live. A migrated row may still name the old folder; it is read from the archive."""
        rel = row["storage_path"]
        if rel.startswith(OLD_STORE_PREFIX):
            rel = ARCHIVE_PREFIX + rel[len(OLD_STORE_PREFIX):]
        return self.lab / rel

    def _artifact(self, aid: str) -> dict:
        for row in self.rows("artifacts"):
            if row["id"] == aid:
                return row
        raise UnknownId(f"unknown artifact {aid}")

    def _versions_of(self, aid: str) -> list[dict]:
        return [v for v in self.rows("versions") if v["artifact_id"] == aid]

    def _latest_version(self, aid: str) -> dict:
        versions = self._versions_of(aid)
        if not versions:
            raise StoreError(f"artifact {aid} has no versions")
        latest_id = self._artifact(aid).get("latest_version_id")
        for v in versions:
            if v["id"] == latest_id:
                return v
        return max(versions, key=lambda v: v["version_number"])

    def _version_row(self, ref: str) -> dict:
        """The version row a reference names; an artifact reference means its latest version."""
        kind, rid = self.resolve_id(ref)
        if kind == "artifact":
            return self._latest_version(rid)
        for v in self.rows("versions"):
            if v["id"] == rid:
                return v
        raise UnknownId(f"unknown id {ref}")

    def resolve_id(self, ref: str) -> tuple[str, str]:
        """Resolve a full id, `art_<id>`, or a unique prefix to ("artifact"|"version", id)."""
        if ref.startswith("art_"):
            key = ref[4:]
            candidates = [("artifact", r["id"]) for r in self.rows("artifacts")]
        else:
            key = ref
            candidates = [("artifact", r["id"]) for r in self.rows("artifacts")]
            candidates += [("version", r["id"]) for r in self.rows("versions")]
        for kind, rid in candidates:
            if rid == key:
                return kind, rid
        if len(key) < 6:
            raise UnknownId(f"unknown id {ref} (an id prefix needs at least 6 characters)")
        matches = [(kind, rid) for kind, rid in candidates if rid.startswith(key)]
        if len(matches) == 1:
            return matches[0]
        if matches:
            raise AmbiguousId(f"ambiguous id {ref}: matches " + ", ".join(rid for _, rid in matches[:5]))
        raise UnknownId(f"unknown id {ref}")

    # ---- save ----------------------------------------------------------

    @property
    def _attributes_path(self) -> Path:
        return self.root / ".gitattributes"

    def _write_attributes(self, lines: list[str]) -> None:
        self._write_lines(self._attributes_path, lines)

    def ensure_gitattributes(self) -> bool:
        """Make sure the archive's .gitattributes carries the two byte-exact rules.

        A missing file is created with the header. An existing file keeps its own lines, in order;
        whichever of the two rules is missing is appended. True when the file was written."""
        if not self._attributes_path.exists():
            self._write_attributes(list(GITATTRIBUTES_HEADER))
            return True
        lines = self._attribute_lines()
        present = {line.strip() for line in lines}
        missing = [rule for rule in GITATTRIBUTES_HEADER[1:] if rule not in present]
        if not missing:
            return False
        self._write_attributes(lines + missing)
        return True

    def _remove_lfs_line(self, stored: Path) -> bool:
        """Drop the LFS line of a stored copy that is going away; True when the file changed."""
        if not self._attributes_path.is_file():
            return False
        pattern = self._lfs_pattern(stored)
        lines = self._attribute_lines()
        kept = [l for l in lines if self._lfs_line_pattern(l) != pattern]
        if len(kept) == len(lines):
            return False
        self._write_attributes(kept)
        return True

    def _lfs_pattern(self, stored: Path) -> str:
        """The .gitattributes pattern for a stored copy: its exact path, or a wildcard for awkward names."""
        rel = stored.relative_to(self.root).as_posix()
        prefix, _, name = stored.name.partition("_")
        if any(c.isspace() or c in '"*?[]\\' for c in name):
            return f"{PurePosixPath(rel).parent.as_posix()}/{prefix}_*"
        return rel

    def _lfs_line(self, stored: Path) -> str:
        return f"{self._lfs_pattern(stored)} {LFS_ATTRIBUTES}"

    def _attribute_lines(self) -> list[str]:
        if not self._attributes_path.is_file():
            return []
        text = self._attributes_path.read_text(encoding="utf-8")
        lines = [line[:-1] if line.endswith("\r") else line for line in text.split("\n")]
        if lines and lines[-1] == "":
            lines.pop()
        return lines

    @staticmethod
    def _lfs_line_pattern(line: str) -> str | None:
        """The pattern of an LFS line (all four LFS attributes, in any order), else None."""
        tokens = line.split()
        if len(tokens) < 2 or tokens[0].startswith("#"):
            return None
        return tokens[0] if _LFS_ATTRIBUTE_SET <= set(tokens[1:]) else None

    def _lfs_patterns(self) -> list[str]:
        found = (self._lfs_line_pattern(line) for line in self._attribute_lines())
        return [pattern for pattern in found if pattern is not None]

    def _lfs_covered(self, stored: Path, patterns: set[str]) -> bool:
        """True when an LFS line names the stored copy itself or folds its whole artifact."""
        return self._lfs_pattern(stored) in patterns or f"archive/{stored.parent.name}/**" in patterns

    def lfs_line_if_needed(self, stored: Path) -> bool:
        """Append the LFS line for `stored` when it is at or above the threshold; True when tracked."""
        if stored.stat().st_size < self.threshold_bytes:
            return False
        if self._lfs_covered(stored, set(self._lfs_patterns())):
            return True
        if self._attributes_path.is_file():
            lines = self._attribute_lines()
        else:
            lines = list(GITATTRIBUTES_HEADER)
        lines.append(self._lfs_line(stored))
        self._write_attributes(lines)
        return True

    def _lfs_versions(self) -> list[dict]:
        return [v for v in self.rows("versions") if v["kind"] == "copy" and v["status"] == "ok"]

    def lfs_total(self) -> int:
        present = set(self._lfs_patterns())
        return sum(
            v["size_bytes"]
            for v in self._lfs_versions()
            if self._lfs_covered(self._copy_path(v), present)
        )

    def lfs_filter_configured(self) -> bool | None:
        """None outside a git work tree; else whether the git-lfs clean filter is configured."""
        try:
            inside = self._git(["rev-parse", "--is-inside-work-tree"], self.project_root)
            if inside.stdout.strip() != "true":
                return None
            clean = self._git(["config", "--get", "filter.lfs.clean"], self.project_root)
        except OSError:
            return None
        return bool(clean.stdout.strip())

    def lfs_install_hint(self) -> str:
        """What to run when the LFS filter is not configured: `git lfs install`, after installing git-lfs
        itself when `git lfs version` fails."""
        try:
            installed = self._git(["lfs", "version"], self.project_root).returncode == 0
        except OSError:
            installed = False
        return "run: git lfs install" if installed else "install git-lfs, then run: git lfs install"

    def lfs_check(self) -> dict:
        present = set(self._lfs_patterns())
        missing = [
            self._copy_path(v).relative_to(self.root).as_posix()
            for v in self._lfs_versions()
            if v["size_bytes"] >= self.threshold_bytes
            and not self._lfs_covered(self._copy_path(v), present)
        ]
        total = self.lfs_total()
        line_count = len(self._lfs_patterns())
        suggestion = None
        if line_count >= 1000:
            suggestion = (
                f"{line_count} LFS lines: fold each artifact's lines into one pattern, "
                f"archive/<aid>/** {LFS_ATTRIBUTES}"
            )
        return {
            "missing_lines": missing,
            "total_bytes": total,
            "budget_bytes": self.budget_warn_bytes,
            "over_budget": total > self.budget_warn_bytes,
            "lfs_filter_configured": self.lfs_filter_configured(),
            "line_count": line_count,
            "suggestion": suggestion,
        }

    def _git(self, args: list[str], cwd: Path) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)

    def _stage(self, paths: list[Path]) -> None:
        try:
            self._stage_paths(paths)
        except OSError:
            print("warning: git not found; nothing staged", file=sys.stderr)

    def _stage_paths(self, paths: list[Path]) -> None:
        inside = self._git(["rev-parse", "--is-inside-work-tree"], self.lab)
        if inside.stdout.strip() != "true":
            return
        keep: list[str] = []
        for p in paths:
            rel = p.resolve().relative_to(self.project_root).as_posix()
            if p.exists() or self._git(["ls-files", "--", rel], self.project_root).stdout.strip():
                keep.append(rel)
        if not keep:
            return
        added = self._git(["add", "-A", "--", *keep], self.project_root)
        if added.returncode != 0:
            first = (added.stderr.splitlines() or [""])[0]
            print(f"warning: git add failed: {first}", file=sys.stderr)

    def _archive_leaf(self, art: dict) -> str:
        """The file-name part of an artifact's stored copies, checked against the table row:
        the id must be a plain token and the copy must land inside the archive."""
        aid = art["id"]
        leaf = re.split(r"[\\/]", str(art["filename"]))[-1]
        problem = (
            not isinstance(aid, str)
            or not re.fullmatch(r"[A-Za-z0-9_-]+", aid)
            or leaf in ("", ".", "..")
        )
        if not problem:
            stored = (self.archive / aid / f"v001_{leaf}").resolve()
            problem = not stored.is_relative_to(self.archive.resolve())
        if problem:
            raise StoreError(f"table row {aid} names a path outside the archive")
        return leaf

    def _version_of_target(self, ref: str) -> dict:
        """The artifact row `--version-of` names: an id, or the project-relative path of a saved file."""
        try:
            kind, rid = self.resolve_id(ref)
        except UnknownId:
            link_ids = {v["artifact_id"] for v in self.rows("versions") if v["kind"] == "link"}
            named = [a for a in self.rows("artifacts") if a["filename"] == ref and a["id"] not in link_ids]
            if len(named) != 1:
                raise
            return named[0]
        return self._artifact(rid if kind == "artifact" else self._version_row(ref)["artifact_id"])

    def _refuse_secret(self, p: Path, *, force: bool) -> None:
        """Refuse a file that looks like a secret or that git ignores, unless `force`."""
        if force:
            return
        rel = p.relative_to(self.project_root).as_posix()
        parts = rel.lower().split("/")
        suspicious = any(part in SECRET_FOLDERS for part in parts[:-1]) or any(
            fnmatch.fnmatchcase(parts[-1], pattern) for pattern in SECRET_NAME_PATTERNS
        )
        if not suspicious:
            try:
                suspicious = self._git(["check-ignore", "-q", "--", rel], self.project_root).returncode == 0
            except OSError:
                suspicious = False
        if suspicious:
            raise StoreError(f"{rel} looks like a secret or ignored file; use --force to save it anyway")

    def _project_file(self, f) -> Path:
        """Resolve `f` (relative paths against the project root) to a regular file inside the project."""
        p = Path(f)
        if not p.is_absolute():
            p = self.project_root / p
        p = p.resolve()
        if not p.is_file():
            raise StoreError(f"not a file: {p}")
        try:
            p.relative_to(self.project_root)
        except ValueError:
            raise StoreError(f"outside the project root: {p}") from None
        return p

    def _classify_inputs(self, inputs: list[str], *, force: bool = False) -> list[tuple[str, object]]:
        """Step 1 over inputs: ("version", id) for a known id, ("path", Path) for a file to link.

        Writes nothing; every entry that cannot be used raises here, before anything is saved."""
        classified: list[tuple[str, object]] = []
        for entry in inputs:
            try:
                classified.append(("version", self._version_row(entry)["id"]))
                continue
            except UnknownId:
                pass
            p = Path(entry)
            if not p.is_absolute():
                p = self.project_root / p
            p = p.resolve()
            if p.is_file():
                try:
                    p.relative_to(self.project_root)
                except ValueError:
                    raise StoreError(f"outside the project root: {p}") from None
                self._refuse_secret(p, force=force)
                classified.append(("path", p))
            elif p.exists():
                raise StoreError(f"not a file: {p}")
            elif "," in entry:
                raise StoreError(f"unknown input: {entry}; separate inputs with spaces, not commas")
            else:
                raise StoreError(f"unknown input: {entry}")
        return classified

    def _link_pending(
        self, classified: list[tuple[str, object]], *, role: str, task: str, session: str | None,
        force: bool = False,
    ) -> list[str]:
        """Step 2: link the path inputs; return distinct dependency version ids, first-seen order."""
        dep_ids: list[str] = []
        for kind, value in classified:
            if kind == "version":
                dep = value
            else:
                dep = self.link(
                    [value], role=role, task=task, session=session, stage=False, force=force
                )[0]["version_id"]
            if dep not in dep_ids:
                dep_ids.append(dep)
        return dep_ids

    def _filenames_of(self, version_ids: list[str]) -> dict[str, str]:
        version_artifact = {v["id"]: v["artifact_id"] for v in self.rows("versions")}
        filenames = {a["id"]: a["filename"] for a in self.rows("artifacts")}
        names: dict[str, str] = {}
        for d in version_ids:
            name = filenames.get(version_artifact.get(d))
            if name is None:
                raise StoreError(f"version {d} has no artifact row")
            names[d] = name
        return names

    # ---- link ----------------------------------------------------------

    @staticmethod
    def _task_of(task: str | None, command: str | None) -> str:
        """The producing task; the older keyword is accepted for the same value."""
        value = task if task is not None else command
        if value is None or not str(value).strip():
            raise StoreError("a save needs the task that produced it (--task)")
        return value

    def link(
        self,
        paths: list,
        *,
        role: str,
        task: str | None = None,
        command: str | None = None,
        session: str | None = None,
        inputs: list[str] | None = None,
        description: str | None = None,
        stage: bool = True,
        force: bool = False,
    ) -> list[dict]:
        """Record files that already live in the project without copying them."""
        task = self._task_of(task, command)
        files = [self._project_file(f) for f in paths]
        for p in files:
            self._refuse_secret(p, force=force)
        classified = self._classify_inputs(inputs or [], force=force)
        self._filenames_of([v for k, v in classified if k == "version"])
        dep_ids = self._link_pending(classified, role=role, task=task, session=session, force=force)
        wrote: set[str] = set()
        results: list[dict] = []
        for p in files:
            filename = p.relative_to(self.project_root).as_posix()
            sha = sha256_file(p)
            versions = self.rows("versions")
            link_ids = {v["artifact_id"] for v in versions if v["kind"] == "link"}
            art = next((a for a in self.rows("artifacts") if a["filename"] == filename and a["id"] in link_ids), None)
            latest = self._latest_version(art["id"]) if art is not None else None
            if latest is not None and latest["sha256"] == sha:
                results.append({
                    "artifact_id": art["id"],
                    "version_id": latest["id"],
                    "version_number": latest["version_number"],
                    "storage_path": latest["storage_path"],
                    "lfs": False,
                    "reused": True,
                })
                continue
            created = now_iso()
            vid = str(uuid.uuid4())
            if art is None:
                aid, number, parent = str(uuid.uuid4()), 1, None
            else:
                aid, number, parent = art["id"], latest["version_number"] + 1, latest["id"]
                for old in versions:
                    if old["artifact_id"] == aid and old["status"] == "ok":
                        old["status"] = "changed"
            storage = f"link:{filename}"
            versions.append({
                "id": vid,
                "artifact_id": aid,
                "version_number": number,
                "parent_version_id": parent,
                "kind": "link",
                "content_type": _MIME.guess_type(p.name)[0] or "application/octet-stream",
                "size_bytes": p.stat().st_size,
                "sha256": sha,
                "storage_path": storage,
                "agent_name": role,
                "producing_command": task,
                "producing_session": session,
                "code_description": description,
                "is_intermediate": False,
                "is_checkpoint": False,
                "destination": "milestone",
                "environment": None,
                "created_at": created,
                "source": "lab",
                "status": "ok",
            })
            if art is None:
                self.append("artifacts", {
                    "id": aid,
                    "filename": filename,
                    "latest_version_id": vid,
                    "folder": None,
                    "is_user_upload": False,
                    "is_ephemeral": False,
                    "superseded_by": None,
                    "retention": None,
                    "destination": "milestone",
                    "created_at": created,
                    "source": "lab",
                })
            self.rewrite("versions", versions)
            if art is not None:
                current = self.rows("artifacts")
                for a in current:
                    if a["id"] == aid:
                        a["latest_version_id"] = vid
                self.rewrite("artifacts", current)
            wrote.update(("artifacts", "versions"))
            if dep_ids:
                names = self._filenames_of(dep_ids)
                for dep in dep_ids:
                    self.append("dependencies", {
                        "version_id": vid,
                        "depends_on_version_id": dep,
                        "reference_name": names[dep],
                    })
                wrote.add("dependencies")
            results.append({
                "artifact_id": aid,
                "version_id": vid,
                "version_number": number,
                "storage_path": storage,
                "lfs": False,
                "reused": False,
            })
        if stage and wrote:
            self._stage([self._table_path(n) for n in TABLES if n in wrote])
        return results

    # ---- search --------------------------------------------------------

    def search(self, text: str, *, include_intermediate: bool = False) -> list[dict]:
        needle = text.lower()
        versions = self.rows("versions")
        position = {v["id"]: i for i, v in enumerate(versions)}
        by_artifact: dict[str, list[dict]] = {}
        for v in versions:
            by_artifact.setdefault(v["artifact_id"], []).append(v)
        found: list[tuple[int, dict]] = []
        for a in self.rows("artifacts"):
            mine = by_artifact.get(a["id"])
            if not mine:
                continue
            latest = next((v for v in mine if v["id"] == a.get("latest_version_id")), None)
            if latest is None:
                latest = max(mine, key=lambda v: v["version_number"])
            if latest["is_intermediate"] and not include_intermediate:
                continue
            if needle not in a["filename"].lower() and needle not in (latest["code_description"] or "").lower():
                continue
            found.append((position[latest["id"]], {
                "artifact_id": a["id"],
                "filename": a["filename"],
                "latest_version_id": latest["id"],
                "version_number": latest["version_number"],
                "kind": latest["kind"],
                "content_type": latest["content_type"],
                "size_bytes": latest["size_bytes"],
                "code_description": latest["code_description"],
                "created_at": latest["created_at"],
                "status": latest["status"],
            }))
        found.sort(key=lambda item: item[0], reverse=True)
        return [row for _, row in found]

    # ---- path ----------------------------------------------------------

    def _version_path(self, row: dict) -> Path | None:
        """Where a version's bytes should be. A copy must lie inside the archive and a relative link
        inside the project; a table row that names anything else raises StoreError."""
        if row["kind"] == "copy":
            p = self._copy_path(row)
            if not p.resolve().is_relative_to(self.archive.resolve()):
                raise StoreError(f"version {row['id']} names a path outside the archive")
            return p
        if row["kind"] == "link":
            rest = row["storage_path"]
            if rest.startswith("link:"):
                rest = rest[len("link:"):]
            if rest == "~" or rest.startswith(("~/", "~\\")):
                rest = str(Path.home() / rest[2:])
            if PureWindowsPath(rest).is_absolute() or PurePosixPath(rest).is_absolute():
                return Path(rest)
            p = self.project_root / rest
            if not p.resolve().is_relative_to(self.project_root.resolve()):
                raise StoreError(f"version {row['id']} names a path outside the project")
            return p
        return None

    def _set_status(self, version_id: str, status: str) -> None:
        rows = self.rows("versions")
        for v in rows:
            if v["id"] == version_id:
                v["status"] = status
        self.rewrite("versions", rows)

    @staticmethod
    def _is_lfs_pointer(p: Path, row: dict) -> bool:
        """A pointer is smaller or larger than the recorded size and starts with the LFS spec line."""
        if not p.is_file() or p.stat().st_size == row["size_bytes"]:
            return False
        with open(p, "rb") as fh:
            return fh.read(len(LFS_POINTER_PREFIX)) == LFS_POINTER_PREFIX

    def locate(self, ref: str, *, stage: bool = True) -> dict:
        """Where a version's bytes are: {"version_id", "path", "status"} with status ok, missing or pointer."""
        row = self._version_row(ref)
        vid = row["id"]
        if row["status"] == "replaced":
            raise StoreError(f"replaced: version {vid} was superseded by a working save; its copy is gone")
        try:
            p = self._version_path(row)
        except StoreError:
            if row["kind"] != "link":
                raise
            return {"version_id": vid, "path": row["storage_path"].removeprefix("link:"), "status": "outside-project"}
        if p is None:
            raise StoreError(f"version {vid} has unknown kind {row['kind']!r}")
        if row["kind"] == "link" and not p.resolve().is_relative_to(self.project_root.resolve()) and not p.is_file():
            return {"version_id": vid, "path": p.as_posix(), "status": "outside-project"}
        new_status: str | None = None
        if p.exists():
            result = "pointer" if self._is_lfs_pointer(p, row) else "ok"
            if row["status"] == "missing":
                new_status = "ok"
        else:
            result = "missing"
            if row["status"] != "missing":
                new_status = "missing"
        if new_status is not None:
            self._set_status(vid, new_status)
            if stage:
                self._stage([self._table_path("versions")])
        return {"version_id": vid, "path": p.as_posix(), "status": result}

    def path(self, ref: str, *, stage: bool = True) -> Path:
        found = self.locate(ref, stage=stage)
        vid, shown = found["version_id"], found["path"]
        if found["status"] == "outside-project":
            raise StoreError(f"outside-project: {shown} is not inside the project (version {vid}); not followed")
        if found["status"] == "missing":
            raise MissingFile(f"missing: {shown} (version {vid})", vid, shown)
        if found["status"] == "pointer":
            raise LfsPointer(
                f"pointer: {shown} is a Git LFS pointer, not the file (version {vid}); run: git lfs pull",
                vid,
                shown,
            )
        return Path(shown)

    # ---- provenance and graph ------------------------------------------

    def provenance(self, ref: str) -> dict:
        version = self._version_row(ref)
        artifact = self._artifact(version["artifact_id"])
        by_id = {v["id"]: v for v in self.rows("versions")}
        names = {a["id"]: a["filename"] for a in self.rows("artifacts")}
        inputs: list[dict] = []
        for dep in self.rows("dependencies"):
            if dep["version_id"] != version["id"]:
                continue
            row = by_id.get(dep["depends_on_version_id"])
            try:
                p = self._version_path(row) if row is not None else None
            except StoreError:
                p = None
            inputs.append({
                "version_id": dep["depends_on_version_id"],
                "filename": names.get(row["artifact_id"]) if row is not None else None,
                "path": p.as_posix() if p is not None else None,
                "exists": p is not None and p.exists(),
            })
        findings = [
            report_finding(c) for c in self.rows("verification_checks") if c.get("version_id") == version["id"]
        ]
        return {"version": version, "artifact": artifact, "inputs": inputs, "findings": findings}

    lineage = provenance  # the 0.1 name

    def graph(self, ref: str) -> dict:
        root = self._version_row(ref)["id"]
        by_id = {v["id"]: v for v in self.rows("versions")}
        names = {a["id"]: a["filename"] for a in self.rows("artifacts")}
        edges_from: dict[str, list[dict]] = {}
        for dep in self.rows("dependencies"):
            edges_from.setdefault(dep["version_id"], []).append(dep)
        nodes: list[dict] = []
        edges: list[dict] = []
        seen = {root}
        queue = [root]
        while queue:
            vid = queue.pop(0)
            row = by_id.get(vid)
            nodes.append({
                "version_id": vid,
                "artifact_id": row["artifact_id"] if row else None,
                "filename": names.get(row["artifact_id"]) if row else None,
                "version_number": row["version_number"] if row else None,
            })
            for dep in edges_from.get(vid, []):
                to = dep["depends_on_version_id"]
                edges.append({"from": vid, "to": to, "reference_name": dep["reference_name"]})
                if to not in seen:
                    seen.add(to)
                    queue.append(to)
        return {"root": root, "nodes": nodes, "edges": edges}

    # ---- reviewer findings ---------------------------------------------

    def finding_add(
        self,
        ref: str,
        *,
        claim: str,
        verdict: str,
        reviewer_role: str,
        severity: str | None = None,
        evidence: str | None = None,
        rebuttal: str | None = None,
        stage: bool = True,
    ) -> dict:
        """Attach a reviewer finding to a version (an artifact reference means its latest version)."""
        if verdict not in FINDING_VERDICTS:
            raise StoreError(f"invalid verdict: {verdict} ({', '.join(FINDING_VERDICTS)})")
        if not claim or not claim.strip():
            raise StoreError("a reviewer finding needs a claim")
        if not reviewer_role or not reviewer_role.strip():
            raise StoreError("a reviewer finding needs a reviewer role")
        version = self._version_row(ref)
        row = {
            "id": str(uuid.uuid4()),
            "version_id": version["id"],
            "claim": claim,
            "verdict": verdict,
            "severity": severity,
            "evidence": evidence,
            "rebuttal": rebuttal,
            "reviewer_role": reviewer_role,
            "status": "open",
            "resolution": None,
            "created_at": now_iso(),
            "source_ref": None,
        }
        self.append("verification_checks", row)
        if stage:
            self._stage([self._table_path("verification_checks")])
        return row

    check_add = finding_add  # the 0.1 name

    def _finding(self, finding_id: str) -> dict:
        """The reviewer-finding row for a full id or a unique prefix of at least 6 characters."""
        rows = self.rows("verification_checks")
        for row in rows:
            if row["id"] == finding_id:
                return row
        if len(finding_id) < 6:
            raise UnknownId(
                f"unknown reviewer finding {finding_id} (a finding id prefix needs at least 6 characters)"
            )
        matches = [r for r in rows if r["id"].startswith(finding_id)]
        if len(matches) == 1:
            return matches[0]
        if matches:
            raise AmbiguousId(
                f"ambiguous finding id {finding_id}: matches " + ", ".join(r["id"] for r in matches[:5])
            )
        raise UnknownId(f"unknown reviewer finding {finding_id}")

    def _update_finding(self, finding_id: str, changes: dict, *, stage: bool) -> dict:
        rows = self.rows("verification_checks")
        updated: dict | None = None
        for row in rows:
            if row["id"] == finding_id:
                row.update(changes)
                updated = row
        if updated is None:
            raise UnknownId(f"unknown reviewer finding {finding_id}")
        self.rewrite("verification_checks", rows)
        if stage:
            self._stage([self._table_path("verification_checks")])
        return report_finding(updated)

    def respond(self, finding_id: str, note: str, *, stage: bool = True) -> dict:
        """The author responds to a reviewer finding: open or re-opened becomes author-responded."""
        finding = self._finding(finding_id)
        current = finding_status(finding["status"])
        if current not in ("open", "re-opened"):
            raise StoreError(
                f"reviewer finding {finding['id']} is {current}; only open or re-opened findings can receive a response"
            )
        if not note or not note.strip():
            raise StoreError("respond needs a note saying what was changed")
        resolution = {"note": note, "at": now_iso()}
        previous = finding.get("resolution")
        if isinstance(previous, dict) and "review" in previous:
            resolution["review"] = previous["review"]
        elif isinstance(previous, str) and previous.strip():
            resolution["earlier_note"] = previous
        return self._update_finding(
            finding["id"], {"status": "author-responded", "resolution": resolution}, stage=stage
        )

    mark_addressed = respond  # the 0.1 name

    def finding_review(
        self,
        finding_id: str,
        *,
        status: str,
        reviewer_role: str,
        note: str | None = None,
        stage: bool = True,
    ) -> dict:
        """A reviewer closes a finding (closed) or re-opens it (re-opened)."""
        status = finding_status(status)
        if status not in REVIEW_STATUSES:
            raise StoreError(f"invalid review status: {status} (closed or re-opened)")
        finding = self._finding(finding_id)
        if finding_status(finding["status"]) == "closed":
            raise StoreError(f"reviewer finding {finding['id']} is already closed")
        if not reviewer_role or not reviewer_role.strip():
            raise StoreError("a review needs a reviewer role")
        previous = finding.get("resolution")
        if isinstance(previous, dict):
            resolution = dict(previous)
        elif isinstance(previous, str) and previous.strip():
            resolution = {"note": previous}
        else:
            resolution = {}
        resolution["review"] = {"status": status, "by": reviewer_role, "note": note, "at": now_iso()}
        return self._update_finding(finding["id"], {"status": status, "resolution": resolution}, stage=stage)

    check_review = finding_review  # the 0.1 name

    def _findings_for(self, ref: str | None) -> list[dict]:
        rows = self.rows("verification_checks")
        if ref is None:
            return rows
        kind, rid = self.resolve_id(ref)
        if kind == "artifact":
            wanted = {v["id"] for v in self._versions_of(rid)}
        else:
            wanted = {rid}
        return [c for c in rows if c["version_id"] in wanted]

    def findings(self, ref: str | None = None) -> list[dict]:
        """Every reviewer finding, narrowed to a version or to every version of an artifact."""
        return [report_finding(c) for c in self._findings_for(ref)]

    checks = findings  # the 0.1 name

    def outstanding(self, ref: str | None = None) -> list[dict]:
        """Open or re-opened findings with a warning or failing verdict, in table order."""
        return [
            report_finding(c) for c in self._findings_for(ref)
            if finding_status(c["status"]) in ("open", "re-opened") and c["verdict"] in OUTSTANDING_VERDICTS
        ]

    def save(
        self,
        files: list,
        *,
        role: str,
        task: str | None = None,
        command: str | None = None,
        session: str | None = None,
        version_of: str | None = None,
        inputs: list[str] | None = None,
        checkpoint: bool = False,
        intermediate: bool = False,
        destination: str | None = None,
        description: str | None = None,
        environment: str | None = None,
        stage: bool = True,
        force: bool = False,
    ) -> list[dict]:
        # Validate everything first; a failing call writes nothing.
        task = self._task_of(task, command)
        if destination is not None:
            destination = destination_word(destination)
            if destination not in DESTINATIONS:
                raise StoreError(f"invalid destination: {destination} (milestone or working)")
        paths = [self._project_file(f) for f in files]
        for p in paths:
            self._refuse_secret(p, force=force)

        target: dict | None = None
        if version_of is not None:
            if len(paths) != 1:
                raise StoreError("--version-of takes exactly one file")
            target = self._version_of_target(version_of)
            self._archive_leaf(target)
            if any(v["kind"] == "link" for v in self._versions_of(target["id"])):
                raise StoreError(f"{target['filename']} is a linked file; record a new state with link, not save")

        link_ids = {v["artifact_id"] for v in self.rows("versions") if v["kind"] == "link"}
        by_name = {a["filename"]: a for a in self.rows("artifacts") if a["id"] not in link_ids}
        # (path, artifact, latest version, destination, version rows this save replaces)
        plan: list[tuple[Path, dict | None, dict | None, str, list[dict]]] = []
        seen: set[str] = set()
        archive_root = self.archive.resolve()
        for p in paths:
            sha = sha256_file(p)
            if target is not None:
                latest = self._latest_version(target["id"])
                if latest["sha256"] == sha:
                    raise StoreError(
                        f"identical to latest version of {target['filename']} ({latest['id']}); nothing saved"
                    )
                dest = destination or destination_word(target.get("destination", "milestone"))
                replaced: list[dict] = []
                if dest == "working":
                    replaced = [
                        v for v in self._versions_of(target["id"])
                        if v["kind"] == "copy" and v["status"] == "ok"
                        and destination_word(v.get("destination", "milestone")) == "working"
                    ]
                    for old in replaced:
                        old_path = self._copy_path(old)
                        if not old_path.resolve().is_relative_to(archive_root):
                            raise StoreError(f"refusing to delete {old_path}: outside the archive")
                plan.append((p, target, latest, dest, replaced))
                continue
            rel = p.relative_to(self.project_root).as_posix()
            existing = by_name.get(rel)
            if existing is not None:
                raise StoreError(
                    f"artifact {rel} exists ({existing['id']}); use --version-of {existing['id']} "
                    "for a new state of the same file"
                )
            if rel in seen:
                raise StoreError(f"{rel} is named twice in this call")
            seen.add(rel)
            plan.append((p, None, None, destination or "milestone", []))

        classified = self._classify_inputs(inputs or [], force=force)
        self._filenames_of([v for k, v in classified if k == "version"])

        # Everything checks out: link the path inputs, then write.
        dep_ids = self._link_pending(classified, role=role, task=task, session=session, force=force)
        dep_names = self._filenames_of(dep_ids) if dep_ids else {}
        written: list[Path] = []
        results: list[dict] = []
        attributes_touched = self.ensure_gitattributes()
        for p, art, latest, dest, replaced in plan:
            created = now_iso()
            new_artifact = art is None
            if new_artifact:
                aid = str(uuid.uuid4())
                filename = p.relative_to(self.project_root).as_posix()
                number, parent = 1, None
            else:
                aid, filename = art["id"], art["filename"]
                number, parent = latest["version_number"] + 1, latest["id"]
            vid = str(uuid.uuid4())
            rel_archive = (
                f"{ARCHIVE_PREFIX}{aid}/v{number:03d}_{self._archive_leaf({'id': aid, 'filename': filename})}"
            )
            stored = self.lab / rel_archive
            stored.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, stored)
            written.append(stored)
            lfs = self.lfs_line_if_needed(stored)
            attributes_touched = attributes_touched or lfs

            version = {
                "id": vid,
                "artifact_id": aid,
                "version_number": number,
                "parent_version_id": parent,
                "kind": "copy",
                "content_type": _MIME.guess_type(filename)[0] or "application/octet-stream",
                "size_bytes": stored.stat().st_size,
                "sha256": sha256_file(stored),
                "storage_path": rel_archive,
                "agent_name": role,
                "producing_command": task,
                "producing_session": session,
                "code_description": description,
                "is_intermediate": bool(intermediate),
                "is_checkpoint": bool(checkpoint),
                "destination": dest,
                "environment": environment,
                "created_at": created,
                "source": "lab",
                "status": "ok",
            }
            if new_artifact:
                self.append("artifacts", {
                    "id": aid,
                    "filename": filename,
                    "latest_version_id": vid,
                    "folder": None,
                    "is_user_upload": False,
                    "is_ephemeral": False,
                    "superseded_by": None,
                    "retention": None,
                    "destination": dest,
                    "created_at": created,
                    "source": "lab",
                })
            versions = self.rows("versions")
            replaced_ids = {old["id"] for old in replaced}
            for old in versions:
                if old["id"] in replaced_ids:
                    old["status"] = "replaced"
            versions.append(version)
            self.rewrite("versions", versions)
            if not new_artifact:
                current = self.rows("artifacts")
                for a in current:
                    if a["id"] == aid:
                        a["latest_version_id"] = vid
                self.rewrite("artifacts", current)

            for dep in dep_ids:
                self.append("dependencies", {
                    "version_id": vid,
                    "depends_on_version_id": dep,
                    "reference_name": dep_names[dep],
                })
            results.append({
                "artifact_id": aid,
                "version_id": vid,
                "version_number": number,
                "storage_path": rel_archive,
                "lfs": lfs,
            })

            # The table already says "replaced"; only now do the copies go.
            for old in replaced:
                old_path = self._copy_path(old)
                if self._remove_lfs_line(old_path):
                    attributes_touched = True
                if old_path.exists():
                    old_path.unlink()
                written.append(old_path)

        if stage:
            tables = ["artifacts", "versions"] + (["dependencies"] if dep_ids else [])
            extra = [self._attributes_path] if attributes_touched else []
            self._stage(written + extra + [self._table_path(n) for n in tables])
        tracked = [r["storage_path"] for r in results if r["lfs"]]
        if tracked and self.lfs_filter_configured() is False:
            hint = self.lfs_install_hint()
            for rel in tracked:
                shown = (self.lab / rel).relative_to(self.project_root).as_posix()
                print(
                    f"warning: git-lfs filter not configured; {shown} will be committed as plain bytes; "
                    + hint,
                    file=sys.stderr,
                )
        total = self.lfs_total()
        if total > self.budget_warn_bytes:
            print(
                f"warning: LFS total {total / 1048576:.1f} MB exceeds "
                f"{self.budget_warn_bytes / 1048576:.1f} MB (lfs.budgetWarnMB in lab.json)",
                file=sys.stderr,
            )
        return results

    # ---- marker resolution ---------------------------------------------

    def resolve_markers(self, text: str, *, relative_to: Path) -> str:
        """Replace every {{artifact:REF}} with a Markdown link relative to `relative_to`."""
        base = Path(relative_to).resolve()

        def replace(match: re.Match) -> str:
            row = self._version_row(match.group(1))
            target = self._version_path(row)
            if target is None:
                raise StoreError(f"version {row['id']} has unknown kind {row['kind']!r}")
            name = PurePosixPath(self._artifact(row["artifact_id"])["filename"]).name
            try:
                href = os.path.relpath(target, base).replace(os.sep, "/")
            except ValueError:
                href = target.as_posix()
            if any(c in href for c in (" ", "(", ")")):
                href = f"<{href}>"
            if match.string[max(0, match.start() - 2):match.start()] == "](":
                return href
            return f"[{name}]({href})"

        return MARKER_RE.sub(replace, text)


COMMANDS: dict[str, Callable] = {}


def _dispatch(store: LabStore, args: argparse.Namespace) -> int:
    return COMMANDS[args.subcommand](store, args)


def _cli_paths(entries: list[str]) -> list[str]:
    cwd = Path.cwd()
    return [e if Path(e).is_absolute() else str(cwd / e) for e in entries]


def _cli_inputs(entries: list[str] | None) -> list[str]:
    cwd = Path.cwd()
    out = []
    for entry in entries or []:
        candidate = cwd / entry
        out.append(str(candidate) if candidate.exists() else entry)
    return out


def _print_json(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def _cmd_save(store: LabStore, args: argparse.Namespace) -> int:
    result = store.save(
        _cli_paths(args.files),
        role=args.role,
        task=args.task,
        session=args.session,
        version_of=args.version_of,
        inputs=_cli_inputs(args.inputs),
        checkpoint=args.checkpoint,
        intermediate=args.intermediate,
        destination=args.destination,
        description=args.description,
        environment=args.environment,
        stage=not args.no_stage,
        force=args.force,
    )
    _print_json(result)
    return 0


def _cmd_link(store: LabStore, args: argparse.Namespace) -> int:
    _print_json(store.link(
        _cli_paths(args.paths),
        role=args.role,
        task=args.task,
        session=args.session,
        inputs=_cli_inputs(args.inputs),
        description=args.description,
        stage=not args.no_stage,
        force=args.force,
    ))
    return 0


def _cmd_search(store: LabStore, args: argparse.Namespace) -> int:
    _print_json(store.search(args.text, include_intermediate=args.include_intermediate))
    return 0


def _cmd_path(store: LabStore, args: argparse.Namespace) -> int:
    found = store.locate(args.ref, stage=not args.no_stage)
    _print_json(found)
    if found["status"] == "outside-project":
        print(
            f"error: outside-project: {found['path']} is not inside the project "
            f"(version {found['version_id']}); not followed",
            file=sys.stderr,
        )
        return 1
    if found["status"] == "missing":
        print(f"error: missing: {found['path']} (version {found['version_id']})", file=sys.stderr)
        return 1
    if found["status"] == "pointer":
        print(
            f"error: pointer: {found['path']} is a Git LFS pointer, not the file "
            f"(version {found['version_id']}); run: git lfs pull",
            file=sys.stderr,
        )
        return 1
    return 0


def _cmd_provenance(store: LabStore, args: argparse.Namespace) -> int:
    _print_json(store.provenance(args.ref))
    return 0


def _cmd_graph(store: LabStore, args: argparse.Namespace) -> int:
    _print_json(store.graph(args.ref))
    return 0


COMMANDS["save"] = _cmd_save
COMMANDS["link"] = _cmd_link
COMMANDS["search"] = _cmd_search
COMMANDS["path"] = _cmd_path
COMMANDS["provenance"] = _cmd_provenance
COMMANDS["lineage"] = _cmd_provenance  # legacy
COMMANDS["graph"] = _cmd_graph


def _cmd_lfs_check(store: LabStore, args: argparse.Namespace) -> int:
    report = store.lfs_check()
    _print_json(report)
    unfiltered = report["lfs_filter_configured"] is False and report["line_count"] > 0
    if unfiltered:
        print(
            "warning: git-lfs filter not configured; LFS-tracked files would be committed as plain bytes; "
            + store.lfs_install_hint(),
            file=sys.stderr,
        )
    return 1 if report["missing_lines"] or unfiltered else 0


COMMANDS["lfs-check"] = _cmd_lfs_check


def _cmd_findings(store: LabStore, args: argparse.Namespace) -> int:
    if args.findings_command == "add":
        _print_json(store.finding_add(
            args.version,
            claim=args.claim,
            verdict=args.verdict,
            reviewer_role=args.reviewer,
            severity=args.severity,
            evidence=args.evidence,
            rebuttal=args.rebuttal,
            stage=not args.no_stage,
        ))
    elif args.findings_command == "list":
        _print_json(store.findings(args.ref) if args.all else store.outstanding(args.ref))
    else:
        _print_json(store.finding_review(
            args.finding_id,
            status=args.status,
            reviewer_role=args.reviewer,
            note=args.note,
            stage=not args.no_stage,
        ))
    return 0


def _cmd_respond(store: LabStore, args: argparse.Namespace) -> int:
    _print_json(store.respond(args.finding_id, args.note, stage=not args.no_stage))
    return 0


COMMANDS["findings"] = _cmd_findings
COMMANDS["check"] = _cmd_findings  # legacy
COMMANDS["respond"] = _cmd_respond
COMMANDS["mark-addressed"] = _cmd_respond  # legacy


def _cmd_resolve(store: LabStore, args: argparse.Namespace) -> int:
    path = Path(_cli_paths([args.file])[0])
    if not path.is_file():
        raise StoreError(f"not a file: {path}")
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    resolved = store.resolve_markers(text, relative_to=path.resolve().parent)
    if not args.write:
        sys.stdout.write(resolved)
        return 0
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(resolved)
    os.replace(tmp, path)
    _print_json({"file": path.resolve().as_posix(), "markers": len(MARKER_RE.findall(text))})
    return 0


COMMANDS["resolve"] = _cmd_resolve


INPUTS_HELP = "versions or files this one was made from; put --inputs after the files, or repeat it"
TASK_HELP = "the task id (TASK-NNNN) of the task that produced the file"


def _destination_arg(value: str) -> str:
    word = destination_word(value)
    if word not in DESTINATIONS:
        raise argparse.ArgumentTypeError(f"invalid choice: {value!r} (choose milestone or working)")
    return word


def _review_status_arg(value: str) -> str:
    word = finding_status(value)
    if word not in REVIEW_STATUSES:
        raise argparse.ArgumentTypeError(f"invalid choice: {value!r} (choose closed or re-opened)")
    return word


def _add_task(p: argparse.ArgumentParser) -> None:
    p.add_argument("--task", metavar="TASK_ID", help=TASK_HELP)  # required: checked after parsing, because the hidden alias shares the value
    p.add_argument("--command", dest="task", help=argparse.SUPPRESS)  # legacy


def _add_findings_parser(sub, name: str, hidden: bool) -> None:
    kwargs = {} if hidden else {"help": "reviewer findings attached to versions"}
    findings = sub.add_parser(name, **kwargs)
    findings_sub = findings.add_subparsers(dest="findings_command", required=True, metavar="<findings-subcommand>")

    p = findings_sub.add_parser("add", help="attach a reviewer finding to a version")
    p.add_argument("--version", required=True, metavar="REF")
    p.add_argument("--claim", required=True)
    p.add_argument("--verdict", required=True, choices=FINDING_VERDICTS)
    p.add_argument("--reviewer", required=True)
    p.add_argument("--severity")
    p.add_argument("--evidence")
    p.add_argument("--rebuttal")
    p.add_argument("--no-stage", dest="no_stage", action="store_true")

    p = findings_sub.add_parser("list", help="list outstanding findings (open or re-opened, with a warning or failing verdict)")
    p.add_argument("ref", nargs="?", default=None, metavar="REF")
    p.add_argument("--all", action="store_true", help="list every finding, whatever its status or verdict")

    p = findings_sub.add_parser("review", help="a reviewer closes or re-opens a finding")
    p.add_argument("finding_id", metavar="FINDING_ID")
    p.add_argument("--status", required=True, type=_review_status_arg, metavar="{closed,re-opened}")
    p.add_argument("--reviewer", required=True)
    p.add_argument("--note")
    p.add_argument("--no-stage", dest="no_stage", action="store_true")


def _add_respond_parser(sub, name: str, hidden: bool) -> None:
    kwargs = {} if hidden else {"help": "the author responds to a reviewer finding"}
    p = sub.add_parser(name, **kwargs)
    p.add_argument("finding_id", metavar="FINDING_ID")
    p.add_argument("--note", required=True)
    p.add_argument("--no-stage", dest="no_stage", action="store_true")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="artifacts.py", description="Project-local artifact archive.")
    parser.add_argument("--lab", default=None, help="path to research_lab (default: found from the current directory)")
    sub = parser.add_subparsers(dest="subcommand", required=True, metavar="<subcommand>")

    p = sub.add_parser("save", help="save files as artifact versions")
    p.add_argument("files", nargs="+", metavar="FILES")
    p.add_argument("--role", required=True)
    _add_task(p)
    p.add_argument("--session")
    p.add_argument("--version-of", dest="version_of")
    p.add_argument("--inputs", action="extend", nargs="+", metavar="ID_OR_PATH", help=INPUTS_HELP)
    p.add_argument("--checkpoint", action="store_true")
    p.add_argument("--intermediate", action="store_true")
    p.add_argument("--destination", type=_destination_arg, default=None, metavar="{milestone,working}")
    p.add_argument("--description")
    p.add_argument("--environment")
    p.add_argument("--no-stage", dest="no_stage", action="store_true")
    p.add_argument("--force", action="store_true", help="save a file that looks like a secret or that git ignores")

    p = sub.add_parser("link", help="record files already in the project, without copying them")
    p.add_argument("paths", nargs="+", metavar="PATHS")
    p.add_argument("--role", required=True)
    _add_task(p)
    p.add_argument("--session")
    p.add_argument("--inputs", action="extend", nargs="+", metavar="ID_OR_PATH", help=INPUTS_HELP)
    p.add_argument("--description")
    p.add_argument("--no-stage", dest="no_stage", action="store_true")
    p.add_argument("--force", action="store_true", help="link a file that looks like a secret or that git ignores")

    p = sub.add_parser("search", help="find artifacts by filename or description")
    p.add_argument("text", nargs="?", default="", metavar="TEXT")
    p.add_argument("--include-intermediate", dest="include_intermediate", action="store_true")

    for name, helptext in (
        ("path", "print the absolute path of a version's bytes"),
        ("provenance", "show a version's inputs and reviewer findings"),
        ("graph", "show a version's full ancestry"),
    ):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("ref", metavar="REF")
        if name == "path":
            p.add_argument("--no-stage", dest="no_stage", action="store_true")
    p = sub.add_parser("lineage")  # legacy
    p.add_argument("ref", metavar="REF")

    sub.add_parser("lfs-check", help="report large stored copies that lack an LFS line, and the LFS total")

    _add_findings_parser(sub, "findings", hidden=False)
    _add_findings_parser(sub, "check", hidden=True)  # legacy
    _add_respond_parser(sub, "respond", hidden=False)
    _add_respond_parser(sub, "mark-addressed", hidden=True)  # legacy

    p = sub.add_parser("resolve", help="replace {{artifact:REF}} markers with relative Markdown links")
    p.add_argument("file", metavar="FILE")
    p.add_argument("--write", action="store_true", help="rewrite FILE in place instead of printing")
    return parser


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.subcommand in ("save", "link") and args.task is None:
        parser.error("the following arguments are required: --task")
    try:
        if args.lab and not Path(args.lab).is_dir():
            raise StoreError(f"lab directory not found: {args.lab}")
        if args.lab:
            chosen = Path(args.lab).resolve()
            if chosen.name != "research_lab" and not (chosen / "lab.json").is_file() \
                    and not (chosen / "artifacts").is_dir():
                hint = f"; did you mean {chosen / 'research_lab'}?" if (chosen / "research_lab").is_dir() else ""
                raise StoreError(f"not a research_lab: {chosen}{hint}")
        lab = Path(args.lab) if args.lab else find_lab(Path.cwd())
        store = LabStore(lab)
        return _dispatch(store, args)
    except OldLayout:
        print(OLD_LAYOUT_MESSAGE, file=sys.stderr)
        return 2
    except StoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: {exc.strerror}: {exc.filename}" if exc.filename else f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
