#!/usr/bin/env python3
"""Set up a project-local research lab: compute a plan, print it, apply it with --yes.

The plan lists what would be created, appended to or skipped. Nothing is written without --yes, and a
file that already exists is never overwritten. Standard library only.
"""

from __future__ import annotations

import argparse
import functools
import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS.parent
TEMPLATE_ROOT = SKILL_ROOT / "templates"
SKILLS_ROOT = SKILL_ROOT.parent
PLUGIN_ROOT = SCRIPTS.parents[2]

BEGIN_MARKER = "<!-- science-ultrapowers:begin -->"
END_MARKER = "<!-- science-ultrapowers:end -->"
GITATTRIBUTES_REL = "research_lab/artifacts/.gitattributes"
LAB_JSON_REL = "research_lab/lab.json"
INSTRUCTION_FILES = ("CLAUDE.md", ".claude/CLAUDE.md")
OLD_SKILL_NAMES = (
    "doi-verified-evidence",
    "research-lab-workflow",
    "findings-ledger",  # legacy
    "reference-access-request",
    "jev-decisions",
)
SETTINGS_REL = ".claude/settings.json"
HOST_RE = re.compile(r"[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+")
GIT_REL = ".git/"
REFERENCES_REL = "references/"
COMMIT_MESSAGE = "chore: initialise the research lab"
OUT_OF_SCOPE_PROMPT = "*List the folders no role may open.*"
DRY_RUN_LINE = "Dry run: nothing written. Re-run with --yes to apply."

# Files copied at run time from other skills: destination -> source, relative to SKILLS_ROOT.
COPIED_FILES = {
    "research_lab/memory/MEMORY.md": "remembering-for-the-lab/templates/MEMORY.md",
    "research_lab/memory/README.md": "remembering-for-the-lab/templates/README.md",
    "research_lab/templates/LAB_MEETING.md": "holding-lab-meetings/templates/LAB_MEETING.md",
    "research_lab/templates/SESSION_OPENING.md": "holding-lab-meetings/templates/SESSION_OPENING.md",
    "research_lab/templates/SESSION_CLOSE.md": "holding-lab-meetings/templates/SESSION_CLOSE.md",
}

_PLACEHOLDER = re.compile(r"\{\{([A-Z_]+)\}\}")
_artifacts_module = None


@dataclass
class Options:
    name: str
    short_name: str = ""
    description: str = ""
    lfs_threshold_mb: int = 10
    git_init: bool = False
    yes: bool = False
    json_output: bool = False
    project_root: Path | None = None
    connectors: list[str] = field(default_factory=list)  # catalog ids, resolved and in catalog order
    permissions: bool = False
    allow_domains: list[str] = field(default_factory=list)  # lowercased, validated hosts
    out_of_scope: list[str] = field(default_factory=list)  # cleaned folders no role may open
    tracks: list[str] = field(default_factory=list)  # --track values, in the order given; empty means the whole lab


@dataclass
class Plan:
    create: list[str] = field(default_factory=list)
    append: list[str] = field(default_factory=list)
    skip: list[str] = field(default_factory=list)
    warn: list[str] = field(default_factory=list)
    connectors: dict = field(default_factory=dict)
    duplicates: list[str] = field(default_factory=list)
    # The mcp connector ids .mcp.json holds after the run (added now or already there); lab.json records them.
    configured_connectors: list[str] = field(default_factory=list)
    # With --permissions: {"file", "action": "create" | "skip", "rules": [...]}; empty without it.
    permissions: dict = field(default_factory=dict)
    # The migration of a 0.1 lab: the shown lines, the (old, new) renames in the order they run, the new folders it
    # stops for, and the lab.json it would write.
    migration: list[str] = field(default_factory=list)
    migration_renames: list = field(default_factory=list)
    migration_skip_folders: list[str] = field(default_factory=list)
    lab_json_migrated: bytes | None = None
    # False for a lab with the new layout: only the column additions run, no rename, header rename or token rewrite.
    migration_old_layout: bool = False
    # {"file", "action": "create" | "skip", "setting"}; empty when the plugin lacks the style file.
    output_style: dict = field(default_factory=dict)
    # The tracks lab.json holds after the run: the ones it holds now, then the ones asked for.
    tracks: list[str] = field(default_factory=list)
    # The instructions file whose lab section (between the markers) differs from the current template.
    section_refresh: str | None = None


# --- helpers -----------------------------------------------------------------------------------------


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "lab"


@functools.lru_cache(maxsize=None)
def plugin_version() -> str:
    try:
        data = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        version = data.get("version")
        return version if isinstance(version, str) and version else "unknown"
    except (OSError, ValueError, AttributeError):
        return "unknown"


def load_artifacts():
    """PLAN-02's store module, imported by path so init and the store share one definition."""
    global _artifacts_module
    if _artifacts_module is not None:
        return _artifacts_module
    path = SKILLS_ROOT / "saving-artifacts" / "scripts" / "artifacts.py"
    spec = importlib.util.spec_from_file_location("lab_artifacts_store", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"init_lab: cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["lab_artifacts_store"] = module
    try:
        spec.loader.exec_module(module)
    except (OSError, SyntaxError, ImportError) as exc:
        raise SystemExit(f"init_lab: cannot load {path}: {exc}")
    _artifacts_module = module
    return module


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess | None:
    """Run git; None when git cannot be started."""
    try:
        return subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
        )
    except OSError:
        return None


def git_toplevel(cwd: Path) -> Path | None:
    result = run_git(["rev-parse", "--show-toplevel"], cwd)
    if result is None or result.returncode != 0 or not result.stdout.strip():
        return None
    top = Path(result.stdout.strip())
    return top if top.is_dir() else None


def git_lfs_available(cwd: Path) -> bool:
    result = run_git(["lfs", "version"], cwd)
    return result is not None and result.returncode == 0


def clean_scope_folder(text: str) -> str | None:
    """A folder as lab.json and the brief record it: POSIX separators, no leading ./; None when nothing is left."""
    folder = text.strip().replace("\\", "/")
    while folder.startswith("./"):
        folder = folder[2:].lstrip("/")
    folder = folder.rstrip("/") if folder != "/" else folder
    if not folder or any(ord(ch) < 32 or ch == "`" for ch in folder):
        return None
    return folder


def out_of_scope_block(folders: list[str]) -> str:
    """Section 7 of the brief: a bullet per folder, else the prompt for the researcher to answer."""
    if not folders:
        return OUT_OF_SCOPE_PROMPT
    return "\n".join(f"- `{folder}`" for folder in folders)


def description_sentence(description: str) -> str:
    """What follows the name in the README's first sentence: ': <description>' with its end mark, else a full stop."""
    text = description.strip()
    if not text:
        return "."
    return f": {text}" if text[-1] in ".!?" else f": {text}."


def substitutions(project_root: Path, opts: Options) -> dict[str, str]:
    return {
        "NAME": opts.name,
        "SHORT_NAME": opts.short_name or slugify(opts.name),
        "DESCRIPTION": opts.description,
        "DESCRIPTION_SENTENCE": description_sentence(opts.description),
        "OUT_OF_SCOPE": out_of_scope_block(opts.out_of_scope),
        "DATE": date.today().isoformat(),
        "PLUGIN_VERSION": plugin_version(),
        "PROJECT_ROOT": Path(project_root).as_posix(),
    }


def substitute(text: str, subs: dict[str, str]) -> str:
    return _PLACEHOLDER.sub(lambda m: subs.get(m.group(1), m.group(0)), text)


def read_template(path: Path, subs: dict[str, str]) -> str:
    text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    return substitute(text, subs)


def template_files() -> dict[str, Path]:
    """Destination (relative to the project root, POSIX) -> source file, for every file the lab holds."""
    items: dict[str, Path] = {}
    base = TEMPLATE_ROOT / "research_lab"
    for source in sorted(p for p in base.rglob("*") if p.is_file()):
        items[(Path("research_lab") / source.relative_to(base)).as_posix()] = source
    items[LAB_JSON_REL] = TEMPLATE_ROOT / "lab.json"
    for dest, rel in COPIED_FILES.items():
        items[dest] = SKILLS_ROOT / rel
    return items


TRACKS = ("idea", "literature", "review", "writing", "dissemination")


def _under(items: dict[str, Path], *prefixes: str) -> list[str]:
    """Every template destination that starts with one of the folder prefixes."""
    return sorted(rel for rel in items if rel.startswith(prefixes))


def _track_files() -> dict[str, list[str]]:
    """Track -> the template destinations its minimal lab holds (every set has the shared files)."""
    items = template_files()
    shared = [
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
        LAB_JSON_REL,
    ] + _under(items, "research_lab/decisions/")
    t = "research_lab/templates/"
    extra = {
        "idea": _under(items, "research_lab/project/")
        + [t + "HYPOTHESIS_RECORD.md", t + "EVIDENCE_RECORD.md"],
        "literature": [t + "EVIDENCE_RECORD.md", t + "SYNTHESIS_MATRIX.md", t + "CITATION_AUDIT.md"],
        "review": [
            t + "REFEREE_REPORT.md",
            t + "CITATION_AUDIT.md",
            t + "RESPONSE_MATRIX.md",
            t + "ADVERSARIAL_REVIEW.md",
        ],
        "writing": _under(items, "research_lab/findings/", "research_lab/planning/")
        + [t + "INTERNAL_REVIEW.md", t + "ARCHIVE_MANIFEST.md"],
        "dissemination": _under(items, "research_lab/findings/") + [t + "EVIDENCE_RECORD.md"],
    }
    return {track: sorted(set(shared + extra[track])) for track in TRACKS}


