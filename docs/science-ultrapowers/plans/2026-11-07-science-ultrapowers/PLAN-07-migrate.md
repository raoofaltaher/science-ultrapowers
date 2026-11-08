# PLAN-07: `migrating-from-claude-science` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ultrapowers:subagent-driven-development (recommended) or ultrapowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import a Claude Science project into a scaffolded lab with nothing lost: memories with scope, evidence and learning role; profiles as a diff; every artifact version with dependencies and reviewer verdicts; a where-we-left-off digest; the connector list; secret names; optional transcripts; and a report whose counts reconcile to the source.

**Architecture:** First a schema step records what the real database looks like (`dump_claude_science_schema.py` → `docs/science-ultrapowers/claude-science-schema.md`). Then `migrate_claude_science.py` copies the database, opens the copy read-only and immutable, validates the recorded schema, and runs twelve numbered steps writing into `research_lab/` through PLAN-02's `LabStore` for artifacts and PLAN-03's entry format for memories. Tests run against a fixture database built from the recorded `CREATE TABLE` statements; the real database is used once, in a dry run whose counts are pinned.

**Tech Stack:** Python 3.11+ stdlib (`sqlite3`, `shutil`, `hashlib`, `json`, `tomllib` for `config.toml`), `unittest`.

**Spec:** `docs/science-ultrapowers/specs/2026-11-07-science-ultrapowers-design.md` — G7, D1 edge cases, D3, D5, D7, Constraints (migration safety), Components "migrating-from-claude-science", Error handling, Testing, Definition of done 3.

