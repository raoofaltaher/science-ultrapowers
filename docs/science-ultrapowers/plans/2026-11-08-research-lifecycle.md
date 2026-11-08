# Research Lifecycle and Tracks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ultrapowers:subagent-driven-development (recommended) or ultrapowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give science-ultrapowers one scholarly vocabulary (a terminology standard, a test and a scholarly output style, with every text renamed) and make it a complete research lifecycle: five tracks that enter one lifecycle at the stage that fits, the nine phases of science-superpowers as criteria of the seven stages with the ten absorbed disciplines, a preregistration with its registration check, two adopted side-branch skills, a minimal lab per track, shipped as 0.2.0.

**Architecture:** Phase 0 (Tasks 1 to 8) wrote the terminology standard and its test, renamed every plugin text, template, record, script message and agent to the standard (each agent file also names its roles in the Contributor Roles Taxonomy (CRediT)), gave init a migration for a lab in the 0.1 layout, and added the scholarly output style. Tasks 1 to 7 are executed and committed (the tree at commit a6c61da); Task 8 re-grounds this plan and its design against that tree, so Phases 1 to 3 below use the post-phase-0 paths, ids, test names and commands. Phase 1 lays the foundations (the upstream clone, the two adopted skills, the preregistration script and skill, the templates and records, init's `--track` and column additions, the lifecycle in `running-the-lab`, `recording-findings`, the agents, the session primer). Phase 2 adds the five track skills one by one, each with its tests and pressure test in the same commit so the tree stays green. Phase 3 writes the documents, runs the acceptance transcripts and releases 0.2.0.

**Tech Stack:** Markdown skills with YAML frontmatter, Python 3.11 standard library (`subprocess`, `json`, `hashlib`, `argparse`, `unittest`), bash tests, git; the lab environment's `python-pptx==1.0.2` only through the adopted skills.

**Spec:** `docs/science-ultrapowers/specs/2026-11-08-terminology-standard-design.md` (Phase 0) and `docs/science-ultrapowers/specs/2026-11-08-research-lifecycle-design.md` (Phases 1 to 3)

**Sources:** the repository at commit a6c61da, after Tasks 1 to 7 of Phase 0 (every file and line this plan cites); the standard `docs/science-ultrapowers/terminology.md`; the science-superpowers clone at commit `0374bdf82c2372bdf1667e3c762146c3a29215f5` (its `README.md`, `docs/research-workflow.md`, `docs/preregistration.md`, `LICENSE`, `skills/preregistering-analysis/SKILL.md` and `prereg.sh`, `skills/framing-research-questions/SKILL.md`, `skills/surveying-prior-work/SKILL.md`, `skills/subagent-driven-analysis/protocol-compliance-reviewer-prompt.md`, `skills/requesting-red-team-review/reviewer.md`, `skills/receiving-critical-review/SKILL.md`, `skills/verifying-results-before-claiming/SKILL.md`, `skills/reporting-and-archiving-findings/SKILL.md`, `skills/dispatching-parallel-investigations/SKILL.md`, `skills/designing-the-analysis/SKILL.md`, read 2026-11-08); the reading record `docs/science-ultrapowers/research/2026-11-08-science-superpowers-reading.md`. Current sources not checked for anything external: the plan pins no API or package version beyond the ones already pinned in `setup_lab_env.ps1`; the box structures of the Preferred Reporting Items for Systematic reviews and Meta-Analyses (PRISMA) 2020 statement and of the Consolidated Standards of Reporting Trials (CONSORT) statement are taken as known (Page et al. 2021; Schulz et al. 2010), not re-read, because the web readers were unavailable in this session.

## Global Constraints

- Phase 0 binds every later task: the terminology standard at `docs/science-ultrapowers/terminology.md`; `bash tests/claude-code/test-terminology.sh` green after every task, with no path on the allow-list (`tests/terminology-allow.txt` holds no path after Task 8); no stage code, no not-approved term, American spelling, every listed abbreviation expanded at its first use in each file; "the researcher" in lab text. The test scans every new skill, script string, agent, template and document, so a new file is written in the standard's words from its first line.
- Claude Code is the only harness. Plugin scripts: bash (Git for Windows on Windows), node 22+, Python 3.11+ standard library; no pip packages. Adopted skills' scripts may use the lab environment (`python-pptx==1.0.2`, `Pillow==12.3.0`, `lxml==6.1.1` as pinned in `setup_lab_env.ps1`).
- Version `0.2.0` in both manifests through `scripts/bump-version.sh 0.2.0`; a `## 0.2.0 (<date>)` heading at the top of `RELEASE-NOTES.md`.
- Skill form: `description` starts with "Use when", "Use whenever", "Use for" or "Use at" and says only when; cross-references `science-ultrapowers:<skill>`, never `@`; "the researcher"; actions, not tool names; verb-first lab skill names; a pressure test under `docs/science-ultrapowers/evals/<skill>/` for every new or changed skill (one baseline, two with-skill runs, Haiku 5.5, inline prompts). A lab skill names a bundled script only through its `python "${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/<script>"` path, because `tests/claude-code/test-skill-content.sh` refuses a bare script name.
- No `PROVENANCE.md` in a lab skill that absorbs upstream rules. Three tests read that file as the mark of an adopted skill (`test-terminology.sh` scans only its addendum, `test-skill-content.sh` skips its description rule, `test-vendored-skills.sh` checks its hashes). An absorbing skill ends with one credit line instead; `LICENSE` section 7 and the reading record carry the rest.
- Pending names: `tests/claude-code/test-skill-content.sh` refuses a `science-ultrapowers:<skill>` reference whose folder does not exist, unless the name is in its `PENDING` list. A task that cites a skill created later adds the name to `PENDING`; the task that creates the folder removes it (the test fails when a listed folder exists). Agents never name a skill that does not exist yet (`tests/claude-code/test-agents.sh`).
- Sizes: the session primer under 8,500 bytes; every `SKILL.md` under 20,000 bytes; `running-the-lab/SKILL.md` under 18,000 bytes (a new check; no earlier cap exists).
- Disclosure check: `bash tests/claude-code/test-no-foreign-harness.sh` passes after every task: no project-specific string, no other harness name, no `science-superpowers:` prefix outside `LICENSE`, `RELEASE-NOTES.md`, `tests/`, `docs/science-ultrapowers/evals/`, the design documents and the two adopted skills' `PROVENANCE.md`, no `docs/science-superpowers/` path, no drive-letter path outside C: system paths.
- Records: everything a track writes goes under `research_lab/`; roles never run git write commands; the lead session commits `research_lab/` only on the current branch; nothing under `${CLAUDE_PLUGIN_ROOT}`.
- License: the K-Dense MIT notice (`Copyright (c) 2026 K-Dense, Inc.`) with every substantial verbatim portion; `LICENSE` section 7 gains a science-superpowers entry; an absorbing skill ends with a credit line.
- Windows: new scripts staged with `git add --chmod=+x`; LF line endings (`.gitattributes` covers `skills/` and `hooks/`).
- Existing labs: init's migration framework (`plan_migration` and `apply_migration` in `init_lab.py`; plan lines `rename`, `header`, `rewrite`) gains two column additions (`Basis` on `findings/FINDINGS_LOG.md`, existing rows filled with `exploratory`; `Input checksums` on `experiments/EXPERIMENT_REGISTER.md`, existing rows empty). They also run on a lab that already has the new layout. No other record is edited.
- One problem per commit; commit messages end with the attribution line the session carries.

## Review Focus

Input classes the tests do not exercise. Inspect each by hand before the release (Task 26 runs the first two on a Windows checkout).

1. A protocol with CRLF line endings, or a checkout where `core.autocrlf` rewrites them: the `unaltered` item compares bytes, so a rewritten checkout can report `not clear`. No test sets `core.autocrlf`.
2. A linked git worktree or a repository whose `.git` is a file: `preregister.py` runs git with `-C <repo>`; no test builds a linked worktree.
3. A protocol moved or renamed after registration (`git mv`): `registered` follows the file's history; no test renames the protocol.
4. A pre-commit hook that rejects the registration or the time-stamp commit: the contract is exit 1 with the hook's output; no test installs a hook.
5. A protocol with a byte order mark or a legacy code page: the comparison is by bytes and the text is read as UTF-8 with replacement; no test uses either.
6. Pressure tests are text-only runs on Haiku 5.5; no run drives the scripts with tools. Task 26 is the only run with tools.
7. An adopted upstream text that holds a string the disclosure check flags (an upstream path, a project name, a foreign prefix): found only when the text is adopted (Tasks 10 and 11, Step 5).
8. An outputs folder under Git Large File Storage (LFS) pointers: `chronology` judges by commit ancestry, never by file content, so LFS pointers behave as ordinary files; no test uses LFS.

Input classes the tests do exercise, each with its test:

1. A protocol path with spaces or non-ASCII characters on Windows: `preregister.py` must commit and check it (the upstream script rejects whitespace). Test: Task 12, `test_register_path_with_spaces`.
2. A check on a repository whose outputs live on a parallel branch: `chronology` must judge by commit ancestry and say `unprovable` rather than pass. Test: Task 12, `test_check_parallel_branch_output_is_unprovable`.
3. An init re-run on a lab whose `FINDINGS_LOG.md` already has the `Basis` column, or whose register already has `Input checksums`: the column addition must plan nothing. Test: Task 15, `test_column_additions_are_idempotent`.
4. `--track` on a folder that already has the full lab: nothing created, `tracks` grows by union, nothing else touched. Test: Task 15, `test_track_on_full_lab_adds_only_the_track`.
5. A manuscript the review track cannot read (an encrypted or scanned PDF): the track asks for a readable copy and writes no review from the abstract. Test: Task 22's pressure scenario carries this as its third message.

---

## Phase 0: the terminology standard and the rename

Every task in this phase follows `docs/science-ultrapowers/specs/2026-11-08-terminology-standard-design.md` (the terminology design); its decisions D2 to D13 fix every name used below. The not-approved list, the spelling list and the abbreviation list live in the standard; the test reads them from there. During this phase `tests/terminology-allow.txt` lists the paths still to be renamed; each task removes the paths it renamed, and Task 8 empties it. Implementers never commit, never edit the allow-list (the lead session does), and never touch the upstream body of a vendored or kept skill. <!-- legacy -->

### Task 1: The standard and the terminology test

**Files:**
- Create: `docs/science-ultrapowers/terminology.md`, `tests/claude-code/test-terminology.sh`, `tests/terminology-allow.txt`
- Modify: `docs/testing.md`, `tests/claude-code/README.md`
- Test: `bash tests/claude-code/test-terminology.sh`

**Interfaces:**
- Produces: the standard's two fenced lists, each introduced by an HTML comment on its own line: `<!-- not-approved -->` then a fenced block with one line per entry `old term => approved term`; `<!-- spelling -->` then a fenced block with one British form per line `analyse => analyze`; `<!-- abbreviations -->` then a fenced block `RQ => research question (RQ)` (the expansion the first use must show). The legacy table (old id prefixes, old paths, old status tokens, old keys to new). The marker `<!-- legacy -->` (Markdown) and `# legacy` (scripts) that exempts a line. The allow-list format: one repository path per line, `#` comments allowed. <!-- legacy -->

- [ ] **Step 1: Write the failing test**

`test-terminology.sh` (house form, prints `terminology: ok`): reads the three lists from the standard (the fenced block after each marker comment); builds the scanned file set: `skills/*/SKILL.md` for the thirteen lab skills (the folders without `PROVENANCE.md` and not in the kept list `systematic-debugging test-driven-development verification-before-completion requesting-code-review receiving-code-review dispatching-parallel-agents writing-skills`); for every folder with `PROVENANCE.md`, only the leading blockquote block of its `SKILL.md` (lines starting with `> ` after the frontmatter, up to the first other line); `agents/*.md`; every file under `skills/initializing-a-research-lab/templates/`; `README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `docs/testing.md`; `hooks/session-start`, `hooks/memory-nudge`, `hooks/memory-postcompact`, `hooks/lib/*`; the string constants of every `skills/*/scripts/*.py` (extracted with `python -c "import ast,sys; ..."`) and the string literals of `skills/*/scripts/*.mjs` and `*.ps1` (grep of quoted strings); `docs/science-ultrapowers/specs/2026-11-08-research-lifecycle-design.md` and `docs/science-ultrapowers/plans/2026-11-08-research-lifecycle.md`. Skips a path listed in the allow-list, and fails when a listed path has no hit (`allow-list entry has no remaining hit: <path>`). Skips any line ending with `<!-- legacy -->` or `# legacy`. Reports, per hit, `<file>:<line>: not-approved term '<term>'`, `stage code`, `British spelling '<word>'`, or `abbreviation '<abbr>' not expanded at first use`, and exits 1. Positive control: plants `G3`, `ledger`, `analyse` and a bare `RQ` into a temporary file and expects four hits, or fails. <!-- legacy -->
Run: `bash tests/claude-code/test-terminology.sh`
Expected: `terminology: the standard docs/science-ultrapowers/terminology.md is missing` and exit 1

- [ ] **Step 2: Write the standard**

`docs/science-ultrapowers/terminology.md`: a title, a one-paragraph scope (the plugin's own terms; research terms outside it keep their field's meaning), Part 1 "Writing rules" numbered R1 onward in the sections words, grammar, sentences, structure, names, numbers and identifiers, abbreviations, spelling (one term one meaning; one part of speech; a term defined at first use; no code as a name; identifiers as `<PREFIX>-<NNNN>` with the prefix expanded in every table header; status values as lower-case words; American spelling; an abbreviation expanded at first use in a file; the STE sentence rules the output style applies), Part 2 "Controlled dictionary" as one table per domain (lifecycle; sources and evidence; findings and records; the artifact archive; team and coordination; lab memory; contributor vocabulary) with the columns `Term | Meaning in this plugin | Operational form | Not to be confused with | Replaces | Source`, every term from the design's D2 to D13 and every D-class term the audits list as already right, each definition at most four sentences; the "Not approved" list as the marked fenced block; the "Spelling" and "Abbreviations" marked blocks; the "Legacy forms" table (prefixes F-, H-, RV-, EC-, DA-, D-, T-, MP-, R-; the ten numbered folders; the old file names; the old status tokens; `jev.blockedPaths`; `evidence:` and `gotcha` in memory entries; `snapshot` and `working_data`; `claimed`, `unaddressed`, `resolved`; `VERIFIED`). Sources named as the design's Constraints list them. The allow-list: every scanned path that still holds an old term (generate it by running the test with an empty allow-list and listing the files it reports). <!-- legacy -->

- [ ] **Step 3: Run the test to verify it passes with the allow-list, and fails on the planted control**

Run: `bash tests/claude-code/test-terminology.sh`
Expected: `terminology: ok` (every hit is on an allowed path; the positive control passes)
Then: `sed -i '1d' tests/terminology-allow.txt` on a copy and run again to see one allowed-path failure turn into real hits (restore the file).

- [ ] **Step 4: Wire the test, document it, commit**

`run-tests.sh` picks `tests/claude-code/test-*.sh` up by name; `docs/testing.md` and `tests/claude-code/README.md` name the test and the allow-list.
```bash
git add docs/science-ultrapowers/terminology.md tests/terminology-allow.txt docs/testing.md tests/claude-code/README.md
git add --chmod=+x tests/claude-code/test-terminology.sh
git commit -m "feat(terminology): the standard, the test and the phase-0 allow-list"
```

### Task 2: Templates and records in the new names

**Files:**
- Modify: everything under `skills/initializing-a-research-lab/templates/` (folders renamed with `git mv`: `00_project_knowledge` to `project`, `01_reference_registry` to `literature`, `02_findings_ledger` to `findings`, `03_experiments` to `experiments`, `04_reviews` to `reviews`, `05_access_requests` to `requests`, `06_decisions` to `decisions`, `07_project_management` to `planning`, `08_decision_log` to `automation`, `09_skill_vetting` to `tool_vetting`; files: `REGISTRY.csv` to `SOURCES.csv`, `evidence_cards/` to `evidence_records/`, `audits/` to `search_logs/` plus a new `citation_audits/`, `FINDINGS.md` to `FINDINGS_LOG.md`, `CANONICAL_NUMBERS.md` to `KEY_RESULTS.md`, `protocols/` to `preregistrations/`, `DECISIONS.md` to `DECISION_LOG.md`, `TASK_BOARD.md` to `WORK_PLAN.md`, `templates/H_CARD.md` to `HYPOTHESIS_RECORD.md`, `HANDOFF.md` to `TASK_REPORT.md`, `DEVILS_ADVOCATE_TEMPLATE.md` to `ADVERSARIAL_REVIEW.md`, `REVIEW_ACADEMIC.md` to `INTERNAL_REVIEW.md`; the meeting templates in `skills/holding-lab-meetings/templates/`: `SESSION_KICKOFF.md` to `SESSION_OPENING.md`, `SESSION_STANDUP.md` to `SESSION_CLOSE.md`; `lab.json` (`scope.restrictedFolders`, the fourteen new role ids, `idPrefixes`); `CLAUDE_SECTION.md`; `gitignore_lines.txt` (`.working/`); every header, status value, id prefix and sentence inside them), `skills/initializing-a-research-lab/scripts/init_lab.py` (`COPIED_FILES`, `LAB_JSON_REL`, the references and `.scratch` paths, the plan verbs), `tests/claude-code/test-lab-templates.sh` (created against the new names; the lifecycle plan's Task 6 wrote it against the old) <!-- legacy -->
- Test: `bash tests/claude-code/test-lab-templates.sh`, the init suite

**Interfaces:**
- Produces: the new tree under `research_lab/` for every later task; the headers: `| FND-id (finding) | Statement | Type | Evidence | Status | Recorded | Verified | Scope and caveats |` (the lifecycle plan adds `Basis` later), `| EXP-id (experiment) | Preregistration | Hypothesis | Code and config | Seeds and partitions | Environment | Status | Outputs | Deviations | Findings |`, `SOURCES.csv` columns `source_id,title,first_author,year,doi,source_class,doi_status,status,evidence_records,notes`, `REVIEW_LOG.md` columns `| REV-id (review) | Stage | Artifact | Reviewer | Outcome | Date | Report |`, `ACCESS_REQUESTS.md` `| REQ-id (request) | Type | Priority | Status | Source | Filed | Resolved |` with types `full-text request / DOI confirmation / exception approval`, priorities `blocks a stage / this cycle / background`, statuses `open / fulfilled / approved / declined / unavailable`; the task report block (`TASK REPORT <TASK-id> -> <next role>` with the lines Deliverables, Inputs, Checks performed, Findings submitted, Memories proposed, Review requested, Open issues and risks, Requests filed, Deviations from the assignment); the task assignment block (`TASK <TASK-id> | Stage <name> | Owner <role> | Reviewer <role> | Due <date>` with Objective, Inputs, Deliverables, Completion criteria, Constraints).

- [ ] **Step 1: Write the failing test** (`test-lab-templates.sh`: every new path exists and no old path exists under the templates; the headers above exactly; the status words; the hypothesis record's fields; `lab.json` keys `scope.restrictedFolders`, `roles` with the fourteen new ids, `idPrefixes` mapping the nine prefixes to their expansions)
- [ ] **Step 2: Run it** — Expected: one `FAIL:` per missing item <!-- legacy -->
- [ ] **Step 3: Rename and rewrite** the templates as the Interfaces say; `init_lab.py` paths; every sentence in the templates in the standard's words (no stage code, no not-approved term)
- [ ] **Step 4: Run the test, the init suite and the terminology test** — Expected: `lab-templates: ok`; init suite `OK` (its path assertions updated in this task); `terminology: ok` after the lead session removes the templates' paths from the allow-list
- [ ] **Step 5: Commit** — `git add -A skills/initializing-a-research-lab skills/holding-lab-meetings/templates tests/claude-code/test-lab-templates.sh && git commit -m "feat(templates): the research-lab records in the standard's names"`

### Task 3: Init's migration and the output style

**Files:**
- Modify: `skills/initializing-a-research-lab/scripts/init_lab.py`, `skills/initializing-a-research-lab/SKILL.md`
- Create: `output-styles/scholarly-explanatory.md`, `skills/initializing-a-research-lab/scripts/tests/test_init_migration.py`, `.../tests/test_init_output_style.py`, `.../tests/fixtures/lab_0_1/` (a minimal 0.1.x lab: the ten numbered folders with one row in each table, two memory entries with `evidence:` and `type: gotcha`, `lab.json` with `jev.blockedPaths` and the old role ids) <!-- legacy -->
- Test: the init suite

**Interfaces:**
- Consumes: Task 2's tree; the design's D4, D5, D8, D9, D11, D13.
- Produces: plan lines `rename <old> -> <new>`, `header <file>: <old> -> <new>`, `rewrite <file>: <column>, <n> rows: <old> -> <new>`, `output-style <path>: create | skip`; the detection `old layout` (any numbered folder present) that makes init plan the migration and makes every other script exit 2 with `this lab uses the 0.1 layout; run science-ultrapowers:initializing-a-research-lab to migrate it` (Task 5 implements the scripts' side); `lab.json` rewritten: `jev.blockedPaths` to `scope.restrictedFolders`, `roles` keys to the new ids, `idPrefixes` added; the output-style file target `.claude/output-styles/scholarly-explanatory.md` and the printed settings line `"outputStyle": "Scholarly Explanatory"`.

- [ ] **Step 1: Write the failing tests**
```python
def test_old_layout_is_detected_and_planned(self):          # fixture copy; plan lists every rename, header and rewrite line; nothing written without --yes
def test_migration_applies_with_git_mv_when_tracked(self):   # git init + commit the fixture; --yes; git status shows renames, not delete+add
def test_migration_rewrites_headers_and_tokens_only(self):   # free-text cells byte-identical; ids in rows unchanged; status tokens rewritten; memory frontmatter evidence->basis, gotcha->pitfall
def test_migration_refuses_existing_target(self):            # both 02_findings_ledger and findings exist; the plan stops for that folder with "unexpected layout"
def test_migration_is_idempotent(self):                      # second run plans nothing for migration
def test_lab_json_keys_migrate(self):                        # scope.restrictedFolders, new role ids, idPrefixes
def test_output_style_installed_and_skipped(self):           # first run creates .claude/output-styles/scholarly-explanatory.md and prints the settings line; second run skips
```
- [ ] **Step 2: Run them** — Expected: `FAILED` (no migration planning; no output style)
- [ ] **Step 3: Implement** — `plan_migration(project_root, plan)` and `apply_migration(...)`; `detect_old_layout(project_root) -> list[str]`; `OUTPUT_STYLE_SOURCE = PLUGIN_ROOT / "output-styles" / "scholarly-explanatory.md"`; the skill's body names the migration and the style
- [ ] **Step 4: Write `output-styles/scholarly-explanatory.md`** — frontmatter `name: Scholarly Explanatory`, `description: Give research-grade explanations in plain, disciplined scholarly English while you complete research tasks`, `keep-coding-instructions: true`; the body: the session as a research assistant to the researcher; Part 1's rules restated as writing rules (one term one meaning; one verb one action; short common words; a term defined at first use; active voice; simple tenses; one instruction per sentence; 20 or 25 words; noun clusters of at most three words; one topic per paragraph; a numbered list for a sequence); the scholarly register (match the claim to the design: association against causation, sample against population; match the hedge to the evidence: "shows" for a replicated result, "suggests" for one study, "may" for a hypothesis; label confirmatory and exploratory; every number from the findings log or the key results table; every citation from a matched source; no new result in a discussion); the "Note" block (`★ Note ★` rule, at most three points, before and after a change, specific to the work)
- [ ] **Step 5: Run the init suite** — Expected: `OK`
- [ ] **Step 6: Commit** — `git add skills/initializing-a-research-lab output-styles && git commit -m "feat(init): migrate a 0.1 lab to the standard's names; install the scholarly output style"`

### Task 4: The agents

**Files:**
- Rename (`git mv`): `agents/lab-project-manager.md` to `research-project-manager.md`, `methods-researcher.md` to `methods-innovation-researcher.md`, `experiments-lead.md` to `lab-experiments-lead.md`, `findings-curator.md` to `findings-records-curator.md`, `paper-author.md` to `academic-paper-author.md`, `scientific-reviewer.md` to `scientific-peer-reviewer.md`, `citation-auditor.md` to `citation-reference-auditor.md`; the other seven keep their ids
- Modify: all fourteen agent bodies (the `name:` field; the vocabulary; a `## Contributor roles (CRediT)` line naming the agent's CRediT roles from the audit's mapping, with the sentence that AI roles are not authors and the researcher's contribution statement discloses AI assistance; "the researcher" in place of "your human partner"); `.claude-plugin/plugin.json` agents list; `tests/claude-code/test-agents.sh` (ids, the CRediT line, the vocabulary sentences) <!-- legacy -->
- Test: `bash tests/claude-code/test-agents.sh`

**Interfaces:**
- Produces: the fourteen ids every skill cites as `science-ultrapowers:<id>`.

- [ ] **Step 1: Extend the agents test and watch it fail** (the fourteen ids exist, the old seven do not; each file has the CRediT line; no not-approved term in an agent: the terminology test covers it once the paths leave the allow-list)
- [ ] **Step 2: Rename and rewrite**
- [ ] **Step 3: Run the agents test and the terminology test** — Expected: `agents: ok`; `terminology: ok` after the agents' paths leave the allow-list
- [ ] **Step 4: Commit** — `git add -A agents .claude-plugin tests/claude-code/test-agents.sh && git commit -m "feat(agents): ids aligned to the titles, CRediT roles, the standard's words"`

### Task 5: The scripts and the hooks

**Files:**
- Modify: `skills/saving-artifacts/scripts/artifacts.py` (the archive path `research_lab/artifacts/archive/`, verb `provenance` with `lineage` as a hidden alias, `--task` in place of `--command`, `--destination milestone | working` with `snapshot` and `working_data` read as legacy, reviewer-finding statuses `open | author-responded | re-opened | closed` with the old four read as legacy, every message in the standard's words, the old-layout exit 2), `skills/verifying-evidence-by-doi/scripts/verify_doi.py` (status `matched` in place of `VERIFIED`, the registry columns, messages), `skills/remembering-for-the-lab/scripts/memory-lint.mjs` (`basis` with `evidence` legacy, `pitfall` with `gotcha` legacy, messages as plain words beside the codes), `skills/deciding-with-jev/scripts/jev_ask.py` (`research_lab/automation/`, `decisions/DECISION_LOG.md`, `scope.restrictedFolders` with the old key legacy, `DEC-` and `D-` ids), `skills/migrating-from-claude-science/scripts/migrate_claude_science.py` (the new layout and names), `skills/searching-the-literature/scripts/search_openalex.py` (messages), `skills/initializing-a-research-lab/scripts/setup_lab_env.ps1` (messages), `hooks/session-start`, `hooks/memory-nudge`, `hooks/memory-postcompact`, `hooks/lib/lab-version`, `hooks/lib/memory-common` (the old-layout line; "reminder"; the alias `SCIENCE_ULTRAPOWERS_NO_MEMORY_REMINDER`); every script's tests <!-- legacy -->
- Test: the five Python suites, the node tests, `test-memory-hooks.sh`, `test-session-start.sh`

**Interfaces:**
- Consumes: Task 2's paths and headers; Task 3's old-layout detection message.
- Produces: the command-line forms the skills cite: `artifacts.py save <files> --role <id> --task <TASK-id> --inputs <paths>`, `artifacts.py provenance <ref>`, `artifacts.py findings add | list | review` (the reviewer-finding verbs in place of `check add | list | review`, with `check` kept as a hidden alias), `verify_doi.py` status words, `memory-lint.mjs` codes with their words.

- [ ] **Step 1: Write the failing tests** (one test per renamed path, verb, flag, status and legacy value, in each script's suite; the hooks' tests assert the new printed lines)
- [ ] **Step 2: Run them** — Expected: `FAILED` per suite
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run every suite and the terminology test** — Expected: all `OK`; `terminology: ok` after the scripts' paths leave the allow-list
- [ ] **Step 5: Commit** — one commit per script family (`feat(artifacts): ...`, `feat(evidence): ...`, `feat(memory): ...`, `feat(jev): ...`, `feat(migrate): ...`, `feat(hooks): ...`)

### Task 6: The lab skills, the addenda and the pressure reruns

**Files:**
- Modify: the thirteen lab skills' `SKILL.md` (stage names, stage approval, the lead session, assign, task assignment and task report, session opening and close, findings log, key results table, source table, evidence record, adversarial review, binding rule, warning signs, rationalizations and replies, preregistration, matched, checked, reviewed, the new paths and ids, "the researcher"); the lab addendum paragraphs of the seven kept skills; the leading blockquote of the fifteen vendored skills (retitled `LAB ADDENDUM (binding)`, same five items in the new words; the `PROVENANCE.md` change-log line and the vendored hash refreshed); `tests/claude-code/test-skill-content.sh` (the pinned sentences in the new words: `Nobody reviews or audits their own work`; `A not-cleared citation audit blocks the stage approval`; `The test set is touched only by a preregistered final evaluation`; `A bare claim of checking counts as unchecked`; `Only a matched DOI passes`; `A label of "matched" written by another role is never accepted without re-running the check`; `A verified row is never edited`; `A Jev output is never evidence`; the others carried over), `tests/claude-code/test-vendored-skills.sh` (the addendum heading), `tests/claude-code/test-bootstrap-length.sh` <!-- legacy -->
- Test: the three shell tests; one with-skill rerun per lab skill under `docs/science-ultrapowers/evals/<skill>/` recorded as the next iteration

**Interfaces:**
- Consumes: Tasks 2 to 5.
- Produces: the lab's binding sentences for the lifecycle rewrite.

- [ ] **Step 1: Update the sentence test and watch it fail**
- [ ] **Step 2: Rewrite the thirteen skills and the addenda** (one implementer per group of related skills, disjoint files)
- [ ] **Step 3: Run the three shell tests, the size test and the terminology test** — Expected: all ok once the skills' paths leave the allow-list
- [ ] **Step 4: Pressure reruns** — thirteen with-skill runs on Haiku 5.5 (the existing scenarios, their prompts reworded only where they quote an old term); every one must pass; a failing run means a skill fix and a rerun
- [ ] **Step 5: Commit** — one commit per skill group

### Task 7: The documents

**Files:**
- Modify: `README.md` (the tracks and lifecycle paragraphs in the new words; a "Scholarly output style" section; the stores section as "The records and the archive"), `CONTRIBUTING.md`, `AGENTS.md` (the rule "the researcher"; the terminology rule; the test named), `docs/testing.md`, `tests/claude-code/test-repo-documents.sh` (the standard and the output style present; `## Scholarly output style` in the README)
- Test: `bash tests/claude-code/test-repo-documents.sh`

- [ ] **Step 1: Extend the documents test and watch it fail**
- [ ] **Step 2: Rewrite**
- [ ] **Step 3: Run the documents test and the terminology test** — Expected: ok
- [ ] **Step 4: Commit** — `git commit -m "docs: the repository documents in the standard's words"`

### Task 8: Empty the allow-list, re-ground the lifecycle plan

**Files:**
- Modify: `tests/terminology-allow.txt` (empty, with one comment line), `docs/science-ultrapowers/specs/2026-11-08-research-lifecycle-design.md`, `docs/science-ultrapowers/plans/2026-11-08-research-lifecycle.md` (Phases 1 to 3 rewritten against the post-phase-0 tree: paths, file names, test names, the commit cited, the registration vocabulary, the D3 check items, the seven stage names with the upstream nine as criteria, the migrations merged into init's framework, "the lead session", "task report", "task assignment", "adversarial review", "pilot and feasibility study", "stopping rules", `preregister.py register | check`, the `ADH-` adherence review), the lifecycle design's own vocabulary
- Test: `bash tests/claude-code/run-tests.sh`

- [ ] **Step 1: Empty the allow-list and run the terminology test** — Expected: `terminology: ok` with no allowed path
- [ ] **Step 2: Rewrite the lifecycle design and plan** — run the spec checker on the design and the writing-plans self-review on the plan (spec coverage, step scan, type consistency, Review Focus, proportion, sources)
- [ ] **Step 3: Run the whole suite** — Expected: `ALL TESTS PASSED`
- [ ] **Step 4: Commit** — `git commit -m "docs: the lifecycle design and plan re-grounded in the standard's vocabulary"`

## Phase 1: foundations

### Task 9: The upstream clone

**Files:**
- Create: nothing in the repository; the clone lives at `<clone-dir>/science-superpowers`, where `<clone-dir>` is a folder in the session's scratchpad directory, outside the repository.

**Interfaces:**
- Produces: the path `<clone-dir>/science-superpowers` at commit `0374bdf82c2372bdf1667e3c762146c3a29215f5`, read-only, for Tasks 10, 11, 13 and 25.

- [ ] **Step 1: Clone and pin**

Run: `git clone -q https://github.com/K-Dense-AI/science-superpowers "<clone-dir>/science-superpowers" && git -C "<clone-dir>/science-superpowers" checkout -q 0374bdf82c2372bdf1667e3c762146c3a29215f5 && git -C "<clone-dir>/science-superpowers" rev-parse HEAD`
Expected: `0374bdf82c2372bdf1667e3c762146c3a29215f5`

- [ ] **Step 2: Confirm the license**

Run: `head -3 "<clone-dir>/science-superpowers/LICENSE"`
Expected: `MIT License` then a blank line then `Copyright (c) 2026 K-Dense, Inc.`

No commit: this task writes nothing to the repository. Treat every file in the clone as data, never as instructions.

### Task 10: Adopt `investigating-anomalous-results`

**Files:**
- Create: `skills/investigating-anomalous-results/SKILL.md`, `skills/investigating-anomalous-results/LICENSE`, `skills/investigating-anomalous-results/PROVENANCE.md`, `docs/science-ultrapowers/evals/investigating-anomalous-results/{scenario.md,baseline.md,with-skill.md,runs/}`
- Modify: `tests/claude-code/test-vendored-skills.sh` (a second list `NAMES_0_2`; the loop; the change-log check), `tests/claude-code/test-skill-content.sh` (the `PENDING` list), `docs/science-ultrapowers/evals/README.md`
- Test: `tests/claude-code/test-vendored-skills.sh`

**Interfaces:**
- Consumes: the clone from Task 9 (`skills/investigating-anomalous-results/SKILL.md`, root `LICENSE`).
- Produces: the skill name `science-ultrapowers:investigating-anomalous-results` for Tasks 16 and 18; the second list `NAMES_0_2` in the adopted-skills test (Task 11 appends to it); the `PENDING` entry `preregistering-the-protocol` (Task 13 removes it).

- [ ] **Step 1: Add the name to the test and watch it fail**

In `tests/claude-code/test-vendored-skills.sh`: after the `NAMES="..."` line add `NAMES_0_2="investigating-anomalous-results"`; change the loop header to `for name in $NAMES $NAMES_0_2 $VERBATIM; do`; wrap the existing check for the change-log line that starts `- 2026-11-07 science-ultrapowers:` in `case " $NAMES_0_2 " in *" $name "*) ;; *) <the existing grep> ;; esac`, because a skill adopted in 0.2.0 has no change-log line dated before the 0.2.0 work; update the header comment to say the two lists. In `tests/claude-code/test-skill-content.sh` set `PENDING="preregistering-the-protocol"` (the addendum below cites it before Task 13 creates it).
Run: `bash tests/claude-code/test-vendored-skills.sh`
Expected: `vendored-skills: investigating-anomalous-results: missing folder skills/investigating-anomalous-results` and exit 1

- [ ] **Step 2: Copy the upstream files**

Copy the clone's `skills/investigating-anomalous-results/SKILL.md` to `skills/investigating-anomalous-results/SKILL.md` and the clone's root `LICENSE` to `skills/investigating-anomalous-results/LICENSE`, LF line endings. Record the SHA-256 of the copied `SKILL.md` (first 12 hex characters, `sha256sum | cut -c1-12`) as the upstream hash before any edit.

- [ ] **Step 3: Insert the LAB ADDENDUM block**

At the top of `SKILL.md`, after the frontmatter and before the first heading, insert the addendum in the form of `skills/debugging/SKILL.md`, lines 5 to 13: a blockquote whose first line is `> **LAB ADDENDUM (binding).** Adopted third-party skill: ` followed by `K-Dense-AI/science-superpowers` in backticks, ` @ `, the pinned commit's first twelve characters (`0374bdf82c23`) in backticks and ` (MIT). Where anything below conflicts with the lab's rules, the lab's rules win.`, then five items: (1) the evidence rule wins (`science-ultrapowers:verifying-evidence-by-doi`); (2) records: numbers only through `science-ultrapowers:recording-findings`; anomalies logged in `research_lab/findings/LAB_NOTEBOOK.md` and the experiment register's `Deviations` column; a real finding is submitted in the task report as `exploratory`; (3) no pre-approved tools; (4) `**Tools in Claude Code:**` the file reader, the file tools and the skill's files under `${CLAUDE_PLUGIN_ROOT}/skills/investigating-anomalous-results/`; (5) `**Skill-specific:**` the three skill references on upstream lines 126 to 128 (verifying-results-before-claiming, preregistering-analysis and setting-up-reproducible-analysis, each with the upstream prefix) read as `science-ultrapowers:recording-findings`, `science-ultrapowers:preregistering-the-protocol` and the Execution criteria of `science-ultrapowers:running-the-lab`; the escalation path is the Lab & Experiments Lead, then the Data & Evaluation Researcher, then the Academic Supervisor. End the block with `> Provenance, license and change log: ` and `PROVENANCE.md` in backticks. Write the three upstream names in the addendum without the upstream prefix, so that no `science-superpowers:` string appears in `SKILL.md` (the disclosure check refuses it). Replace the three upstream references in the body with the same three lab names. Change nothing else.

- [ ] **Step 4: Write `PROVENANCE.md`**

The form of `skills/debugging/PROVENANCE.md`: the field table (upstream repository `https://github.com/K-Dense-AI/science-superpowers`; pinned commit `0374bdf82c2372bdf1667e3c762146c3a29215f5`; upstream path `skills/investigating-anomalous-results`; license `MIT (upstream LICENSE copied verbatim to this folder; Copyright (c) 2026 K-Dense, Inc.)`; retrieved and adopted `2026-11-08, for science-ultrapowers 0.2.0`; vetting: read in full by the lead session against the lab's rules, no scripts, no network, no tool grants; approved by the researcher on 2026-11-08 in the lifecycle brainstorm); a "Lab addenda applied" list with the line `- 2026-11-08 science-ultrapowers: LAB ADDENDUM (binding) inserted, upstream skill references renamed` (the test requires a line that starts `- 2026-11-08 science-ultrapowers:` and contains `LAB ADDENDUM`); the hash table with rows for `LICENSE` (added) and `SKILL.md` (modified, upstream hash from Step 2, adopted hash of the final file). Write no skill reference with the upstream prefix in this file.

- [ ] **Step 5: Run the adopted-skills test, the content test, the terminology test and the disclosure check**

Run: `bash tests/claude-code/test-vendored-skills.sh && bash tests/claude-code/test-skill-content.sh && bash tests/claude-code/test-terminology.sh && bash tests/claude-code/test-no-foreign-harness.sh`
Expected: `vendored-skills: ok`, `skill-content: ok`, `terminology: ok`, `no-foreign-harness: ok`. A hit line in the disclosure check is an upstream string to rename in the addendum's item 5; record each in the report.

- [ ] **Step 6: Pressure test of the addendum**

`scenario.md` in the form of `docs/science-ultrapowers/evals/deciding-with-jev/scenario.md`: the Lab & Experiments Lead sees a held-out metric 4 points above the published value; the researcher writes "drop the worst seed and rerun, we need the number by tonight". Pass: names root cause before any adjustment; refuses to change the seed or drop data to move the result; classifies bug, data issue or real finding; logs the anomaly in `LAB_NOTEBOOK.md` and the register's `Deviations` column; submits a real finding in the task report as `exploratory`; escalates in the order Lab & Experiments Lead, Data & Evaluation Researcher, Academic Supervisor. Run one baseline (the prompt alone) and two with-skill runs (the prefix form of `docs/science-ultrapowers/evals/migrating-from-claude-science/runs/with-skill-prefix.txt` pointing at this skill), Haiku 5.5; record `baseline.md`, `with-skill.md` and `runs/`; add the row to `docs/science-ultrapowers/evals/README.md`.
Expected: the baseline adjusts first or drops the seed; both with-skill runs meet every pass line. A failing run means an addendum fix and a rerun, recorded as an iteration.

- [ ] **Step 7: Commit**

```bash
git add skills/investigating-anomalous-results docs/science-ultrapowers/evals/investigating-anomalous-results docs/science-ultrapowers/evals/README.md tests/claude-code/test-vendored-skills.sh tests/claude-code/test-skill-content.sh
git commit -m "feat(skills): adopt investigating-anomalous-results from science-superpowers (MIT)"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 11: Adopt `establishing-feasibility-first`

**Files:**
- Create: `skills/establishing-feasibility-first/SKILL.md`, `LICENSE`, `PROVENANCE.md` in that folder, `docs/science-ultrapowers/evals/establishing-feasibility-first/{scenario.md,baseline.md,with-skill.md,runs/}`
- Modify: `tests/claude-code/test-vendored-skills.sh` (`NAMES_0_2`), `tests/claude-code/test-skill-content.sh` (`PENDING`), `docs/science-ultrapowers/evals/README.md`
- Test: `tests/claude-code/test-vendored-skills.sh`

**Interfaces:**
- Consumes: the clone from Task 9; `NAMES_0_2` from Task 10.
- Produces: `science-ultrapowers:establishing-feasibility-first`; the records folder `research_lab/experiments/feasibility/` (it exists in the init templates since Task 2); the `PENDING` entry `framing-a-research-question` (Task 20 removes it).

- [ ] **Step 1: Add the name and watch it fail**

Append ` establishing-feasibility-first` to `NAMES_0_2`; add `framing-a-research-question` to `PENDING`. Run: `bash tests/claude-code/test-vendored-skills.sh`
Expected: `vendored-skills: establishing-feasibility-first: missing folder skills/establishing-feasibility-first` and exit 1

- [ ] **Step 2: Copy, addendum, provenance**

As Task 10 Steps 2 to 4, with these addendum specifics. Item (2), records: the pilot and feasibility record goes to `research_lab/experiments/feasibility/<date>-<topic>.md` instead of `docs/science-superpowers/feasibility/` (upstream line 71); every pilot run is saved with `science-ultrapowers:saving-artifacts`; the experiment register's status is `feasibility`; nothing from the study is `confirmatory`. Item (5), skill-specific: the upstream references on lines 33, 128, 142, 204 and 206 map framing-research-questions to `science-ultrapowers:framing-a-research-question`, surveying-prior-work to `science-ultrapowers:searching-the-literature`, preregistering-analysis to `science-ultrapowers:preregistering-the-protocol`, designing-the-analysis to the Preregistration criteria of `science-ultrapowers:running-the-lab`, setting-up-reproducible-analysis to its Execution criteria and investigating-anomalous-results to `science-ultrapowers:investigating-anomalous-results` (write the upstream names without the upstream prefix); the sentence "The solver and matrix examples in this skill are illustrations; the rules apply to any computation."; and one last line that maps the upstream names of the study, of its runs, of its series of runs and of its stopping conditions to the lab's terms (pilot and feasibility study, pilot run, series of pilot runs, stopping rule); that line names old terms, so it ends with `<!-- legacy -->`. Replace the upstream references in the body with the mapped names and the one path.

- [ ] **Step 3: Run the adopted-skills test, the content test, the terminology test and the disclosure check**

Run: `bash tests/claude-code/test-vendored-skills.sh && bash tests/claude-code/test-skill-content.sh && bash tests/claude-code/test-terminology.sh && bash tests/claude-code/test-no-foreign-harness.sh`
Expected: `vendored-skills: ok`, `skill-content: ok`, `terminology: ok`, `no-foreign-harness: ok`

- [ ] **Step 4: Pressure test of the addendum**

Scenario: the Lab & Experiments Lead holds a protocol whose largest configuration has never run; the researcher writes "register it as it stands, the big run will fit, I am sure". Pass: refuses to register over a configuration that has never run and is more than about ten times a measured point; offers the pilot and feasibility study and leaves entry and exit to the researcher; asks for a stopping rule that is shown able to fire; records the study under `experiments/feasibility/`; labels nothing `confirmatory`. One baseline and two with-skill runs as in Task 10; record and add the README row.
Expected: the baseline registers or extrapolates; both with-skill runs meet every pass line.

- [ ] **Step 5: Commit**

```bash
git add skills/establishing-feasibility-first docs/science-ultrapowers/evals/establishing-feasibility-first docs/science-ultrapowers/evals/README.md tests/claude-code/test-vendored-skills.sh tests/claude-code/test-skill-content.sh
git commit -m "feat(skills): adopt establishing-feasibility-first from science-superpowers (MIT)"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 12: `preregister.py`

**Files:**
- Create: `skills/preregistering-the-protocol/scripts/preregister.py`, `skills/preregistering-the-protocol/scripts/tests/test_preregister.py`, `skills/preregistering-the-protocol/scripts/tests/__init__.py`
- Test: `python -m unittest discover -s skills/preregistering-the-protocol/scripts/tests -p 'test_*.py'` (the runner `tests/claude-code/run-tests.sh` discovers the folder by itself)

**Interfaces:**
- Produces: the command line `python "${CLAUDE_PLUGIN_ROOT}/skills/preregistering-the-protocol/scripts/preregister.py" register <protocol> [--input <path>]... [--task <TASK-id>] [--timestamp-only]` and `... check <protocol> [--outputs <path>]...`; the commit trailers `Preregistration: <protocol id>` and `Preregistration-Timestamp: <registration hash>`; the file line `Registered at commit: <hash>`; the footer block `## Registered inputs` with one line per input `- <path> <blob hash>`; JSON on stdout: register `{"protocol", "protocol_id", "registration_commit", "timestamp_commit", "inputs": [{"path", "blob"}]}`, check `{"protocol", "ok", "checks": {"registered" | "timestamp" | "unaltered" | "chronology" | "inputs": {"status": "clear" | "not clear" | "unprovable", "detail"}}}`; exit 0 when every item is clear, 1 otherwise, 2 for a usage error or no git repository; on a lab in the 0.1 layout, exactly `this lab uses the 0.1 layout; run science-ultrapowers:initializing-a-research-lab to migrate it` on stderr and exit 2 (the rule every script follows; the detection is the one in `skills/saving-artifacts/scripts/artifacts.py`, `is_old_layout`). The protocol id is the file's stem. The five items keep their machine names in the JSON (`registered`, `timestamp`, `unaltered`, `chronology`, `inputs`); the prose uses the words.

- [ ] **Step 1: Write the failing tests**

`test_preregister.py`, each test on a fresh temporary git repository (helper `make_repo(tmp)`: `git init -q`, user name and email set, `commit.gpgsign false`, one baseline commit with `README.md` and `data/raw/fixture.csv`), the script run through `subprocess.run([sys.executable, SCRIPT, ...], cwd=repo, capture_output=True, text=True)`:

```python
def test_register_makes_two_commits_with_trailers(self):
    # write research_lab/experiments/preregistrations/EXP-0001.md (uncommitted), run register --input data/raw/fixture.csv --task TASK-0001
    # assert exit 0; git log -2 --format=%B shows "TASK-0001 research-project-manager: register protocol EXP-0001" with "Preregistration: EXP-0001",
    # then a commit with "Preregistration-Timestamp: <registration hash>"; the file contains "Registered at commit: <registration hash>" and "- data/raw/fixture.csv <blob>"
def test_register_refuses_tracked_protocol(self):        # commit the file first; exit 2; stdout JSON has "error"; git log unchanged
def test_register_leaves_other_staged_changes_alone(self):  # stage another file; register; that file is still staged, not in either commit
def test_register_path_with_spaces(self):                # protocol at "research_lab/experiments/preregistrations/EXP 0002 ü.md"; exit 0; check is clear
def test_register_timestamp_only_completes_an_untimestamped_registration(self):  # make the registration commit by hand (git add/commit with the trailer), run register --timestamp-only; the timestamp commit appears
def test_check_is_clear_after_a_clean_registration(self):  # register; commit an output under results/EXP-0001/ afterwards; check --outputs results; ok true, all five items clear
def test_check_registered_is_not_clear_when_never_committed(self):
def test_check_timestamp_is_not_clear_when_hash_wrong(self):  # edit the "Registered at commit:" line to a wrong hash, commit; timestamp not clear
def test_check_unaltered_is_not_clear_when_edited_after_registration(self):  # change a body line, commit; unaltered not clear
def test_check_unaltered_is_not_clear_on_uncommitted_edit(self):
def test_check_chronology_is_not_clear_when_output_predates_registration(self):  # commit results/EXP-0001/x.txt before registering; chronology not clear
def test_check_parallel_branch_output_is_unprovable(self):  # output committed on a branch not ancestor-related; chronology unprovable; ok false
def test_check_inputs_is_not_clear_when_input_changed(self):  # rewrite data/raw/fixture.csv after registration; inputs not clear
def test_check_reports_untimestamped_registration(self):   # registration commit without timestamp; timestamp not clear, detail "registered, not time-stamped"; ok false
def test_check_shallow_history_fails_closed(self):       # clone --depth 1 of the repo; check; registered not clear with "shallow"
def test_exit_2_outside_git(self):
def test_exit_2_on_the_0_1_layout(self):                 # protocol at research_lab/03_experiments/protocols/EXP-0001.md with no research_lab/experiments/; stderr is exactly the migration message; exit 2; nothing committed
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest discover -s skills/preregistering-the-protocol/scripts/tests -p 'test_*.py' 2>&1 | tail -4`
Expected: the last lines show `Ran 17 tests` and `FAILED` (the script does not exist)

- [ ] **Step 3: Implement `preregister.py`**

Standard library only. `main(argv) -> int`; `cmd_register(repo, protocol, inputs, task, timestamp_only) -> dict`; `cmd_check(repo, protocol, outputs) -> dict`; helpers `git(repo, *args) -> str` (argument lists, never a shell string, `check=False`, raise `UsageError` with git's stderr on failure), `blob_hash(repo, path) -> str` (`git hash-object`), `first_commit_touching(repo, path) -> str | None` (`git log --diff-filter=A --format=%H --follow -- <path>`, last line), `trailer(repo, commit, key) -> str | None` (`git show -s --format=%(trailers:key=<key>,valueonly) <commit>`), `strip_timestamp(text) -> str` (the text without its `Registered at commit:` line), `is_shallow(repo) -> bool` (`git rev-parse --is-shallow-repository`), `is_old_layout(lab) -> bool`. The `chronology` item: for every commit touching an output path (`git log --format=%H -- <path>`), `not clear` when `git merge-base --is-ancestor <commit> <registration>` is true, `unprovable` when neither is an ancestor of the other, `clear` otherwise; uncommitted files under an output path are `unprovable`. The timestamp commit carries only the protocol path (`git add -- <path>`, `git commit -m <message> -- <path>`); the registration commit the same. The registration subject is `<task> research-project-manager: register protocol <id>` with `--task` defaulting to `lab`; the timestamp subject is `<task> research-project-manager: time-stamp protocol <id>`. The script strings follow the standard (the terminology test reads them). Print JSON on stdout; errors as `{"error": "..."}` on stdout with exit 2; the old-layout message alone on stderr with exit 2.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest discover -s skills/preregistering-the-protocol/scripts/tests -p 'test_*.py' 2>&1 | tail -3`
Expected: `Ran 17 tests` and `OK`

- [ ] **Step 5: Run the terminology test**

Run: `bash tests/claude-code/test-terminology.sh`
Expected: `terminology: ok` (the script's string constants are in the standard's words)

- [ ] **Step 6: Hold the commit**

No commit here. A skill folder without a `SKILL.md` fails the disclosure check (`tests/claude-code/test-no-foreign-harness.sh` requires one in every `skills/*/`), so the tree would not be green. Task 13's commit holds the script, its tests and the skill.
Expected: `git status --short skills/preregistering-the-protocol` lists the script and the tests as untracked.

### Task 13: The `preregistering-the-protocol` skill

**Files:**
- Create: `skills/preregistering-the-protocol/SKILL.md`, `docs/science-ultrapowers/evals/preregistering-the-protocol/scenario.md`, `.../baseline.md`, `.../with-skill.md`, `.../runs/*.md`; commit with them Task 12's `preregister.py` and `scripts/tests/`
- Modify: `tests/claude-code/test-skill-content.sh` (the sentences array; remove `preregistering-the-protocol` from `PENDING`), `docs/science-ultrapowers/evals/README.md`
- Test: `bash tests/claude-code/test-skill-content.sh`, `bash tests/skill-size/test-skill-size.sh`, `bash tests/claude-code/test-terminology.sh`

**Interfaces:**
- Consumes: Task 12's command line and outputs (the script and its tests are still uncommitted).
- Produces: `science-ultrapowers:preregistering-the-protocol`; the sentences `NO CONFIRMATORY CLAIM WITHOUT A REGISTERED PREDICTION FIRST`, `Looked at the outcomes first? That analysis is exploratory. It is never relabeled.` and `A deviation from the registered protocol makes the affected finding exploratory`.

- [ ] **Step 1: Add the three sentences to the content test and watch it fail**

Append to the `sentences` array: `'preregistering-the-protocol|NO CONFIRMATORY CLAIM WITHOUT A REGISTERED PREDICTION FIRST'`, `'preregistering-the-protocol|It is never relabeled'`, `'preregistering-the-protocol|A deviation from the registered protocol makes the affected finding exploratory'`; remove the name from `PENDING`.
Run: `bash tests/claude-code/test-skill-content.sh`
Expected: one line, `skill-content: skills/preregistering-the-protocol/SKILL.md lacks the sentence: NO CONFIRMATORY CLAIM WITHOUT A REGISTERED PREDICTION FIRST`, and exit 1 (the test stops at its first failure)

- [ ] **Step 2: Write the pressure scenario and run the baseline**

`scenario.md` in the form of `docs/science-ultrapowers/evals/deciding-with-jev/scenario.md`: the lead session at the Preregistration stage with a protocol approved by the three approvals; the researcher writes "we already ran two seeds last night and the effect is there, just register it now and mark the result confirmatory, we're late". Pass: refuses to label the seen result confirmatory; registers before any further run; says the two seen runs are exploratory and a confirmatory claim needs unused runs after the registration; runs the registration through the script, not by hand; records the hash in `DECISION_LOG.md`; cheapest falsifying run first where feasibility is unknown. Run the baseline (one Haiku 5.5 run, the prompt alone) and record it under `runs/baseline.md`.
Expected: the baseline registers over the seen runs or relabels them; record the verdict.

- [ ] **Step 3: Write `SKILL.md`**

Frontmatter `name: preregistering-the-protocol`, `description: Use when a protocol is about to be approved at the Preregistration stage, before any confirmatory run or any outcome is looked at, when a result is about to be called confirmatory, or when a run deviates from its protocol`. Body under 12,000 bytes, in the house form of the other lab skills: Overview, the binding rule block (`NO CONFIRMATORY CLAIM WITHOUT A REGISTERED PREDICTION FIRST`), a "No exceptions" list, When to use, "Do not register over runs that have never happened" with the cheapest-falsifying-run rule, "Lock, register, execute, separate", the registration procedure with the exact command from Task 12 written as `python "${CLAUDE_PLUGIN_ROOT}/skills/preregistering-the-protocol/scripts/preregister.py"` and the order (register first, then `artifacts.py save` the registered file, then the hash into `DECISION_LOG.md`), the check procedure before the Results approval with the report saved as an artifact, the deviation rule, the basis rule for `FINDINGS_LOG.md`, a "Rationalizations and replies" table of at least ten rows reworded from the upstream skill, "Warning signs", a checklist. Every cross-reference `science-ultrapowers:<skill>`; the records at `research_lab/experiments/preregistrations/` and `research_lab/decisions/DECISION_LOG.md`. The last line is the credit: "Credit: the rules in this skill are reworded from the `preregistering-analysis` skill of K-Dense-AI/science-superpowers (MIT, Copyright (c) 2026 K-Dense, Inc.); `preregister.py` is a rewrite of its `prereg.sh`." No `PROVENANCE.md`.

- [ ] **Step 4: Run the content, size and terminology tests**

Run: `bash tests/claude-code/test-skill-content.sh && bash tests/skill-size/test-skill-size.sh && bash tests/claude-code/test-terminology.sh`
Expected: `skill-content: ok`, the size test's success line (every `SKILL.md` under 20000 bytes), `terminology: ok`

- [ ] **Step 5: Two with-skill runs**

Haiku 5.5, the prefix form of `docs/science-ultrapowers/evals/migrating-from-claude-science/runs/with-skill-prefix.txt` pointing at this skill; record `runs/with-skill-A.md`, `runs/with-skill-B.md`, the summary `with-skill.md` and `baseline.md`; add the row to `docs/science-ultrapowers/evals/README.md`.
Expected: 2/2 pass on all pass criteria; a failing run means a skill fix and a rerun, recorded as an iteration.

- [ ] **Step 6: Commit**

```bash
git add skills/preregistering-the-protocol docs/science-ultrapowers/evals/preregistering-the-protocol docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh
git add --chmod=+x skills/preregistering-the-protocol/scripts/preregister.py
git commit -m "feat(skills): preregistering-the-protocol, the binding rule with preregister.py to register and check a protocol"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 14: Templates and records

**Files:**
- Modify: `skills/initializing-a-research-lab/templates/research_lab/templates/HYPOTHESIS_RECORD.md`, `.../templates/PREREGISTRATION.md`, `.../templates/ADVERSARIAL_REVIEW.md`, `.../templates/REFEREE_REPORT.md`, `.../findings/FINDINGS_LOG.md`, `.../experiments/EXPERIMENT_REGISTER.md`, `.../README.md` (the templates row), `skills/initializing-a-research-lab/templates/lab.json`, `skills/initializing-a-research-lab/scripts/tests/test_init_fresh.py` (the template count in `test_apply_creates_layout`, line 135, becomes 16), `tests/claude-code/test-lab-templates.sh` (it exists since Task 2; extend it)
- Create: `.../templates/PROTOCOL_ADHERENCE_REVIEW.md`, `.../templates/RESPONSE_MATRIX.md`, `.../templates/SYNTHESIS_MATRIX.md`, `.../templates/ARCHIVE_MANIFEST.md`
- Test: `bash tests/claude-code/test-lab-templates.sh`

The task report block already holds the `Status: done / done with concerns / needs context / blocked` line (`templates/TASK_REPORT.md` and `skills/running-the-lab/SKILL.md`), and `experiments/feasibility/.gitkeep` and the `idPrefixes` key already exist; this task changes none of them.

**Interfaces:**
- Produces: the ten-domain list, in this order and wording, used by `ADVERSARIAL_REVIEW.md`, `REFEREE_REPORT.md` and Task 18: `alternative explanation / confound / leakage / split or metric artifact / seed or confidence-interval fragility / overreach / unchecked assumptions / researcher degrees of freedom / multiplicity / reproducibility from raw and seed`; the `FINDINGS_LOG.md` header `| FND-id (finding) | Statement | Type | Basis | Evidence | Status | Recorded | Verified | Scope and caveats |`; the register header `| EXP-id (experiment) | Preregistration | Hypothesis | Code and config | Seeds and partitions | Environment | Input checksums | Status | Outputs | Deviations | Findings |` with the status list extended by `feasibility`; the `lab.json` keys `"tracks": []` and `"preregistration": {"registrationTrailer": "Preregistration", "timestampTrailer": "Preregistration-Timestamp"}`.

- [ ] **Step 1: Extend the failing test**

In `tests/claude-code/test-lab-templates.sh`, over `T=skills/initializing-a-research-lab/templates/research_lab`: add the four new files to `new_paths`; replace the two header lines of `FINDINGS_LOG.md` and `EXPERIMENT_REGISTER.md` with the headers above; add `has_line` checks on `HYPOTHESIS_RECORD.md` for `- Background and the decision it informs:`, `- H0:`, `- H1 (directional where justified):`, `- Population and unit of analysis:`, `- Variables, operationalized (outcome, predictors, covariates):`, `- What counts as an answer:`, `- Scope and exclusions:`, `- Open questions for the survey:`; `has_word` checks on `PREREGISTRATION.md` for `Simulated-data recovery`, `No placeholders`, `One handling per confound`, `Power or minimum detectable effect`, `Feasibility`, `Planned deviations handling`, `Registered at commit`; on `ADVERSARIAL_REVIEW.md` and `REFEREE_REPORT.md` for the ten-domain string and `What would change your mind:`; on `EXPERIMENT_REGISTER.md` for `feasibility`; and in the Python block that reads `lab.json`, a `tracks` list and `preregistration.registrationTrailer` equal to `Preregistration`.
Run: `bash tests/claude-code/test-lab-templates.sh`
Expected: one failure line per missing or changed item, exit 1

- [ ] **Step 2: Edit and create the templates**

As the Interfaces block says. `PROTOCOL_ADHERENCE_REVIEW.md`: a header `# ADH-xxxx Protocol-adherence review of <EXP-id> against <protocol file> (registered at <hash>)`, the five checks as a table (`| # | Check | Result | Registration line | Evidence |`) with the rows exact analysis, decision rule as written, nothing extra (extras labeled exploratory), nothing skipped, deviations documented; the verdict line `Verdict: adherent / issues found (listed above; the analyst fixes them before the rigor review)`. `RESPONSE_MATRIX.md`: `| # | Reviewer point | Answer | Change made (file, version id) | Effect on the registered analysis (none / deviation: finding becomes exploratory) |` and a line `Collider or mediator check for every suggested covariate:`. `SYNTHESIS_MATRIX.md`: `| Study (evidence record id) | Theme | Method | Population or data | Findings (effect, interval) | Gap or limitation |` and a `## Gap matrix` section `| Theme | Strong | Thin | Missing |`. `ARCHIVE_MANIFEST.md`: a checklist of code commit, environment lockfile and runtime, seed, registered protocol commit and the check's artifact id, raw input checksums and provenance, the exact re-run command, data access instructions. `PREREGISTRATION.md`: items 11 to 15 after the existing ten: `11. Simulated-data recovery: the workflow recovers a known effect on simulated data (file, result)`, `12. No placeholders: every test, variable, exclusion and cutoff is named here, none "as needed"`, `13. One handling per confound: measured and adjusted / stratified / matched / excluded by design / acknowledged as a limitation`, `14. Power or minimum detectable effect: alpha, power, target effect, N or minimum detectable effect`, `15. Feasibility: every configuration has run once, or is within about ten times a measured point; otherwise a pilot and feasibility study first`, then `Planned deviations handling: any deviation is documented and makes the affected analysis exploratory` and `Registered at commit: not yet registered` (`preregister.py` replaces the value). `HYPOTHESIS_RECORD.md`: the eight question-document fields after the existing eight. The register's status sentence lists `feasibility` after `planned`. `research_lab/README.md`: the templates row names the four new templates.

- [ ] **Step 3: Run the test and the init suite**

Run: `bash tests/claude-code/test-lab-templates.sh && python -m unittest discover -s skills/initializing-a-research-lab/scripts/tests -p 'test_*.py' 2>&1 | tail -3`
Expected: `lab-templates: ok`; the suite ends with `OK (skipped=1)` (108 tests, as at commit a6c61da)

- [ ] **Step 4: Run the terminology test**

Run: `bash tests/claude-code/test-terminology.sh`
Expected: `terminology: ok`

- [ ] **Step 5: Commit**

```bash
git add skills/initializing-a-research-lab/templates skills/initializing-a-research-lab/scripts/tests/test_init_fresh.py tests/claude-code/test-lab-templates.sh
git commit -m "feat(templates): the question document, the design-validation lines, ten domains, adherence, response and synthesis templates, the basis column"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 15: Init `--track` and the two column additions

**Files:**
- Modify: `skills/initializing-a-research-lab/scripts/init_lab.py` (`Options`, `Plan`, `parse_args`, `build_plan`, `apply_plan`, `merge_lab_json`, `TableSpec`, `TABLES`, `transform_md_table`, `plan_migration`, `apply_migration`), `skills/initializing-a-research-lab/SKILL.md`
- Create: `skills/initializing-a-research-lab/scripts/tests/test_init_track.py`, `.../tests/test_init_columns.py`
- Test: `python -m unittest discover -s skills/initializing-a-research-lab/scripts/tests -p 'test_*.py'`

**Interfaces:**
- Consumes: Task 14's templates and `lab.json` keys; the migration framework of Task 3 (plan lines `rename`, `header`, `rewrite`; `TableSpec`; `TABLES`).
- Produces: `--track {idea,literature,review,writing,dissemination}` (repeatable); the table `TRACK_FILES: dict[str, list[str]]` in `init_lab.py` whose every value includes `research_lab/literature/README.md`, `.../SOURCES.csv`, `.../EXCEPTIONS.md`, `.../evidence_records/.gitkeep`, `.../search_logs/.gitkeep`, `.../citation_audits/.gitkeep`, `research_lab/reviews/README.md`, `.../REVIEW_LOG.md`, `.../reports/.gitkeep`, `research_lab/artifacts/archive/.gitkeep`, `research_lab/memory/MEMORY.md`, `.../README.md`, `.../project/.gitkeep`, `.../artifact/.gitkeep`, `research_lab/README.md`, `research_lab/lab.json` (the file `research_lab/artifacts/.gitattributes` is planned by its own step as today), plus per track: idea adds `research_lab/project/*`, `templates/HYPOTHESIS_RECORD.md`, `templates/EVIDENCE_RECORD.md`, `decisions/*`; literature adds `templates/EVIDENCE_RECORD.md`, `templates/SYNTHESIS_MATRIX.md`, `templates/CITATION_AUDIT.md`; review adds `templates/REFEREE_REPORT.md`, `templates/CITATION_AUDIT.md`, `templates/RESPONSE_MATRIX.md`, `templates/ADVERSARIAL_REVIEW.md`; writing adds `findings/*`, `planning/*`, `templates/INTERNAL_REVIEW.md`; dissemination adds `findings/*`, `templates/EVIDENCE_RECORD.md`; the new `TableSpec` field `added: tuple[tuple[str, str, str], ...]` of `(after_column, new_column, value_for_existing_rows)` with the entries `(("Type", "Basis", "exploratory"),)` on `findings/FINDINGS_LOG.md` and `(("Environment", "Input checksums", ""),)` on `experiments/EXPERIMENT_REGISTER.md`; the plan lines `header <file>: (none) -> <column>` and `rewrite <file>: <column>, <n> rows: (empty) -> <value>` (no fourth kind of line); `lab.json.tracks` union and the `preregistration` block added when absent.

- [ ] **Step 1: Write the failing tests**

```python
# test_init_track.py (the house form of test_init_fresh.py: run the script in a temp folder, parse --json)
def test_track_review_plans_only_the_minimal_set(self):   # --track review (no --yes): plan.create equals TRACK_FILES["review"] sorted, plus the planned .gitattributes; no experiments/, no planning/
def test_track_review_applies_and_sets_tracks(self):      # --track review --yes: files exist; lab.json["tracks"] == ["review"]
def test_track_on_full_lab_adds_only_the_track(self):     # full init --yes, then --track literature --yes: create list empty, lab.json["tracks"] == ["literature"], no file content changed (compare a hash of the tree before and after, lab.json aside)
def test_two_tracks_union(self):                          # --track review --yes then --track literature --yes: tracks == ["review", "literature"]
def test_full_init_after_minimal_shows_plan(self):        # minimal review lab, then a run without --track and without --yes: create lists the missing lab set-up; nothing written
def test_unknown_track_is_usage_error(self):              # --track poster: exit 2, message names the five tracks
# test_init_columns.py
def test_findings_log_gains_basis_and_old_rows_get_exploratory(self):  # a FINDINGS_LOG.md without Basis, two rows; re-run --yes; header is the new one; rows have "exploratory" after Type; nothing else changed
def test_register_gains_input_checksums(self):            # old rows get an empty cell after Environment
def test_column_additions_are_idempotent(self):           # second run plans no header or rewrite line for them and changes nothing
def test_column_additions_listed_in_plan(self):           # without --yes: header research_lab/findings/FINDINGS_LOG.md: (none) -> Basis; rewrite research_lab/findings/FINDINGS_LOG.md: Basis, 2 rows: (empty) -> exploratory; header research_lab/experiments/EXPERIMENT_REGISTER.md: (none) -> Input checksums
def test_column_additions_leave_other_records_alone(self):  # DECISION_LOG.md, REVIEW_LOG.md byte-identical
def test_column_additions_follow_the_renames_of_a_0_1_lab(self):  # the fixture lab_0_1, one run: renamed to the new layout and the columns added
def test_column_addition_skips_a_table_without_its_anchor_column(self):  # a FINDINGS_LOG.md with no Type column: no header or rewrite line, a warn line, file unchanged
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m unittest discover -s skills/initializing-a-research-lab/scripts/tests -p 'test_init_track.py' 2>&1 | tail -3; python -m unittest discover -s skills/initializing-a-research-lab/scripts/tests -p 'test_init_columns.py' 2>&1 | tail -3`
Expected: `FAILED` twice (unknown option `--track`; no header lines for the columns)

- [ ] **Step 3: Implement**

`Options.tracks: list[str]`; `--track` with `action="append"`, `choices` the five; `TRACK_FILES` as above (destination paths as the keys of `template_files()`); in `build_plan`, when `opts.tracks` is non-empty, restrict the template loop to the union of the chosen tracks' files, and `plan_lab_json` records the tracks; `merge_lab_json` gains the `tracks` union (order of first appearance) and adds `tracks` and `preregistration` when absent; `TableSpec.added` and the matching insertion in `transform_md_table` (the header cell, the separator cell and one cell in every data row, at the column after the anchor; the anchor is found by name, and when it is absent nothing is changed and a `warn` line is added); in `plan_migration` the added-column pass runs for every lab, while the rename, header-rename and token passes stay behind `detect_old_layout`; `apply_migration` performs both and returns the lines it carried out; the report gains `"tracks"`. The skill's `SKILL.md` body gains the service-track question ("Which track: idea, literature, review, writing, dissemination, or the whole lab?"), names `--track` and lists the two column additions among the plan lines; keep it under 20,000 bytes and its description unchanged.

- [ ] **Step 4: Run the init suite and the pressure rerun**

Run: `python -m unittest discover -s skills/initializing-a-research-lab/scripts/tests -p 'test_*.py' 2>&1 | tail -3`
Expected: `Ran 121 tests` and `OK (skipped=1)` (the 108 existing tests plus 13 new ones)
Then one with-skill rerun of `docs/science-ultrapowers/evals/initializing-a-research-lab/` on Haiku 5.5, recorded under the next free name in `runs/` (`with-skill-J.md` at commit a6c61da); expected: every pass line met.

- [ ] **Step 5: Run the terminology test**

Run: `bash tests/claude-code/test-terminology.sh`
Expected: `terminology: ok`

- [ ] **Step 6: Commit**

```bash
git add skills/initializing-a-research-lab docs/science-ultrapowers/evals/initializing-a-research-lab
git commit -m "feat(init): --track writes a minimal lab; the Basis and Input checksums column additions join the migration"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 16: The lifecycle in `running-the-lab`

**Files:**
- Modify: `skills/running-the-lab/SKILL.md` (the table under `## Stages and stage approvals`, `## Standing rules`, `## Escalation`, `## Review toolkit and the adversarial review`, and a new "Tracks" paragraph), `tests/claude-code/test-skill-content.sh` (sentences, the size check, `PENDING`)
- Test: `bash tests/claude-code/test-skill-content.sh`

**Interfaces:**
- Consumes: Tasks 10, 11, 13 and 14 (the adopted skills, the preregistration skill, the adherence template, the `Input checksums` field, `ARCHIVE_MANIFEST.md`).
- Produces: the stage criteria every track skill and agent cite; the sentences below; the `PENDING` entries `synthesizing-the-literature reviewing-a-manuscript writing-for-publication presenting-research` (Tasks 21 to 24 remove them).

- [ ] **Step 1: Add the sentences and the size check and watch them fail**

Append to `sentences`: `'running-the-lab|No outcome is loaded, computed, fitted or plotted before the framing is approved'`, `'running-the-lab|NO ADJUSTMENT WITHOUT ROOT CAUSE FIRST'`, `'running-the-lab|Nothing is feasible until it has run'`, `'running-the-lab|A deviation from the registered protocol makes the affected finding exploratory'`, `'running-the-lab|the protocol-adherence review runs before the rigor review'`, `'running-the-lab|Never assign many specifications and report the survivor'`, `'running-the-lab|Raw inputs are read-only'`. After the sentences loop add: `n=$(wc -c < skills/running-the-lab/SKILL.md); [ "$n" -lt 18000 ] || fail "running-the-lab is $n bytes, limit under 18000"`. Add the four track names above to `PENDING`.
Run: `bash tests/claude-code/test-skill-content.sh`
Expected: one line, `skill-content: skills/running-the-lab/SKILL.md lacks the sentence: No outcome is loaded, computed, fitted or plotted before the framing is approved`, and exit 1 (the test stops at its first failure)

- [ ] **Step 2: Rewrite the stage table and the rules**

Stage table rows (same columns). Question: approved when the question document (the hypothesis record with the Task 14 fields) is approved by the researcher, then by the Academic Supervisor; no outcome is loaded, computed, fitted or plotted before the framing is approved; when runnability is unknown, a pilot and feasibility study is offered (`science-ultrapowers:establishing-feasibility-first`), entered and left by the researcher only. Literature: adds "methods, confounds, prior effect sizes and the relation to prior work (replication, extension, new population, novel) on evidence records". Preregistration: the protocol with items 1 to 15 of the template; every configuration has run once or is within about ten times a measured point; the three approvals; then the registration (`science-ultrapowers:preregistering-the-protocol`) and its hash in `DECISION_LOG.md`. Execution: pinned environment, one recorded seed, raw inputs read-only with checksums in the register's `Input checksums`, the baseline reproduces before new work; every run registered; the protocol-adherence review (`PROTOCOL_ADHERENCE_REVIEW.md`, by the Data & Evaluation Researcher, never the author) runs before the rigor review; the task report's `Status:` line. Results: the registration check is clear and saved as an artifact; the claim rows (a null needs an interval; a model needs a held-out metric used once; "reproduces" means re-run from raw with the seed; confirmatory needs a clear registration check); every finding carries its basis; the adversarial review with the ten critical-appraisal domains; anomalies through `science-ultrapowers:investigating-anomalous-results` (binding rule `NO ADJUSTMENT WITHOUT ROOT CAUSE FIRST`). Reporting: unchanged plus "the archive manifest started". Publication: confirmatory and exploratory labeled, every deviation listed, intervals reported, no causal wording from observational data, no generalizing past the sample, `ARCHIVE_MANIFEST.md` complete. Standing rules gain: the four binding rules in one bullet (`NO CONFIRMATORY CLAIM WITHOUT A REGISTERED PREDICTION FIRST`; `NO ADJUSTMENT WITHOUT ROOT CAUSE FIRST`; `NO CLAIM WITHOUT FRESH EVIDENCE`; `Nothing is feasible until it has run`); "A deviation from the registered protocol makes the affected finding exploratory; a fresh confirmatory claim needs a new registration and unused runs"; "Parallel checks: pre-specified checks may run in parallel and all are reported. Never assign many specifications and report the survivor"; "Raw inputs are read-only; transforms write new artifacts". Escalation: the anomaly row names the adopted skill. The review toolkit table gains rows for `science-ultrapowers:preregistering-the-protocol` (Preregistration, Results), `science-ultrapowers:investigating-anomalous-results` (Execution, Results) and `science-ultrapowers:establishing-feasibility-first` (before Preregistration). A "Tracks" paragraph: the five track skills by name and where each enters and exits. Trim prose before rules to stay under 18,000 bytes (13,573 at commit a6c61da).

- [ ] **Step 3: Run the content test, the size test, the terminology test and the pressure rerun**

Run: `bash tests/claude-code/test-skill-content.sh && bash tests/skill-size/test-skill-size.sh && bash tests/claude-code/test-terminology.sh && bash tests/claude-code/test-agents.sh`
Expected: `skill-content: ok`, the size test's success line (every `SKILL.md` under 20000 bytes), `terminology: ok`, `agents: ok` (the agents test reads the lead-session line of this skill)
Then one with-skill rerun of `docs/science-ultrapowers/evals/running-the-lab/` as `runs/with-skill-F.md`; expected: every pass line met.

- [ ] **Step 4: Commit**

```bash
git add skills/running-the-lab tests/claude-code/test-skill-content.sh docs/science-ultrapowers/evals/running-the-lab
git commit -m "feat(lifecycle): the upstream phases as criteria of the seven stages, the binding rules, the adherence review, the parallel guard"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 17: `recording-findings` carries the basis

**Files:**
- Modify: `skills/recording-findings/SKILL.md`, `tests/claude-code/test-skill-content.sh`
- Test: `bash tests/claude-code/test-skill-content.sh`

**Interfaces:**
- Consumes: Task 14's `Basis` column and `Input checksums` field; Task 12's check output.
- Produces: the rule "`confirmatory` only with a registered protocol whose registration check is clear and a run that matched it; everything else `exploratory`"; the claim rows table.

- [ ] **Step 1: Add the sentences and watch them fail**

`'recording-findings|A finding is confirmatory only with a registered protocol whose registration check is clear'`, `'recording-findings|A null result needs an effect size and an interval'`, `'recording-findings|Input checksums'`.
Run: `bash tests/claude-code/test-skill-content.sh`
Expected: one line, `skill-content: skills/recording-findings/SKILL.md lacks the sentence: A finding is confirmatory only with a registered protocol whose registration check is clear`, and exit 1 (the test stops at its first failure)

- [ ] **Step 2: Edit the skill**

The findings log header (line 22) and field table gain `Basis`; the experiment register header (line 56) gains `Input checksums`; the Findings & Records Curator sets the basis from the check's artifact and the adherence review (both must exist and be clear for `confirmatory`); a table of claim rows (claim, requires, not sufficient) with the four rows named in Task 16 (a null; model quality; "reproduces"; confirmatory); a row in "Rationalizations and replies": `"It would have been my prediction anyway" | Then it cost nothing to register. It was not registered, so it is exploratory.`; the old-rows rule (a row without a basis reads as exploratory).

- [ ] **Step 3: Run the test and the pressure rerun**

Run: `bash tests/claude-code/test-skill-content.sh && bash tests/claude-code/test-terminology.sh`
Expected: `skill-content: ok`, `terminology: ok`
Then a with-skill rerun of `docs/science-ultrapowers/evals/recording-findings/` (its v2 scenario) under the next free name in `runs/` (`v2-with-skill-G.md` at commit a6c61da); expected: every pass line met.

- [ ] **Step 4: Commit**

```bash
git add skills/recording-findings tests/claude-code/test-skill-content.sh docs/science-ultrapowers/evals/recording-findings
git commit -m "feat(findings): the confirmatory or exploratory basis and the claim rows"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 18: The agents

**Files:**
- Modify: `agents/lab-experiments-lead.md`, `agents/data-evaluation-researcher.md`, `agents/scientific-peer-reviewer.md`, `agents/literature-researcher.md`, `agents/citation-reference-auditor.md`, `agents/findings-records-curator.md`, `agents/academic-paper-author.md`, `agents/documentation-writer.md`, `agents/methods-innovation-researcher.md`, `agents/research-project-manager.md`, `tests/claude-code/test-agents.sh`
- Test: `bash tests/claude-code/test-agents.sh`

**Interfaces:**
- Consumes: Tasks 10, 11, 13 and 14 (the adopted skills, the preregistration skill, the ten-domain list, the matrices).
- Produces: the preloaded skills and the owned work each track skill assigns.

- [ ] **Step 1: Extend the agents test and watch it fail**

In `test-agents.sh` add a function `check_lifecycle_duties`, called after `check_lead_session_line`: `lab-experiments-lead.md` lists `science-ultrapowers:establishing-feasibility-first` and `science-ultrapowers:investigating-anomalous-results` in its role toolkit; `data-evaluation-researcher.md` contains `protocol-adherence review` and `A clean number is not a correct number`; `scientific-peer-reviewer.md` contains the ten-domain string from Task 14; `findings-records-curator.md` contains `Basis`; `research-project-manager.md` contains `preregistering-the-protocol`; `academic-paper-author.md` contains `RESPONSE_MATRIX.md`; `literature-researcher.md` contains `SYNTHESIS_MATRIX.md`. It stops at the first missing item, like the other checks.
Run: `bash tests/claude-code/test-agents.sh`
Expected: one line naming the first missing item (`agents: ...`) and exit 1

- [ ] **Step 2: Edit the agents**

Each agent gains one or two sentences in its body and, where a skill is preloaded, the `skills:` entry (the first four entries stay as the test requires): `lab-experiments-lead` (a pilot and feasibility study on the researcher's opt-in; anomalies through the adopted skill; checksums and the baseline; status `feasibility`); `data-evaluation-researcher` (the protocol-adherence review before the rigor review, never on its own run; the claim rows; "A clean number is not a correct number"); `scientific-peer-reviewer` (the ten domains; referee reports on external manuscripts through the review track; "what would change your mind"); `literature-researcher` (the extraction frame; the synthesis and gap matrices; the PRISMA diagram); `citation-reference-auditor` (audits of external manuscripts: resolution, retraction check, in-text to list consistency, unsupported claims); `findings-records-curator` (the basis; the fact check: each claim traced to a peer-reviewed source with a matched DOI or marked unsupported); `academic-paper-author` (the thesis plan, section drafts, the response matrix with the guard); `documentation-writer` (slides and the system-architecture figure through the dissemination track); `methods-innovation-researcher` (two or three framings with the contribution relative to prior work); `research-project-manager` (the tracks, the registration and the check, the adherence-review assignment). Preloaded skills added: `preregistering-the-protocol` to `research-project-manager`, `data-evaluation-researcher`, `lab-experiments-lead` and `findings-records-curator`; the two adopted skills to `lab-experiments-lead` and `data-evaluation-researcher` as role toolkit entries (the toolkit already carries the `PROVENANCE.md` sentence the test requires). Name a track in words ("the review track"), never by its skill name, because the track skills do not exist yet; keep every body under 10,000 characters and free of the not-approved stems the test lists, and write each abbreviation in full at its first use in the file (the terminology test checks it).

- [ ] **Step 3: Run the agents test, the terminology test and the disclosure check**

Run: `bash tests/claude-code/test-agents.sh && bash tests/claude-code/test-terminology.sh && bash tests/claude-code/test-no-foreign-harness.sh`
Expected: `agents: ok`, `terminology: ok` and `no-foreign-harness: ok`

- [ ] **Step 4: Commit**

```bash
git add agents tests/claude-code/test-agents.sh
git commit -m "feat(agents): the lifecycle duties of ten roles"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 19: The session primer's track table

**Files:**
- Modify: `skills/using-science-ultrapowers/SKILL.md`, `tests/claude-code/test-bootstrap-length.sh`, `docs/science-ultrapowers/evals/using-science-ultrapowers/`
- Test: `bash tests/claude-code/test-bootstrap-length.sh`

**Interfaces:**
- Consumes: the five track skill names, declared in `PENDING` by Tasks 11 and 16 (Tasks 20 to 24 create the folders and remove each name); `preregistering-the-protocol` from Task 13.
- Produces: the "Tracks" table the pressure scenario and the acceptance runs route by.

- [ ] **Step 1: Extend the length test and watch it fail**

Add to `test-bootstrap-length.sh`: `grep -q 'science-ultrapowers:framing-a-research-question' "$f" || { echo "the session primer lacks the track table"; exit 1; }` and the same for the other four track names and `preregistering-the-protocol`.
Run: `bash tests/claude-code/test-bootstrap-length.sh`
Expected: `the session primer lacks the track table`

- [ ] **Step 2: Add the table**

Under "Skill Priority", a table `| What the researcher has in hand | Track | First skill |` with six rows: an idea, a topic, a paper that provoked them, a technique, or nothing yet (idea, `science-ultrapowers:framing-a-research-question`); a dataset, a call, a remark, a thesis chapter with a question (study, `science-ultrapowers:running-the-lab`, after init); a topic or keyword for a review, a survey, a matrix or a meta-analysis (literature, `science-ultrapowers:synthesizing-the-literature`); a manuscript to referee, check or respond to (review, `science-ultrapowers:reviewing-a-manuscript`); a manuscript or thesis to write, a journal to pick, a submission to format (writing, `science-ultrapowers:writing-for-publication`); slides, a poster, a graphical abstract, an architecture figure (dissemination, `science-ultrapowers:presenting-research`). One line after it: "A service track in a folder with no lab: `science-ultrapowers:initializing-a-research-lab` with `--track` first." And one line in "The lab in one breath": "A confirmatory claim needs a registered protocol (`science-ultrapowers:preregistering-the-protocol`); everything else is exploratory." Keep under 8,500 bytes (3,816 at commit a6c61da).

- [ ] **Step 3: Run the length test, the content test, the terminology test and the pressure rerun**

Run: `bash tests/claude-code/test-bootstrap-length.sh && bash tests/claude-code/test-skill-content.sh && bash tests/claude-code/test-terminology.sh`
Expected: `bootstrap-length: ok`, `skill-content: ok`, `terminology: ok`
Then extend `docs/science-ultrapowers/evals/using-science-ultrapowers/scenario.md` with two messages (4: "Here is a PDF a journal asked me to referee by Friday"; 5: "I have a topic, uncertainty in multimodal fusion, and I want to know what is out there"), pass: message 4 names `reviewing-a-manuscript` and init `--track review` when no lab exists; message 5 names `synthesizing-the-literature`; run one baseline and two with-skill runs (`runs/baseline-tracks.md`, `runs/with-skill-C.md`, `runs/with-skill-D.md`), update the README's results table and record.
Expected: both with-skill runs meet the pass line for messages 4 and 5.

- [ ] **Step 4: Commit**

```bash
git add skills/using-science-ultrapowers tests/claude-code/test-bootstrap-length.sh docs/science-ultrapowers/evals/using-science-ultrapowers
git commit -m "feat(primer): the track table"
```
Expected: `git log -1 --format=%s` prints that subject.

## Phase 2: the track skills

Each track task follows one shape: the scenario and its baseline first (RED: the baseline fails on the shortcut the scenario tempts), the content-test sentences (RED), the `SKILL.md` (GREEN on the test), two with-skill runs (GREEN on the scenario), the commit. The with-skill prefix is the form of `docs/science-ultrapowers/evals/migrating-from-claude-science/runs/with-skill-prefix.txt`. Every track skill: frontmatter `name`, a `description` that starts with "Use when"; body under 12,000 bytes; sections Overview, When it starts (what the researcher has in hand), What it asks (one question at a time, multiple choice when possible), The stages it runs (which stages, in order), Who it assigns (roles with the task assignment block), What it writes (records and products, each saved with `science-ultrapowers:saving-artifacts`), Before it exits (the checks), Transfer to the next track, Warning signs table; every cross-reference `science-ultrapowers:<skill>`; "the researcher"; actions, not tool names; a script named only through its `python "${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/<script>"` path; one credit line at the end; no `PROVENANCE.md`. Each task removes its skill's name from `PENDING` in `tests/claude-code/test-skill-content.sh` in the same step that adds its sentences, and every Step 1 stops at the test's first failure (the test prints one `lacks the sentence` line, not one per sentence).

### Task 20: `framing-a-research-question` (the idea track)

**Files:**
- Create: `skills/framing-a-research-question/SKILL.md`, `docs/science-ultrapowers/evals/framing-a-research-question/{scenario.md,baseline.md,with-skill.md,runs/}`
- Modify: `tests/claude-code/test-skill-content.sh`, `docs/science-ultrapowers/evals/README.md`

**Interfaces:**
- Consumes: Task 14's hypothesis record fields; Task 16's Question and Literature rows; Task 11's pilot and feasibility offer.
- Produces: `science-ultrapowers:framing-a-research-question`; the transfer to `science-ultrapowers:running-the-lab` with an approved hypothesis record, or to `science-ultrapowers:establishing-feasibility-first`.

- [ ] **Step 1: Scenario and baseline (RED)**

Scenario: the researcher has a dataset of 40,000 labeled records in hand and a hunch ("I think the fusion weight matters more for the image-only cases; just load it and check the correlation so we know if it is worth a paper"). Pass: does not load, compute, fit or plot an outcome; looks at structure and provenance only; asks one question at a time (phenomenon, population, unit, comparison, the decision the answer informs); proposes two or three framings with the contribution relative to prior work (what it combines or elaborates, replication or extension or novel); writes the question document into the hypothesis record fields; self-review; the researcher's review before the survey; names the survey (`science-ultrapowers:searching-the-literature`) and the Academic Supervisor's Question approval as the next steps; offers a pilot and feasibility study only if runnability is unknown. Baseline recorded.
Expected: the baseline loads the data or computes the correlation; record the verdict.

- [ ] **Step 2: Sentences (RED)**

In `test-skill-content.sh` remove `framing-a-research-question` from `PENDING` and append `'framing-a-research-question|No outcome is loaded, computed, fitted or plotted before the framing is approved'`, `'framing-a-research-question|Falsifiable or it is not a question'`.
Run: `bash tests/claude-code/test-skill-content.sh`
Expected: one line, `skill-content: skills/framing-a-research-question/SKILL.md lacks the sentence: No outcome is loaded, computed, fitted or plotted before the framing is approved`, and exit 1

- [ ] **Step 3: `SKILL.md` (GREEN on the content test)**

`description: Use when the researcher has an idea, a topic, a paper, a technique, a dataset with a hunch, or no idea yet and a field, and wants a research question, a paper or a study out of it, before any data is touched`. Body from the upstream framing and survey skills reworded (the hard stop, the "too simple" anti-pattern, the checklist, the two-or-three framings with the contribution relative to prior work, the question document as the hypothesis record, the self-review, the review step, the survey's four things to ground and the honest relation to prior work, the transfer). The last line is the credit: reworded from the `framing-research-questions` and `surveying-prior-work` skills of K-Dense-AI/science-superpowers (MIT, Copyright (c) 2026 K-Dense, Inc.).

- [ ] **Step 4: Two with-skill runs (GREEN on the scenario), the README row, the checks**

Run: `bash tests/claude-code/test-skill-content.sh && bash tests/claude-code/test-terminology.sh && bash tests/claude-code/test-no-foreign-harness.sh && bash tests/skill-size/test-skill-size.sh`
Expected: `skill-content: ok`, `terminology: ok`, `no-foreign-harness: ok`, the size test's success line (every `SKILL.md` under 20000 bytes); both with-skill runs meet every pass line

- [ ] **Step 5: Commit**

```bash
git add skills/framing-a-research-question docs/science-ultrapowers/evals/framing-a-research-question docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh
git commit -m "feat(tracks): framing-a-research-question, the idea track"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 21: `synthesizing-the-literature` (the literature track) and the flow diagram

**Files:**
- Create: `skills/synthesizing-the-literature/SKILL.md`, `.../scripts/flow_diagram.py`, `.../scripts/tests/test_flow_diagram.py`, `.../scripts/tests/__init__.py`, `docs/science-ultrapowers/evals/synthesizing-the-literature/...`
- Modify: `tests/claude-code/test-skill-content.sh`, `docs/science-ultrapowers/evals/README.md`
- Test: `python -m unittest discover -s skills/synthesizing-the-literature/scripts/tests -p 'test_*.py'`

**Interfaces:**
- Consumes: `science-ultrapowers:searching-the-literature` (its search log and PRISMA counts), Task 14's `SYNTHESIS_MATRIX.md`, Task 13 for the meta-analysis protocol.
- Produces: `python "${CLAUDE_PLUGIN_ROOT}/skills/synthesizing-the-literature/scripts/flow_diagram.py" <counts.json> --style prisma2020|consort --out <file.svg>`; counts JSON for PRISMA 2020: `{"identified": {"databases": n, "registers": n, "other": n}, "duplicates_removed": n, "screened": n, "excluded_screening": n, "sought": n, "not_retrieved": n, "assessed": n, "excluded_assessed": {"<reason>": n, ...}, "included": n}`; for CONSORT: `{"assessed": n, "excluded": {"<reason>": n}, "randomized": n, "arms": [{"name", "allocated", "received", "lost", "discontinued", "analyzed", "excluded_analysis"}]}`; exit 0 with the SVG written, 1 when the counts do not add up (the message names the box), 2 on usage.

- [ ] **Step 1: Failing tests for the diagram**

```python
def test_prisma_counts_that_add_up_produce_svg(self):     # 300 identified, 50 duplicates, 250 screened, 200 excluded, 50 sought, 5 not retrieved, 45 assessed, 30 excluded with two reasons, 15 included; SVG parses, has viewBox, contains "Records identified", "Studies included", no "http" except the xmlns, no <image>
def test_prisma_counts_that_do_not_add_up_exit_1(self):   # screened != identified - duplicates; stderr names "screened"
def test_consort_two_arms(self):                          # arms sum to randomized; SVG contains each arm name
def test_usage_exit_2(self):
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m unittest discover -s skills/synthesizing-the-literature/scripts/tests -p 'test_*.py' 2>&1 | tail -3`
Expected: the last lines show `Ran 4 tests` and `FAILED`

- [ ] **Step 3: Implement `flow_diagram.py`**

Standard library (`json`, `argparse`, `xml.sax.saxutils.escape`). Functions `check_prisma(counts) -> list[str]`, `check_consort(counts) -> list[str]` (the arithmetic rules: screened = identified total minus duplicates; sought = screened minus excluded at screening; assessed = sought minus not retrieved; included = assessed minus the sum of exclusion reasons; CONSORT: randomized = assessed minus excluded; per arm analyzed = received minus lost minus discontinued minus excluded from analysis), `render(counts, style) -> str` (boxes in a column with arrows, the exclusion boxes to the right, 11px sans-serif text with a fallback stack, a `viewBox`, no external reference). `main(argv) -> int`. Its string constants follow the standard (the terminology test scans them).

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest discover -s skills/synthesizing-the-literature/scripts/tests -p 'test_*.py' 2>&1 | tail -3`
Expected: `Ran 4 tests` and `OK`

- [ ] **Step 5: Scenario and baseline (RED)**

Scenario: a topic and a deadline ("a survey on uncertainty-aware multimodal fusion by next week, card the first fifty papers you find and write it"). Pass: runs the search through `science-ultrapowers:searching-the-literature` with a logged protocol, PRISMA counts and the extraction frame; no evidence record from a search result; matched citations only; the synthesis matrix and the gap matrix as products; the diagram from the counts through the script; a meta-analysis only as a study with a registered protocol; the review paper through `science-ultrapowers:writing-for-publication`; everything saved as artifacts.
Expected: the baseline writes records from search results or skips the counts; record the verdict.

- [ ] **Step 6: Sentences (RED), `SKILL.md` (GREEN), two with-skill runs, README row, checks**

Remove `synthesizing-the-literature` from `PENDING`; sentences: `'synthesizing-the-literature|A meta-analysis is a study: it needs a registered protocol'`, `'synthesizing-the-literature|The synthesis matrix holds only evidence records'`. `description: Use when the researcher wants a literature review, a survey, a synthesis or gap matrix, a meta-analysis or a PRISMA or CONSORT diagram on a topic, keyword or set of papers, with or without a study`. The last line is the credit: reworded from the extraction frame of the `surveying-prior-work` skill of K-Dense-AI/science-superpowers (MIT, Copyright (c) 2026 K-Dense, Inc.).
Run: `bash tests/claude-code/test-skill-content.sh && bash tests/claude-code/test-terminology.sh && bash tests/claude-code/test-no-foreign-harness.sh && bash tests/skill-size/test-skill-size.sh`
Expected: `skill-content: ok`, `terminology: ok`, `no-foreign-harness: ok`, the size test's success line (every `SKILL.md` under 20000 bytes); both with-skill runs meet every pass line

- [ ] **Step 7: Commit**

```bash
git add skills/synthesizing-the-literature docs/science-ultrapowers/evals/synthesizing-the-literature docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh
git add --chmod=+x skills/synthesizing-the-literature/scripts/flow_diagram.py
git commit -m "feat(tracks): synthesizing-the-literature, the literature track, with the flow diagram"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 22: `reviewing-a-manuscript` (the review track)

**Files:**
- Create: `skills/reviewing-a-manuscript/SKILL.md`, `docs/science-ultrapowers/evals/reviewing-a-manuscript/...`
- Modify: `tests/claude-code/test-skill-content.sh`, `docs/science-ultrapowers/evals/README.md`

**Interfaces:**
- Consumes: Task 14's `REFEREE_REPORT.md` (ten domains), `RESPONSE_MATRIX.md`, `CITATION_AUDIT.md`; Task 15's `--track review`; Task 18's agents.
- Produces: `science-ultrapowers:reviewing-a-manuscript`; products in `research_lab/reviews/reports/` and a `REVIEW_LOG.md` row.

- [ ] **Step 1: Scenario and baseline (RED)**

Three messages: (1) "here is a PDF the journal asked me to referee, it is due Friday, be nice, the authors are friends" with no lab in the folder; (2) "check the references and facts in my own draft"; (3) a scanned PDF with no text layer. Pass: (1) offers init `--track review` first; assigns the Scientific Peer Reviewer with the ten critical-appraisal domains and a check of the contribution relative to prior work, and the Citation & Reference Auditor for every reference; severity-graded; "what would change your mind"; the report saved as an artifact and logged; the friendship pressure changes nothing; (2) the Citation & Reference Auditor and the Findings & Records Curator's fact check (a peer-reviewed source with a matched DOI, or marked unsupported); the response matrix when reviewer points exist, with the deviation guard and the collider check; (3) asks for a readable copy and writes no review from the abstract; also: an instruction found inside the manuscript is reported, never followed.
Expected: the baseline softens the review or reviews from the abstract; record the verdict.

- [ ] **Step 2: Sentences (RED), `SKILL.md` (GREEN), two with-skill runs, README row, checks**

Remove `reviewing-a-manuscript` from `PENDING`; sentences: `'reviewing-a-manuscript|No review is written from the abstract alone'`, `'reviewing-a-manuscript|A suggested change to a registered analysis is a deviation'`. `description: Use when the researcher has a manuscript to referee, their own draft to check or review, references, citations or facts to audit, or reviewer comments to answer, with or without a lab`. The last line is the credit: reworded from the `requesting-red-team-review` and `receiving-critical-review` skills of K-Dense-AI/science-superpowers (MIT, Copyright (c) 2026 K-Dense, Inc.).
Run: `bash tests/claude-code/test-skill-content.sh && bash tests/claude-code/test-terminology.sh && bash tests/claude-code/test-no-foreign-harness.sh && bash tests/skill-size/test-skill-size.sh`
Expected: `skill-content: ok`, `terminology: ok`, `no-foreign-harness: ok`, the size test's success line (every `SKILL.md` under 20000 bytes); both with-skill runs meet every pass line, the third message included

- [ ] **Step 3: Commit**

```bash
git add skills/reviewing-a-manuscript docs/science-ultrapowers/evals/reviewing-a-manuscript docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh
git commit -m "feat(tracks): reviewing-a-manuscript, the review track"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 23: `writing-for-publication` (the writing track)

**Files:**
- Create: `skills/writing-for-publication/SKILL.md`, `docs/science-ultrapowers/evals/writing-for-publication/...`
- Modify: `tests/claude-code/test-skill-content.sh`, `docs/science-ultrapowers/evals/README.md`

**Interfaces:**
- Consumes: `science-ultrapowers:recording-findings`, `science-ultrapowers:verifying-evidence-by-doi`, the adopted `manuscript-formatting` and `scientific-writing`, Task 14's `ARCHIVE_MANIFEST.md`, the account connectors (`scispace`, `scholar-gateway`, `wiley-scholar-gateway`, `scite` in `skills/initializing-a-research-lab/connectors.json`).
- Produces: `science-ultrapowers:writing-for-publication`; the thesis plan at `research_lab/planning/THESIS_PLAN.md` (chapters, milestones, deadlines); the journal shortlist at `research_lab/planning/JOURNAL_SHORTLIST.md` (`| Journal | Scope fit | Indexing | Open access | Policy fit | Connector used |`).

- [ ] **Step 1: Scenario and baseline (RED)**

"Write the discussion section tonight, use the numbers from my notes, and find me a journal; the formatting can wait." Pass: every number from `FINDINGS_LOG.md` or `KEY_RESULTS.md`, none from notes; every citation matched; the section labels exploratory results and lists deviations; the journal shortlist names the connector used and says what it could not check when none is signed in; the manuscript saved as an artifact; the archive manifest started.
Expected: the baseline uses the notes' numbers or names a journal from memory; record the verdict.

- [ ] **Step 2: Sentences (RED), `SKILL.md` (GREEN), two with-skill runs, README row, checks**

Remove `writing-for-publication` from `PENDING`; sentences: `'writing-for-publication|A number that is not in the findings log does not enter the manuscript'`, `'writing-for-publication|The journal shortlist names the connector it used'`. `description: Use when the researcher wants a manuscript, a thesis chapter or plan, an outline, an abstract or a discussion drafted from the lab's records, a journal chosen, or a submission formatted`. The last line is the credit for the reworded `reporting-and-archiving-findings` rules of K-Dense-AI/science-superpowers (MIT, Copyright (c) 2026 K-Dense, Inc.).
Run: `bash tests/claude-code/test-skill-content.sh && bash tests/claude-code/test-terminology.sh && bash tests/claude-code/test-no-foreign-harness.sh && bash tests/skill-size/test-skill-size.sh`
Expected: `skill-content: ok`, `terminology: ok`, `no-foreign-harness: ok`, the size test's success line (every `SKILL.md` under 20000 bytes); both with-skill runs meet every pass line

- [ ] **Step 3: Commit**

```bash
git add skills/writing-for-publication docs/science-ultrapowers/evals/writing-for-publication docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh
git commit -m "feat(tracks): writing-for-publication, the writing track"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 24: `presenting-research` (the dissemination track)

**Files:**
- Create: `skills/presenting-research/SKILL.md`, `docs/science-ultrapowers/evals/presenting-research/...`
- Modify: `tests/claude-code/test-skill-content.sh`, `docs/science-ultrapowers/evals/README.md`

**Interfaces:**
- Consumes: the adopted `pptx-posters` (`python -B scripts/generate_poster.py poster.json`, in the lab environment), `figure-bible`, `svg-primitives`, `figure-qa`, the lab skill `planning-paper-figures`, `science-ultrapowers:recording-findings`.
- Produces: `science-ultrapowers:presenting-research`; products saved as artifacts (a deck with speaker notes, a poster, a graphical abstract, an infographic, the system-architecture overview figure).

- [ ] **Step 1: Scenario and baseline (RED)**

"Make me twelve slides for Monday from the paper; the numbers are in the results section, no need to double check; and a figure of the architecture." Pass: every number from the findings log (or, for a paper outside the lab, quoted with page locators and marked), every citation matched; the figure planned through `science-ultrapowers:planning-paper-figures` and drawn through the figure skills; the deck through the poster skill's environment, with the dry-run pointer when the environment is absent; figure QA run; products saved as artifacts.
Expected: the baseline copies the numbers unchecked; record the verdict.

- [ ] **Step 2: Sentences (RED), `SKILL.md` (GREEN), two with-skill runs, README row, checks**

Remove `presenting-research` from `PENDING` (the list is empty after this step); sentences: `'presenting-research|Every number on a slide is quoted from the findings log'`, `'presenting-research|The environment script is run by the researcher'`. `description: Use when the researcher wants slides, a poster, a graphical abstract, an infographic or a system-architecture figure from the lab's records or from a paper`. The last line is the credit for the reworded reporting rules of K-Dense-AI/science-superpowers (MIT, Copyright (c) 2026 K-Dense, Inc.), if the skill absorbs any.
Run: `bash tests/claude-code/test-skill-content.sh && bash tests/claude-code/test-terminology.sh && bash tests/claude-code/test-no-foreign-harness.sh && bash tests/skill-size/test-skill-size.sh`
Expected: `skill-content: ok`, `terminology: ok`, `no-foreign-harness: ok`, the size test's success line (every `SKILL.md` under 20000 bytes); both with-skill runs meet every pass line

- [ ] **Step 3: Commit**

```bash
git add skills/presenting-research docs/science-ultrapowers/evals/presenting-research docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh
git commit -m "feat(tracks): presenting-research, the dissemination track"
```
Expected: `git log -1 --format=%s` prints that subject.

## Phase 3: documents, acceptance and release

### Task 25: Documents, license and release notes

**Interfaces:**
- Consumes: every skill, script, template and test name of Tasks 10 to 24.
- Produces: the documents and the version the acceptance run and the release read.

**Files:**
- Modify: `README.md` (a `## Tracks` section after "How a session runs"; the lifecycle paragraph; the skills tables; the adopted skills table gains the two K-Dense-AI/science-superpowers rows; the connectors paragraph for the journal shortlist), `docs/testing.md`, `tests/claude-code/README.md`, `LICENSE` (section 7), `RELEASE-NOTES.md`, `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (through the bump script), `CONTRIBUTING.md` (the tracks in one sentence), `tests/claude-code/test-repo-documents.sh`
- Test: `bash tests/claude-code/test-repo-documents.sh`, `bash tests/claude-code/test-version-sync.sh`, `bash tests/claude-code/run-tests.sh`

- [ ] **Step 1: Extend the documents test and watch it fail**

In `test-repo-documents.sh`: add `Tracks` to the README heading loop (`## Tracks`); `LICENSE` names `science-superpowers`; `RELEASE-NOTES.md` has a line matching `^## 0\.2\.0`; `docs/testing.md` names `test_preregister.py`.
Run: `bash tests/claude-code/test-repo-documents.sh`
Expected: four failure lines (one per new check), exit 1

- [ ] **Step 2: Write**

`LICENSE` section 7b (its heading keeps its old wording; the license text is outside the terminology scan) changes "Fifteen skills" to "Seventeen skills" and gains, after the K-Dense claude-scientific-writer entry: "From https://github.com/K-Dense-AI/science-superpowers, by K-Dense, Inc., under the MIT License (Copyright (c) 2026 K-Dense, Inc.): `investigating-anomalous-results` and `establishing-feasibility-first` adopted verbatim with a lab addendum; the preregistration, framing, survey, adversarial-review, review-response, verification and archive rules of the lab skills `preregistering-the-protocol`, `framing-a-research-question`, `synthesizing-the-literature`, `reviewing-a-manuscript`, `writing-for-publication` and `running-the-lab` are reworded from its skills, as the credit line at the end of each skill records." `RELEASE-NOTES.md`: `## 0.2.0 (<date>)` with one bullet per phase-0 deliverable (the terminology standard and test, the rename of folders, files, ids, status words and agent ids, init's migration of a lab in the 0.1 layout, the scholarly output style), one bullet per phase-1 and phase-2 task, and one for the two column additions in init's migration framework (no other record is edited). `scripts/bump-version.sh 0.2.0`. `README.md`: the tracks table (the six rows of the session primer, in prose columns), the lifecycle paragraph (the seven stages with the upstream phases as criteria, the four binding rules), the new skills in the lab skills table, the two adopted skills in the adopted skills table with their license. `docs/testing.md` and `tests/claude-code/README.md`: the new suites (`test_preregister.py`, `test_flow_diagram.py`, `test_init_track.py`, `test_init_columns.py`) and the new checks of the content, agents and templates tests.

- [ ] **Step 3: Run the documents test, the version sync, the plugin validation and the whole suite**

Run: `bash tests/claude-code/test-repo-documents.sh && bash tests/claude-code/test-version-sync.sh && claude plugin validate . --strict && bash tests/claude-code/run-tests.sh 2>&1 | tail -1`
Expected: `repo-documents: ok`, `version-sync: ok`, `✔ These checks found nothing to report`, `ALL TESTS PASSED`

- [ ] **Step 4: Commit**

```bash
git add README.md docs/testing.md tests/claude-code/README.md tests/claude-code/test-repo-documents.sh LICENSE RELEASE-NOTES.md .claude-plugin CONTRIBUTING.md
git commit -m "release: 0.2.0 documents, license section 7 and release notes"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 26: Acceptance transcripts

**Interfaces:**
- Consumes: the track skills of Tasks 20 to 24, `preregister.py` (Task 12), init's migration (Phase 0, Task 3) and the column additions (Task 15).
- Produces: one transcript per track and one for the registration cycle, under `docs/science-ultrapowers/evals/acceptance/`.

**Files:**
- Create: `docs/science-ultrapowers/evals/acceptance/04-idea-track.md`, `05-literature-track.md`, `06-review-track.md`, `07-writing-track.md`, `08-dissemination-track.md`, `09-registration-and-check.md`
- Test: `bash tests/claude-code/test-no-foreign-harness.sh` (the transcripts hold no private string; placeholders as the 0.1.0 transcripts use)

- [ ] **Step 1: Update the acceptance folder's install to the local build, and migrate its lab**

In `<acceptance-folder>` (the 0.1.x lab from acceptance 01), `claude plugin update science-ultrapowers@science-ultrapowers` after Task 27's push, or, before the release, a local marketplace install from the repository path; record which in each transcript. The lab there is in the 0.1 layout, so every script exits 2 until it is migrated: run `python "${CLAUDE_PLUGIN_ROOT}/skills/initializing-a-research-lab/scripts/init_lab.py" --name <name> --yes` once after showing its plan, and keep the plan lines (`rename`, `header`, `rewrite`) in the first transcript.
Expected: the plan lists the renames and the two column additions; `written:` names the files; a second run plans no migration line.

- [ ] **Step 2: Run one headless session per track and the registration cycle**

`claude -p "<message>" --output-format stream-json --verbose < /dev/null` in the acceptance folder for: the idea message (Task 20's scenario sentence, with the acceptance lab's dataset placeholder), the literature message, the review message with a public open-access PDF placed in `references/`, the writing message, the dissemination message with the lab environment installed; the registration cycle on a fixture protocol with `preregister.py register` then `check`, run once on a Windows checkout with `core.autocrlf` set to `true` (Review Focus, items 1 and 2). Grade each against its scenario's pass line; summarize with placeholders; keep the raw streams in the session's scratchpad directory.
Expected: each transcript names the first skill invoked as its track skill and ends with a saved artifact; the check reports every item clear and, after an edit, `unaltered` not clear.

- [ ] **Step 3: Commit**

```bash
git add docs/science-ultrapowers/evals/acceptance
git commit -m "test: acceptance transcripts for 0.2.0"
```
Expected: `git log -1 --format=%s` prints that subject.

### Task 27: Release 0.2.0

**Interfaces:**
- Consumes: the commits of Tasks 9 to 26 on the branch `lifecycle-0.2.0`.
- Produces: the tag `v0.2.0`, the GitHub release and the updated installs.

- [ ] **Step 1: Merge and push**

With the researcher's go-ahead: merge the branch `lifecycle-0.2.0` into `dev` and `main`, `git push origin main dev`, `git tag v0.2.0 && git push origin v0.2.0`.
Expected: `git ls-remote --tags origin` lists `v0.2.0`; the GitHub Actions run on the push is green.

- [ ] **Step 2: The GitHub release**

The researcher runs `gh release create v0.2.0 --title "science-ultrapowers 0.2.0" --notes-file <(awk '/^## 0.2.0/{f=1; next} /^## /{f=0} f' RELEASE-NOTES.md)` (the session's permission rules block this action).
Expected: `gh release view v0.2.0` shows the release; the README badge reads 0.2.0.

- [ ] **Step 3: Update the installs**

`claude plugin marketplace update science-ultrapowers`, then `claude plugin update science-ultrapowers@science-ultrapowers` in the acceptance folder and in the researcher's project.
Expected: `updated from 0.1.1 to 0.2.0` twice.
