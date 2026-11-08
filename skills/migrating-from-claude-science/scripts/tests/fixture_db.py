"""Build a fixture Claude Science data directory for the migration tests.

The database is created ONLY from the CREATE TABLE statements recorded in
docs/science-ultrapowers/claude-science-schema.md, so the fixture cannot drift
from the recorded schema. Every id and every value is invented.
"""

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA_DOC = Path(__file__).resolve().parents[4] / "docs" / "science-ultrapowers" / "claude-science-schema.md"

TABLES = (
    "projects", "memories", "user_agents", "frames", "frame_messages", "compaction_archives",
    "artifacts", "artifact_versions", "artifact_dependencies", "artifact_folders",
    "verification_checks", "execution_log", "directory_attachments",
    "capability_settings", "user_secrets",
)

ORG_UUID = "00000000-0000-4000-8000-0000000000f0"
USER_ID = "user-fixture-0001"
PROJECT_ID = "proj_fix"
OTHER_PROJECT_ID = "proj_other"
ORPHAN_ARTIFACT_ID = "00000000-0000-4000-8000-0000000dead0"
DIR_UUID_PUBMED = "00000000-0000-4000-8000-00000000d001"
DIR_UUID_UNLISTED = "00000000-0000-4000-8000-00000000d002"

T0 = 1760000000000  # epoch milliseconds, 13 digits


def create_statements():
    """Table name -> CREATE TABLE statement, parsed from the schema record."""
    text = SCHEMA_DOC.read_text(encoding="utf-8")
    start = text.index("\n## Tables")
    rest = text[start + 1:]
    end = re.search(r"^## (?!Tables)", rest, re.M)
    section = rest[: end.start()] if end else rest
    pattern = re.compile(r"^### (\w+)\n\n(`{3,})sql\n(.*?)\n\2$", re.M | re.S)
    statements = {m.group(1): m.group(3) for m in pattern.finditer(section)}
    missing = [t for t in TABLES if t not in statements]
    if missing:
        raise RuntimeError("schema record lacks tables: " + ", ".join(missing))
    return {t: statements[t] for t in TABLES}


@dataclass
class FixtureInfo:
    root: Path
    data_dir: Path
    org_uuid: str
    org_dir: Path
    db_path: Path
    project_id: str
    other_project_id: str
    artifacts: dict = field(default_factory=dict)
    versions: dict = field(default_factory=dict)
    frames: dict = field(default_factory=dict)
    memories: dict = field(default_factory=dict)
    files: dict = field(default_factory=dict)


def _uid(n):
    return "00000000-0000-4000-8000-%012x" % n


def _insert(conn, table, row):
    names = list(row)
    sql = "INSERT INTO {} ({}) VALUES ({})".format(
        table, ", ".join('"' + n + '"' for n in names), ", ".join("?" for _ in names)
    )
    conn.execute(sql, [row[n] for n in names])


def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    path.write_bytes(data)


def _write_json(path, value):
    _write(path, json.dumps(value, indent=2) + "\n")