TRACK_FILES: dict[str, list[str]] = _track_files()


def gitignore_lines() -> list[str]:
    text = (TEMPLATE_ROOT / "gitignore_lines.txt").read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


def missing_gitignore_lines(raw: bytes) -> list[str]:
    """The template lines the .gitignore bytes lack; a line counts as present with or without its leading slash."""

    def bare(line: str) -> str:
        line = line.strip()
        return line[1:] if line.startswith("/") else line

    have = {bare(line) for line in raw.decode("utf-8", errors="replace").splitlines()}
    return [line for line in gitignore_lines() if bare(line) not in have]


def read_bytes_or_none(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except OSError:
        return None


def build_lab_json(
    project_root: Path, opts: Options, configured: list[str] | None = None, permissions_written: bool = False
) -> str:
    subs = substitutions(project_root, opts)
    data = json.loads((TEMPLATE_ROOT / "lab.json").read_text(encoding="utf-8"))
    data["name"] = opts.name
    data["shortName"] = subs["SHORT_NAME"]
    data["description"] = opts.description
    data["pluginVersion"] = subs["PLUGIN_VERSION"]
    data["scaffoldedAt"] = subs["DATE"]
    data["lfs"]["thresholdMB"] = opts.lfs_threshold_mb
    data["permissions"] = {"written": bool(permissions_written)}
    chosen = set(configured or [])
    data["connectors"] = [e["id"] for e in load_catalog() if e["id"] in chosen and e["kind"] == "mcp"]
    data["scope"]["restrictedFolders"] = list(opts.out_of_scope)
    data["tracks"] = list(opts.tracks)
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def parse_lab_json(raw: bytes) -> dict:
    """The parsed lab.json; ValueError (with a readable reason) unless it is a JSON object."""
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError(str(exc))
    if not isinstance(data, dict):
        raise ValueError("the top level is not an object")
    return data


def merge_lab_json(data: dict, opts: Options, configured: list[str], permissions_written: bool) -> bool:
    """Bring an existing lab.json's own values up to date in place; True when something changed.

    Only these change: the plugin version, the connectors list (union with the ones configured now, catalog
    order), permissions.written (only ever to true), scope.restrictedFolders (union with --out-of-scope), tracks
    (union with --track, order of first appearance) and the preregistration block (added when absent)."""
    changed = False
    version = plugin_version()
    if version != "unknown" and data.get("pluginVersion") != version:
        data["pluginVersion"] = version
        changed = True
    if configured:
        have = data.get("connectors") if isinstance(data.get("connectors"), list) else []
        wanted = set(have) | set(configured)
        merged = [e["id"] for e in load_catalog() if e["id"] in wanted]
        merged += [item for item in have if isinstance(item, str) and item not in merged]
        if merged != data.get("connectors"):
            data["connectors"] = merged
            changed = True
    if permissions_written:
        permissions = data.get("permissions")
        if not isinstance(permissions, dict):
            data["permissions"] = {"written": True}
            changed = True
        elif permissions.get("written") is not True:
            permissions["written"] = True
            changed = True
    if opts.out_of_scope:
        scope = data.get("scope")
        if not isinstance(scope, dict):
            scope = data["scope"] = {}
        have_paths = scope.get("restrictedFolders") if isinstance(scope.get("restrictedFolders"), list) else []
        merged_paths = list(have_paths) + [p for p in opts.out_of_scope if p not in have_paths]
        if merged_paths != scope.get("restrictedFolders"):
            scope["restrictedFolders"] = merged_paths
            changed = True
    have_tracks = data.get("tracks") if isinstance(data.get("tracks"), list) else []
    merged_tracks = list(have_tracks) + [t for t in opts.tracks if t not in have_tracks]
    if merged_tracks != data.get("tracks"):
        data["tracks"] = merged_tracks
        changed = True
    if "preregistration" not in data:
        template = json.loads((TEMPLATE_ROOT / "lab.json").read_text(encoding="utf-8"))
        data["preregistration"] = template["preregistration"]
        changed = True
    return changed


def merged_lab_json_text(raw: bytes, opts: Options, configured: list[str], permissions_written: bool) -> str | None:
    """The text an existing lab.json becomes, or None when nothing in it needs to change."""
    data = parse_lab_json(raw)
    if not merge_lab_json(data, opts, configured, permissions_written):
        return None
    return json.dumps(data, indent=mcp_json_indent(raw), ensure_ascii=False) + "\n"


def claude_section(project_root: Path, opts: Options) -> str:
    return read_template(TEMPLATE_ROOT / "CLAUDE_SECTION.md", substitutions(project_root, opts))


def is_symlink(path: Path) -> bool:
    return os.path.islink(path)


def symlink_target(path: Path) -> str:
    try:
        return os.readlink(path)
    except OSError:
        return "an unreadable target"


def symlink_warning(name: str, path: Path, remedy: str) -> str:
    return f"{name} is a symlink to {symlink_target(path)}; it was not written through: {remedy}"


def section_bounds(text: str):
    """(start, end) of the lab section in text, markers included; None without both markers in order."""
    start = text.find(BEGIN_MARKER)
    if start < 0:
        return None
    end = text.find(END_MARKER, start)
    if end < 0:
        return None
    return start, end + len(END_MARKER)


def plan_instructions(project_root: Path, plan: Plan, opts: Options | None = None) -> None:
    """Decide which instructions file gets the lab section: never a second section anywhere. A section that
    exists but differs from the current template (a lab set up by an older plugin) is planned as a rewrite."""
    existing = [rel for rel in INSTRUCTION_FILES if os.path.lexists(project_root / rel)]
    unreadable: list[str] = []
    for rel in existing:
        raw = read_bytes_or_none(project_root / rel)
        if raw is None:
            unreadable.append(rel)
        elif BEGIN_MARKER in raw.decode("utf-8", errors="replace"):
            text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
            bounds = section_bounds(text)
            if bounds is None:
                plan.warn.append(f"{rel} has the lab section's begin marker but no end marker; the section was not refreshed")
                plan.skip.append(rel)
                return
            if opts is not None and not is_symlink(project_root / rel):
                current = claude_section(project_root, opts).strip("\n")
                if rel != "CLAUDE.md":
                    current = current.replace("@research_lab/", "@../research_lab/")
                if text[bounds[0]:bounds[1]].strip("\n") != current:
                    plan.section_refresh = rel
                    plan.migration.append(f"rewrite {rel}: the lab section between the markers -> the current template")
                    return
            plan.skip.append(rel)
            return
    if not existing:
        plan.create.append(INSTRUCTION_FILES[0])
        return
    chosen = existing[0]
    if is_symlink(project_root / chosen):
        plan.warn.append(
            f"{chosen} is a symlink to {symlink_target(project_root / chosen)}; it was not written through: "
            "add the lab section to it by hand (the text is templates/CLAUDE_SECTION.md in the plugin)"
        )
    elif chosen in unreadable:
        plan.warn.append(f"cannot read {chosen}; the lab section was not planned")
    else:
        plan.append.append(chosen)


def find_duplicates(project_root: Path) -> list[str]:
    """Agents and skills the plugin already ships that the project also carries under .claude/."""
    found: list[str] = []
    try:
        roles = json.loads((TEMPLATE_ROOT / "lab.json").read_text(encoding="utf-8")).get("roles", {})
    except (OSError, ValueError):
        roles = {}
    for name in (*roles, *ROLE_RENAMES):
        rel = f".claude/agents/{name}.md"
        if os.path.lexists(project_root / rel):
            found.append(rel)
    names = {p.parent.name for p in SKILLS_ROOT.glob("*/SKILL.md")} | set(OLD_SKILL_NAMES)
    for name in names:
        rel = f".claude/skills/{name}"
        if os.path.lexists(project_root / rel):
            found.append(rel)
    return sorted(found)


# --- permissions -------------------------------------------------------------------------------------


def permission_rules(allow_domains: list[str]) -> list[str]:
    """The template's rules plus one WebFetch rule per approved host: sorted, unique, never a Bash rule."""
    path = TEMPLATE_ROOT / "permissions.json"
    try:
        base = json.loads(path.read_text(encoding="utf-8"))["permissions"]["allow"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit(f"init_lab: cannot read {path}: {exc}")
    rules = {rule for rule in base if isinstance(rule, str)}
    rules.update(f"WebFetch(domain:{host})" for host in allow_domains)
    return sorted(rule for rule in rules if not rule.startswith("Bash("))


def settings_text(rules: list[str]) -> str:
    return json.dumps({"permissions": {"allow": list(rules)}}, indent=2, ensure_ascii=False) + "\n"


def plan_permissions(project_root: Path, opts: Options, plan: Plan) -> None:
    rules = permission_rules(opts.allow_domains)
    if os.path.lexists(project_root / SETTINGS_REL):
        plan.skip.append(f"{SETTINGS_REL} exists; merge the rules by hand")
        action = "skip"
    else:
        plan.create.append(SETTINGS_REL)
        action = "create"
    plan.permissions = {"file": SETTINGS_REL, "action": action, "rules": rules}


def plan_lab_json(project_root: Path, opts: Options, plan: Plan) -> None:
    """An existing lab.json is merged, not skipped: it is appended to only when a value in it would change."""
    target = project_root / LAB_JSON_REL
    if is_symlink(target):
        plan.skip.append(LAB_JSON_REL)
        plan.warn.append(symlink_warning(LAB_JSON_REL, target, "update it by hand"))
        return
    raw = read_bytes_or_none(target)
    if raw is None:
        plan.skip.append(LAB_JSON_REL)
        plan.warn.append(f"cannot read {LAB_JSON_REL}; left unchanged")
        return
    if plan.lab_json_migrated is not None:
        raw = plan.lab_json_migrated  # the migration writes it first
    try:
        text = merged_lab_json_text(
            raw, opts, plan.configured_connectors, plan.permissions.get("action") == "create"
        )
    except ValueError as exc:
        plan.skip.append(LAB_JSON_REL)
        plan.warn.append(f"{LAB_JSON_REL} is not valid JSON ({exc}); it was left unchanged")
        return
    (plan.skip if text is None else plan.append).append(LAB_JSON_REL)


# --- connectors --------------------------------------------------------------------------------------


def load_catalog() -> list[dict]:
    path = SKILL_ROOT / "connectors.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"init_lab: cannot read the connector catalog {path}: {exc}")
    if not isinstance(data, list):
        raise SystemExit(f"init_lab: the connector catalog {path} must be a list")
    return data


def resolve_connectors(text: str) -> list[str]:
    """Ids and the word `science`, comma separated -> catalog ids in catalog order.

    Raises ValueError carrying the list of unknown ids."""
    catalog = load_catalog()
    known = {entry["id"] for entry in catalog}
    chosen: set[str] = set()
    unknown: list[str] = []
    for item in (part.strip() for part in text.split(",")):
        if not item:
            continue
        if item == "science":
            chosen.update(e["id"] for e in catalog if e["kind"] == "mcp" and e.get("tag") == "science")
        elif item in known:
            chosen.add(item)
        elif item not in unknown:
            unknown.append(item)
    if unknown:
        raise ValueError(unknown)
    return [e["id"] for e in catalog if e["id"] in chosen]


def server_entry(entry: dict, project_root: Path) -> dict:
    """The .mcp.json server for one `mcp` catalog entry."""
    if entry["transport"] == "stdio":
        subs = {"PROJECT_ROOT": Path(project_root).as_posix()}
        return {
            "type": "stdio",
            "command": entry["command"],
            "args": [substitute(arg, subs) for arg in entry.get("args") or []],
        }
    server = {"type": entry["transport"], "url": entry["url"]}
    if entry.get("headers"):
        server["headers"] = dict(entry["headers"])
    return server


def parse_mcp_json(raw: bytes) -> dict:
    """The parsed .mcp.json; ValueError (with a readable reason) unless it is an object with an object `mcpServers`."""
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError(str(exc))
    if not isinstance(data, dict):
        raise ValueError("the top level is not an object")
    if "mcpServers" in data and not isinstance(data["mcpServers"], dict):
        raise ValueError("mcpServers is not an object")
    return data


def mcp_json_indent(raw: bytes):
    """The indent the file already uses: its first indented line's leading whitespace; 2 when there is none."""
    match = re.search(r"^([ \t]+)\S", raw.decode("utf-8", errors="replace"), re.MULTILINE)
    if match is None:
        return 2
    lead = match.group(1)
    return "\t" if lead.startswith("\t") else len(lead)


def plan_connectors(project_root: Path, opts: Options, plan: Plan) -> None:
    catalog = {entry["id"]: entry for entry in load_catalog()}
    desired: dict[str, dict] = {}
    for cid in opts.connectors:
        entry = catalog[cid]
        if entry["kind"] == "mcp":
            desired[cid] = server_entry(entry, project_root)
        else:
            plan.warn.append(f"{cid}: {entry.get('note') or 'not configurable in .mcp.json'}")
    if "optuna" in desired:
        plan.warn.append(
            "optuna: needs uv; its .mcp.json entry holds this machine's path "
            f"{Path(project_root).as_posix()}/outputs/optuna/optuna.db "
            "(create outputs/optuna/ before first use; a collaborator edits the path)"
        )
    if not desired:
        return
    target = project_root / ".mcp.json"
    if not os.path.lexists(target):
        plan.create.append(".mcp.json")
        plan.connectors = desired
        plan.configured_connectors = list(desired)
        return
    if is_symlink(target):
        plan.warn.append(symlink_warning(".mcp.json", target, "add the servers by hand"))
        return
    raw = read_bytes_or_none(target)
    if raw is None:
        plan.warn.append(".mcp.json cannot be read; it was left unchanged and no connector was written")
        return
    try:
        data = parse_mcp_json(raw)
    except ValueError as exc:
        plan.warn.append(
            f".mcp.json is not valid JSON ({exc}); it was left unchanged and no connector was written"
        )
        return
    existing = {name.lower(): name for name in data.get("mcpServers", {})}
    add: dict[str, dict] = {}
    for cid, server in desired.items():
        if cid.lower() in existing:
            plan.skip.append(f'.mcp.json: {cid} (already configured as "{existing[cid.lower()]}")')
        else:
            add[cid] = server
    plan.configured_connectors = list(desired)
    if add:
        plan.append.append(".mcp.json")
        plan.connectors = add
    else:
        plan.skip.append(".mcp.json")


def apply_mcp_json(project_root: Path, action: str, servers: dict) -> bool:
    dest = project_root / ".mcp.json"
    if action == "create":
        return write_new(dest, json.dumps({"mcpServers": servers}, indent=2, ensure_ascii=False) + "\n")
    raw = dest.read_bytes()
    data = parse_mcp_json(raw)
    current = data.setdefault("mcpServers", {})
    existing = {name.lower() for name in current}
    fresh = {cid: server for cid, server in servers.items() if cid.lower() not in existing}
    if not fresh:
        return False
    current.update(fresh)
    text = json.dumps(data, indent=mcp_json_indent(raw), ensure_ascii=False) + "\n"
    with open(dest, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return True


# --- migration of a 0.1 lab --------------------------------------------------------------------------
# Three kinds of plan line and no others: `rename <old> -> <new>`, `header <file>: <old> -> <new>` and
# `rewrite <file>: <column>, <n> rows: <old> -> <new>`. Free-text cells and existing ids in rows are never edited.

OLD_FOLDERS = {  # old folder under research_lab/ -> new folder
    "00_project_knowledge": "project",  # legacy
    "01_reference_registry": "literature",  # legacy
    "02_findings_ledger": "findings",  # legacy
    "03_experiments": "experiments",  # legacy
    "04_reviews": "reviews",  # legacy
    "05_access_requests": "requests",  # legacy
    "06_decisions": "decisions",  # legacy
    "07_project_management": "planning",  # legacy
    "08_decision_log": "automation",  # legacy
    "09_skill_vetting": "tool_vetting",  # legacy
}
OTHER_FOLDER_RENAMES = (
    ("artifacts/store", "artifacts/archive"),  # legacy
    (".scratch", ".working"),  # legacy
)
# Renames inside a renamed folder, in paths of the new layout (relative to research_lab/).
INNER_RENAMES = (
    ("literature/REGISTRY.csv", "literature/SOURCES.csv"),  # legacy
    ("literature/evidence_cards", "literature/evidence_records"),  # legacy
    ("literature/audits", "literature/search_logs"),  # legacy
    ("findings/FINDINGS.md", "findings/FINDINGS_LOG.md"),  # legacy
    ("findings/CANONICAL_NUMBERS.md", "findings/KEY_RESULTS.md"),  # legacy
    ("experiments/protocols", "experiments/preregistrations"),  # legacy
    ("decisions/DECISIONS.md", "decisions/DECISION_LOG.md"),  # legacy
    ("planning/TASK_BOARD.md", "planning/WORK_PLAN.md"),  # legacy
    ("migration/WHERE_WE_LEFT_OFF.md", "migration/HANDOVER_SUMMARY.md"),  # legacy
    ("templates/H_CARD.md", "templates/HYPOTHESIS_RECORD.md"),  # legacy
    ("templates/EVIDENCE_CARD.md", "templates/EVIDENCE_RECORD.md"),  # legacy
    ("templates/HANDOFF.md", "templates/TASK_REPORT.md"),  # legacy
    ("templates/DEVILS_ADVOCATE_TEMPLATE.md", "templates/ADVERSARIAL_REVIEW.md"),  # legacy
    ("templates/REVIEW_ACADEMIC.md", "templates/INTERNAL_REVIEW.md"),  # legacy
    ("templates/SESSION_KICKOFF.md", "templates/SESSION_OPENING.md"),  # legacy
    ("templates/SESSION_STANDUP.md", "templates/SESSION_CLOSE.md"),  # legacy
)
MEETINGS_FOLDER = "decisions/lab_meetings"
MEETING_SUFFIXES = (("_kickoff.md", "_opening.md"), ("_standup.md", "_close.md"))  # legacy
ROLE_RENAMES = {  # old agent id -> new agent id
    "lab-project-manager": "research-project-manager",  # legacy
    "methods-researcher": "methods-innovation-researcher",  # legacy
    "experiments-lead": "lab-experiments-lead",  # legacy
    "findings-curator": "findings-records-curator",  # legacy
    "paper-author": "academic-paper-author",  # legacy
    "scientific-reviewer": "scientific-peer-reviewer",  # legacy
    "citation-auditor": "citation-reference-auditor",  # legacy
}
OLD_BRIEF_IMPORT = "research_lab/00_project_knowledge/"  # legacy
GITATTRIBUTES_OLD_PREFIX = "store/"  # legacy
GITATTRIBUTES_NEW_PREFIX = "archive/"
STAGE_NAMES = {
    "G0": "Question",  # legacy
    "G1": "Literature",  # legacy
    "G2": "Preregistration",  # legacy
    "G3": "Execution",  # legacy
    "G4": "Results",  # legacy
    "G5": "Reporting",  # legacy
    "G6": "Publication",  # legacy
}
SOURCE_STATUSES = {
    "ADMITTED": "citable",  # legacy
    "ADMITTED_EXCEPTION": "citable by exception",  # legacy
    "DOI_VERIFIED": "metadata matched",  # legacy
    "PENDING_FULLTEXT": "awaiting full text",  # legacy
    "PENDING_APPROVAL": "awaiting approval",  # legacy
    "CANDIDATE_DOI": "candidate",  # legacy
    "EXCLUDED_PREPRINT": "excluded: preprint",  # legacy
    "EXCLUDED_RETRACTED": "excluded: retracted",  # legacy
    "REJECTED_MISMATCH": "rejected: mismatch",  # legacy
}
SOURCE_CLASSES = {
    "A": "peer-reviewed matched doi",  # legacy
    "B": "peer-reviewed no doi",  # legacy
    "C": "not peer-reviewed",  # legacy
    "X": "retracted",  # legacy
}
DOI_STATUSES = {
    "VERIFIED": "matched",  # legacy
    "RESOLVES_UNCHECKED": "resolves unchecked",  # legacy
    "NO_DOI": "no doi",  # legacy
    "MISMATCH": "mismatch",  # legacy
    "UNRESOLVED": "unresolved",  # legacy
    "RETRACTED": "retracted",  # legacy
    "CONCERN": "concern",  # legacy
    "PREPRINT": "preprint",  # legacy
    "ERROR": "error",  # legacy
}
REQUEST_TYPES = {
    "FULLTEXT": "full-text request",  # legacy
    "CONFIRM_DOI": "DOI confirmation",  # legacy
    "APPROVAL": "exception approval",  # legacy
}
REQUEST_PRIORITIES = {
    "P1": "blocks a stage",  # legacy
    "P2": "this cycle",  # legacy
    "P3": "background",  # legacy
}
OUTPUT_STYLE_SOURCE = PLUGIN_ROOT / "output-styles" / "scholarly-explanatory.md"
OUTPUT_STYLE_REL = ".claude/output-styles/scholarly-explanatory.md"
OUTPUT_STYLE_SETTING = '"outputStyle": "Scholarly Explanatory"'


def lowercase_of(*words: str):
    """A token rewrite that only lower-cases the listed words (a status written in capitals)."""
    wanted = {word.lower() for word in words}
    return lambda value: value.lower() if value.lower() in wanted else value


def table_of(table: dict):
    return lambda value: table.get(value, value)


def finding_status(value: str) -> str:
    match = re.fullmatch(r"(superseded by|refuted by)(\s+)(\S+)", value, re.IGNORECASE)
    if match:
        return f"{match.group(1).lower()}{match.group(2)}{match.group(3)}"
    return lowercase_of("tentative", "verified")(value)


@dataclass(frozen=True)
class TableSpec:
    path: str  # the file in the new layout, relative to research_lab/
    kind: str  # "md" or "csv"
    headers: dict  # old column name -> new column name
    tokens: dict  # new column name -> a function from an old token to a new token
    # (after_column, new_column, value_for_existing_rows): a column added when the table lacks it.
    added: tuple = ()


TABLES = (
    TableSpec(
        "findings/FINDINGS_LOG.md",
        "md",
        {"F-id": "FND-id (finding)", "Scope / caveats": "Scope and caveats"},  # legacy
        {"Status": finding_status},
        (("Type", "Basis", "exploratory"),),
    ),
    TableSpec("findings/KEY_RESULTS.md", "md", {"F-id": "FND-id (finding)"}, {}),  # legacy
    TableSpec(
        "literature/SOURCES.csv",
        "csv",
        {
            "ref_id": "source_id",  # legacy
            "lab_status": "status",  # legacy
            "tier": "source_class",  # legacy
            "verify_status": "doi_status",  # legacy
            "evidence_cards": "evidence_records",  # legacy
        },
        {
            "status": table_of(SOURCE_STATUSES),
            "source_class": table_of(SOURCE_CLASSES),
            "doi_status": table_of(DOI_STATUSES),
        },
    ),
    TableSpec(
        "experiments/EXPERIMENT_REGISTER.md",
        "md",
        {
            "Experiment id": "EXP-id (experiment)",  # legacy
            "Protocol": "Preregistration",  # legacy
            "Code / config": "Code and config",  # legacy
            "Seeds / splits (where applicable)": "Seeds and partitions",  # legacy
        },
        {"Status": lowercase_of("planned", "feasibility", "registered", "running", "completed", "failed", "aborted")},
        (("Environment", "Input checksums", ""),),
    ),
    TableSpec(
        "reviews/REVIEW_LOG.md",
        "md",
        {
            "RV-id": "REV-id (review)",  # legacy
            "Artifact (path / version)": "Artifact",  # legacy
            "Gate": "Stage",  # legacy
            "Reviewer role": "Reviewer",  # legacy
            "Verdict": "Outcome",  # legacy
        },
        {"Stage": table_of(STAGE_NAMES)},
    ),
    TableSpec(
        "requests/ACCESS_REQUESTS.md",
        "md",
        {"REQ-id": "REQ-id (request)"},
        {
            "Type": table_of(REQUEST_TYPES),
            "Priority": table_of(REQUEST_PRIORITIES),
            "Status": lowercase_of("open", "fulfilled", "approved", "declined", "unavailable"),
        },
    ),
    TableSpec(
        "decisions/DECISION_LOG.md",
        "md",
        {"D-id": "DEC-id (decision)", "Evidence ids": "Evidence"},  # legacy
        {},
    ),
    TableSpec(
        "planning/WORK_PLAN.md",
        "md",
        {"Task": "TASK-id (task)", "Gate": "Stage"},  # legacy
        {"Stage": table_of(STAGE_NAMES)},
    ),
    TableSpec("planning/RISK_REGISTER.md", "md", {"R-id": "RSK-id (risk)"}, {}),  # legacy
)
BOM = chr(0xFEFF)  # a byte order mark in front of the first CSV field
_SEPARATOR_ROW = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
_CELL_SPLIT = re.compile(r"(?<!\\)\|")


def _split_eol(line: str) -> tuple[str, str]:
    body = line.rstrip("\r\n")
    return body, line[len(body):]


def _swap_cell(cell: str, new: str) -> str:
    lead = cell[: len(cell) - len(cell.lstrip())]
    trail = cell[len(cell.rstrip()):]
    return f"{lead}{new}{trail}"


def _tally(counts: dict, column: str, old: str, new: str) -> None:
    counts[(column, old, new)] = counts.get((column, old, new), 0) + 1


def _add_md_column(lines: list[str], start: int, after: str, new: str, value: str):
    """Insert the column `new` after `after` in the table at `start`: (header change or None, rewrite or None, skipped).

    The header cell, the separator cell and one cell in every data row are added; rows with another cell count are
    left alone. Nothing is changed (skipped is the reason) when the anchor is absent."""
    body, eol = _split_eol(lines[start])
    cells = _CELL_SPLIT.split(body)
    names = [cell.strip() for cell in cells]
    if new in names:
        return None, None, None
    if after not in names:
        return None, None, f"no {after} column"
    index = names.index(after) + 1
    sep_body, sep_eol = _split_eol(lines[start + 1])
    sep_cells = _CELL_SPLIT.split(sep_body)
    if len(sep_cells) != len(cells):
        return None, None, "the separator row does not match the header"
    width = len(cells)
    cells.insert(index, f" {new} ")
    lines[start] = "|".join(cells) + eol
    sep_cells.insert(index, "---")
    lines[start + 1] = "|".join(sep_cells) + sep_eol
    rows = 0
    row = start + 2
    while row < len(lines) and lines[row].lstrip().startswith("|"):
        row_body, row_eol = _split_eol(lines[row])
        row_cells = _CELL_SPLIT.split(row_body)
        if len(row_cells) == width:
            row_cells.insert(index, f" {value} ")
            lines[row] = "|".join(row_cells) + row_eol
            rows += 1
        row += 1
    rewrite = (new, rows, "(empty)", value) if value and rows else None
    return ("(none)", new), rewrite, None


def transform_md_table(text: str, spec: TableSpec, warnings: list[str] | None = None):
    """Rewrite the first table of a Markdown file: (new text, [(old, new) header changes], [(column, n, old, new)]).

    A column the spec adds shows as the header change ("(none)", column) and, when its value for the existing rows
    is not empty, the rewrite (column, n, "(empty)", value). A reason an addition was skipped goes to `warnings`."""
    lines = text.splitlines(keepends=True)
    start = next(
        (
            i
            for i in range(len(lines) - 1)
            if lines[i].lstrip().startswith("|") and _SEPARATOR_ROW.match(lines[i + 1].rstrip("\r\n"))
        ),
        None,
    )
    if start is None:
        return text, [], []
    body, eol = _split_eol(lines[start])
    cells = _CELL_SPLIT.split(body)
    header_changes: list[tuple[str, str]] = []
    for index in range(1, len(cells) - 1):
        name = cells[index].strip()
        if name in spec.headers:
            header_changes.append((name, spec.headers[name]))
            cells[index] = _swap_cell(cells[index], spec.headers[name])
    lines[start] = "|".join(cells) + eol
    names = [cell.strip() for cell in cells]
    columns = {column: names.index(column) for column in spec.tokens if column in names}
    counts: dict = {}
    order: list[tuple] = []
    row = start + 2
    while row < len(lines) and lines[row].lstrip().startswith("|"):
        body, eol = _split_eol(lines[row])
        row_cells = _CELL_SPLIT.split(body)
        if len(row_cells) == len(cells):
            for column, index in columns.items():
                value = row_cells[index].strip()
                new = spec.tokens[column](value) if value else value
                if new != value:
                    if (column, value, new) not in counts:
                        order.append((column, value, new))
                    _tally(counts, column, value, new)
                    row_cells[index] = _swap_cell(row_cells[index], new)
            lines[row] = "|".join(row_cells) + eol
        row += 1
    rewrites = [(column, counts[(column, old, new)], old, new) for column, old, new in order]
    rewrites.sort(key=lambda item: names.index(item[0]))
    for after, column, value in spec.added:
        header_change, rewrite, skipped = _add_md_column(lines, start, after, column, value)
        if header_change is not None:
            header_changes.append(header_change)
        if rewrite is not None:
            rewrites.append(rewrite)
        if skipped is not None and warnings is not None:
            warnings.append(f"{spec.path}: {skipped}; the {column} column was not added")
    return "".join(lines), header_changes, rewrites


def split_csv_records(text: str) -> list[tuple[list[str], str]]:
    """Records as (raw fields, line ending); joining the fields with commas and the ending restores the text."""
    records: list[tuple[list[str], str]] = []
    fields: list[str] = []
    buf: list[str] = []
    quoted = False
    i = 0
    while i < len(text):
        ch = text[i]
        if quoted:
            buf.append(ch)
            if ch == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    buf.append('"')
                    i += 1
                else:
                    quoted = False
        elif ch == '"':
            buf.append(ch)
            quoted = True
        elif ch == ",":
            fields.append("".join(buf))
            buf = []
        elif ch in "\r\n":
            eol = ch
            if ch == "\r" and i + 1 < len(text) and text[i + 1] == "\n":
                eol = "\r\n"
                i += 1
            fields.append("".join(buf))
            records.append((fields, eol))
            fields, buf = [], []
        else:
            buf.append(ch)
        i += 1
    if buf or fields:
        fields.append("".join(buf))
        records.append((fields, ""))
    return records


def _csv_value(raw: str) -> str:
    raw = raw.lstrip(BOM)
    if len(raw) >= 2 and raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('""', '"')
    return raw


def _csv_swap(raw: str, new: str) -> str:
    bom = BOM if raw.startswith(BOM) else ""
    quoted = raw.lstrip(BOM).startswith('"')
    return f'{bom}"{new}"' if quoted else f"{bom}{new}"


def transform_csv_table(text: str, spec: TableSpec):
    records = split_csv_records(text)
    if not records:
        return text, [], []
    head, eol = records[0]
    header_changes: list[tuple[str, str]] = []
    names: list[str] = []
    for index, raw in enumerate(head):
        name = _csv_value(raw)
        if name in spec.headers:
            header_changes.append((name, spec.headers[name]))
            head[index] = _csv_swap(raw, spec.headers[name])
            name = spec.headers[name]
        names.append(name)
    columns = {column: names.index(column) for column in spec.tokens if column in names}
    counts: dict = {}
    order: list[tuple] = []
    for fields, _ in records[1:]:
        if len(fields) != len(head):
            continue
        for column, index in columns.items():
            value = _csv_value(fields[index])
            new = spec.tokens[column](value) if value else value
            if new != value:
                if (column, value, new) not in counts:
                    order.append((column, value, new))
                _tally(counts, column, value, new)
                fields[index] = _csv_swap(fields[index], new)
    rewrites = [(column, counts[(column, old, new)], old, new) for column, old, new in order]
    rewrites.sort(key=lambda item: names.index(item[0]))
    return "".join(",".join(fields) + end for fields, end in records), header_changes, rewrites


def transform_table(text: str, spec: TableSpec, warnings: list[str] | None = None):
    if spec.kind == "csv":
        return transform_csv_table(text, spec)
    return transform_md_table(text, spec, warnings)


def added_only(spec: TableSpec) -> TableSpec:
    """The spec without its renames and token rewrites: for a lab that already has the new layout."""
    return TableSpec(spec.path, spec.kind, {}, {}, spec.added)


def transform_frontmatter(text: str):
    """A memory entry's frontmatter keys: (new text, [(column, n, old, new)]); the body is never touched."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return text, []
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip("\r\n") == "---"), None)
    if end is None:
        return text, []
    has_basis = any(re.match(r"\s*basis:", line) for line in lines[1:end])
    rewrites: list[tuple[str, int, str, str]] = []
    for i in range(1, end):
        body, eol = _split_eol(lines[i])
        key = re.match(r"(\s*)evidence:(.*)$", body)  # legacy
        if key and not has_basis:
            lines[i] = f"{key.group(1)}basis:{key.group(2)}{eol}"
            rewrites.append(("evidence", 1, "evidence", "basis"))  # legacy
            continue
        kind = re.match(r"(\s*type:\s*)gotcha(\s*)$", body)  # legacy
        if kind:
            lines[i] = f"{kind.group(1)}pitfall{kind.group(2)}{eol}"
            rewrites.append(("type", 1, "gotcha", "pitfall"))  # legacy
    rewrites.sort(key=lambda item: item[0])  # the key `evidence` before the key `type`
    return "".join(lines), rewrites


def transform_gitattributes(text: str):
    """Patterns that name the old archive folder now name the new one: (new text, count of lines)."""
    lines = text.splitlines(keepends=True)
    count = 0
    for i, line in enumerate(lines):
        if line.startswith(GITATTRIBUTES_OLD_PREFIX):
            lines[i] = GITATTRIBUTES_NEW_PREFIX + line[len(GITATTRIBUTES_OLD_PREFIX):]
            count += 1
    return "".join(lines), count


def transform_lab_json(raw: bytes):
    """The migrated lab.json: (new bytes or None, [(column, n, old, new)]); None when nothing changes."""
    data = parse_lab_json(raw)
    rewrites: list[tuple[str, int, str, str]] = []
    jev = data.get("jev")
    if isinstance(jev, dict) and "blockedPaths" in jev:  # legacy
        paths = jev.pop("blockedPaths")  # legacy
        scope = data.get("scope")
        if not isinstance(scope, dict):
            scope = data["scope"] = {}
        have = scope.get("restrictedFolders") if isinstance(scope.get("restrictedFolders"), list) else []
        listed = paths if isinstance(paths, list) else []
        scope["restrictedFolders"] = list(have) + [p for p in listed if p not in have]
        if not jev:
            del data["jev"]
        rewrites.append(("jev.blockedPaths", len(listed), "jev.blockedPaths", "scope.restrictedFolders"))  # legacy
    roles = data.get("roles")
    if isinstance(roles, dict):
        renamed: dict = {}
        for name, value in roles.items():
            new = ROLE_RENAMES.get(name)
            if new is not None and new not in roles:
                renamed[new] = value
                rewrites.append(("roles", 1, name, new))
            else:
                renamed[name] = value
        if renamed != roles or list(renamed) != list(roles):
            data["roles"] = renamed
    if "idPrefixes" not in data:
        template = json.loads((TEMPLATE_ROOT / "lab.json").read_text(encoding="utf-8"))
        data["idPrefixes"] = template["idPrefixes"]
        rewrites.append(("idPrefixes", 1, "absent", "added"))
    if not rewrites:
        return None, []
    rewrites.sort(key=lambda item: ("jev.blockedPaths", "roles", "idPrefixes").index(item[0]))  # legacy
    return (json.dumps(data, indent=mcp_json_indent(raw), ensure_ascii=False) + "\n").encode("utf-8"), rewrites


def detect_old_layout(project_root: Path) -> list[str]:
    """The numbered folders of the 0.1 layout present under research_lab/."""
    lab = Path(project_root) / "research_lab"
    return [name for name in OLD_FOLDERS if (lab / name).is_dir()]


def _before_renames(rel: str, renames: list[tuple[str, str]]) -> str:
    """The path (relative to the project root) that holds `rel` before the planned renames run."""
    for old, new in reversed(renames):
        if rel == new:
            rel = old
        elif rel.startswith(new + "/"):
            rel = old + rel[len(new):]
    return rel


def plan_migration(project_root: Path, plan: Plan) -> None:
    """Plan the migration: fills plan.migration (the shown lines) and the steps apply_migration runs.

    A lab in the 0.1 layout gets the renames and rewrites and the column additions; a lab with the new layout only
    the column additions."""
    project_root = Path(project_root)
    if detect_old_layout(project_root):
        plan.migration_old_layout = True
        _plan_old_layout(project_root, plan)
    else:
        _plan_added_columns(project_root, plan)


def _plan_added_columns(project_root: Path, plan: Plan) -> None:
    """The column additions alone, for a lab that already has the new layout (nothing else in a table changes)."""
    headers: list[str] = []
    rewrites: list[str] = []
    for spec in TABLES:
        if not spec.added:
            continue
        rel = f"research_lab/{spec.path}"
        text = _read_text(project_root / rel)
        if text is None:
            continue
        _, header_changes, token_changes = transform_table(text, added_only(spec), plan.warn)
        headers += [f"header {rel}: {old} -> {new}" for old, new in header_changes]
        rewrites += [f"rewrite {rel}: {column}, {n} rows: {old} -> {new}" for column, n, old, new in token_changes]
    plan.migration += headers + rewrites


def _plan_old_layout(project_root: Path, plan: Plan) -> None:
    lab = project_root / "research_lab"
    renames: list[tuple[str, str]] = []  # project-relative (old, new), in the order they run

    def exists(rel: str) -> bool:
        return os.path.lexists(project_root / rel)

    def try_rename(old: str, new: str) -> bool:
        if not exists(old):
            return False
        if exists(new):
            plan.warn.append(f"unexpected layout: {old} and {new} both exist; nothing was moved for it")
            return False
        renames.append((old, new))
        plan.migration.append(f"rename {old} -> {new}")
        return True

    for old_name, new_name in OLD_FOLDERS.items():
        try_rename(f"research_lab/{old_name}", f"research_lab/{new_name}")
    for old, new in OTHER_FOLDER_RENAMES:
        try_rename(f"research_lab/{old}", f"research_lab/{new}")
    renamed_to = {new for _, new in renames}
    for folder in OLD_FOLDERS.values():
        if f"research_lab/{folder}" not in renamed_to and any(
            exists(f"research_lab/{old}") for old, target in OLD_FOLDERS.items() if target == folder
        ):
            plan.migration_skip_folders.append(folder)
    for old, new in INNER_RENAMES:
        folder = new.split("/")[0]
        if folder in plan.migration_skip_folders:
            continue
        source = _before_renames(f"research_lab/{old}", renames)
        if not exists(source):
            continue
        if exists(_before_renames(f"research_lab/{new}", renames)):
            plan.warn.append(f"unexpected layout: research_lab/{old} and research_lab/{new} both exist; nothing was moved for it")
            continue
        renames.append((f"research_lab/{old}", f"research_lab/{new}"))
        plan.migration.append(f"rename research_lab/{old} -> research_lab/{new}")
    meetings = project_root / _before_renames(f"research_lab/{MEETINGS_FOLDER}", renames)
    if meetings.is_dir():
        for entry in sorted(meetings.iterdir()):
            for old_suffix, new_suffix in MEETING_SUFFIXES:
                if entry.is_file() and entry.name.endswith(old_suffix):
                    old = f"research_lab/{MEETINGS_FOLDER}/{entry.name}"
                    new = f"research_lab/{MEETINGS_FOLDER}/{entry.name[: -len(old_suffix)]}{new_suffix}"
                    if exists(_before_renames(new, renames)):
                        plan.warn.append(f"unexpected layout: {old} and {new} both exist; nothing was moved for it")
                    else:
                        renames.append((old, new))
                        plan.migration.append(f"rename {old} -> {new}")
    plan.migration_renames = renames

    headers: list[str] = []
    rewrites: list[str] = []
    for spec in TABLES:
        rel = f"research_lab/{spec.path}"
        if spec.path.split("/")[0] in plan.migration_skip_folders:
            continue
        path = project_root / _before_renames(rel, renames)
        text = _read_text(path)
        if text is None:
            continue
        _, header_changes, token_changes = transform_table(text, spec, plan.warn)
        headers += [f"header {rel}: {old} -> {new}" for old, new in header_changes]
        rewrites += [f"rewrite {rel}: {column}, {n} rows: {old} -> {new}" for column, n, old, new in token_changes]
    plan.migration += headers + rewrites

    memory = lab / "memory"
    if memory.is_dir():
        for path in sorted(memory.rglob("*.md")):
            text = _read_text(path)
            if text is None:
                continue
            _, changes = transform_frontmatter(text)
            rel = path.relative_to(project_root).as_posix()
            plan.migration += [f"rewrite {rel}: {column}, {n} rows: {old} -> {new}" for column, n, old, new in changes]

    lab_json = lab / "lab.json"
    if lab_json.is_file() and not is_symlink(lab_json):
        raw = read_bytes_or_none(lab_json)
        try:
            new_raw, changes = transform_lab_json(raw if raw is not None else b"")
        except ValueError as exc:
            plan.warn.append(f"research_lab/lab.json is not valid JSON ({exc}); it was left unchanged")
        else:
            if new_raw is not None:
                plan.lab_json_migrated = new_raw
                plan.migration += [
                    f"rewrite {LAB_JSON_REL}: {column}, {n} rows: {old} -> {new}" for column, n, old, new in changes
                ]
    attributes = project_root / _before_renames(GITATTRIBUTES_REL, renames)
    text = _read_text(attributes)
    if text is not None:
        _, count = transform_gitattributes(text)
        if count:
            plan.migration.append(
                f"rewrite {GITATTRIBUTES_REL}: patterns, {count} lines: "
                f"{GITATTRIBUTES_OLD_PREFIX} -> {GITATTRIBUTES_NEW_PREFIX}"
            )

    for rel in INSTRUCTION_FILES:
        raw = read_bytes_or_none(project_root / rel)
        if raw is not None and OLD_BRIEF_IMPORT.encode("utf-8") in raw:
            plan.warn.append(
                f"{rel} imports {OLD_BRIEF_IMPORT}PROJECT_BRIEF.md; change the import to "
                "research_lab/project/PROJECT_BRIEF.md by hand"
            )


def _read_text(path: Path) -> str | None:
    if is_symlink(path) or not path.is_file():
        return None
    raw = read_bytes_or_none(path)
    if raw is None:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _git_tracked(project_root: Path, rel: str) -> bool:
    result = run_git(["ls-files", "--", rel], project_root)
    return result is not None and result.returncode == 0 and bool(result.stdout.strip())


def _move(project_root: Path, old: str, new: str, warn: list[str]) -> bool:
    source, target = project_root / old, project_root / new
    if not os.path.lexists(source):
        return False
    if os.path.lexists(target):
        warn.append(f"unexpected layout: {old} and {new} both exist; nothing was moved for it")
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    if _git_tracked(project_root, old):
        result = run_git(["mv", "--", old, new], project_root)
        if result is not None and result.returncode == 0:
            return True
        warn.append(f"git mv failed for {old}; moved without git")
    os.rename(source, target)
    return True


def _write_text(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def apply_migration(project_root: Path, plan: Plan, warn: list[str]) -> list[str]:
    """Run the planned migration; returns the plan lines that were carried out."""
    project_root = Path(project_root)
    done: list[str] = []
    if not plan.migration:
        return done
    for old, new in plan.migration_renames:
        if _move(project_root, old, new, warn):
            done.append(f"rename {old} -> {new}")
    headers: list[str] = []
    rewrites: list[str] = []
    for spec in TABLES:
        rel = f"research_lab/{spec.path}"
        if plan.migration_old_layout:
            if spec.path.split("/")[0] in plan.migration_skip_folders:
                continue
        elif spec.added:
            spec = added_only(spec)
        else:
            continue
        path = project_root / rel
        text = _read_text(path)
        if text is None:
            continue
        new_text, header_changes, token_changes = transform_table(text, spec)
        if new_text != text:
            _write_text(path, new_text)
        headers += [f"header {rel}: {old} -> {new}" for old, new in header_changes]
        rewrites += [f"rewrite {rel}: {column}, {n} rows: {old} -> {new}" for column, n, old, new in token_changes]
    done += headers + rewrites
    if not plan.migration_old_layout:
        return done
    memory = project_root / "research_lab" / "memory"
    if memory.is_dir():
        for path in sorted(memory.rglob("*.md")):
            text = _read_text(path)
            if text is None:
                continue
            new_text, changes = transform_frontmatter(text)
            if new_text != text:
                _write_text(path, new_text)
            rel = path.relative_to(project_root).as_posix()
            done += [f"rewrite {rel}: {column}, {n} rows: {old} -> {new}" for column, n, old, new in changes]
    lab_json = project_root / LAB_JSON_REL
    if plan.lab_json_migrated is not None and lab_json.is_file():
        raw = read_bytes_or_none(lab_json)
        try:
            new_raw, changes = transform_lab_json(raw if raw is not None else b"")
        except ValueError:
            new_raw, changes = None, []
        if new_raw is not None:
            lab_json.write_bytes(new_raw)
            done += [f"rewrite {LAB_JSON_REL}: {column}, {n} rows: {old} -> {new}" for column, n, old, new in changes]
    attributes = project_root / GITATTRIBUTES_REL
    text = _read_text(attributes)
    if text is not None:
        new_text, count = transform_gitattributes(text)
        if count:
            _write_text(attributes, new_text)
            done.append(
                f"rewrite {GITATTRIBUTES_REL}: patterns, {count} lines: "
                f"{GITATTRIBUTES_OLD_PREFIX} -> {GITATTRIBUTES_NEW_PREFIX}"
            )
    return done


# --- the scholarly output style ----------------------------------------------------------------------


def plan_output_style(project_root: Path, plan: Plan) -> None:
    target = project_root / OUTPUT_STYLE_REL
    if os.path.lexists(target):
        plan.output_style = {"file": OUTPUT_STYLE_REL, "action": "skip"}
    elif not OUTPUT_STYLE_SOURCE.is_file():
        plan.warn.append("plugin file missing: output-styles/scholarly-explanatory.md; the output style was not planned")
    else:
        plan.output_style = {"file": OUTPUT_STYLE_REL, "action": "create", "setting": OUTPUT_STYLE_SETTING}


def apply_output_style(project_root: Path) -> bool:
    text = OUTPUT_STYLE_SOURCE.read_bytes().decode("utf-8").replace("\r\n", "\n")
    return write_new(project_root / OUTPUT_STYLE_REL, text)


# --- plan --------------------------------------------------------------------------------------------


def tracks_after(project_root: Path, opts: Options) -> list[str]:
    """The tracks in the lab's lab.json now, then the ones asked for (order of first appearance)."""
    raw = read_bytes_or_none(Path(project_root) / LAB_JSON_REL)
    have: list[str] = []
    if raw is not None:
        try:
            listed = parse_lab_json(raw).get("tracks")
        except ValueError:
            listed = None
        if isinstance(listed, list):
            have = [t for t in listed if isinstance(t, str)]
    return have + [t for t in opts.tracks if t not in have]


def build_plan(project_root: Path, opts: Options) -> Plan:
    project_root = Path(project_root)
    plan = Plan()

    # 0: a 0.1 lab is migrated first; what the migration moves counts as present below.
    plan_migration(project_root, plan)

    def present(rel: str) -> bool:
        return os.path.lexists(project_root / rel)

    def present_after_migration(rel: str) -> bool:
        return present(rel) or os.path.lexists(project_root / _before_renames(rel, plan.migration_renames))

    # 1 and 2: template files and the files copied from other skills; --track limits them to the tracks' sets.
    track_set = {rel for track in opts.tracks for rel in TRACK_FILES[track]}
    for rel, source in template_files().items():
        if opts.tracks and rel not in track_set:
            continue
        if rel == LAB_JSON_REL and present(rel):
            continue  # merged below, once the connectors and permissions are planned
        if present(rel):
            plan.skip.append(rel)
        elif present_after_migration(rel):
            continue  # the migration moves it into place
        elif not source.is_file():
            try:
                shown = source.relative_to(PLUGIN_ROOT).as_posix()
            except ValueError:
                shown = source.as_posix()
            plan.warn.append(f"plugin file missing: {shown}; {rel} was not planned")
        else:
            plan.create.append(rel)

    # 3: the store's .gitattributes.
    wanted = load_artifacts().GITATTRIBUTES_HEADER[1:]
    attrs = project_root / GITATTRIBUTES_REL
    if not os.path.lexists(attrs):
        plan.create.append(GITATTRIBUTES_REL)
    else:
        raw = read_bytes_or_none(attrs)
        if raw is None:
            plan.warn.append(f"cannot read {GITATTRIBUTES_REL}; left alone")
        else:
            lines = {line.strip() for line in raw.decode("utf-8", errors="replace").splitlines()}
            has_both = all(rule in lines for rule in wanted)
            (plan.skip if has_both else plan.append).append(GITATTRIBUTES_REL)

    # 4: the instructions file that holds the lab section.
    plan_instructions(project_root, plan, opts)

    # 4b: connectors into .mcp.json.
    if opts.connectors:
        plan_connectors(project_root, opts, plan)

    # 4c: opt-in project permission rules.
    if opts.permissions:
        plan_permissions(project_root, opts, plan)

    # 4d: an existing lab.json takes the connectors, the permissions flag, the version and the folders.
    if present(LAB_JSON_REL):
        plan_lab_json(project_root, opts, plan)

    # 4e: the scholarly output style.
    plan_output_style(project_root, plan)

    # 5: .gitignore.
    ignore = project_root / ".gitignore"
    if not os.path.lexists(ignore):
        plan.append.append(".gitignore")
    elif is_symlink(ignore):
        plan.warn.append(symlink_warning(".gitignore", ignore, "add the lines by hand"))
    else:
        raw = read_bytes_or_none(ignore)
        if raw is None:
            plan.warn.append("cannot read .gitignore; left alone")
        else:
            missing = missing_gitignore_lines(raw)
            (plan.append if missing else plan.skip).append(".gitignore")

    # 6: references/.
    (plan.skip if present("references") else plan.create).append(REFERENCES_REL)

    # 7: git init.
    if opts.git_init:
        if present(".git"):
            plan.warn.append("already a git repository; --git-init ignored")
        else:
            plan.create.append(GIT_REL)

    # 8: git-lfs.
    if not git_lfs_available(project_root):
        plan.warn.append(
            "git-lfs is not installed; the artifact archive needs it for files at or above "
            f"lfs.thresholdMB ({opts.lfs_threshold_mb} MB): install it before saving large artifacts"
        )
    # 8b: the tracks lab.json holds after the run.
    plan.tracks = tracks_after(project_root, opts)
    # 9: duplicates of plugin agents and skills: reported, never touched.
    plan.duplicates = find_duplicates(project_root)
    if plan.duplicates:
        plan.warn.append(
            "same names as the plugin's agents or skills were left in place; "
            "check each for local changes and remove it by hand: "
            + ", ".join(plan.duplicates)
        )
    return plan


# --- apply -------------------------------------------------------------------------------------------


def write_new(dest: Path, text: str) -> bool:
    """Create `dest` with `text`; False when it already exists."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(dest, "x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    except FileExistsError:
        return False
    return True


def append_bytes(dest: Path, data: bytes) -> None:
    with open(dest, "ab") as handle:
        handle.write(data)


def ends_with_blank_line(raw: bytes) -> bool:
    return raw.endswith(b"\n\n") or raw.endswith(b"\r\n\r\n")


def apply_claude(project_root: Path, opts: Options, action: str, rel: str = "CLAUDE.md") -> bool:
    dest = project_root / rel
    section = claude_section(project_root, opts)
    if rel != "CLAUDE.md":
        # Claude Code resolves an @import relative to the file that holds it.
        section = section.replace("@research_lab/", "@../research_lab/")
    if action == "create":
        return write_new(dest, section)
    raw = dest.read_bytes()
    if BEGIN_MARKER.encode("utf-8") in raw:
        return False
    eol = b"\r\n" if b"\r\n" in raw else b"\n"  # a CRLF file stays CRLF
    if not raw or ends_with_blank_line(raw):
        gap = b""
    elif raw.endswith(b"\n"):
        gap = eol
    else:
        gap = eol + eol
    append_bytes(dest, gap + section.encode("utf-8").replace(b"\n", eol))
    return True


def apply_section_refresh(project_root: Path, opts: Options, rel: str) -> bool:
    """Replace the lab section between the markers with the current template; the rest of the file and its
    line endings stay as they are."""
    dest = project_root / rel
    raw = dest.read_bytes()
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    bounds = section_bounds(text)
    if bounds is None:
        return False
    section = claude_section(project_root, opts).strip("\n")
    if rel != "CLAUDE.md":
        section = section.replace("@research_lab/", "@../research_lab/")
    new_text = text[:bounds[0]] + section + text[bounds[1]:]
    with open(dest, "wb") as handle:
        handle.write(new_text.encode("utf-8").replace(b"\n", eol))
    return True


def apply_gitignore(project_root: Path) -> bool:
    dest = project_root / ".gitignore"
    raw = dest.read_bytes() if os.path.lexists(dest) else b""
    missing = missing_gitignore_lines(raw)
    if not missing:
        return False
    lead = b"\n" if raw and not raw.endswith(b"\n") else b""
    append_bytes(dest, lead + ("\n".join(missing) + "\n").encode("utf-8"))
    return True


def apply_gitattributes(project_root: Path) -> bool:
    store_module = load_artifacts()
    lab = project_root / "research_lab"
    lab.mkdir(parents=True, exist_ok=True)
    (lab / "artifacts").mkdir(parents=True, exist_ok=True)
    return bool(store_module.LabStore(lab).ensure_gitattributes())


def apply_lab_json(project_root: Path, opts: Options, configured: list[str], permissions_written: bool) -> bool:
    """Merge into the lab.json on disk; False (nothing written) when no value in it needs to change."""
    dest = project_root / LAB_JSON_REL
    text = merged_lab_json_text(dest.read_bytes(), opts, configured, permissions_written)
    if text is None:
        return False
    with open(dest, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return True


def apply_item(
    rel: str,
    action: str,
    project_root: Path,
    opts: Options,
    files: dict[str, Path],
    plan: Plan | None = None,
    permissions_written: bool = False,
) -> bool:
    """Carry out one planned item; True when something was written, False when it already existed."""
    plan = plan or Plan()
    if rel == ".mcp.json":
        return apply_mcp_json(project_root, action, plan.connectors)
    if rel == SETTINGS_REL:
        return write_new(project_root / rel, settings_text(plan.permissions.get("rules", [])))
    if rel == LAB_JSON_REL and action == "append":
        return apply_lab_json(project_root, opts, plan.configured_connectors, permissions_written)
    if rel == LAB_JSON_REL:
        return write_new(
            project_root / rel,
            build_lab_json(project_root, opts, plan.configured_connectors, permissions_written),
        )
    if rel in files:
        return write_new(project_root / rel, read_template(files[rel], substitutions(project_root, opts)))
    if rel == GITATTRIBUTES_REL:
        return apply_gitattributes(project_root)
    if rel in INSTRUCTION_FILES:
        return apply_claude(project_root, opts, action, rel)
    if rel == ".gitignore":
        return apply_gitignore(project_root)
    if rel == REFERENCES_REL:
        target = project_root / "references"
        if os.path.lexists(target):
            return False
        target.mkdir(parents=True)
        return True
    raise ValueError(f"no handler for {rel}")


def git_commit_scaffold(project_root: Path, created: list[str], left: list[str], warn: list[str]) -> None:
    """git init, then commit research_lab/ and the files init created; the files it only appended to stay out."""
    result = run_git(["init", "-b", "main"], project_root)
    if result is None:
        warn.append("git is not installed; --git-init skipped")
        return
    if result.returncode != 0:
        warn.append(f"git init failed: {result.stderr.strip() or result.stdout.strip()}")
        return
    # research_lab/ is the lab's own folder (its ignored .working stays out); anywhere else only the exact
    # files init created are added, never a whole folder such as .claude/ that may hold personal files.
    paths: list[str] = []
    for rel in created:
        path = "research_lab" if rel.startswith("research_lab/") else rel
        if path not in paths:
            paths.append(path)
    if paths:
        result = run_git(["add", "--", *paths], project_root)
        if result is None or result.returncode != 0:
            detail = result.stderr.strip() if result is not None else "git could not be started"
            warn.append(f"git add failed: {detail}")
            return
    result = run_git(["commit", "-m", COMMIT_MESSAGE], project_root)
    if result is None or result.returncode != 0:
        detail = (result.stderr.strip() or result.stdout.strip()) if result is not None else "git could not be started"
        warn.append(f"git commit failed: {detail}")
        return
    for rel in left:
        warn.append(f"review and commit {rel} yourself: init appended to it and left it out of the first commit")


def _order(rel: str) -> int:
    if rel == SETTINGS_REL:
        return -1  # first, so lab.json records whether the settings file really was written
    if rel == GIT_REL:
        return 2
    if rel == GITATTRIBUTES_REL:
        return 1
    return 0


def apply_plan(plan: Plan, project_root: Path, opts: Options) -> dict:
    project_root = Path(project_root)
    files = template_files()
    report = {
        "create": [],
        "append": [],
        "skip": list(plan.skip),
        "warn": list(plan.warn),
        "connectors": plan.connectors,
        "duplicates": list(plan.duplicates),
        "permissions": dict(plan.permissions),
        "written": [],
        "migration": [],
        "outputStyle": dict(plan.output_style),
        "tracks": list(plan.tracks),
    }
    report["migration"] = apply_migration(project_root, plan, report["warn"])
    if plan.section_refresh and apply_section_refresh(project_root, opts, plan.section_refresh):
        report["migration"].append(f"rewrite {plan.section_refresh}: the lab section between the markers -> the current template")
    permissions_written = False
    items = [(rel, "create") for rel in plan.create] + [(rel, "append") for rel in plan.append]
    items.sort(key=lambda item: _order(item[0]))
    existed = {rel: os.path.lexists(project_root / rel) for rel, _ in items}
    created: list[str] = []  # files init made, whatever the plan called them
    left: list[str] = []  # files outside research_lab/ that init only appended to: the researcher commits them
    git_planned = False
    for rel, action in items:
        if rel == GIT_REL:
            git_planned = True
            continue
        try:
            done = apply_item(rel, action, project_root, opts, files, plan, permissions_written)
        except Exception as exc:  # one item failing never stops the run
            report["warn"].append(f"could not write {rel}: {exc}")
            continue
        if not done:
            report["skip"].append(rel)
            continue
        if rel == SETTINGS_REL:
            permissions_written = True
        report[action].append(rel)
        if not rel.endswith("/"):
            report["written"].append(rel)
            if action == "create" or not existed[rel]:
                created.append(rel)
            elif not rel.startswith("research_lab/"):
                left.append(rel)
    if plan.output_style.get("action") == "create":
        try:
            if apply_output_style(project_root):
                report["written"].append(OUTPUT_STYLE_REL)
                created.append(OUTPUT_STYLE_REL)
            else:
                report["outputStyle"]["action"] = "skip"
        except OSError as exc:
            report["warn"].append(f"could not write {OUTPUT_STYLE_REL}: {exc}")
    if git_planned:
        git_commit_scaffold(project_root, created, left, report["warn"])
        if os.path.isdir(project_root / ".git"):
            report["create"].append(GIT_REL)
    return report


# --- command line ------------------------------------------------------------------------------------


def positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not an integer: {text!r}")
    if value <= 0:
        raise argparse.ArgumentTypeError(f"must be greater than 0: {value}")
    return value


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="init_lab.py",
        description="Set up a research lab in a project folder. Prints the plan; --yes applies it.",
    )
    parser.add_argument("--project-root", help="project folder (default: the git top-level, else the cwd)")
    parser.add_argument("--name", required=True, help="the project's name")
    parser.add_argument("--short-name", help="short name (default: a lowercase slug of the name)")
    parser.add_argument("--description", default="", help="one or two sentences")
    parser.add_argument("--lfs-threshold-mb", type=positive_int, default=10, help="Git Large File Storage (LFS) threshold in MB (default 10)")
    parser.add_argument("--git-init", action="store_true", help="git init and commit the lab set-up when there is no repository")
    parser.add_argument(
        "--connectors",
        default="",
        help="comma-separated connector ids from connectors.json, and/or `science` for every science MCP entry",
    )
    parser.add_argument(
        "--permissions",
        action="store_true",
        help="write .claude/settings.json with WebFetch allow rules for the literature domains (only if absent)",
    )
    parser.add_argument(
        "--allow-domain",
        action="append",
        default=[],
        metavar="HOST",
        help="one more host to allow with --permissions (repeatable)",
    )
    parser.add_argument(
        "--out-of-scope",
        action="append",
        default=[],
        metavar="FOLDER",
        help="a folder no role may open; written to the brief and to lab.json (repeatable)",
    )
    parser.add_argument(
        "--track",
        action="append",
        default=[],
        choices=TRACKS,
        metavar="{" + ",".join(TRACKS) + "}",
        help="set up only the minimal lab for one track (repeatable); without it, the whole lab",
    )
    parser.add_argument("--yes", action="store_true", help="apply the plan (without it nothing is written)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="print the report as JSON")
    return parser.parse_args(argv)


def resolve_root(given: str | None, parser_error) -> Path:
    if given:
        root = Path(given)
        if not root.is_dir():
            parser_error(f"--project-root is not a directory: {given}")
        return root.resolve()
    cwd = Path.cwd()
    return (git_toplevel(cwd) or cwd).resolve()


def render(report: dict, as_json: bool, dry_run: bool = False) -> str:
    if as_json:
        return json.dumps(report, indent=2, ensure_ascii=False)
    lines = list(report.get("migration") or [])
    lines += [f"{verb} {path}" for verb in ("create", "append", "skip") for path in report[verb]]
    lines += [f"warn {text}" for text in report["warn"]]
    style = report.get("output_style") or report.get("outputStyle") or {}
    if style.get("file"):
        lines.append(f"output-style {style['file']}: {style['action']}")
        if style["action"] == "create":
            lines.append("settings line to add to .claude/settings.json:")
            lines.append(f"  {style['setting']}")
    permissions = report.get("permissions") or {}
    if permissions.get("action") == "skip":
        lines.append(f"rules to merge into {permissions['file']}:")
        lines += settings_text(permissions["rules"]).splitlines()
    lines.append(DRY_RUN_LINE if dry_run else f"written: {len(report['written'])} files")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args = parse_args(argv)

    def fail(message: str) -> None:
        print(f"init_lab.py: error: {message}", file=sys.stderr)
        raise SystemExit(2)

    if not args.name.strip():
        fail("--name must not be empty")
    if args.allow_domain and not args.permissions:
        fail("--allow-domain needs --permissions")
    allow_domains: list[str] = []
    for given in args.allow_domain:
        host = given.strip().lower()
        if not HOST_RE.fullmatch(host):
            fail(f"invalid --allow-domain host: {given.strip()}")
        if host not in allow_domains:
            allow_domains.append(host)
    out_of_scope: list[str] = []
    for given in args.out_of_scope:
        folder = clean_scope_folder(given)
        if folder is None:
            fail(f"invalid --out-of-scope folder: {given!r}")
        if folder not in out_of_scope:
            out_of_scope.append(folder)
    try:
        connectors = resolve_connectors(args.connectors)
    except ValueError as exc:
        for cid in exc.args[0]:
            print(f"init_lab.py: error: unknown connector id: {cid}", file=sys.stderr)
        raise SystemExit(2)
    tracks: list[str] = []
    for track in args.track:
        if track not in tracks:
            tracks.append(track)
    root = resolve_root(args.project_root, fail)
    opts = Options(
        name=args.name,
        short_name=args.short_name or slugify(args.name),
        description=args.description,
        lfs_threshold_mb=args.lfs_threshold_mb,
        git_init=args.git_init,
        yes=args.yes,
        json_output=args.json_output,
        project_root=root,
        connectors=connectors,
        permissions=args.permissions,
        allow_domains=allow_domains,
        out_of_scope=out_of_scope,
        tracks=tracks,
    )
    plan = build_plan(root, opts)
    if not opts.yes:
        internal = ("migration_renames", "migration_skip_folders", "lab_json_migrated", "migration_old_layout")
        out = {**{k: v for k, v in plan.__dict__.items() if k not in internal}, "projectRoot": root.as_posix()}
        if not opts.json_output:
            # the order the applied report lists them in
            out["create"] = sorted(plan.create, key=_order)
            out["append"] = sorted(plan.append, key=_order)
        print(render(out, opts.json_output, dry_run=True))
        return 0
    report = apply_plan(plan, root, opts)
    report["projectRoot"] = root.as_posix()
    print(render(report, opts.json_output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
