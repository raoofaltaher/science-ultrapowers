#!/usr/bin/env python3
"""Scaffold a project-local research lab: compute a plan, print it, apply it with --yes.

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
    "findings-ledger",
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
    "research_lab/templates/SESSION_KICKOFF.md": "holding-lab-meetings/templates/SESSION_KICKOFF.md",
    "research_lab/templates/SESSION_STANDUP.md": "holding-lab-meetings/templates/SESSION_STANDUP.md",
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
    connectors: list[str] = field(default_factory=list)  # catalogue ids, resolved and in catalogue order
    permissions: bool = False
    allow_domains: list[str] = field(default_factory=list)  # lowercased, validated hosts
    out_of_scope: list[str] = field(default_factory=list)  # cleaned folders no role may open


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
    """Section 7 of the brief: a bullet per folder, else the prompt for your human partner to answer."""
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
    data["connectors"] = [e["id"] for e in load_catalogue() if e["id"] in chosen and e["kind"] == "mcp"]
    data["jev"]["blockedPaths"] = list(opts.out_of_scope)
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

    Only these change: the plugin version, the connectors list (union with the ones configured now, catalogue
    order), permissions.written (only ever to true) and jev.blockedPaths (union with --out-of-scope)."""
    changed = False
    version = plugin_version()
    if version != "unknown" and data.get("pluginVersion") != version:
        data["pluginVersion"] = version
        changed = True
    if configured:
        have = data.get("connectors") if isinstance(data.get("connectors"), list) else []
        wanted = set(have) | set(configured)
        merged = [e["id"] for e in load_catalogue() if e["id"] in wanted]
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
        jev = data.get("jev")
        if not isinstance(jev, dict):
            jev = data["jev"] = {}
        have_paths = jev.get("blockedPaths") if isinstance(jev.get("blockedPaths"), list) else []
        merged_paths = list(have_paths) + [p for p in opts.out_of_scope if p not in have_paths]
        if merged_paths != jev.get("blockedPaths"):
            jev["blockedPaths"] = merged_paths
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


def plan_instructions(project_root: Path, plan: Plan) -> None:
    """Decide which instructions file gets the lab section: never a second section anywhere."""
    existing = [rel for rel in INSTRUCTION_FILES if os.path.lexists(project_root / rel)]
    unreadable: list[str] = []
    for rel in existing:
        raw = read_bytes_or_none(project_root / rel)
        if raw is None:
            unreadable.append(rel)
        elif BEGIN_MARKER in raw.decode("utf-8", errors="replace"):
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
    for name in roles:
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


def load_catalogue() -> list[dict]:
    path = SKILL_ROOT / "connectors.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"init_lab: cannot read the connector catalogue {path}: {exc}")
    if not isinstance(data, list):
        raise SystemExit(f"init_lab: the connector catalogue {path} must be a list")
    return data


def resolve_connectors(text: str) -> list[str]:
    """Ids and the word `science`, comma separated -> catalogue ids in catalogue order.

    Raises ValueError carrying the list of unknown ids."""
    catalogue = load_catalogue()
    known = {entry["id"] for entry in catalogue}
    chosen: set[str] = set()
    unknown: list[str] = []
    for item in (part.strip() for part in text.split(",")):
        if not item:
            continue
        if item == "science":
            chosen.update(e["id"] for e in catalogue if e["kind"] == "mcp" and e.get("tag") == "science")
        elif item in known:
            chosen.add(item)
        elif item not in unknown:
            unknown.append(item)
    if unknown:
        raise ValueError(unknown)
    return [e["id"] for e in catalogue if e["id"] in chosen]


def server_entry(entry: dict, project_root: Path) -> dict:
    """The .mcp.json server for one `mcp` catalogue entry."""
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
    catalogue = {entry["id"]: entry for entry in load_catalogue()}
    desired: dict[str, dict] = {}
    for cid in opts.connectors:
        entry = catalogue[cid]
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


# --- plan --------------------------------------------------------------------------------------------


def build_plan(project_root: Path, opts: Options) -> Plan:
    project_root = Path(project_root)
    plan = Plan()

    def present(rel: str) -> bool:
        return os.path.lexists(project_root / rel)

    # 1 and 2: template files and the files copied from other skills.
    for rel, source in template_files().items():
        if rel == LAB_JSON_REL and present(rel):
            continue  # merged below, once the connectors and permissions are planned
        if present(rel):
            plan.skip.append(rel)
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
    plan_instructions(project_root, plan)

    # 4b: connectors into .mcp.json.
    if opts.connectors:
        plan_connectors(project_root, opts, plan)

    # 4c: opt-in project permission rules.
    if opts.permissions:
        plan_permissions(project_root, opts, plan)

    # 4d: an existing lab.json takes the connectors, the permissions flag, the version and the folders.
    if present(LAB_JSON_REL):
        plan_lab_json(project_root, opts, plan)

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
            "git-lfs is not installed; the artifact store needs it for files at or above "
            f"lfs.thresholdMB ({opts.lfs_threshold_mb} MB): install it before saving large artifacts"
        )
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
    # research_lab/ is the lab's own folder (its ignored .scratch stays out); anywhere else only the exact
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
    }
    permissions_written = False
    items = [(rel, "create") for rel in plan.create] + [(rel, "append") for rel in plan.append]
    items.sort(key=lambda item: _order(item[0]))
    existed = {rel: os.path.lexists(project_root / rel) for rel, _ in items}
    created: list[str] = []  # files init made, whatever the plan called them
    left: list[str] = []  # files outside research_lab/ that init only appended to: your human partner commits them
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
        description="Scaffold a research lab in a project folder. Prints the plan; --yes applies it.",
    )
    parser.add_argument("--project-root", help="project folder (default: the git top-level, else the cwd)")
    parser.add_argument("--name", required=True, help="the project's name")
    parser.add_argument("--short-name", help="short name (default: a lowercase slug of the name)")
    parser.add_argument("--description", default="", help="one or two sentences")
    parser.add_argument("--lfs-threshold-mb", type=positive_int, default=10, help="LFS threshold in MB (default 10)")
    parser.add_argument("--git-init", action="store_true", help="git init and commit the scaffold when there is no repository")
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
    lines = [f"{verb} {path}" for verb in ("create", "append", "skip") for path in report[verb]]
    lines += [f"warn {text}" for text in report["warn"]]
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
    )
    plan = build_plan(root, opts)
    if not opts.yes:
        out = {**plan.__dict__, "projectRoot": root.as_posix()}
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
