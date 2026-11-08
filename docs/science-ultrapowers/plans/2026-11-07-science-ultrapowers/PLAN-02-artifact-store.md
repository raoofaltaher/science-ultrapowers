# PLAN-02: Artifact Store Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ultrapowers:subagent-driven-development (recommended) or ultrapowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the lab Claude Science's artifact model as a git-committed, project-local store: `artifacts.py` (save, link, search, path, lineage, graph, check, mark-addressed, resolve, lfs-check) and the `saving-artifacts` discipline skill that makes every role use it.

**Architecture:** One stdlib Python module with a `LabStore` class over four JSONL ledgers and a `store/` tree under `research_lab/artifacts/`, exposed as an argparse CLI printing JSON. Writes are atomic (temp file + `os.replace`). LFS is one exact-path `.gitattributes` line per file at or above the threshold, written before the file is staged. The skill carries the rules; the script carries the mechanics.

**Tech Stack:** Python 3.11+ stdlib (`argparse`, `json`, `hashlib`, `mimetypes`, `uuid`, `datetime`, `pathlib`, `subprocess` for `git add`), `unittest`.

**Spec:** `specs/2026-11-07-science-ultrapowers-design.md` — G8, D3, D4, D10, Components "saving-artifacts", Data flow, Error handling, Testing "Scripts".