def build_fixture(root, *, lint_rows=False):
    root = Path(root).resolve()
    root_posix = root.as_posix()
    org_dir = root / "orgs" / ORG_UUID
    org_dir.mkdir(parents=True, exist_ok=True)
    db_path = org_dir / "operon-cli.db"

    frame_ids = {"root": _uid(0xF01), "lit": _uid(0xF02), "other_lit": _uid(0xF03)}
    other_root = _uid(0xF04)
    if lint_rows:
        frame_ids["odd"] = _uid(0xF05)
    artifact_ids = {"a1": _uid(0xA01), "a2": _uid(0xA02), "a3": _uid(0xA03), "a4": _uid(0xA04)}
    version_ids = {
        "a1v1": _uid(0xB01), "a1v2": _uid(0xB02), "a2v1": _uid(0xB03),
        "a3v1": _uid(0xB04), "a4v1": _uid(0xB05),
    }
    memory_names = ["m1", "m2", "m3", "m4", "m5", "m6"]
    if lint_rows:
        memory_names += ["m7", "m8", "m9", "m10", "m11"]
    memory_ids = {name: _uid(0xC00 + i + 1) for i, name in enumerate(memory_names)}
    folder_id = _uid(0xE01)
    exec_id = _uid(0xE11)

    info = FixtureInfo(
        root=root, data_dir=root, org_uuid=ORG_UUID, org_dir=org_dir, db_path=db_path,
        project_id=PROJECT_ID, other_project_id=OTHER_PROJECT_ID,
        artifacts=artifact_ids, versions=version_ids, frames=frame_ids, memories=memory_ids,
    )

    # Files on disk.
    artifact_root = org_dir / "artifacts" / PROJECT_ID
    hexes = {"a1v1": "1a2b3c4d", "a1v2": "5e6f7a8b", "a2v1": "9c0d1e2f"}
    names = {"a1v1": "results.csv", "a1v2": "results.csv", "a2v1": "notes.md"}
    owners = {"a1v1": "a1", "a1v2": "a1", "a2v1": "a2"}
    contents = {
        "a1v1": b"split,score\ndev,0.71\n",
        "a1v2": b"split,score\ndev,0.71\ntest,0.64\n",
        "a2v1": b"# Notes\nA short note.\n",
    }
    checksums = {}
    storage = {}
    for name in ("a1v1", "a1v2", "a2v1"):
        leaf = "v" + hexes[name] + "_" + names[name]
        path = artifact_root / artifact_ids[owners[name]] / leaf
        _write(path, contents[name])
        info.files[name] = path
        checksums[name] = hashlib.sha256(contents[name]).hexdigest()
        storage[name] = "\\".join((PROJECT_ID, artifact_ids[owners[name]], leaf))
    host_file = root / "host" / "data.csv"
    host_bytes = b"id,value\n1,10\n2,20\n"
    _write(host_file, host_bytes)
    absent_file = root / "host" / "absent.csv"
    info.files["a3v1"] = host_file
    info.files["a4v1"] = absent_file
    checksums["a3v1"] = hashlib.sha256(host_bytes).hexdigest()
    checksums["a4v1"] = hashlib.sha256(b"absent").hexdigest()
    storage["a3v1"] = "~/" + host_file.as_posix()
    storage["a4v1"] = "~/" + absent_file.as_posix()

    for skill, text in (
        ("doi-verified-evidence", "Cite only sources whose DOI you verified.\nState the DOI beside every claim.\n"),
        ("peer-review", "Review the manuscript as a peer.\nReport findings by severity.\n"),
    ):
        _write(org_dir / "skills" / skill / "SKILL.md", text)

    # Config, connector cache, preferences.
    _write(root / "config.toml", "data_dir = " + json.dumps(root_posix) + '\nlast_move_from = ""\n')
    connector = {
        "source": "directory", "authState": "authorized", "transport": "streamable_http",
        "iconUrl": "", "hidden": False, "isOrgProvisioned": False,
    }
    _write_json(root / "mcp" / "directory-cache.json", {
        "fetchedAt": T0,
        "accountId": "acct-fixture",
        "connectors": [
            dict(connector, id=DIR_UUID_PUBMED, name="PubMed",
                 backendUrl="https://pubmed.mcp.claude.com/mcp"),
            dict(connector, id=DIR_UUID_UNLISTED, name="Some Unlisted Server",
                 backendUrl="https://mcp.unlisted.example/mcp"),
        ],
    })
    _write_json(org_dir / "preferences.json", {
        "approvalGrants": {
            "always": {
                "allow": {"network": ["data.example.org"], "host": ["rw:" + root_posix + "/host"]},
                "deny": {},
                "ask": {},
            },
            "alwaysOrigins": {
                "host": {},
                "network": {"data.example.org": {
                    "userId": "u1", "rootFrameId": frame_ids["root"], "projectId": PROJECT_ID,
                }},
            },
            "project": {
                PROJECT_ID: {
                    "allow": {
                        "local_exec": ["python"],
                        "credential_access": ["TYPESAFE_API_KEY"],
                        "customize_mutation": [],
                    },
                    "deny": {}, "ask": {},
                },
                OTHER_PROJECT_ID: {"allow": {"local_exec": ["Rscript"]}, "deny": {}, "ask": {}},
            },
        },
        "hostGrants": [],
        "userAllowedDomains": [],
        "builtinAllowlistDisabledGroups": ["clinical"],
        "autoMode": False,
        "gpuEnabled": False,
        "reviewerModel": "fixture-reviewer-model",
        "memoryEnabled": True,
    })

    # Database.
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    try:
        for statement in create_statements().values():
            conn.execute(statement)

        for pid, name, description in (
            (PROJECT_ID, "Fixture Study", "A fixture project"),
            (OTHER_PROJECT_ID, "Other Project", None),
        ):
            _insert(conn, "projects", {
                "id": pid, "name": name, "description": description,
                "created_at": T0, "updated_at": T0, "user_id": USER_ID,
            })

        for name, display, prompt, skills in (
            ("LAB_PROJECT_MANAGER", "Lab Project Manager",
             "You are the project manager of the lab.\nYou keep the task board.",
             ["doi-verified-evidence", "peer-review", "pdf-explore", "deep-research",
              "theme-factory", "no-such-skill"]),
            ("OPERON", "Operon", "You are the main agent.", []),
        ):
            _insert(conn, "user_agents", {
                "id": _uid(0x501 if name == "OPERON" else 0x502), "user_id": USER_ID,
                "name": name, "display_name": display,
                "description": "Fixture profile " + name, "system_prompt": prompt,
                "skill_names": json.dumps(skills), "created_at": T0, "updated_at": T0,
            })

        def frame(key, agent, parent, root_key_id, project, **extra):
            row = {
                "id": frame_ids[key], "parent_frame_id": parent, "root_frame_id": root_key_id,
                "agent_name": agent, "status": "completed", "created_at": T0, "updated_at": T0,
                "project_id": project, "conversation_type": "agent",
                "model": "fixture-model", "effort": "medium", "is_hidden": 0,
                "input_tokens": 100, "output_tokens": 40, "total_cost": 0.25,
                "completed_at": T0 + 9000,
                "input_data": json.dumps({"task": "fixture input"}),
                "output_data": json.dumps({"result": "fixture output"}),
                "context_data": json.dumps({"note": "fixture context"}),
            }
            row.update(extra)
            _insert(conn, "frames", row)

        frame("root", "OPERON", None, frame_ids["root"], PROJECT_ID, name="Fixture kickoff")
        frame("lit", "LIT_RESEARCHER", frame_ids["root"], frame_ids["root"], PROJECT_ID,
              task_summary="Screened 12 papers for the review", delegate_name="literature",
              created_at=T0 + 1000, completed_at=T0 + 5000,
              input_tokens=200, output_tokens=60, total_cost=0.5)
        frame("other_lit", "LIT_RESEARCHER", None, frame_ids["other_lit"], OTHER_PROJECT_ID,
              name="Other kickoff")
        if lint_rows:
            frame("odd", "Lit Researcher v2.1", frame_ids["root"], frame_ids["root"], PROJECT_ID)

        for frame_key, idx, role, content in (
            ("root", 0, "user", "hello"), ("root", 1, "assistant", "hi there"),
            ("lit", 0, "user", "screen the papers"),
        ):
            _insert(conn, "frame_messages", {
                "frame_id": frame_ids[frame_key], "idx": idx,
                "msg_json": json.dumps({"role": role, "content": content}),
            })

        _insert(conn, "compaction_archives", {
            "id": _uid(0xF51), "frame_id": frame_ids["lit"], "compaction_index": 0,
            "message_count": 2, "token_count": 30, "summary": "Compacted the screening",
            "messages": json.dumps([
                {"role": "user", "content": "earlier question"},
                {"role": "assistant", "content": "earlier answer"},
            ]),
            "created_at": T0 + 3000,
        })

        def memory(name, body, origin="extractor", evidence="stated", **extra):
            row = {
                "id": memory_ids[name], "user_id": USER_ID, "body": body,
                "origin": origin, "evidence": evidence,
                "created_at": T0 + 1000 * int(name[1:]), "updated_at": T0 + 1000 * int(name[1:]),
            }
            row.update(extra)
            _insert(conn, "memories", row)

        memory("m1", "Mixed-precision training fails on the old GPU driver; upcast the loss to float32.",
               origin="agent_tool", evidence="observed",
               subject_project_id=PROJECT_ID, source_frame_id=frame_ids["lit"])
        memory("m2", "The researcher prefers short summaries.")
        memory("m3", "An older note about the GPU driver.",
               subject_project_id=PROJECT_ID, superseded_by=memory_ids["m1"])
        memory("m4", "The results table lists dev-split numbers only.",
               subject_artifact_id=artifact_ids["a1"])
        memory("m5", "A fact of the other project.", subject_project_id=OTHER_PROJECT_ID)
        memory("m6", "A note about a deleted artifact.", subject_artifact_id=ORPHAN_ARTIFACT_ID)
        if lint_rows:
            memory("m7", "Tokenizer drops emoji in captions",
                   subject_project_id=PROJECT_ID, source_frame_id=frame_ids["odd"])
            memory("m8", "Tokenizer drops emoji in caption", subject_project_id=PROJECT_ID)
            memory("m9", "see D-0124", subject_project_id=PROJECT_ID)
            memory("m10", "Search the review corpus by venue first.",
                   subject_frame_id=frame_ids["lit"])
            memory("m11", "A frame fact of the other project.",
                   subject_frame_id=frame_ids["other_lit"])

        _insert(conn, "artifact_folders", {
            "id": folder_id, "project_id": PROJECT_ID, "name": "Results", "sort_order": 0,
            "is_conversation_folder": 0, "is_user_uploads_folder": 0,
            "created_at": T0, "updated_at": T0,
        })

        for order, (key, filename) in enumerate((
            ("a1", "results.csv"), ("a2", "notes.md"), ("a3", "data.csv"), ("a4", "missing.csv"),
        )):
            latest = {"a1": "a1v2", "a2": "a2v1", "a3": "a3v1", "a4": "a4v1"}[key]
            _insert(conn, "artifacts", {
                "id": artifact_ids[key], "project_id": PROJECT_ID,
                "root_frame_id": frame_ids["root"], "frame_id": frame_ids["lit"],
                "filename": filename, "created_at": T0, "latest_version_id": version_ids[latest],
                "is_user_upload": 0, "is_ephemeral": 0,
                "folder_id": folder_id if key == "a1" else None, "sort_order": order,
            })

        content_types = {"a1": "text/csv", "a2": "text/markdown", "a3": "text/csv", "a4": "text/csv"}
        sizes = {
            "a1v1": len(contents["a1v1"]), "a1v2": len(contents["a1v2"]),
            "a2v1": len(contents["a2v1"]), "a3v1": len(host_bytes), "a4v1": 6,
        }
        for number, (name, owner) in enumerate((
            ("a1v1", "a1"), ("a1v2", "a1"), ("a2v1", "a2"), ("a3v1", "a3"), ("a4v1", "a4"),
        )):
            row = {
                "id": version_ids[name], "artifact_id": artifact_ids[owner],
                "version_number": 2 if name == "a1v2" else 1,
                "frame_id": frame_ids["lit"], "content_type": content_types[owner],
                "size_bytes": sizes[name], "checksum": checksums[name],
                "storage_path": storage[name], "created_at": T0 + 100 * number,
                "agent_name": "LIT_RESEARCHER", "is_intermediate": 0, "is_checkpoint": 0,
            }
            if name == "a1v2":
                row.update(parent_version_id=version_ids["a1v1"], producing_cell_id=exec_id,
                           code_description="Builds the results table")
            _insert(conn, "artifact_versions", row)

        _insert(conn, "artifact_dependencies", {
            "id": _uid(0xD01), "artifact_version_id": version_ids["a1v2"],
            "depends_on_version_id": version_ids["a3v1"], "reference_name": "data.csv",
            "created_at": T0,
        })

        _insert(conn, "verification_checks", {
            "id": _uid(0xD11), "root_frame_id": frame_ids["root"],
            "artifact_version_id": version_ids["a1v2"],
            "claim": "The table mixes dev and test numbers.",
            "verdict": "warn", "severity": "minor",
            "evidence": "Row 3 cites the test split.",
            "reviewer_frame_id": frame_ids["lit"], "source_ref": "fixture-ref",
            "status": "unaddressed", "created_at": T0,
        })

        _insert(conn, "execution_log", {
            "id": exec_id, "frame_id": frame_ids["lit"], "cell_index": 0,
            "kernel_id": _uid(0xE21), "conda_env": "fixture-env", "language": "python",
            "source": "print('hi')", "exit_status": "ok", "created_at": T0,
        })

        for server in ("bundled:literature", DIR_UUID_PUBMED):
            _insert(conn, "directory_attachments", {
                "server_uuid": server, "agent_name": "LAB_PROJECT_MANAGER",
                "user_id": USER_ID, "created_at": T0,
            })

        _insert(conn, "user_secrets", {
            "id": _uid(0xE31), "user_id": USER_ID, "name": "TYPESAFE_API_KEY",
            "provider": "fixture", "encrypted_value": "dummy-encrypted-value",
            "created_at": T0, "updated_at": T0,
        })

        for key, enabled in (("pdf-explore", 0), ("doi-verified-evidence", 1)):
            _insert(conn, "capability_settings", {
                "user_id": USER_ID, "kind": "skill", "key": key,
                "enabled": enabled, "updated_at": T0,
            })

        conn.commit()
    finally:
        conn.close()

    # The version a2v1 is recorded but its file is gone.
    info.files["a2v1"].unlink()
    return info
