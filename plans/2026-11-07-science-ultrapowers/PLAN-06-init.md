# PLAN-06: `initializing-a-research-lab` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ultrapowers:subagent-driven-development (recommended) or ultrapowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold a project-local lab in any folder — records, templates, artifact and memory stores, the standing rules in the project `CLAUDE.md`, connectors in `.mcp.json`, LFS and ignore rules — adding only what is missing, never touching global settings, and offering the Claude Science migration when a data directory exists.

**Architecture:** A stdlib Python script `init_lab.py` that computes a plan (`create` / `append` / `skip` / `warn`) from a template tree and the current project, prints it as JSON in dry-run mode and applies it with `--yes`; a `connectors.json` catalogue; the project templates (records, twelve lab templates, `PROJECT_BRIEF.md` skeleton, the `CLAUDE.md` section, `lab.json`); an optional PowerShell environment script; and the skill that asks the questions, shows the file list, and runs the script.

**Tech Stack:** Python 3.11+ stdlib, JSON, PowerShell 7 (`setup_lab_env.ps1`), `unittest`.

**Spec:** `specs/2026-11-07-science-ultrapowers-design.md` — G6, G10, D8, D4, D10, Components "initializing-a-research-lab", "Project lab templates", Error handling, Testing.

**Sources:** Claude Code MCP reference (https://code.claude.com/docs/en/mcp.md: `.mcp.json` entries `type: http` with `url`, `headers` with `${VAR}` expansion, `stdio` with `command`/`args`, project-scope approval prompt), plugin skills reference (`${CLAUDE_PLUGIN_ROOT}` substitution), both read 2026-11-07; Claude Science `mcp/directory-cache.json` (connector names and URLs) and `directory_attachments` (46 rows), read 2026-11-07; the source project's `.mcp.json` (Optuna stdio entry); the current `research_lab/templates/*`, `README.md`, `claude_code_team/CLAUDE.md`, `claude_code_team/setup_claude_code_env.ps1`. Not checked: which directory connectors complete OAuth from a `.mcp.json` `http` entry (spec ledger row 1); `init` writes `url` only and the skill tells your human partner to run `/mcp` to authenticate.

## Global Constraints

- PLAN-01 Global Constraints apply.
- `init` writes only under the project root: `research_lab/**`, `CLAUDE.md` or `.claude/CLAUDE.md` (append between markers), `.mcp.json` (merge), `.gitattributes` is **not** touched at the root (the artifact store's own `research_lab/artifacts/.gitattributes` is created with the three lines of PLAN-02's `GITATTRIBUTES_HEADER`: the header comment, `store/** -text`, `*.jsonl text eol=lf`; `artifacts.py` `ensure_gitattributes()` also guarantees the two rule lines in an existing file), `.gitignore` (append two lines). Never `~/.claude/*`, never `.claude/agents`, never `.claude/skills`, never `.claude/settings.json`.
- Nothing is written before `--yes`; the dry run prints the full plan.
- Existing files are never overwritten; a file that exists is `skip`.
- The `CLAUDE.md` section sits between `<!-- science-ultrapowers:begin -->` and `<!-- science-ultrapowers:end -->`; a second run with the markers present is `skip`.
- Record folders and files are exactly the current layout plus `artifacts/`, `memory/`, `.scratch/`.
- `lab.json` keys: `name`, `shortName`, `description`, `pluginVersion`, `scaffoldedAt`, `roles` (the fourteen, all `true`), `lfs: {thresholdMB: 10, budgetWarnMB: 800}`, `memory: {indexBudget: 150, rediscoveryMinutes: 15, trailer: "Memory-Ref"}`, `connectors: [ids]`, `jev: {blockedPaths: []}`, `claudeScience: null | {dataDir, projectId}`.

## Review Focus

1. A project whose `CLAUDE.md` is a symlink or is read-only: `init` reports the append as `warn` with the OS error and continues; Task 3's test makes the file read-only and asserts no traceback.
2. `.mcp.json` with a trailing comma or comments (invalid JSON): `init` refuses to merge and says why, leaving the file alone; Task 4's test covers it.
3. A connector id passed on the command line that is not in the catalogue: `init` exits 2 naming the id, before writing anything; Task 4's test.
4. Running `init` from a subfolder of the project (cwd ≠ root): `--project-root` is required and defaults to the git top-level when inside a repo, else to the cwd; Task 2's test runs from `proj/src`.
5. Windows paths in `lab.json` and `.mcp.json` must use forward slashes; Task 2 and Task 4 assert no backslash in the written JSON.
7. Every place an agent body says "named in the project brief" (PLAN-05: the fields, the method and its implementation, the documentation set, the manuscript, the quality gates, the data risks and compute limits) has a slot in the `PROJECT_BRIEF.md` skeleton: §1, §3, §4, §5, §6; Task 1's review reads the agents against the skeleton.
6. `--permissions` when `.claude/settings.json` already exists: `init` writes nothing there, reports `skip` with the reason and prints the rules; Task 6's test. Without `--permissions`, no settings file is ever created; Task 6's test.

---

### Task 1: Templates and the connector catalogue

**Files:**
- Create: `skills/initializing-a-research-lab/templates/research_lab/README.md`, `…/templates/research_lab/<NN_folder>/README.md` for the ten record folders, the empty ledgers (`02_findings_ledger/FINDINGS.md`, `CANONICAL_NUMBERS.md`, `LAB_NOTEBOOK.md`; `01_reference_registry/REGISTRY.csv` (header row only), `EXCEPTIONS.md`; `03_experiments/EXPERIMENT_REGISTER.md`; `04_reviews/REVIEW_LOG.md`; `05_access_requests/ACCESS_REQUESTS.md`; `06_decisions/DECISIONS.md`; `07_project_management/TASK_BOARD.md`, `ROADMAP_STATUS.md`, `RISK_REGISTER.md`; `08_decision_log/JEV_CALLS.jsonl` (empty), `thresholds.json` (`{}`); `09_skill_vetting/README.md`), `…/templates/research_lab/templates/*.md` (the twelve current templates generalised: `EVIDENCE_CARD`, `H_CARD`, `PREREGISTRATION`, `REVIEW_ACADEMIC`, `REFEREE_REPORT`, `CITATION_AUDIT`, `HANDOFF` (the PLAN-04 block with `Inputs:` and `Memories proposed:`), `METHOD_PROPOSAL`, `DEVILS_ADVOCATE_TEMPLATE`; the three meeting templates `SESSION_KICKOFF`, `SESSION_STANDUP`, `LAB_MEETING` are **not** duplicated here: `init_lab.py` copies them at run time from `skills/holding-lab-meetings/templates/`, the way it copies the memory templates, so `research_lab/templates/` ends with twelve files), `…/templates/research_lab/00_project_knowledge/PROJECT_BRIEF.md` (skeleton), `…/templates/CLAUDE_SECTION.md`, `…/templates/lab.json`, `…/templates/gitignore_lines.txt`
- Create: `skills/initializing-a-research-lab/connectors.json`

**Interfaces:**
- Produces: the template tree `init_lab.py` copies verbatim (with `{{NAME}}`, `{{SHORT_NAME}}`, `{{DESCRIPTION}}`, `{{DATE}}`, `{{PLUGIN_VERSION}}` substituted); `connectors.json` as a list of `{id, name, kind: "mcp"|"account"|"bundled", tag: "science"|"other", transport: "http"|"stdio"|null, url, command, args, headers, apiKeyEnv, note}`

- [ ] **Step 1: Write the record folder READMEs and ledgers**

Each folder README: one paragraph naming what lives there and who maintains it (from the current `research_lab/README.md` map and `TEAM_SPEC.md` §4, roles by name). Ledgers: the heading and the column header row from the current files, no rows. Fields that apply only to some fields of research (seeds, GPU and CUDA versions, train/dev/test splits, hyper-parameter studies) carry "(where applicable)" in the header or README; the lab is otherwise field-agnostic (spec anti-goals, Components).

- [ ] **Step 2: Write `PROJECT_BRIEF.md` skeleton**

Sections with one italic prompt each: `# {{NAME}} project brief`; `## 1. The project in one paragraph` (*and its research fields*); `## 2. Research questions and hypotheses`; `## 3. Method` (*name the method and where it is implemented*); `## 4. Data and known risks` (*name the datasets, their splits, the known leakage paths and the compute limits*); `## 5. Code, environment and quality gates` (*name the repository folders, the environment manager, the linter, type checker, security scanner and test command the Research Engineer must run*); `## 6. Documents and the manuscript` (*name the documentation set and the manuscript file*); `## 7. Out of scope` (*folders no role may open*); `## 8. Current phase and critical path`; `## 9. Source tiers and approved exceptions` (*Tier B approvals live in `research_lab/01_reference_registry/EXCEPTIONS.md`*).

- [ ] **Step 3: Write `CLAUDE_SECTION.md`**

Between the two markers: `# Research lab ({{SHORT_NAME}})`; one line pointing at `science-ultrapowers:running-the-lab`; `## Standing rules` with the generic forms of the current rules 1-6, 8, 11-15 (evidence rule incl. attribution-only preprints; every level re-checks; numbers from the ledger; gates; test split; paywalled papers through your human partner; Jev positioning and `TYPESAFE_API_KEY` from the environment; verification claims name the check; environment changes need approval; session kickoff; session stand-up; scratch files in `research_lab/.scratch/`; and the lab commit rule: the orchestrator commits `research_lab/` after each hand-off and stand-up, never code); `## Team` (the fourteen agent names); `## Project knowledge` with `@research_lab/00_project_knowledge/PROJECT_BRIEF.md` and `@research_lab/memory/MEMORY.md` (the script rewrites both to `@../research_lab/…` when writing into `.claude/CLAUDE.md`). Project-specific items (out-of-scope folders, dev commands, legacy agents) are **not** here; the brief holds them.

- [ ] **Step 4: Write `lab.json` template and `gitignore_lines.txt`**

`lab.json` with the keys in Global Constraints and placeholders; `gitignore_lines.txt`: `research_lab/.scratch/`, `.venv-lab-skills/` and `references/` (PLAN-04's skills keep full-text PDFs in `references/` at the project root; licensed full texts stay out of shared git history by default). `init_lab.py` also creates the empty `references/` folder.

- [ ] **Step 5: Write `connectors.json`**

`kind: "mcp"`, `transport: "http"`: `firecrawl` (science, `https://mcp.firecrawl.dev/v2/mcp-search`), `pubmed` (science, `https://pubmed.mcp.claude.com/mcp`), `biorxiv` (science, `https://hcls.mcp.claude.com/biorxiv/mcp`), `chembl` (science, `https://hcls.mcp.claude.com/chembl/mcp`), `clinical-trials` (science, `https://hcls.mcp.claude.com/clinical_trials/mcp`), `microsoft-learn` (science, `https://learn.microsoft.com/api/mcp`), `canva` (other, `https://mcp.canva.com/mcp`), `figma` (other, `https://mcp.figma.com/mcp`), `notion` (other, `https://mcp.notion.com/mcp`), `linear` (other, `https://mcp.linear.app/mcp`), `atlassian` (other, `https://mcp.atlassian.com/v1/mcp`), `asana` (other, `https://mcp.asana.com/sse`, transport `sse`), `box` (other, `https://mcp.box.com`), `monday` (other, `https://mcp.monday.com/mcp`), `hubspot` (other, `https://mcp.hubspot.com/anthropic`), `intercom` (other, `https://mcp.intercom.com/mcp`), `euler` (other, `https://mcp.eulerapp.com/mcp`), `microsoft-365` (other, `https://microsoft365.mcp.claude.com/mcp`), `gojiberry` (other, `https://mcp.gojiberry.ai`), `lusha` (other, `https://mcp.lusha.com/mcp/claude`), `apollo` (other, `https://mcp.apollo.io/mcp`); org-specific ones (`gitlab`, `nextit`, `odoo`) as `kind: "mcp"`, `tag: "other"`, with their URLs and `note: "organisation-specific"`. `kind: "mcp"`, `transport: "stdio"`: `optuna` (science, `command: "uvx"`, `args: ["optuna-mcp", "--storage", "sqlite:///{{PROJECT_ROOT}}/outputs/optuna/optuna.db"]`, `note: "requires uv"`). `kind: "account"` (science): `scispace`, `scholar-gateway`, `wiley-scholar-gateway`, `scite`, `hugging-face`, `context7`, `deepwiki`, `mermaid-chart`, `excalidraw`, `claude-docs`, `google-drive`, `github`; `kind: "account"` (other): `gmail`, `google-calendar`; each with `note: "reachable through the claude.ai sign-in in Claude Code; not configurable in .mcp.json"`. `kind: "bundled"`: the twenty `bundled:*` names with `note: "Claude Science only; not portable"`. Every entry has `headers: {}` and `apiKeyEnv: null` unless a key is known to be required.

- [ ] **Step 6: Validate and commit**

Run: `python -c "import json;d=json.load(open('skills/initializing-a-research-lab/connectors.json'));print(len(d))"` → prints the entry count (expected 59 = 25 http/sse + 1 stdio + 14 account + 20 bundled; adjust the plan's count if a URL is missing).
Run: `bash tests/claude-code/test-no-foreign-harness.sh && git add skills/initializing-a-research-lab && git commit -m "feat(init): project templates, CLAUDE.md section and the connector catalogue"`

### Task 2: `init_lab.py` plan and apply for a fresh folder

**Files:**
- Create: `skills/initializing-a-research-lab/scripts/init_lab.py`, `skills/initializing-a-research-lab/scripts/tests/test_init_fresh.py`

**Interfaces:**
- Produces: `python init_lab.py --project-root P --name N --short-name S --description D [--connectors id,id] [--lfs-threshold-mb 10] [--git-init] [--yes] [--json]`; functions `build_plan(project_root: Path, opts: Options) -> Plan` where `Plan` has `create: list[str]`, `append: list[str]`, `skip: list[str]`, `warn: list[str]`, `connectors: dict` (the `.mcp.json` servers to merge), `duplicates: list[str]`; `apply_plan(plan: Plan, project_root: Path, opts: Options) -> dict` (report with the same keys plus `written`); without `--yes` the script prints the plan JSON and exits 0 writing nothing

- [ ] **Step 1: Write the failing tests**

`test_init_fresh.py` (temp dir `proj/`):
- `test_dry_run_writes_nothing_and_lists_files`: no `--yes` → `proj/` unchanged; stdout JSON `create` contains `research_lab/lab.json`, `research_lab/artifacts/.gitattributes`, `research_lab/memory/MEMORY.md`, `research_lab/templates/HANDOFF.md`, `CLAUDE.md`; `append` contains `.gitignore`.
- `test_apply_creates_layout`: with `--yes`: the ten record folders, `templates/` with 12 files, `artifacts/store/`, `memory/project/`, `memory/artifact/`, `.scratch/.gitkeep`, `lab.json` with `name`, `shortName`, `lfs.thresholdMB == 10`, `memory.indexBudget == 150`, `roles` has 14 true entries, `claudeScience is None`; `CLAUDE.md` contains both markers and `@research_lab/00_project_knowledge/PROJECT_BRIEF.md`; `.gitignore` has the two lines; `research_lab/artifacts/.gitattributes` has the header line.
- `test_rerun_skips_everything`: second `--yes` run → `create == []`, `append == []`, all in `skip`.
- `test_placeholders_substituted`: `PROJECT_BRIEF.md` first line is `# <name> project brief`; no `{{` remains in any written file.
- `test_project_root_defaults_to_git_toplevel_from_subdir`: `git init proj`, run from `proj/src` without `--project-root` → writes into `proj/`.
- `test_no_backslashes_in_written_json`.
- `test_lfs_threshold_flag`: `--lfs-threshold-mb 25` → `lab.json` `lfs.thresholdMB == 25`.

- [ ] **Step 2: Run to see them fail; Step 3: implement**

`init_lab.py`: `TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates"`; `Options` dataclass; `build_plan` walks `TEMPLATE_ROOT/research_lab`, mapping each file to `create` or `skip`; `CLAUDE.md` → `create` when absent, `append` when present without markers, `skip` with markers; `.gitignore` → `append` of missing lines; `apply_plan` writes with `{{…}}` substitution (`{{PROJECT_ROOT}}` as POSIX path), creates `.scratch/.gitkeep`, copies `MEMORY.md`/`README.md` from `skills/remembering-for-the-lab/templates/` (path `parents[2] / "remembering-for-the-lab/templates"`) and the three meeting templates from `parents[2] / "holding-lab-meetings/templates"` into `research_lab/templates/`, creates `research_lab/artifacts/.gitattributes` by calling PLAN-02's `LabStore(lab).ensure_gitattributes()` (imported by path from `parents[2] / "saving-artifacts/scripts"`), so init and the store can never disagree on its lines; `--git-init` → `git init -b main` then `git add research_lab CLAUDE.md .gitignore && git commit -m "chore: initialise the research lab"` only when `.git` is absent. Project root default: `git rev-parse --show-toplevel` if inside a repo, else cwd.

- [ ] **Step 4: Run the tests, commit**

Run: `python -m unittest discover -s skills/initializing-a-research-lab/scripts/tests -v`
Expected: `OK`.
Run: `git add skills/initializing-a-research-lab && git commit -m "feat(init): plan-and-apply scaffold for a fresh project"`

### Task 3: Existing projects: skip, append, duplicates, `.claude/CLAUDE.md`

**Files:**
- Modify: `skills/initializing-a-research-lab/scripts/init_lab.py`
- Create: `skills/initializing-a-research-lab/scripts/tests/test_init_existing.py`

- [ ] **Step 1: Write the failing tests**

Fixture `make_afn_like(tmp)`: `research_lab/` with the ten folders and some files present (`FINDINGS.md` with content, `templates/EVIDENCE_CARD.md`), no `artifacts/`, no `memory/`, `.claude/CLAUDE.md` with content and no root `CLAUDE.md`, `.claude/agents/citation-auditor.md`, `.claude/skills/doi-verified-evidence/SKILL.md`, `.claude/skills/peer-review/SKILL.md`.
- `test_existing_files_are_skipped_and_untouched`: `FINDINGS.md` bytes identical after `--yes`; it is in `skip`.
- `test_missing_pieces_are_created`: `artifacts/`, `memory/`, `lab.json`, `.scratch/.gitkeep` created.
- `test_section_goes_to_dot_claude_when_it_is_the_only_instructions_file`: `.claude/CLAUDE.md` gains the markers and `@../research_lab/00_project_knowledge/PROJECT_BRIEF.md`; no root `CLAUDE.md` created.
- `test_root_claude_md_preferred_when_present`: with both files, the root one gets the section.
- `test_duplicates_are_reported_not_touched`: `duplicates` lists `.claude/agents/citation-auditor.md`, `.claude/skills/doi-verified-evidence`, `.claude/skills/peer-review`; the files are unchanged; the report has a `warn` line naming them.
- `test_readonly_claude_md_is_a_warning`: `chmod 0o444` on `.claude/CLAUDE.md` → `warn` contains the path; exit 0; no traceback.

- [ ] **Step 2: Run to fail; Step 3: implement**

Duplicate detection: agent names = the fourteen; skill names = PLAN-04's lab skill names, the five old names, and the fourteen vendored names. Read-only append: catch `PermissionError`, add to `warn`.

- [ ] **Step 4: Run, commit**

Run: `git add skills/initializing-a-research-lab && git commit -m "feat(init): existing-project handling, duplicate detection and .claude/CLAUDE.md placement"`

### Task 4: Connectors into `.mcp.json`

**Files:**
- Modify: `skills/initializing-a-research-lab/scripts/init_lab.py`
- Create: `skills/initializing-a-research-lab/scripts/tests/test_init_connectors.py`

**Interfaces:**
- Produces: `--connectors firecrawl,pubmed,optuna` merges `{"mcpServers": {"firecrawl": {"type": "http", "url": …}, "pubmed": {…}, "optuna": {"type": "stdio", "command": "uvx", "args": [...]}}}`; `--connectors science` selects every `kind == "mcp"` and `tag == "science"` entry; `account` and `bundled` ids are reported in `warn`, never written

- [ ] **Step 1: Write the failing tests**

- `test_science_selects_the_tagged_mcp_entries`: keys are exactly `firecrawl, pubmed, biorxiv, chembl, clinical-trials, microsoft-learn, optuna`.
- `test_merge_keeps_existing_servers`: an existing `.mcp.json` with `Optuna` (capital O) stays; new keys added; file still valid JSON with 4-space indent.
- `test_invalid_existing_mcp_json_is_left_alone`: a file with a trailing comma → `warn` names it, file bytes unchanged.
- `test_unknown_connector_id_exits_2_before_writing`.
- `test_account_and_bundled_ids_are_warnings`: `--connectors scispace,bundled:literature` → nothing written to `.mcp.json`, two `warn` lines.
- `test_project_root_placeholder_in_args_is_posix`: optuna `args[2]` contains the project root with forward slashes.
- `test_lab_json_records_connectors`: `lab.json` `connectors == ["firecrawl", "pubmed", …]`.

- [ ] **Step 2: Run to fail; Step 3: implement; Step 4: run, commit**

Run: `git add skills/initializing-a-research-lab && git commit -m "feat(init): connector catalogue selection merged into the project .mcp.json"`

### Task 5: `setup_lab_env.ps1`

**Files:**
- Create: `skills/initializing-a-research-lab/scripts/setup_lab_env.ps1`
- Test: `tests/claude-code/test-setup-env-dryrun.sh`
- Source: `claude_code_team/setup_claude_code_env.ps1`

- [ ] **Step 1: Write the failing test**

`test-setup-env-dryrun.sh`: skips with `ok (pwsh absent)` when `pwsh` is not on PATH; otherwise runs `pwsh -NoProfile -File skills/initializing-a-research-lab/scripts/setup_lab_env.ps1 -ProjectRoot <tmp> -DryRun` and asserts the output names `.venv-lab-skills`, the package list contains `pillow` and `python-pptx`, mentions `TESSDATA_PREFIX` and `TYPESAFE_API_KEY` as steps that need a separate yes, and that `<tmp>` has no new files.

- [ ] **Step 2: Adapt the script**

Parameters `-ProjectRoot`, `-DryRun`, `-SetUserEnv` (default off; only with it does the script touch the Windows user environment, and it asks `Read-Host` for confirmation before each variable); pinned packages copied from the source; remove the lab load-tests call.

- [ ] **Step 3: Run the test, commit**

Run: `git add skills/initializing-a-research-lab tests/claude-code/test-setup-env-dryrun.sh && git commit -m "feat(init): optional figure-skill environment script with dry run"`

### Task 6: Project permission rules (opt-in)

**Files:**
- Modify: `skills/initializing-a-research-lab/scripts/init_lab.py`
- Create: `skills/initializing-a-research-lab/templates/permissions.json`, `skills/initializing-a-research-lab/scripts/tests/test_init_permissions.py`

**Interfaces:**
- Produces: `--permissions [--allow-domain HOST ...]` adds `.claude/settings.json` to the plan as `create` with `{"permissions": {"allow": ["WebFetch(domain:api.crossref.org)", "WebFetch(domain:doi.org)", "WebFetch(domain:api.openalex.org)", "WebFetch(domain:arxiv.org)", "WebFetch(domain:openreview.net)", "WebFetch(domain:proceedings.mlr.press)", "WebFetch(domain:pubmed.ncbi.nlm.nih.gov)", "WebFetch(domain:www.biorxiv.org)", "WebFetch(domain:www.semanticscholar.org)", ...]}}` (the template list plus one rule per `--allow-domain`, sorted, no duplicates), only when the file does not exist; when it exists, a `skip` line naming the file and the rules printed to stdout for hand merging; without `--permissions`, nothing. No Bash rule is ever written (spec D11). `lab.json` records `permissions: {"written": true|false}`.

- [ ] **Step 1: Write the failing tests**

- `test_permissions_writes_webfetch_allows_when_absent`: `--permissions --allow-domain ieeexplore.ieee.org --yes` → `.claude/settings.json` exists, valid JSON, `permissions.allow` holds every template rule and `WebFetch(domain:ieeexplore.ieee.org)`, no rule starts with `Bash(`.
- `test_permissions_skips_existing_settings`: a pre-existing `.claude/settings.json` with `{"theme": "x"}` → bytes unchanged, `skip` line in the plan, the rules in stdout.
- `test_no_permissions_flag_writes_no_settings`: default run → no `.claude/` created.
- `test_permission_rules_are_sorted_and_unique`: `--allow-domain doi.org` twice → one `doi.org` rule.

- [ ] **Step 2: Run to fail; Step 3: implement; Step 4: run, commit**

Run: `git add skills/initializing-a-research-lab && git commit -m "feat(init): opt-in project permission rules for the literature domains"`

### Task 7: The skill

**Files:**
- Create: `skills/initializing-a-research-lab/SKILL.md`

- [ ] **Step 1: Write the skill**

Frontmatter: `name: initializing-a-research-lab`; `description: Use when a project has no research_lab/, when your human partner asks to start, set up, join or upgrade a lab for a paper or project, or when the lab scaffold is older than the plugin`. Body (under 500 words): `## Overview`; `## Ask first` (project name, short name, one-paragraph description; whether a Claude Science data directory exists — auto-detect `%USERPROFILE%\.claude-science\config.toml` and the `data_dir` it names — and offer `science-ultrapowers:migrating-from-claude-science`; which connectors — show the `science` set ticked and the rest unticked, name the `account` connectors as already reachable after `/mcp` sign-in and the `bundled` ones as not portable; LFS threshold, default 10 MB; whether to run the environment script; whether to write project permission rules for the literature domains, default no, and only when `.claude/settings.json` does not exist, with any approved domains from a migration's `PERMISSIONS.md` offered as `--allow-domain`); `## Show, then write` (run the script without `--yes`, show the plan verbatim, write only after yes; in a non-git folder offer `--git-init`); `## After writing` (tell your human partner: review `PROJECT_BRIEF.md`, approve `.mcp.json` when Claude Code prompts, run `/mcp` for connectors needing sign-in, remove duplicate `.claude/agents` and `.claude/skills` copies if the report listed them, install `git lfs` if the report said so); `## Never` (global settings, existing files, `.claude/agents`, `.claude/skills`, secrets in files); `## Command` (the one line with the plugin path).

- [ ] **Step 2: Gate, suite, commit**

Run: `bash tests/claude-code/run-tests.sh && git add skills/initializing-a-research-lab && git commit -m "feat(init): the initializing-a-research-lab skill"`

## Execution record (2026-11-08)

Executed by an Opus 5.5 orchestrator; Sonnet 5.5 implementers wrote the templates, `init_lab.py` (Tasks 2, 3, 4 and 6, one conversation, task by task) and `setup_lab_env.ps1`; a Haiku 5.5 implementer wrote `connectors.json`; none committed. The orchestrator reviewed every diff, sent back what the review found (eight fixes before commit), wrote the skill and its pressure test, and committed in task order. A fresh Fable 5.1 reviewer judged the branch ready "with fixes" (0 Critical, 1 Important, 8 Minor, 8 set aside); every finding was fixed in one pass, each code fix with a test that failed first, or ruled.

- R2 (superseded in the fix pass): `.gitignore` gets three lines, anchored to the project root (`/research_lab/.scratch/`, `/.venv-lab-skills/`, `/references/`), so a nested `references/` folder stays tracked.
- R3, R5, R24: `--permissions` writes `.claude/settings.json` only when absent, with 17 `WebFetch` hosts (the plan's nine, the Tier B proceedings sites, OpenAlex, Semantic Scholar's API, medRxiv, PubMed Central); never a command rule; `lab.json` records `permissions.written`.
- R6, R7, R8, R9: the catalogue has 56 entries (21 http or sse, 1 stdio, 14 account, 20 bundled); GitLab, Odoo and NextIT are organisation deployments and stay out; account URLs are information only.
- R10, R17: Task 1 committed a frontmatter-only SKILL.md; `test-skill-content.sh` dropped the folder from PENDING, and check (g) skips the section markers.
- R12, R13: `lab.json` `lfs` is `{thresholdMB, budgetWarnMB}` as `artifacts.py` reads it; the CLAUDE.md section holds the generic standing rules, the project-specific ones go in the brief.
- R20, R21, F6: duplicates are listed (every plugin skill name and the five old names), never touched; a marker in either instructions file stops a second section; no symlinked instructions file, `.mcp.json` or `.gitignore` is written through.
- R22, R26: the `.mcp.json` merge keeps existing servers (case-insensitive) and the file's indent, and accepts a file saved with a byte-order mark; `lab.json` lists the `mcp` ids `.mcp.json` holds after the run.
- R25, R27: the git tests ignore the machine's git configuration; the `--git-init` commit adds `research_lab/` and every other written file by its own path, so nothing else under `.claude/` enters it.
- R28, R29: the skill finds Claude Science through `config.toml` and its `data_dir`; the pressure test went from a 1/7 baseline through five iterations to 7/7 (records in `docs/science-ultrapowers/evals/initializing-a-research-lab/`).
- Final fixes: anchored ignore lines; CRLF instructions files stay CRLF; the duplicates warning asks for a check first; the optuna warning names the machine path; a missing plugin template is a warning; the re-run sentence in the skill; docs/testing.md.