**Sources:** Claude Science system prompt sections "Working style" (`save_artifacts(files, language, version_of, environment, checkpoints, destination)`, markers `{{artifact:VID}}` / `{{artifact:art_ID}}`, "workspace files are ephemeral", the instruction to discover files through the host object's artifacts call), "Checkpoint Rule" (`working_data` keeps only the latest copy; checkpoints are loadable serializations only) and "The host Object" (the host object's lineage lookup by version id → `{code, messages, env, inputs}`, and its lineage graph for a version id), read 2026-11-07 from the local Claude Science database; Claude Science `self-awareness` skill (table and column names for `artifacts`, `artifact_versions`, `artifact_dependencies`, `verification_checks`); Claude Code worktrees reference (LFS pointer files in worktrees). Not checked against documentation: that `.gitattributes` honours exact-path lines (from the git-attributes man page, from memory; Task 4's test proves it against the installed git); GitHub LFS quota figures (1 GB storage / 1 GB bandwidth) are from memory and appear only in a warning message.

## Global Constraints

- Python 3.11+ standard library only; no pip packages.
- Store root is `research_lab/artifacts/`; ledgers are `artifacts.jsonl`, `versions.jsonl`, `dependencies.jsonl`, `verification_checks.jsonl`; bytes live under `store/<artifact_id>/v<NNN>_<filename>` with `NNN` zero-padded to three digits; `.gitattributes` lives at `research_lab/artifacts/.gitattributes`.
- Thresholds come from `research_lab/lab.json`: `lfs.thresholdMB` (default 10), `lfs.budgetWarnMB` (default 800). The script runs without `lab.json` using the defaults.
- Ids are UUID4 strings for new rows; imported rows keep their Claude Science ids; every command accepts a version id, an artifact id, `art_<artifact_id>` or a unique id prefix.
- The script never runs `git commit`, `reset`, `restore`, `stash`, `checkout`, `rm`, `mv` or `push`; it runs only `git add` on the files it wrote, and only when the lab is inside a git work tree.
- The script refuses any path outside the project root (the parent directory of `research_lab/`).
- All timestamps are ISO-8601 UTC with a `Z` suffix.
- Skill writing follows PLAN-01's Global Constraints (superpowers form, verb-first name, "Use when" description, under 500 words for the skill body).

## Review Focus

1. A role saves a 12 MB CSV whose extension nobody listed: with the exact-threshold design the line is written from size alone; Task 4's test saves an 11 MB `.csv` and asserts the `.gitattributes` line and the `git add` order.
2. Two versions of one artifact saved in the same second collide on `created_at` ordering: `version_number` is the order, not the timestamp; Task 2's test saves two versions and asserts `version_number` 1 then 2 and `parent_version_id` chaining.
3. A marker written with the short id a human copies (`{{artifact:1b92aab8}}`): `resolve` must resolve a unique prefix and refuse an ambiguous one; Task 6's test covers both.
4. A `working_data` artifact's previous bytes must go when the new version lands, but the ledger must still say it existed: Task 2's test asserts the old file is gone and its row has `status: replaced`.
5. A user who moves a repo-linked file breaks `path`: Task 3's test deletes the linked file and asserts `path` exits 1 with `status: missing` in its JSON, never a traceback.

---

### Task 1: Store skeleton, config and atomic ledgers

**Files:**
- Create: `skills/saving-artifacts/scripts/artifacts.py`, `skills/saving-artifacts/scripts/tests/__init__.py` (empty), `skills/saving-artifacts/scripts/tests/test_store_basics.py`

**Interfaces:**
- Produces: `class LabStore` in `artifacts.py` with `__init__(self, lab: Path)`, attributes `lab`, `project_root` (= `lab.parent`), `root` (= `lab / "artifacts"`), `store` (= `root / "store"`), `config: dict` (merged defaults + `lab.json`), `threshold_bytes: int`, `budget_warn_bytes: int`; methods `append(self, ledger: str, row: dict) -> None` (atomic), `rows(self, ledger: str) -> list[dict]`, `rewrite(self, ledger: str, rows: list[dict]) -> None` (atomic); module function `find_lab(start: Path) -> Path` (walks up from `start` to the first directory containing `research_lab/lab.json` or `research_lab/artifacts`, else raises `LabNotFound`); `now_iso() -> str`; `sha256_file(path: Path) -> str`.

- [ ] **Step 1: Write the failing tests**

`test_store_basics.py` (uses `tempfile.TemporaryDirectory`; a helper `make_lab(tmp, lab_json=None)` creates `<tmp>/proj/research_lab/` and optionally writes `lab.json`):
- `test_defaults_without_lab_json`: `LabStore(lab).threshold_bytes == 10 * 1024 * 1024` and `budget_warn_bytes == 800 * 1024 * 1024`.
- `test_lab_json_overrides`: `lab.json` `{"lfs": {"thresholdMB": 1, "budgetWarnMB": 2}}` → `threshold_bytes == 1048576`, `budget_warn_bytes == 2097152`.
- `test_append_and_rows_roundtrip`: `append("artifacts", {"id": "a"})` twice with different ids → `rows("artifacts")` returns both in order; the file ends with a newline.
- `test_append_is_atomic`: no `*.tmp` file remains in `root` after `append`.
- `test_find_lab_walks_up`: from `<tmp>/proj/sub/dir` (created) `find_lab` returns `<tmp>/proj/research_lab`; from a directory with no lab raises `LabNotFound`.
- `test_sha256_file_matches_hashlib`: a 3-byte file's digest equals `hashlib.sha256(b"abc").hexdigest()`.

- [ ] **Step 2: Run them to see them fail**

Run: `python -m unittest skills.saving-artifacts.scripts.tests.test_store_basics -v` fails on import because the package path has a hyphen; use discovery instead: `python -m unittest discover -s skills/saving-artifacts/scripts/tests -v`
Expected: `ModuleNotFoundError: No module named 'artifacts'` (tests import it via `sys.path.insert(0, <scripts dir>)` in the test module header).

- [ ] **Step 3: Implement the skeleton**

In `artifacts.py`: module docstring (usage lines for every subcommand, filled in by later tasks), `DEFAULT_CONFIG = {"lfs": {"thresholdMB": 10, "budgetWarnMB": 800}}`, `LEDGERS = ("artifacts", "versions", "dependencies", "verification_checks")`, `class LabNotFound(Exception)`, `find_lab`, `now_iso`, `sha256_file` (1 MiB chunks), `LabStore` with the interface above (`append` writes the existing content plus the new line to `<ledger>.jsonl.tmp` then `os.replace`; `rewrite` the same from a list). `main(argv=None)` with an argparse parser that has `--lab PATH` (default: `find_lab(Path.cwd())`) and a `subparsers` object; no subcommands yet; `if __name__ == "__main__": sys.exit(main())`.

- [ ] **Step 4: Run the tests**

Run: `python -m unittest discover -s skills/saving-artifacts/scripts/tests -v`
Expected: 6 tests, `OK`.

- [ ] **Step 5: Commit**

Run: `git add skills/saving-artifacts && git commit -m "feat(artifacts): LabStore skeleton with atomic JSONL ledgers and lab discovery"`

### Task 2: `save`

**Files:**
- Modify: `skills/saving-artifacts/scripts/artifacts.py`
- Create: `skills/saving-artifacts/scripts/tests/test_save.py`

**Interfaces:**
- Consumes: Task 1 `LabStore`
- Produces: `LabStore.save(self, files: list[Path], *, role: str, command: str, session: str | None = None, version_of: str | None = None, inputs: list[str] | None = None, checkpoint: bool = False, intermediate: bool = False, destination: str = "snapshot", description: str | None = None, environment: str | None = None, stage: bool = True) -> list[dict]` returning one `{"artifact_id", "version_id", "version_number", "storage_path", "lfs": bool}` per file; CLI `save FILES... --role R --command C [--session S] [--version-of ID] [--inputs ID_OR_PATH ...] [--checkpoint] [--intermediate] [--destination snapshot|working_data] [--description T] [--environment T] [--no-stage]`; `LabStore.resolve_id(self, ref: str) -> tuple[str, str]` returning `("version", id)` or `("artifact", id)` for a full id, `art_<id>`, or a unique prefix, raising `AmbiguousId` / `UnknownId`.
- Row shapes (exact field names): `artifacts.jsonl`: `id, filename, latest_version_id, folder, is_user_upload, is_ephemeral, superseded_by, retention, destination, created_at, source`; `versions.jsonl`: `id, artifact_id, version_number, parent_version_id, kind ("copy"|"link"), content_type, size_bytes, sha256, storage_path, agent_name, producing_command, producing_session, code_description, is_intermediate, is_checkpoint, environment, created_at, source ("lab"|"claude-science"), status ("ok"|"replaced"|"missing"|"changed")`; `dependencies.jsonl`: `version_id, depends_on_version_id, reference_name`.

- [ ] **Step 1: Write the failing tests**

`test_save.py` (helper creates a lab inside a `git init`-ed temp repo and a workspace file):
- `test_save_new_file_creates_artifact_and_version`: one `report.md` → one artifacts row (`filename == "report.md"`, `destination == "snapshot"`, `source == "lab"`), one versions row (`version_number == 1`, `parent_version_id is None`, `kind == "copy"`, `content_type == "text/markdown"`, `sha256` equals the file's, `agent_name == "paper-author"`, `producing_command == "pytest"`, `status == "ok"`), the bytes at `store/<aid>/v001_report.md` equal the source, and `latest_version_id` points at the version.
- `test_save_second_version_chains`: save, edit, `save(version_of=aid)` → `version_number == 2`, `parent_version_id` = first version id, artifact `latest_version_id` updated, `v001_` and `v002_` both present.
- `test_save_same_filename_without_version_of_is_refused`: raises `StoreError` whose message contains `--version-of`.
- `test_save_identical_bytes_is_refused`: `save(version_of=aid)` with unchanged bytes raises `StoreError` containing `identical`.
- `test_save_records_inputs_as_edges`: `inputs=[other_version_id, "data/raw.csv"]` → two dependencies rows: the version id as `depends_on_version_id` with `reference_name == "<its filename>"`, and the path saved first as a `link` version (Task 3's `link`, so this test is marked `skip` until Task 3 and un-skipped there) — write the test now with `@unittest.skip("Task 3")`.
- `test_save_outside_project_root_is_refused`: a file in a sibling temp directory raises `StoreError` containing `outside`.
- `test_working_data_replaces_previous_bytes`: `destination="working_data"`, two saves → `v001_` file absent, its row `status == "replaced"`, `v002_` present.
- `test_save_marks_checkpoint_and_intermediate`: flags land in the row as booleans.
- `test_save_stages_written_files`: after `save(stage=True)` in the git temp repo, `git diff --cached --name-only` lists the stored file and `artifacts.jsonl`, `versions.jsonl`.
- `test_resolve_id_forms`: full version id → `("version", id)`; `art_<aid>` and full `aid` → `("artifact", aid)`; unique 8-char prefix → resolved; a prefix matching two ids raises `AmbiguousId`; `"nope"` raises `UnknownId`.

- [ ] **Step 2: Run them to see them fail**

Run: `python -m unittest discover -s skills/saving-artifacts/scripts/tests -v`
Expected: `AttributeError: 'LabStore' object has no attribute 'save'`.

- [ ] **Step 3: Implement `save`, `resolve_id`, `StoreError`, `AmbiguousId`, `UnknownId`**

Algorithm the signature does not fix: for each file, `rel = file.resolve().relative_to(project_root)` (ValueError → `StoreError("outside the project root")`); with `version_of`: resolve to an artifact (a version id maps to its artifact), compare `sha256` with the latest version's → `StoreError("identical to latest version")`; without it: an existing artifact with the same `filename` → `StoreError("artifact exists; pass --version-of <id>")`; `version_number = latest + 1`; copy bytes to `store/<aid>/v{n:03d}_{filename}`; if `destination == "working_data"` and a previous version has `kind == "copy"`, delete its file and `rewrite` its row with `status: "replaced"`; LFS line (Task 4; stub `self._lfs_line_if_needed(path) -> bool` returning `False` here); append rows; `stage` → `subprocess.run(["git", "add", "--", *paths], cwd=project_root, check=False)` only when `git rev-parse --is-inside-work-tree` succeeds. `content_type` from `mimetypes.guess_type`, default `application/octet-stream`.

- [ ] **Step 4: Run the tests**

Run: `python -m unittest discover -s skills/saving-artifacts/scripts/tests -v`
Expected: all pass except the one skipped test.

- [ ] **Step 5: Wire the CLI subcommand and commit**

Add the `save` subparser with the flags listed in Interfaces; `main` prints `json.dumps(result, indent=2)`; errors print `error: <message>` to stderr and return 1.
Run: `git add skills/saving-artifacts && git commit -m "feat(artifacts): save with version chains, working_data replacement, inputs and staging"`

### Task 3: `link`, `search`, `path`, `lineage`, `graph`

**Files:**
- Modify: `skills/saving-artifacts/scripts/artifacts.py`
- Create: `skills/saving-artifacts/scripts/tests/test_query.py`
- Modify: `skills/saving-artifacts/scripts/tests/test_save.py` (un-skip the inputs test)

**Interfaces:**
- Produces: `LabStore.link(self, paths: list[Path], *, role, command, session=None, inputs=None, description=None, stage=True) -> list[dict]` (a version with `kind == "link"`, `storage_path == "link:<project-relative path>"`); `LabStore.search(self, text: str, *, include_intermediate: bool = False) -> list[dict]` (artifacts whose `filename` or latest `code_description` contains `text`, case-insensitive, newest first, each row joined with its latest version's `content_type`, `size_bytes`, `version_number`); `LabStore.path(self, ref: str) -> Path` (absolute path of the version's bytes; raises `StoreError("missing")` when the file is gone and sets the row `status` to `missing`); `LabStore.lineage(self, ref: str) -> dict` with keys `version, artifact, inputs: [{version_id, filename, path}], checks: [rows]`; `LabStore.graph(self, ref: str) -> dict` with `nodes: [{version_id, artifact_id, filename, version_number}]`, `edges: [{from, to, reference_name}]` for the full ancestry (BFS over `dependencies`).

- [ ] **Step 1: Write the failing tests**

`test_query.py`:
- `test_link_records_repo_file_without_copying`: `link([project/"outputs/run.json"])` → version `kind == "link"`, `storage_path == "link:outputs/run.json"`, no file under `store/`, `sha256` correct.
- `test_link_outside_project_is_refused`.
- `test_search_matches_filename_and_description_case_insensitive`: three artifacts, `search("REPORT")` returns the two whose filename or description contains it, newest first, each with `content_type`.
- `test_search_hides_intermediate_by_default`.
- `test_path_for_copy_link_and_art_prefix`: `path(vid)`, `path(aid)`, `path("art_"+aid)` and `path(vid[:8])` all return the same absolute path.
- `test_path_missing_link_sets_status`: delete the linked file → `path` raises `StoreError` with `missing`; the versions row now has `status == "missing"`.
- `test_lineage_lists_inputs_and_checks`: a version saved with `inputs=[v_in]` → `lineage(v)["inputs"][0]["version_id"] == v_in`; `checks` is `[]`.
- `test_graph_walks_two_levels`: c depends on b depends on a → `graph(c)` has 3 nodes and 2 edges.
Un-skip `test_save_records_inputs_as_edges` and complete it: the path input becomes a `link` version and an edge.

- [ ] **Step 2: Run them to see them fail**

Run: `python -m unittest discover -s skills/saving-artifacts/scripts/tests -v`
Expected: `AttributeError` on `link`.

- [ ] **Step 3: Implement the five methods and their subcommands**

Subcommands: `link PATHS... --role --command [--session] [--inputs ...] [--description] [--no-stage]`; `search TEXT [--include-intermediate]`; `path REF`; `lineage REF`; `graph REF`. In `save`, an `inputs` entry that is not a resolvable id and exists as a file inside the project is linked first (`link`) and its new version id used for the edge; an entry that is neither raises `StoreError("unknown input")`.

- [ ] **Step 4: Run the tests**

Expected: all tests in the three files pass.

- [ ] **Step 5: Commit**

Run: `git add skills/saving-artifacts && git commit -m "feat(artifacts): link, search, path, lineage and graph"`

### Task 4: LFS lines and `lfs-check`

**Files:**
- Modify: `skills/saving-artifacts/scripts/artifacts.py`
- Create: `skills/saving-artifacts/scripts/tests/test_lfs.py`

**Interfaces:**
- Produces: `LabStore._lfs_line_if_needed(self, stored: Path) -> bool` (appends `store/<aid>/v<NNN>_<name> filter=lfs diff=lfs merge=lfs -text` to `root/.gitattributes` when `stored.stat().st_size >= threshold_bytes` and the line is absent; returns whether the file is LFS-tracked); `LabStore.lfs_total(self) -> int`; `LabStore.lfs_check(self) -> dict` with `missing_lines: [relative paths]`, `total_bytes`, `over_budget: bool`; CLI `lfs-check` exits 1 when `missing_lines` is non-empty; `save` prints `warning: LFS total <MB> MB exceeds <budget> MB` to stderr when `over_budget`.

- [ ] **Step 1: Write the failing tests**

`test_lfs.py` with `lab.json` `{"lfs": {"thresholdMB": 1, "budgetWarnMB": 2}}`:
- `test_small_file_gets_no_line`: a 10-byte file → `.gitattributes` has no `store/` line.
- `test_large_file_gets_exact_path_line_before_staging`: a 1.5 MiB `.csv` → `.gitattributes` contains exactly `store/<aid>/v001_big.csv filter=lfs diff=lfs merge=lfs -text`; in the git temp repo `git check-attr filter -- research_lab/artifacts/store/<aid>/v001_big.csv` prints `filter: lfs`; `git diff --cached --name-only` lists `research_lab/artifacts/.gitattributes` and the stored file.
- `test_line_written_once_per_file`: saving a second large version adds one more line, never a duplicate.
- `test_lfs_check_reports_missing_lines`: remove the `.gitattributes` line by hand → `lfs_check()["missing_lines"] == ["store/<aid>/v001_big.csv"]`; CLI exits 1.
- `test_budget_warning`: two 1.5 MiB versions → `over_budget` is True and `save` wrote `warning:` to stderr (capture with `contextlib.redirect_stderr`).

- [ ] **Step 2: Run them to see them fail**

Expected: `test_large_file_gets_exact_path_line_before_staging` fails (no line written).

- [ ] **Step 3: Implement**

`_lfs_line_if_needed` is called in `save` after the copy and before `git add`; the `.gitattributes` header comment (`# science-ultrapowers artifact store: one exact-path line per file at or above lfs.thresholdMB`) is written on first use. `lfs_total` sums `size_bytes` of `copy` versions whose path has a line.

- [ ] **Step 4: Run the tests, then commit**

Run: `python -m unittest discover -s skills/saving-artifacts/scripts/tests -v`
Expected: all pass.
Run: `git add skills/saving-artifacts && git commit -m "feat(artifacts): exact-path LFS lines at the size threshold, lfs-check and the budget warning"`

### Task 5: `check add` and `mark-addressed`

**Files:**
- Modify: `skills/saving-artifacts/scripts/artifacts.py`
- Create: `skills/saving-artifacts/scripts/tests/test_checks.py`

**Interfaces:**
- Produces: `LabStore.check_add(self, ref: str, *, claim: str, verdict: str, reviewer_role: str, severity: str | None = None, evidence: str | None = None, rebuttal: str | None = None) -> dict` (row: `id, version_id, claim, verdict, severity, evidence, rebuttal, reviewer_role, status ("open"), resolution (None), created_at`; `verdict` ∈ `pass|warn|fail|inconclusive` else `StoreError`); `LabStore.mark_addressed(self, check_id: str, note: str) -> dict` (status → `claimed`, `resolution = {"note": note, "at": now_iso()}`); `LabStore.outstanding(self, ref: str | None = None) -> list[dict]` (status `open` or `unaddressed` and verdict `fail` or `warn`); CLI `check add --version REF --claim C --verdict V --reviewer R [--severity] [--evidence] [--rebuttal]`, `check list [REF] [--all]`, `mark-addressed CHECK_ID --note N`.

- [ ] **Step 1: Write the failing tests**

- `test_check_add_defaults_to_open`; `test_check_add_rejects_bad_verdict`; `test_mark_addressed_moves_to_claimed_with_note`; `test_outstanding_filters_like_claude_science` (`pass` and `resolved` rows excluded; `warn`+`open` and `fail`+`unaddressed` included); `test_lineage_includes_checks` (Task 3's `lineage` now returns the rows).

- [ ] **Step 2: Run to see them fail, Step 3: implement, Step 4: run to pass**

Expected after implementation: all pass.

- [ ] **Step 5: Commit**

Run: `git add skills/saving-artifacts && git commit -m "feat(artifacts): reviewer checks on versions, outstanding filter and mark-addressed"`

### Task 6: `resolve` and the `saving-artifacts` skill

**Files:**
- Modify: `skills/saving-artifacts/scripts/artifacts.py`
- Create: `skills/saving-artifacts/scripts/tests/test_resolve.py`, `skills/saving-artifacts/SKILL.md`

**Interfaces:**
- Produces: `LabStore.resolve_markers(self, text: str, *, relative_to: Path) -> str` replacing every `{{artifact:<ref>}}` and `{{artifact:art_<aid>}}` with `[<filename>](<relative path>)` (POSIX separators), raising `AmbiguousId`/`UnknownId` for bad refs; CLI `resolve FILE [--write]` (prints to stdout, or rewrites the file in place with `--write`).

- [ ] **Step 1: Write the failing tests**

- `test_resolve_full_version_marker`; `test_resolve_art_marker_points_at_latest`; `test_resolve_unique_prefix`; `test_resolve_ambiguous_prefix_raises`; `test_resolve_write_rewrites_file`; `test_resolve_leaves_text_without_markers_unchanged`.

- [ ] **Step 2: Run to see them fail, Step 3: implement (`re.sub` with a callback over `\{\{artifact:([A-Za-z0-9_-]+)\}\}`), Step 4: run to pass**

- [ ] **Step 5: Write `skills/saving-artifacts/SKILL.md`**

Frontmatter: `name: saving-artifacts`; `description: Use when a task produces or changes a file the lab should keep (a report, protocol, figure, table, script, dataset, PDF), when a hand-off lists deliverables, or when looking for prior work before recomputing it`. Body, in superpowers form and under 500 words: `## Overview` (core principle: *The workspace is scratch. The store is the record.*); `## The Iron Law` code block `NO DELIVERABLE LEAVES A HAND-OFF UNSAVED, AND NOTHING IS RECOMPUTED BEFORE THE STORE IS SEARCHED`; `## The rules` as a quick-reference table (save after every hand-off, the orchestrator runs `save`; new content of an existing artifact → `--version-of`, never a new filename; repo files → `link`; inputs from the hand-off `Inputs:` line → `--inputs`; checkpoints only for expensive-to-regenerate state; `working_data` for big mutable files; reviewer verdicts → `check add`; reference artifacts in records as `[name]({{artifact:VID}})`; publish with `resolve`; discover with `search`, never with a filesystem listing; big files get an LFS line automatically, `lfs-check` at every stand-up, `git lfs pull` in a worktree); `## Commands` listing each subcommand on one line invoked as `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" <subcommand> …`; `## Common Rationalizations` table (at least: "I'll save it at the end", "it's just an intermediate file", "a new filename is cleaner than a version", "I remember this file exists", "the inputs are obvious", "the reviewer's note can live in chat"); `## Red Flags` list; `## Verification Checklist`.

- [ ] **Step 6: Run the whole suite and the gate, then commit**

Run: `bash tests/claude-code/run-tests.sh`
Expected: exit 0.
Run: `git add skills/saving-artifacts && git commit -m "feat(artifacts): marker resolution and the saving-artifacts skill"`

## Execution record (2026-11-07)

Executed by an Opus 5.5 orchestrator, with Sonnet 5.5 implementers per task and per fix pass. The final whole-branch review was by a fresh Fable 5.1 reviewer: 2 Critical, 6 Important and 20 Minor findings, all fixed, none deferred. Branch `plan-02-artifact-store`, stacked on `plan-01-plugin-shell` (921b82c), commits `06f0cdb..`. Deviations from the tasks above, each ruled with the spec as the authority:

- R2: every path is resolved before comparison, because of Windows 8.3 temp names. R3: content types come from a private `mimetypes.MimeTypes()`, since the registry maps `.csv` to `application/vnd.ms-excel`. R4: the `storage_path` forms are `artifacts/store/<aid>/v<NNN>_<name>`, `link:<project-relative>` and `link:<absolute>`. R19: the script is `#!/usr/bin/env python3`, 100755.
- R5: an awkward stored name gets the wildcard LFS line `store/<aid>/v<NNN>_*`. R6/R28: `.gitattributes` always carries `store/** -text` and `*.jsonl text eol=lf`, and `ensure_gitattributes()` restores them in an existing file. R12: staging uses `git add -A -- <paths>`. R17: an 11 MB CSV test at the default threshold.
- R7: `link` is idempotent on unchanged bytes and auto-versions changed ones. R23: copy and link artifacts never share a chain. R10: search orders by ledger position. R11: ids accept unique prefixes of 6+ characters. R13: lineage inputs carry `exists`.
- R14: `check review` completes the check lifecycle (resolved/unaddressed). R15/R25/R36: `path` prints `{version_id, path, status}`; `locate()` reports `ok`, `missing` or `pointer`, with `--no-stage`.
- R22: the subparser dest is `subcommand` (save has `--command`).
- Final review, Critical: ledgers split on `\n` only (U+2028 and friends bricked the store), and the CLI writes UTF-8 (a piped cp1252 stdout crashed on Greek letters).
- R26/R31: destination is recorded per version. The artifact's destination is set at creation and inherited. A `working_data` save replaces only earlier `working_data` copies; a `snapshot` milestone is kept. Imported Claude Science versions take their artifact's destination.
- R30: `ensure_gitattributes` and `lfs_line_if_needed` are public for PLAN-06/07. Inputs are validated before anything is written. The replaced copy loses its LFS line. The ledger is marked before any unlink, and every unlink is guarded to stay inside the store.
- I2, the citation contradiction between Step 5 and the `resolve_markers` interface above: `resolve` turns a bare marker into `[<filename>](<href>)` and a marker written as a link destination, `[text]({{artifact:VID}})`, into its href.
- R29/R35: `save` warns when the git-lfs filter is not configured. `lfs-check` reports `lfs_filter_configured`, `line_count` and a folding `suggestion` at 1,000 lines, and exits 1 on a missing line or an unconfigured filter. Folded `store/<aid>/**` lines and hand-edited equivalent lines count as coverage.
- `--lab` must name a research_lab, and R34 lets `find_lab` accept a bare one. `--inputs` may be repeated, and a comma-separated value gets a hint. OSError reports without a traceback.
- Task 6 omitted the pressure test that AGENTS.md requires. It was run afterwards (`docs/science-ultrapowers/evals/saving-artifacts/`: baselines 0/3, with the skill 6/6), and it changed both the skill text and the script.