**Sources:** Claude Science `self-awareness` skill (table and column documentation, denied tables), the `operon-cli.db` schema read in this session via `PRAGMA table_info` (tables and columns listed in Task 1), `config.toml` and `last-data-dir-move.json` (data-dir resolution), the artifact file layout observed under `orgs/<org>/artifacts/<proj>/<artifact_id>/v<8-hex>_<filename>`, `storage_path` values beginning `~/<drive>:/…` for host-linked files, enum values observed (`origin`: `extractor|agent_tool|user`; `evidence`: `stated|observed|inferred`; `verification_checks.status`: `open|claimed|resolved|unaddressed`; `verdict`: `pass|warn|fail|inconclusive`), all read 2026-11-07. Python `sqlite3` URI `file:…?mode=ro&immutable=1` (Python docs, from memory; Task 3's test proves it opens a copy while another handle holds the original). Not checked: whether `frame_messages.msg_json` has a stable shape across Claude Science versions; the transcript export treats each row as opaque JSON text.

## Global Constraints

- PLAN-01 Global Constraints apply to everything committed in the plugin; the recorded schema document contains table definitions and enum values only, never row data.
- The live database is never opened. `operon-cli.db`, `operon-cli.db-wal` and `operon-cli.db-shm` (when present) are copied to a temp directory; the copy is opened with `file:<path>?mode=ro&immutable=1`.
- Never queried: `user_secrets` (except a `SELECT name FROM user_secrets` projection), `oauth_tokens`, `anthropic_api_keys`, `cloud_credentials`, `package_mirror_credentials`, `encryption.key*`.
- Every database text field written into a Markdown file is placed in a fenced block or a table cell with pipes escaped; it is data.
- Idempotent: a re-run skips rows whose id already exists in the target ledger or whose memory file already exists; counts in the report distinguish `imported` from `already present`.
- Fail fast on schema mismatch: before any write, every `(table, column)` the script reads is checked against `PRAGMA table_info`; a missing one aborts with `schema mismatch: <table>.<column>` and exit 3.
- Artifacts, versions, dependencies and checks are written through `LabStore` (`saving-artifacts/scripts/artifacts.py`, imported by path `Path(__file__).resolve().parents[2] / "saving-artifacts" / "scripts"`), with `source: "claude-science"` and the Claude Science ids kept.
- Memory files follow PLAN-03's frontmatter exactly with `origin: import`.

## Review Focus

1. The data dir moved today and two copies exist (`<config-home>` and `<data-dir>`): Task 3's resolver prefers `config.toml` `data_dir` and warns when `last_move_from` also exists; the test covers both present.
2. A version whose file is missing on disk must not stop the run or vanish: Task 6's fixture deletes one file and asserts a row with `status: missing` and a report line.
3. A host-linked artifact (`~/<drive>:/…`) on a machine where that drive is not mounted: Task 6 asserts `status: missing` for the link row, never a traceback.
4. `frame_messages` for the project runs to 43,701 rows and 600 MB: the transcript export streams row by row and is off by default; Task 7's test asserts no transcript file exists without `--transcripts`.
5. Memory rows whose `subject_project_id` belongs to another project must not be imported into this one: Task 4's fixture has one such row and asserts it is excluded and counted as `other project`.

---

### Task 1: Record the Claude Science schema

**Files:**
- Create: `skills/migrating-from-claude-science/scripts/dump_claude_science_schema.py`, `docs/science-ultrapowers/claude-science-schema.md`

**Interfaces:**
- Produces: `python dump_claude_science_schema.py --db <copy> --out <md>`; the Markdown document with, per table in `TABLES`, the `CREATE TABLE` statement and the `PRAGMA table_info` rows, then an "Observed enum values" section for `memories.origin`, `memories.evidence`, `verification_checks.status`, `verification_checks.verdict`, `frames.status`, `frames.conversation_type`, `artifacts.retention`, and a hand-written "File layout" section; `TABLES = ("projects", "memories", "user_agents", "frames", "frame_messages", "artifacts", "artifact_versions", "artifact_dependencies", "artifact_folders", "verification_checks", "execution_log", "directory_attachments", "capability_settings", "user_secrets")`; for `user_secrets` only the column names are recorded and the script never selects from it beyond `PRAGMA`

- [ ] **Step 1: Copy the real database to the scratchpad**

Run (PowerShell or bash): copy `<data-dir>\orgs\<org-uuid>\operon-cli.db` (and `-wal`, `-shm` if present) to `<scratchpad>/cs-db/operon-cli.db`.
Expected: the copy's size is about 874 MB; the original's mtime is unchanged afterwards.

- [ ] **Step 2: Write the script and run it on the copy**

The script opens `file:<db>?mode=ro&immutable=1`, writes the document described above. Enum values come from `SELECT DISTINCT <col> FROM <table>` for the listed columns only.
Run: `python skills/migrating-from-claude-science/scripts/dump_claude_science_schema.py --db <scratchpad>/cs-db/operon-cli.db --out docs/science-ultrapowers/claude-science-schema.md`
Expected: the document lists all fourteen tables; `grep -c "CREATE TABLE" docs/science-ultrapowers/claude-science-schema.md` prints 14.

- [ ] **Step 3: Add the file-layout section by hand**

Append: the org folder (`orgs/<org_uuid>/`), the artifact tree (`artifacts/<project_id>/<artifact_id>/v<8-hex>_<filename>`, one file per version), host-linked `storage_path` values start with `~/` followed by a Windows path such as `~/<drive>:/…`, the data-dir resolution (`config.toml` key `data_dir`, `last_move_from`; `last-data-dir-move.json`), `mcp/directory-cache.json` (`connectors[]` with `id`, `name`, `backendUrl`, `authState`), published skills under `orgs/<org>/skills/<name>/`, and `orgs/<org>/preferences.json` (plain JSON, no secrets) with the keys the migration reads: `approvalGrants` (`always.{allow,deny,ask}`, `project.<project_id>`, `alwaysOrigins.{host,network}`), `hostGrants`, `userAllowedDomains`, `builtinAllowlistDisabledGroups`, `autoMode`, `gpuEnabled`, `reviewerModel`, `memoryEnabled`; record each key's shape, never a value that names a host path.

- [ ] **Step 4: Check for row data and commit**

Run: `grep -c -E "<source project name>|<dataset name>|<data-task id>|@" docs/science-ultrapowers/claude-science-schema.md`
Expected: 0.
Run: `git add skills/migrating-from-claude-science docs/science-ultrapowers/claude-science-schema.md && git commit -m "docs(migrate): record the Claude Science database schema and file layout"`

### Task 2: Fixture database builder

**Files:**
- Create: `skills/migrating-from-claude-science/scripts/tests/fixture_db.py`, `skills/migrating-from-claude-science/scripts/tests/test_fixture_db.py`

**Interfaces:**
- Produces: `build_fixture(root: Path) -> FixtureInfo` creating `root/orgs/<org>/operon-cli.db` (and `root/orgs/<org>/preferences.json` with the keys Task 1 records, holding one approved domain, one disabled group and one project grant) from the `CREATE TABLE` statements copied out of `docs/science-ultrapowers/claude-science-schema.md` (the test reads the statements from that file so the fixture cannot drift from the record), `root/config.toml` with `data_dir = "<root>"`, `root/mcp/directory-cache.json`, and the artifact files; `FixtureInfo` holds the ids it created. Rows: projects `proj_fix` (the target) and `proj_other`; `user_agents`: `LAB_PROJECT_MANAGER` with a skill list, `OPERON`; memories: m1 project-scope `agent_tool` `observed` with `source_frame_id` → a frame whose `agent_name` is `LIT_RESEARCHER`; m2 profile-scope (no subject); m3 superseded; m4 artifact-scope pointing at artifact a1; m5 project-scope of `proj_other`; m6 artifact-scope pointing at an id that is not an artifact; frames: one root `OPERON`, one `LIT_RESEARCHER` child with `task_summary`; artifacts: a1 with two copy versions (files on disk), a2 one copy version whose file is deleted after build, a3 host-linked version with `storage_path = "~/" + <root>/host/data.csv` (file present), a4 host-linked with a missing path; `artifact_dependencies`: a1v2 depends on a3v1; `verification_checks`: one `warn` `unaddressed` on a1v2; `execution_log`: one row referenced by a1v2 `producing_cell_id` with `source = "print('hi')"`; `directory_attachments`: two rows (`bundled:literature`, a directory uuid matching a `directory-cache.json` connector named `PubMed`); `user_secrets`: one row with `name = "TYPESAFE_API_KEY"` and a dummy encrypted value

- [ ] **Step 1: Write the failing test**

`test_fixture_db.py`: `build_fixture(tmp)` creates the database; `PRAGMA table_info(memories)` lists `evidence`; counts: 2 projects, 6 memories, 4 artifacts, 5 versions, 1 dependency, 1 check.

- [ ] **Step 2: Implement, run, commit**

Run: `git add skills/migrating-from-claude-science && git commit -m "test(migrate): fixture database built from the recorded schema"`

### Task 3: Resolver, copy, open, validate, list projects

**Files:**
- Create: `skills/migrating-from-claude-science/scripts/migrate_claude_science.py`, `skills/migrating-from-claude-science/scripts/tests/test_migrate_setup.py`

**Interfaces:**
- Produces: CLI `migrate_claude_science.py [--data-dir D] [--project ID_OR_NAME] --lab L [--transcripts] [--dry-run] [--list-projects]`; functions `resolve_data_dir(explicit: Path | None) -> tuple[Path, list[str]]` (warnings), `find_org_dir(data_dir: Path) -> Path` (the single `orgs/<uuid>` with `operon-cli.db`, else error listing candidates), `copy_db(org_dir: Path, tmp: Path) -> Path`, `open_ro(copy: Path) -> sqlite3.Connection`, `validate_schema(conn, required: dict[str, list[str]]) -> list[str]` (missing `table.column` strings), `REQUIRED_COLUMNS` dict covering every column the later steps read, `list_projects(conn) -> list[dict]` (`id, name, description`), `pick_project(conn, ref: str) -> dict` (exact id, else unique case-insensitive name substring, else error listing all); exit codes: 2 usage/not found, 3 schema mismatch

- [ ] **Step 1: Write the failing tests**

- `test_resolve_prefers_config_toml_data_dir`: `%USERPROFILE%` stand-in dir with `config.toml` `data_dir = "<B>"` and `last_move_from = "<A>"` where both exist → returns `<B>` with one warning naming `<A>`.
- `test_resolve_explicit_wins`.
- `test_find_org_dir_errors_on_two_orgs`.
- `test_copy_db_copies_wal_and_shm_and_leaves_original_untouched` (mtime and sha256 of the original unchanged; the copy opens).
- `test_open_ro_refuses_writes`: `INSERT` raises `sqlite3.OperationalError`.
- `test_open_ro_works_while_original_is_open_for_write`: hold a writable `sqlite3.connect(original)` with a pending transaction; `copy_db` + `open_ro` still succeed.
- `test_validate_schema_names_missing_column`: a fixture with `memories.evidence` dropped (built via `ALTER TABLE … DROP COLUMN` on a copy) → `["memories.evidence"]`; CLI exits 3 with `schema mismatch: memories.evidence`.
- `test_pick_project_by_substring_and_ambiguity`.
- `test_list_projects_cli_prints_json`.

- [ ] **Step 2: Run to fail; Step 3: implement; Step 4: run, commit**

Run: `git add skills/migrating-from-claude-science && git commit -m "feat(migrate): data-dir resolution, read-only immutable copy, schema validation, project selection"`

### Task 4: Memories

**Files:**
- Modify: `migrate_claude_science.py`
- Create: `tests/test_migrate_memories.py`

**Interfaces:**
- Produces: `export_memories(conn, project: dict, artifact_ids: set[str], lab: Path) -> MemoryReport` with counts `project, artifact, profile, superseded, other_project, orphan_artifact, already_present`; files under `research_lab/memory/project/<slug>.md` and `research_lab/memory/artifact/<aid>/<slug>.md`; `research_lab/migration/PROFILE_MEMORIES.md` and `SUPERSEDED_MEMORIES.md`; index lines appended under `## Project` / `## Artifacts` in `MEMORY.md`; `classify_type(body: str) -> str` (keywords: `gotcha` for `bug|upcast|fails|breaks|workaround|gotcha|mismatch`; `decision` for `decid|approv|ruling|ratif`; `directive` for `standing rule|directive|must never|no agent may|always`; `vocabulary` for `is defined as|means|stands for|refers to`; else `lesson`); `slugify(text: str, max_len: int = 60) -> str`; `learned_by` from `source_frame_id → frames.agent_name` lower-cased with `_` → `-` and the profile-to-agent mapping (`LIT_RESEARCHER` → `literature-researcher`, `DATA_EVAL_RESEARCHER` → `data-evaluation-researcher`, `DOC_WRITER` → `documentation-writer`, `DECISION_SYSTEMS` → `decision-systems-specialist`, `LAB_PROJECT_MANAGER` → `lab-project-manager`, `OPERON` → `main-session`, others by lower-case/dash), else `unknown`; to pass PLAN-03's lint every `learned_by` is reduced to kebab-case (each run of characters outside `[a-z0-9]` becomes one `-`, leading/trailing `-` trimmed, an empty result becomes `unknown`), a slug that normalises like an earlier one (same letters and digits, ignoring punctuation and a trailing `s`) gets `-2`, `-3`, and a row whose text is only lab-record ids (`see D-0124`, `F-0031, F-0032`) or is empty is not imported but listed for your human partner's prune in `research_lab/migration/PRUNE_CANDIDATES.md` (count `record_only` in the report)

- [ ] **Step 1: Write the failing tests** (against the Task 2 fixture, lab scaffolded with PLAN-06's `init_lab.py --yes` in the temp project)

- `test_project_memory_file_and_index_line`: m1 → `memory/project/<slug>.md` with frontmatter `type` from `classify_type`, `entity: project`, `evidence: observed`, `learned_by: literature-researcher`, `origin: import`, `date` = m1 `created_at` as `YYYY-MM-DD`; body fenced; one index line under `## Project`.
- `test_profile_memory_goes_to_profile_file_and_is_counted`.
- `test_superseded_is_listed_not_imported`.
- `test_artifact_scope_file_under_artifact_folder` (m4 → `memory/artifact/<a1>/…`; `entity: artifact:<a1>`).
- `test_other_project_row_excluded_and_counted`.
- `test_orphan_artifact_row_goes_to_project_with_note` (m6: `entity: project`, `note:` names the missing id).
- `test_rerun_counts_already_present`.
- `test_lint_passes_after_import`: `node skills/remembering-for-the-lab/scripts/memory-lint.mjs <store>` exits 0 (the fixture includes one row whose agent name has a space and a dot, two rows whose slugs differ only by a trailing `s`, and one row whose text is only `see D-0124`, which lands in `PRUNE_CANDIDATES.md`, not the store).
- `test_classify_type_examples` (one body per type).

- [ ] **Step 2: Run to fail; Step 3: implement; Step 4: run, commit**

Run: `git add skills/migrating-from-claude-science && git commit -m "feat(migrate): memories with scope, evidence, learned_by and the reconciliation counts"`

### Task 5: Profiles

**Files:**
- Modify: `migrate_claude_science.py`
- Create: `tests/test_migrate_profiles.py`

**Interfaces:**
- Produces: `export_profiles(conn, plugin_agents_dir: Path, lab: Path) -> ProfileReport` writing `research_lab/migration/profiles/<NAME>.md` (frontmatter `display_name`, `skill_names`; body: the system prompt in a fenced block) and `research_lab/migration/PROFILE_DIFF.md` with one section per profile: matched agent file (by the mapping in Task 4), the skill names present in the profile but not preloaded by the agent (after mapping old names to new; every name the agent does not preload is classified as `bundled` (the Claude Science bundled list in spec D7), `account` (the claude.ai-synced list), `example` (the Anthropic example-skills list) or `unknown`, each under its own heading, so a reader sees which skills reach Claude Code through the account and which are not portable), and a unified diff between the profile's system prompt and the agent body's first paragraph; profiles with no agent (`OPERON`) listed under `## Unmatched`

- [ ] **Step 1: Write the failing tests**

- `test_profile_file_written_with_skills`; `test_diff_matches_profile_to_agent` (fixture `LAB_PROJECT_MANAGER` ↔ a stub `agents/lab-project-manager.md` in a temp plugin dir); `test_unmatched_profile_listed` (`OPERON`); `test_missing_skills_classified` (`pdf-explore` → "bundled", `deep-research` → "account", `theme-factory` → "example", `no-such-skill` → "unknown", each under its own heading in `PROFILE_DIFF.md`).

- [ ] **Step 2: Run to fail; Step 3: implement; Step 4: run, commit**

Run: `git add skills/migrating-from-claude-science && git commit -m "feat(migrate): profile export and diff against the plugin agents"`

### Task 6: Artifacts, versions, dependencies, verification checks

**Files:**
- Modify: `migrate_claude_science.py`
- Create: `tests/test_migrate_artifacts.py`

**Interfaces:**
- Consumes: PLAN-02 `LabStore` (`append`, `rows`, `ensure_gitattributes`, `lfs_line_if_needed`) and the module function `sha256_file`; call `ensure_gitattributes()` once before the first copy so the store's two rule lines exist even when no imported file reaches the LFS threshold
- Produces: `export_artifacts(conn, project, org_dir: Path, store: LabStore, report) -> ArtifactReport` with counts `artifacts, versions_copied, versions_linked, versions_missing, versions_changed, dependencies, checks, already_present`; rows per PLAN-02 field names with `source: "claude-science"`, ids kept, `storage_path` `artifacts/store/<aid>/v<NNN>_<filename>` for copies (`NNN` = `version_number`), `link:<project-relative path>` for host files inside the project root and `link:<absolute POSIX path>` for host files outside it, `agent_name` mapped as in Task 4, `producing_command` from `execution_log.source` when `producing_cell_id` resolves else `null`, `code_description` from the version, `is_intermediate`, `is_checkpoint`, `destination` (the Claude Science artifact's `destination`, `"snapshot"` when null; PLAN-02 ruling R26 records destination per version, so the first lab save of a `working_data` artifact replaces the imported copy as Claude Science would), `environment` from `environment_snapshot` (JSON text or null), `created_at` converted from epoch ms; `dependencies` from `artifact_dependencies` rows whose both ends belong to the project; `verification_checks` rows with `reviewer_role` from `reviewer_frame_id → frames.agent_name` (mapped) else `reviewer`; LFS lines written for copied files at or above the threshold

- [ ] **Step 1: Write the failing tests**

- `test_copy_versions_land_in_store_with_kept_ids` (a1: `v001_`, `v002_` files, sha256 equals the fixture files, rows with the fixture ids).
- `test_missing_source_file_is_a_missing_row_and_report_line` (a2).
- `test_host_link_inside_project_becomes_relative_link` (a3 under the temp project) and `test_host_link_missing_is_missing_row` (a4).
- `test_dependency_edge_and_check_imported` (edge a1v2 → a3v1; the warn check with `status unaddressed`).
- `test_producing_command_from_execution_log`.
- `test_lfs_line_for_large_copied_version` (fixture file above a 1 MB threshold set in `lab.json`).
- `test_rerun_is_idempotent` (second run: `already_present == versions`, no duplicate rows, no duplicate `.gitattributes` lines).
- `test_counts_reconcile` (`artifacts == 4`, `versions_copied + versions_linked + versions_missing == 5`).

- [ ] **Step 2: Run to fail; Step 3: implement; Step 4: run, commit**

Run: `git add skills/migrating-from-claude-science && git commit -m "feat(migrate): artifact store import with lineage, checks and LFS lines"`

### Task 7: Digest, connectors, secret names, permissions, skill state, skill drift, transcripts, report, dry run

**Files:**
- Modify: `migrate_claude_science.py`
- Create: `tests/test_migrate_report.py`

**Interfaces:**
- Produces: `research_lab/migration/WHERE_WE_LEFT_OFF.md` (the last `*_kickoff.md` and `*_standup.md` from `research_lab/06_decisions/lab_meetings/` quoted in full if present, open rows of `TASK_BOARD.md` and `ACCESS_REQUESTS.md` if present, root frames `name, status, updated_at`, the last 20 non-null `task_summary` values of the project's frames); `CONNECTORS.md` (each `directory_attachments` row resolved against `mcp/directory-cache.json` by id, mapped to a `connectors.json` id when the URL matches, else listed as unmapped; `bundled:*` listed as not portable); `ENV_CHECKLIST.md` (`SELECT name FROM user_secrets`, one checkbox line each, no values); `PERMISSIONS.md` (spec D11; from `orgs/<org>/preferences.json` read as JSON: a table per source — the project's `approvalGrants.project.<project_id>` by category, the global `approvalGrants.always` by category, `hostGrants`, `userAllowedDomains`, the enabled built-in groups (every known group name minus `builtinAllowlistDisabledGroups`), `autoMode`, `gpuEnabled`, `reviewerModel` — each row with its Claude Code equivalent: a domain → `WebFetch(domain:<host>)`; a host folder outside the lab's project root → `permissions.additionalDirectories`, inside it → "the working directory"; an execution grant → "Claude Code saves a per-repository Bash rule on the first 'don't ask again'"; credential access → "see ENV_CHECKLIST.md"; auto mode → `defaultMode: auto`; reviewer model and GPU → informational; grants keyed by another project id → listed under "other projects"; followed by the `init --permissions --allow-domain ...` command that would write the domain rules; the migration itself writes no settings file); `SKILLS.md` (every `capability_settings` row: skill name, enabled flag, and its class — lab, vendored, bundled, account, example, unknown — with the lab and vendored names mapped to the plugin's); `SKILLS_DRIFT.md` (for each lab skill published under `orgs/<org>/skills/<old name>/SKILL.md`: sha256 versus the plugin's renamed skill; `differs`/`same`); with `--transcripts`: `research_lab/migration/transcripts/<frame_id>.jsonl` streamed from `frame_messages` for the project's frames and one `.gitattributes` LFS line per file at or above the threshold; `MIGRATION_REPORT.md` with a table `step | source count | imported | already present | skipped (reason)` for every step, the warnings, and the git commands to run next (`git add research_lab/ && git commit -m "lab: import Claude Science project <name>"`); on a real run `research_lab/lab.json` gets `claudeScience: {"dataDir": "<posix path>", "projectId": "<id>", "importedAt": "<ISO date>"}`; `--dry-run` computes every count, writes only `MIGRATION_REPORT.md` with `DRY RUN` in its title, and leaves `lab.json` unchanged

- [ ] **Step 1: Write the failing tests**

- `test_digest_lists_frames_and_task_summaries`; `test_lab_json_records_claude_science_source_on_real_run_only`; `test_connectors_mapped_and_unmapped`; `test_env_checklist_has_names_only` (contains `TYPESAFE_API_KEY`, not the dummy value); `test_permissions_md_maps_domains_and_grants` (the fixture's approved domain appears as a `WebFetch(domain:...)` line; the disabled group is absent from the enabled list; the other-project grant sits under "other projects"; no `.claude/settings.json` exists afterwards); `test_permissions_md_without_preferences_file_says_so` (no `preferences.json` → one line "not found", no error); `test_skills_md_lists_enabled_flags_and_classes` (a disabled bundled row and an enabled lab row); `test_no_transcripts_without_flag`; `test_transcripts_streamed_with_flag` (one file per frame, one JSON object per line); `test_dry_run_writes_only_report` (the lab has no new memory files, no store files; the report has `DRY RUN`); `test_report_counts_reconcile_to_source` (every row: source = imported + already present + skipped).

- [ ] **Step 2: Run to fail; Step 3: implement; Step 4: run, commit**

Run: `git add skills/migrating-from-claude-science && git commit -m "feat(migrate): digest, connectors, env checklist, permissions and skill-state reports, skill drift, optional transcripts, report and dry run"`

### Task 8: Dry run against the real database, and the skill

**Files:**
- Create: `docs/science-ultrapowers/evals/migration-dry-run.md`, `skills/migrating-from-claude-science/SKILL.md`

- [ ] **Step 1: Dry run on the source-project copy**

Run: `python skills/migrating-from-claude-science/scripts/migrate_claude_science.py --data-dir <scratchpad>/cs-data --project "<project name>" --lab "<scratchpad>/source-lab-copy/research_lab" --dry-run` where `<scratchpad>/cs-data` holds a copy of the data dir's `config.toml`, `orgs/<org>/operon-cli.db`, `orgs/<org>/artifacts/<project-id>/` and `mcp/`, and `<scratchpad>/source-lab-copy` is a copy of the source project's `research_lab/` scaffolded with `init_lab.py --yes`.
Expected: `MIGRATION_REPORT.md` source counts: memories 79, profiles 15, artifacts 418, versions 555, dependencies 940 (or the count of edges whose both ends are project versions, stated), verification checks 1,527, with zero `error` lines. Copy the report's table into `docs/science-ultrapowers/evals/migration-dry-run.md` with the date; if a count differs, stop and report the difference to your human partner before continuing.

- [ ] **Step 2: Write the skill**

Frontmatter: `name: migrating-from-claude-science`; `description: Use when a Claude Science data directory exists on this machine and a project in it should continue in this lab, when your human partner says to import, migrate or pick up from Claude Science, or after init detected a data directory`. Body (under 500 words): `## Overview` (*Resume the project from the exact state Claude Science left; lose nothing; read nothing live; copy no secret.*); `## Before running` (Claude Science may stay open: the script copies the database; confirm the lab exists, else run `science-ultrapowers:initializing-a-research-lab`; list projects with `--list-projects`); `## Run` (dry run first, show the report, then the real run after yes; `--transcripts` only when your human partner wants the archive); `## After the run` (read `MIGRATION_REPORT.md` together; `PROFILE_DIFF.md` decides nothing by itself; `PROFILE_MEMORIES.md` goes to Claude Code user memory by hand; `ENV_CHECKLIST.md` names variables to set; `CONNECTORS.md` feeds a second `init --connectors`; `PERMISSIONS.md` is a checklist, and its approved domains feed `init --permissions --allow-domain ...` if your human partner wants them; `SKILLS.md` shows which Claude Science skills reach Claude Code through the account and which do not; commit `research_lab/` under the lab's commit rule; `git lfs push` is your human partner's call); `## Never` (open the live database, read encrypted tables, print a value from `user_secrets`, import into a lab that is not the target project's); `## Command` lines.

- [ ] **Step 3: Suite, gate, commit**

Run: `bash tests/claude-code/run-tests.sh && git add skills/migrating-from-claude-science docs/science-ultrapowers/evals/migration-dry-run.md && git commit -m "feat(migrate): the migrating-from-claude-science skill and the pinned dry run"`

## Execution record (2026-11-08)

Executed by an Opus 5.5 orchestrator (Fable 5.1 for the final review and the closing steps); Sonnet 5.5 implementers wrote the schema dump, the fixture, the migration script task by task, the final-review fix pass and the decisions pass, and never committed. The orchestrator reviewed every diff, ran each step against scratchpad copies of the real Claude Science data between tasks, and committed in task order. A fresh Fable 5.1 reviewer judged the branch ready "with fixes" (0 Critical, 4 Important, 8 Minor, 8 set aside); every finding was fixed in one pass, each with a test that failed first, and the eight set-asides were decided with your human partner and implemented in a second pass.

- R2, R3, R15, R16: the org folder is the one `active-org.json` names when several exist; the WAL is folded into the copy before the immutable open; the config home is an option, defaulting to `~/.claude-science`.
- R4: the pinned counts came from the old org before the account move; the dry run ran on both orgs and all six match (79 / 15 / 418 / 555 / 940 / 1,527).
- R5, R9, R10: the recorded schema is the authority over the plan's prose names; `artifacts` has no `destination` column, so imported rows are snapshots; the record gained `capability_settings.kind`, the timestamp formats, the published-skills layout and the `compaction_archives` table.
- R8: one skill classifier (lab, vendored, bundled, account, example, unknown) reads the account skills from Claude Code's synced-skills folder at run time, so no person's skill names ship.
- R11: memory scope follows the four subject columns; rows scoped to a conversation of the project (10 real rows) are imported with a note.
- R12: built-in domain groups are reported by name only.
- R17, R18, R20, R21: `memory-map.json` keys idempotency (rebuilt from the files when lost); the record-only test is the lint's own pattern; every step takes `write=False` for the dry run; ledgers are written once.
- R23, R24, R26, R27: the lab is checked before the copy; the memory lint runs after import; every reviewer check of the project is imported (1,356 real checks judge conversation claims and have no version); a version without a recorded checksum is `ok`, never `changed`.
- Final fixes: Windows-illegal file names sanitised; every SQL column validated, with a guard test; database errors become the spec's advice; task summaries fenced; the SQLite URI encoded; `--lab` checked before the copy; and the other minors.
- Decided set-asides: refuse while Claude Science runs (`--allow-running` for a copy); transcripts as Claude Science session exports, one JSON per session, streamed; `learned_by` falls back to the parent, the root, then `main-session`; profile names use `_`; long-path failures are per-file warnings; dates are UTC; the dry-run report stays in `migration/`.
- Real data: a real run into a scratchpad copy of the project lab wrote 76 memories, 418 artifacts, 555 versions, 940 edges, 1,527 checks and 2 session exports; a re-run added nothing; the memory lint and `lfs-check` pass.
