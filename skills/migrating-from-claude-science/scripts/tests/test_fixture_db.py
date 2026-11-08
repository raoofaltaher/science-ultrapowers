"""Tests for the fixture database builder."""

import hashlib
import json
import sqlite3
import tempfile
import tomllib
import unittest
from pathlib import Path

import fixture_db


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class FixtureDbTest(unittest.TestCase):
    def build(self, **kwargs):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name).resolve()
        info = fixture_db.build_fixture(root, **kwargs)
        return info

    def connect(self, info):
        conn = sqlite3.connect(str(info.db_path))
        self.addCleanup(conn.close)
        return conn

    def count(self, conn, table):
        return conn.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]

    def test_statements_come_from_the_schema_record(self):
        statements = fixture_db.create_statements()
        self.assertEqual(len(statements), 15)
        for table in (
            "projects", "memories", "user_agents", "frames", "frame_messages",
            "compaction_archives", "artifacts", "artifact_versions", "artifact_dependencies",
            "artifact_folders", "verification_checks", "execution_log",
            "directory_attachments", "capability_settings", "user_secrets",
        ):
            self.assertIn(table, statements)
            self.assertTrue(statements[table].lstrip().startswith("CREATE TABLE"), table)

    def test_counts(self):
        info = self.build()
        conn = self.connect(info)
        self.assertEqual(self.count(conn, "projects"), 2)
        self.assertEqual(self.count(conn, "memories"), 6)
        self.assertEqual(self.count(conn, "artifacts"), 4)
        self.assertEqual(self.count(conn, "artifact_versions"), 5)
        self.assertEqual(self.count(conn, "artifact_dependencies"), 1)
        self.assertEqual(self.count(conn, "verification_checks"), 1)
        columns = [row[1] for row in conn.execute("PRAGMA table_info(memories)")]
        self.assertIn("evidence", columns)
        self.assertEqual(set(info.artifacts), {"a1", "a2", "a3", "a4"})
        self.assertEqual(set(info.versions), {"a1v1", "a1v2", "a2v1", "a3v1", "a4v1"})
        self.assertEqual(set(info.frames), {"root", "lit", "other_lit"})
        self.assertEqual(len(info.memories), 6)

    def test_lint_rows_add_five_memories(self):
        info = self.build(lint_rows=True)
        conn = self.connect(info)
        self.assertEqual(self.count(conn, "memories"), 11)
        self.assertEqual(len(info.memories), 11)

    def test_files_on_disk(self):
        info = self.build()
        self.assertTrue(info.files["a1v1"].is_file())
        self.assertTrue(info.files["a1v2"].is_file())
        self.assertTrue((info.root / "host" / "data.csv").is_file())
        self.assertFalse(info.files["a2v1"].exists())
        self.assertFalse(info.files["a4v1"].exists())
        self.assertNotEqual(info.files["a1v1"].read_bytes(), info.files["a1v2"].read_bytes())
        conn = self.connect(info)
        for name in ("a1v1", "a1v2"):
            checksum = conn.execute(
                "SELECT checksum FROM artifact_versions WHERE id = ?", (info.versions[name],)
            ).fetchone()[0]
            self.assertEqual(checksum, sha256_of(info.files[name]))
        checksum = conn.execute(
            "SELECT checksum FROM artifact_versions WHERE id = ?", (info.versions["a3v1"],)
        ).fetchone()[0]
        self.assertEqual(checksum, sha256_of(info.root / "host" / "data.csv"))

    def test_copy_storage_paths_use_backslashes(self):
        info = self.build()
        conn = self.connect(info)
        for name, artifact in (("a1v1", "a1"), ("a1v2", "a1"), ("a2v1", "a2")):
            path = conn.execute(
                "SELECT storage_path FROM artifact_versions WHERE id = ?", (info.versions[name],)
            ).fetchone()[0]
            self.assertNotIn("/", path)
            parts = path.split("\\")
            self.assertEqual(parts[0], info.project_id)
            self.assertEqual(parts[1], info.artifacts[artifact])
            self.assertRegex(parts[2], r"^v[0-9a-f]{8}_")
            on_disk = info.org_dir / "artifacts" / parts[0] / parts[1] / parts[2]
            self.assertEqual(on_disk, info.files[name])

    def test_host_link_paths_start_with_tilde(self):
        info = self.build()
        conn = self.connect(info)
        for name, target in (("a3v1", "data.csv"), ("a4v1", "absent.csv")):
            path = conn.execute(
                "SELECT storage_path FROM artifact_versions WHERE id = ?", (info.versions[name],)
            ).fetchone()[0]
            self.assertTrue(path.startswith("~/"))
            self.assertNotIn("\\", path)
            self.assertEqual(path, "~/" + (info.root / "host" / target).as_posix())

    def test_preferences_and_cache_written(self):
        info = self.build()
        prefs = json.loads((info.org_dir / "preferences.json").read_text(encoding="utf-8"))
        grants = prefs["approvalGrants"]
        self.assertEqual(grants["always"]["allow"]["network"], ["data.example.org"])
        self.assertEqual(grants["always"]["allow"]["host"], ["rw:" + info.root.as_posix() + "/host"])
        self.assertEqual(grants["always"]["deny"], {})
        self.assertEqual(grants["always"]["ask"], {})
        self.assertEqual(grants["alwaysOrigins"]["host"], {})
        origin = grants["alwaysOrigins"]["network"]["data.example.org"]
        self.assertEqual(origin["projectId"], "proj_fix")
        self.assertEqual(origin["rootFrameId"], info.frames["root"])
        self.assertEqual(grants["project"]["proj_fix"]["allow"]["local_exec"], ["python"])
        self.assertEqual(grants["project"]["proj_fix"]["allow"]["credential_access"], ["TYPESAFE_API_KEY"])
        self.assertEqual(grants["project"]["proj_other"]["allow"]["local_exec"], ["Rscript"])
        self.assertEqual(prefs["hostGrants"], [])
        self.assertEqual(prefs["userAllowedDomains"], [])
        self.assertEqual(prefs["builtinAllowlistDisabledGroups"], ["clinical"])
        self.assertIs(prefs["autoMode"], False)
        self.assertIs(prefs["gpuEnabled"], False)
        self.assertEqual(prefs["reviewerModel"], "fixture-reviewer-model")
        self.assertIs(prefs["memoryEnabled"], True)

        cache = json.loads((info.data_dir / "mcp" / "directory-cache.json").read_text(encoding="utf-8"))
        self.assertEqual(cache["accountId"], "acct-fixture")
        names = [c["name"] for c in cache["connectors"]]
        self.assertEqual(names, ["PubMed", "Some Unlisted Server"])
        self.assertEqual(cache["connectors"][0]["backendUrl"], "https://pubmed.mcp.claude.com/mcp")

        config = tomllib.loads((info.root / "config.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["data_dir"], info.root.as_posix())
        self.assertEqual(config["last_move_from"], "")
        self.assertEqual(info.data_dir, info.root)

        for skill in ("doi-verified-evidence", "peer-review"):
            self.assertTrue((info.org_dir / "skills" / skill / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
