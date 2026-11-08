#!/usr/bin/env python3
"""Record the Claude Science database schema as a Markdown document.

Usage:
    python dump_claude_science_schema.py --db <path to a COPY of operon-cli.db> --out <markdown path>

The database is opened only through a read-only, immutable SQLite URI, so this
script can never write to it. Point it at a copy, never at the live database.

What is read, and nothing else:
  * the CREATE TABLE statement of each table in TABLES (sqlite_master.sql);
  * PRAGMA table_info for each of those tables;
  * SELECT DISTINCT <column> for each (table, column) in ENUM_COLUMNS.

The user_secrets table gets its CREATE statement and PRAGMA table_info only.
No SELECT is ever issued on it, and no row of any table is read or written.

If the output file already holds a "## File layout" section (written by hand),
the section is kept at the end of the rewritten file.

Exit codes: 0 on success (missing tables or columns are listed under
"## Not found"), 2 when --db does not exist.
"""

import argparse
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote

TABLES = (
    "projects",
    "memories",
    "user_agents",
    "frames",
    "frame_messages",
    "artifacts",
    "artifact_versions",
    "artifact_dependencies",
    "artifact_folders",
    "verification_checks",
    "execution_log",
    "directory_attachments",
    "capability_settings",
    "compaction_archives",
    "user_secrets",
)

ENUM_COLUMNS = (
    ("memories", "origin"),
    ("memories", "evidence"),
    ("verification_checks", "status"),
    ("verification_checks", "verdict"),
    ("frames", "status"),
    ("frames", "conversation_type"),
    ("artifacts", "retention"),
    ("capability_settings", "kind"),
)

LAYOUT_HEADING = "## File layout"


def open_readonly(db_path):
    """Open the database read-only and immutable; it cannot be written."""
    uri = "file:" + quote(Path(db_path).resolve().as_posix(), safe="/:") + "?mode=ro&immutable=1"
    return sqlite3.connect(uri, uri=True)


def fence_for(text):
    """A backtick fence longer than any backtick run in the text."""
    runs = re.findall(r"`+", text)
    longest = max((len(r) for r in runs), default=0)
    return "`" * max(3, longest + 1)


def cell(value):
    """A Markdown table cell: pipes escaped, newlines replaced by a space."""
    if value is None:
        return ""
    text = str(value).replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    return text.replace("|", "\\|")


def quote_ident(name):
    return '"' + name.replace('"', '""') + '"'


def table_sql(conn, table):
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
    ).fetchone()
    return row[0] if row else None


def table_info(conn, table):
    return conn.execute("PRAGMA table_info(" + quote_ident(table) + ")").fetchall()


def enum_values(conn, table, column):
    sql = "SELECT DISTINCT " + quote_ident(column) + " FROM " + quote_ident(table) + " ORDER BY 1"
    return [r[0] for r in conn.execute(sql).fetchall()]


def render_value(value):
    return "NULL" if value is None else str(value)


def existing_layout(out_path):
    """The hand-written File layout section of an existing output, or ''."""
    path = Path(out_path)
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    marker = "\n" + LAYOUT_HEADING
    if text.startswith(LAYOUT_HEADING):
        return text.rstrip("\n") + "\n"
    index = text.find(marker)
    if index < 0:
        return ""
    return text[index + 1:].rstrip("\n") + "\n"


def build_document(conn, layout):
    lines = []
    not_found = []
    lines.append("# Claude Science database schema")
    lines.append("")
    lines.append(
        "This document records the structure of the Claude Science local database: "
        "the table definitions, the column lists, the enum values observed in the "
        "enum columns, and the file layout around the database. It holds no row data. "
        "It was read on 2026-11-08 from a copy of the database, opened read-only and "
        "immutable. Regenerate the sections above the file layout with "
        "`python skills/migrating-from-claude-science/scripts/dump_claude_science_schema.py "
        "--db <copy> --out docs/science-ultrapowers/claude-science-schema.md`; the "
        "script keeps the hand-written file layout section."
    )
    lines.append("")
    lines.append("## Tables")
    lines.append("")
    columns_by_table = {}
    for table in TABLES:
        sql = table_sql(conn, table)
        if sql is None:
            not_found.append("table `" + table + "`")
            continue
        info = table_info(conn, table)
        columns_by_table[table] = {row[1] for row in info}
        fence = fence_for(sql)
        lines.append("### " + table)
        lines.append("")
        lines.append(fence + "sql")
        lines.append(sql)
        lines.append(fence)
        lines.append("")
        lines.append("| cid | name | type | notnull | default | pk |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for cid, name, ctype, notnull, default, pk in info:
            lines.append(
                "| " + " | ".join(cell(v) for v in (cid, name, ctype, notnull, default, pk)) + " |"
            )
        lines.append("")
    lines.append("## Observed enum values")
    lines.append("")
    for table, column in ENUM_COLUMNS:
        if table not in columns_by_table:
            not_found.append("column `" + table + "." + column + "` (table missing)")
            continue
        if column not in columns_by_table[table]:
            not_found.append("column `" + table + "." + column + "`")
            continue
        values = enum_values(conn, table, column)
        shown = ", ".join("`" + render_value(v) + "`" for v in values) if values else "(none)"
        lines.append("- `" + table + "." + column + "`: " + shown)
    lines.append("")
    if not_found:
        lines.append("## Not found")
        lines.append("")
        for item in not_found:
            lines.append("- " + item)
        lines.append("")
    text = "\n".join(lines)
    if layout:
        text = text.rstrip("\n") + "\n\n" + layout
    else:
        text = text.rstrip("\n") + "\n"
    return text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--db", required=True, help="path to a COPY of operon-cli.db")
    parser.add_argument("--out", required=True, help="Markdown file to write")
    args = parser.parse_args(argv)

    db_path = Path(args.db)
    if not db_path.is_file():
        print("error: database not found: " + str(db_path), file=sys.stderr)
        return 2

    layout = existing_layout(args.out)
    conn = open_readonly(db_path)
    try:
        text = build_document(conn, layout)
    finally:
        conn.close()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("wrote " + str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
