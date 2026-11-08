"""Tests for data-dir resolution, the read-only copy, schema validation and project choice."""

import ast
import contextlib
import hashlib
import io
import json
import re
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fixture_db  # noqa: E402
import migrate_claude_science as mcs  # noqa: E402


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def toml_path(path):
    return json.dumps(Path(path).as_posix())


class SetupTestCase(unittest.TestCase):
    def setUp(self):
        # No process tool is ever run by a test: the running-program check finds none.
        self.enterContext(mock.patch.object(mcs, "_run_tool", return_value=None))

    def tmpdir(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name).resolve()

    def fixture(self, **kwargs):
        root = self.tmpdir() / "data"
        return fixture_db.build_fixture(root, **kwargs)

    def config_home(self, data_dir=None, last_move_from=""):
        home = self.tmpdir() / "config-home"
        home.mkdir()
        lines = []
        if data_dir is not None:
            lines.append("data_dir = " + toml_path(data_dir))
        if last_move_from is not None:
            lines.append("last_move_from = " + (toml_path(last_move_from) if last_move_from else '""'))
        (home / "config.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return home

    def make_lab(self):
        lab = self.tmpdir() / "research_lab"
        lab.mkdir()
        (lab / "lab.json").write_text("{}\n", encoding="utf-8")
        return lab

    def lab_files(self, lab):
        return sorted(p.relative_to(lab).as_posix() for p in lab.rglob("*") if p.is_file())

    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = mcs.main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def open_copy(self, info):
        tmp = self.tmpdir()
        copy = mcs.copy_db(info.org_dir, tmp)
        conn = mcs.open_ro(copy)
        self.addCleanup(conn.close)
        return conn


class ResolveTest(SetupTestCase):
    def test_resolve_prefers_config_toml_data_dir(self):
        base = self.tmpdir()
        a, b = base / "A", base / "B"
        a.mkdir()
        b.mkdir()
        home = self.config_home(data_dir=b, last_move_from=a)
        data_dir, warnings = mcs.resolve_data_dir(None, home)
        self.assertEqual(data_dir, b)
        self.assertEqual(len(warnings), 1)
        self.assertIn(str(a), warnings[0])
        self.assertIn("two Claude Science data directories exist", warnings[0])

    def test_empty_last_move_from_gives_no_warning(self):
        b = self.tmpdir() / "B"
        b.mkdir()
        home = self.config_home(data_dir=b, last_move_from="")
        data_dir, warnings = mcs.resolve_data_dir(None, home)
        self.assertEqual(data_dir, b)
        self.assertEqual(warnings, [])

    def test_resolve_explicit_wins(self):
        base = self.tmpdir()
        explicit, b = base / "explicit", base / "B"
        explicit.mkdir()
        b.mkdir()
        home = self.config_home(data_dir=b, last_move_from="")
        data_dir, warnings = mcs.resolve_data_dir(explicit, home)
        self.assertEqual(data_dir, explicit)
        self.assertEqual(warnings, [])

    def test_resolve_explicit_must_be_a_directory(self):
        missing = self.tmpdir() / "nope"
        with self.assertRaises(mcs.MigrationError) as ctx:
            mcs.resolve_data_dir(missing, self.tmpdir())
        self.assertIn(str(missing), str(ctx.exception))
        self.assertEqual(ctx.exception.exit_code, 2)

    def test_resolve_falls_back_to_config_home_with_orgs(self):
        home = self.tmpdir() / "config-home"
        (home / "orgs").mkdir(parents=True)
        data_dir, warnings = mcs.resolve_data_dir(None, home)
        self.assertEqual(data_dir, home)
        self.assertEqual(warnings, [])

    def test_resolve_error_lists_paths_tried(self):
        home = self.tmpdir() / "config-home"
        home.mkdir()
        with self.assertRaises(mcs.MigrationError) as ctx:
            mcs.resolve_data_dir(None, home)
        message = str(ctx.exception)
        self.assertIn("no Claude Science data directory found", message)
        self.assertIn(str(home), message)
        self.assertEqual(ctx.exception.exit_code, 2)

    def test_read_active_org(self):
        home = self.tmpdir()
        self.assertIsNone(mcs.read_active_org(home))
        (home / "active-org.json").write_text("not json", encoding="utf-8")
        self.assertIsNone(mcs.read_active_org(home))
        (home / "active-org.json").write_text(
            json.dumps({"org_uuid": "org-fixture-0001", "org_name": "ignored"}), encoding="utf-8"
        )
        self.assertEqual(mcs.read_active_org(home), "org-fixture-0001")


class FindOrgTest(SetupTestCase):
    def two_orgs(self):
        info = self.fixture()
        second = info.data_dir / "orgs" / "org-fixture-0002"
        second.mkdir()
        shutil.copyfile(info.db_path, second / "operon-cli.db")
        return info, second

    def test_find_org_dir_single(self):
        info = self.fixture()
        self.assertEqual(mcs.find_org_dir(info.data_dir), info.org_dir)

    def test_find_org_dir_errors_on_two_orgs(self):
        info, second = self.two_orgs()
        with self.assertRaises(mcs.MigrationError) as ctx:
            mcs.find_org_dir(info.data_dir)
        message = str(ctx.exception)
        self.assertIn(str(info.org_dir), message)
        self.assertIn(str(second), message)
        self.assertIn("--data-dir", message)
        self.assertEqual(ctx.exception.exit_code, 2)

    def test_find_org_dir_picks_the_active_org(self):
        info, second = self.two_orgs()
        self.assertEqual(mcs.find_org_dir(info.data_dir, "org-fixture-0002"), second)
        self.assertEqual(mcs.find_org_dir(info.data_dir, info.org_uuid), info.org_dir)
        with self.assertRaises(mcs.MigrationError):
            mcs.find_org_dir(info.data_dir, "org-not-here")

    def test_find_org_dir_none(self):
        data_dir = self.tmpdir()
        (data_dir / "orgs").mkdir()
        with self.assertRaises(mcs.MigrationError) as ctx:
            mcs.find_org_dir(data_dir)
        self.assertIn(str(data_dir / "orgs"), str(ctx.exception))


class CopyAndOpenTest(SetupTestCase):
    def test_copy_db_copies_wal_and_shm_and_leaves_original_untouched(self):
        info = self.fixture()
        writer = sqlite3.connect(str(info.db_path))
        self.addCleanup(writer.close)
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute(
            "INSERT INTO projects (id, name, created_at, updated_at) VALUES ('proj_wal', 'In the WAL', 1, 1)"
        )
        writer.commit()
        wal = info.org_dir / "operon-cli.db-wal"
        shm = info.org_dir / "operon-cli.db-shm"
        self.assertGreater(wal.stat().st_size, 0)
        before = {p: (p.stat().st_mtime_ns, sha256_of(p)) for p in (info.db_path, wal)}

        copied = []
        real = shutil.copyfile

        def spy(src, dst, *args, **kwargs):
            copied.append(Path(src).name)
            return real(src, dst, *args, **kwargs)

        tmp = self.tmpdir()
        with mock.patch.object(shutil, "copyfile", spy):
            copy = mcs.copy_db(info.org_dir, tmp)
        self.assertEqual(copy, tmp / "operon-cli.db")
        self.assertIn("operon-cli.db", copied)
        self.assertIn("operon-cli.db-wal", copied)
        if shm.exists():
            self.assertIn("operon-cli.db-shm", copied)
        after = {p: (p.stat().st_mtime_ns, sha256_of(p)) for p in (info.db_path, wal)}
        self.assertEqual(before, after)

        conn = mcs.open_ro(copy)
        self.addCleanup(conn.close)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0], 3)

    def test_rows_in_the_wal_are_seen(self):
        info = self.fixture()
        writer = sqlite3.connect(str(info.db_path))
        self.addCleanup(writer.close)
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute(
            "INSERT INTO projects (id, name, created_at, updated_at) VALUES ('proj_wal', 'In the WAL', 1, 1)"
        )
        writer.commit()
        db_hash = sha256_of(info.db_path)
        conn = self.open_copy(info)
        row = conn.execute("SELECT name FROM projects WHERE id = 'proj_wal'").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["name"], "In the WAL")
        self.assertEqual(sha256_of(info.db_path), db_hash)

    def test_copy_dir_with_hash_opens(self):
        info = self.fixture()
        tmp = self.tmpdir() / "odd#name%41 here"
        tmp.mkdir()
        copy = mcs.copy_db(info.org_dir, tmp)
        conn = mcs.open_ro(copy)
        self.addCleanup(conn.close)
        self.assertEqual(mcs.validate_schema(conn), [])
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0], 2)

    def test_dump_script_opens_a_copy_in_a_hash_folder(self):
        import dump_claude_science_schema as dump

        info = self.fixture()
        tmp = self.tmpdir() / "odd#name%41 here"
        tmp.mkdir()
        copy = mcs.copy_db(info.org_dir, tmp)
        conn = dump.open_readonly(copy)
        self.addCleanup(conn.close)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0], 2)

    def test_open_ro_refuses_writes(self):
        info = self.fixture()
        conn = self.open_copy(info)
        with self.assertRaises(sqlite3.OperationalError):
            conn.execute(
                "INSERT INTO projects (id, name, created_at, updated_at) VALUES ('x', 'x', 1, 1)"
            )

    def test_open_ro_works_while_original_is_open_for_write(self):
        info = self.fixture()
        writer = sqlite3.connect(str(info.db_path), isolation_level=None)
        self.addCleanup(writer.close)
        writer.execute("BEGIN")
        writer.execute(
            "INSERT INTO projects (id, name, created_at, updated_at) VALUES ('proj_pending', 'Pending', 1, 1)"
        )
        conn = self.open_copy(info)
        ids = {row["id"] for row in conn.execute("SELECT id FROM projects")}
        self.assertEqual(ids, {"proj_fix", "proj_other"})

    def test_copy_failure_names_mtime_and_never_opens_source(self):
        info = self.fixture()
        tmp = self.tmpdir()
        with mock.patch.object(shutil, "copyfile", side_effect=PermissionError("locked")), \
                mock.patch.object(sqlite3, "connect") as connect:
            with self.assertRaises(mcs.MigrationError) as ctx:
                mcs.copy_db(info.org_dir, tmp)
        connect.assert_not_called()
        message = str(ctx.exception)
        self.assertIn("close Claude Science or retry", message)
        self.assertRegex(message, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertIn("operon-cli.db", message)
        self.assertEqual(ctx.exception.exit_code, 2)


class SchemaTest(SetupTestCase):
    def drop_evidence(self, info):
        conn = sqlite3.connect(str(info.db_path))
        try:
            conn.execute("ALTER TABLE memories DROP COLUMN evidence")
            conn.commit()
        finally:
            conn.close()

    def test_validate_schema_clean(self):
        info = self.fixture()
        conn = self.open_copy(info)
        self.assertEqual(mcs.validate_schema(conn), [])

    def test_validate_schema_names_missing_column(self):
        info = self.fixture()
        self.drop_evidence(info)
        conn = self.open_copy(info)
        self.assertEqual(mcs.validate_schema(conn), ["memories.evidence"])

    def test_validate_schema_missing_table_lists_each_column(self):
        info = self.fixture()
        conn = self.open_copy(info)
        missing = mcs.validate_schema(conn, {"no_such_table": ["b", "a"], "projects": ["id"]})
        self.assertEqual(missing, ["no_such_table.a", "no_such_table.b"])

    def test_every_sql_column_is_validated(self):
        tree = ast.parse(Path(mcs.__file__).read_text(encoding="utf-8"))
        statements = [
            node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and re.search(r"\b(?:SELECT|FROM|JOIN)\b", node.value)
        ]
        self.assertTrue(statements)
        info = self.fixture()
        conn = self.open_copy(info)
        columns = {
            table: {row[1] for row in conn.execute('PRAGMA table_info("' + table + '")')}
            for table in mcs.REQUIRED_COLUMNS
        }
        unvalidated = set()
        checked = 0
        for sql in statements:
            tables = {
                t for t in re.findall(r"\b(?:FROM|JOIN)\s+(\w+)", sql) if t in mcs.REQUIRED_COLUMNS
            }
            words = set(re.findall(r"\w+", sql))
            for table in tables:
                checked += 1
                for word in words & columns[table]:
                    if word not in mcs.REQUIRED_COLUMNS[table]:
                        unvalidated.add(table + "." + word)
        self.assertGreater(checked, 10)
        self.assertEqual(sorted(unvalidated), [])

    def test_dropped_dependency_created_at_exits_3(self):
        info = self.fixture()
        conn = sqlite3.connect(str(info.db_path))
        try:
            conn.execute("ALTER TABLE artifact_dependencies DROP COLUMN created_at")
            conn.commit()
        finally:
            conn.close()
        lab = self.make_lab()
        code, out, err = self.run_cli([
            "--data-dir", str(info.data_dir), "--config-home", str(self.tmpdir()),
            "--project", "proj_fix", "--lab", str(lab),
        ])
        self.assertEqual(code, 3)
        self.assertIn("schema mismatch: artifact_dependencies.created_at", err)
        self.assertEqual(self.lab_files(lab), ["lab.json"])

    def test_schema_mismatch_exits_3_before_writing(self):
        info = self.fixture()
        self.drop_evidence(info)
        lab = self.make_lab()
        code, out, err = self.run_cli([
            "--data-dir", str(info.data_dir), "--config-home", str(self.tmpdir()),
            "--project", "proj_fix", "--lab", str(lab),
        ])
        self.assertEqual(code, 3)
        self.assertIn("schema mismatch: memories.evidence", err)
        self.assertEqual(self.lab_files(lab), ["lab.json"])


class DatabaseErrorTest(SetupTestCase):
    def test_non_database_file_gives_advice_not_traceback(self):
        info = self.fixture()
        info.db_path.write_bytes(b"this is not a sqlite database, only text\n" * 20)
        lab = self.make_lab()
        code, out, err = self.run_cli([
            "--data-dir", str(info.data_dir), "--config-home", str(self.tmpdir()),
            "--project", "proj_fix", "--lab", str(lab),
        ])
        self.assertEqual(code, 2, err)
        self.assertIn("database copy unreadable", err)
        self.assertIn("close Claude Science or retry", err)
        self.assertRegex(err, r"source last modified \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertNotIn("Traceback", err)
        self.assertEqual(self.lab_files(lab), ["lab.json"])


class ProjectTest(SetupTestCase):
    def test_pick_project_by_substring_and_ambiguity(self):
        info = self.fixture()
        conn = self.open_copy(info)
        self.assertEqual(mcs.pick_project(conn, "proj_other")["name"], "Other Project")
        self.assertEqual(mcs.pick_project(conn, "fixture")["id"], "proj_fix")
        self.assertEqual(mcs.pick_project(conn, "STUDY")["id"], "proj_fix")
        with self.assertRaises(mcs.MigrationError) as ctx:
            mcs.pick_project(conn, "t")
        self.assertIn("proj_fix: Fixture Study", str(ctx.exception))
        self.assertIn("proj_other: Other Project", str(ctx.exception))
        with self.assertRaises(mcs.MigrationError) as ctx:
            mcs.pick_project(conn, "zzz")
        self.assertIn("proj_fix: Fixture Study", str(ctx.exception))
        self.assertEqual(ctx.exception.exit_code, 2)

    def test_list_projects(self):
        info = self.fixture()
        conn = self.open_copy(info)
        projects = mcs.list_projects(conn)
        self.assertEqual([p["id"] for p in projects], ["proj_fix", "proj_other"])
        self.assertEqual(set(projects[0]), {"id", "name", "description"})

    def test_list_projects_cli_prints_json(self):
        info = self.fixture()
        code, out, err = self.run_cli([
            "--data-dir", str(info.data_dir), "--config-home", str(self.tmpdir()), "--list-projects",
        ])
        self.assertEqual(code, 0, err)
        projects = json.loads(out)
        self.assertEqual([p["id"] for p in projects], ["proj_fix", "proj_other"])

    def test_cli_requires_lab_unless_listing(self):
        info = self.fixture()
        code, out, err = self.run_cli([
            "--data-dir", str(info.data_dir), "--config-home", str(self.tmpdir()),
            "--project", "proj_fix",
        ])
        self.assertEqual(code, 2)

    def test_cli_several_projects_without_project_exits_2(self):
        info = self.fixture()
        code, out, err = self.run_cli([
            "--data-dir", str(info.data_dir), "--config-home", str(self.tmpdir()),
            "--lab", str(self.make_lab()),
        ])
        self.assertEqual(code, 2)
        self.assertIn("proj_fix: Fixture Study", err)

    def test_cli_picks_the_project(self):
        info = self.fixture()
        lab = self.tmpdir() / "research_lab"
        lab.mkdir()
        (lab / "lab.json").write_text("{}\n", encoding="utf-8")
        code, out, err = self.run_cli([
            "--data-dir", str(info.data_dir), "--config-home", str(self.tmpdir()),
            "--synced-skills-dir", str(self.tmpdir() / "synced"),
            "--project", "Fixture", "--lab", str(lab),
        ])
        self.assertEqual(code, 0, err)
        report = (lab / "migration" / "MIGRATION_REPORT.md").read_text(encoding="utf-8")
        self.assertIn("| project | `proj_fix: Fixture Study` |", report)
        self.assertIn("| data dir | " + info.data_dir.as_posix() + " |", report)
        self.assertIn("| org folder | " + info.org_uuid + " |", report)

    def test_cli_warns_on_two_data_directories(self):
        info = self.fixture()
        old = self.tmpdir() / "old"
        old.mkdir()
        home = self.config_home(data_dir=info.data_dir, last_move_from=old)
        code, out, err = self.run_cli([
            "--config-home", str(home), "--list-projects",
        ])
        self.assertEqual(code, 0, err)
        self.assertIn("two Claude Science data directories exist", err)


WIN_LIST = ("tasklist", "/FO", "CSV", "/NH")
PS_LIST = ("ps", "-A", "-o", "comm=")


def win_pid(pid):
    return ("tasklist", "/FI", "PID eq " + str(pid), "/FO", "CSV", "/NH")


def ps_pid(pid):
    return ("ps", "-o", "comm=", "-p", str(pid))


def csv_row(name, pid):
    return '"%s","%s","Console","1","80,000 K"\n' % (name, pid)


class RunningGuardTest(SetupTestCase):
    """Claude Science running is refused. No process tool is ever run: _run_tool is patched."""

    def setUp(self):
        self.outputs = {}
        self.calls = []
        self.on_windows = True

        def fake_tool(argv):
            self.calls.append(tuple(argv))
            return self.outputs.get(tuple(argv))

        self.enterContext(mock.patch.object(mcs, "_run_tool", side_effect=fake_tool))
        self.enterContext(mock.patch.object(mcs, "_is_windows", side_effect=lambda: self.on_windows))

    def home_with_lock(self, content):
        home = self.tmpdir() / "config-home"
        home.mkdir()
        (home / "auth-owner.lock").write_text(content, encoding="utf-8")
        return home

    def cli(self, info, home, *extra, lab=None):
        lab = lab or self.make_lab()
        code, out, err = self.run_cli([
            "--data-dir", str(info.data_dir), "--config-home", str(home),
            "--synced-skills-dir", str(self.tmpdir() / "synced"),
            "--project", "proj_fix", "--lab", str(lab), *extra,
        ])
        return code, out, err, lab

    def test_running_process_is_refused_with_exit_2(self):
        info = self.fixture()
        self.outputs[WIN_LIST] = csv_row("explorer.exe", 4) + csv_row("claude-science.exe", 4242)
        lab = self.make_lab()
        with mock.patch.object(mcs, "copy_db", side_effect=AssertionError("copy_db must not run")):
            code, out, err, _ = self.cli(info, self.tmpdir(), lab=lab)
        self.assertEqual(code, 2, err)
        self.assertIn("Claude Science is running (", err)
        self.assertIn("quit it first", err)
        self.assertIn("--allow-running", err)
        self.assertEqual(self.lab_files(lab), ["lab.json"])

    def test_running_process_is_found_by_ps_off_windows(self):
        info = self.fixture()
        self.on_windows = False
        self.outputs[PS_LIST] = "bash\n/opt/claude-science/bin/claude-science\n"
        code, out, err, _ = self.cli(info, self.tmpdir())
        self.assertEqual(code, 2, err)
        self.assertIn("quit it first", err)

    def test_live_lock_pid_of_claude_science_is_refused(self):
        info = self.fixture()
        home = self.home_with_lock('{"pid": 777, "token": "sekrit-token"}')
        self.outputs[WIN_LIST] = csv_row("explorer.exe", 4)
        self.outputs[win_pid(777)] = csv_row("claude-science.exe", 777)
        code, out, err, _ = self.cli(info, home)
        self.assertEqual(code, 2, err)
        self.assertIn("quit it first", err)
        self.assertIn("777", err)
        self.assertNotIn("sekrit-token", err)

    def test_live_lock_pid_of_another_program_runs(self):
        info = self.fixture()
        home = self.home_with_lock('{"pid": 777, "token": "sekrit-token"}')
        self.outputs[WIN_LIST] = csv_row("explorer.exe", 4)
        self.outputs[win_pid(777)] = csv_row("notepad.exe", 777)
        code, out, err, _ = self.cli(info, home)
        self.assertEqual(code, 0, err)

    def test_stale_lock_runs(self):
        info = self.fixture()
        home = self.home_with_lock('{"pid": 777}')
        self.outputs[WIN_LIST] = csv_row("explorer.exe", 4)
        self.outputs[win_pid(777)] = "INFO: No tasks are running which match the specified criteria.\n"
        code, out, err, _ = self.cli(info, home)
        self.assertEqual(code, 0, err)

    def test_stale_lock_off_windows_runs(self):
        info = self.fixture()
        self.on_windows = False
        home = self.home_with_lock('{"pid": 777}')
        self.outputs[PS_LIST] = "bash\n"
        self.outputs[ps_pid(777)] = ""
        code, out, err, _ = self.cli(info, home)
        self.assertEqual(code, 0, err)

    def test_unreadable_lock_and_missing_tools_do_not_block(self):
        info = self.fixture()
        for content in ("{not json", '{"pid": "abc"}', '{"nopid": 1}', "[1]"):
            with self.subTest(content=content):
                home = self.home_with_lock(content)
                code, out, err, _ = self.cli(info, home)
                self.assertEqual(code, 0, err)
        self.assertIsNone(mcs.claude_science_running(self.tmpdir()))

    def test_allow_running_runs_anyway(self):
        info = self.fixture()
        self.outputs[WIN_LIST] = csv_row("claude-science.exe", 4242)
        code, out, err, _ = self.cli(info, self.tmpdir(), "--allow-running")
        self.assertEqual(code, 0, err)

    def test_list_projects_is_refused_while_running(self):
        info = self.fixture()
        self.outputs[WIN_LIST] = csv_row("claude-science.exe", 4242)
        with mock.patch.object(mcs, "copy_db", side_effect=AssertionError("copy_db must not run")):
            code, out, err = self.run_cli([
                "--data-dir", str(info.data_dir), "--config-home", str(self.tmpdir()), "--list-projects",
            ])
        self.assertEqual(code, 2, err)
        self.assertIn("quit it first", err)
        self.assertEqual(out, "")

    def test_claude_science_running_returns_a_reason_or_none(self):
        home = self.tmpdir()
        self.outputs[WIN_LIST] = csv_row("Claude-Science.EXE", 9)
        self.assertIn("claude-science", mcs.claude_science_running(home).lower())
        self.outputs[WIN_LIST] = csv_row("claude-science-helper.exe", 9)
        self.assertIsNotNone(mcs.claude_science_running(home))
        self.assertIsNone(mcs.claude_science_running(home, process_names=("other-app",)))
        self.outputs[WIN_LIST] = csv_row("notclaude-science.exe", 9)
        self.assertIsNone(mcs.claude_science_running(home))


if __name__ == "__main__":
    unittest.main()
