# Research Lifecycle and Tracks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ultrapowers:subagent-driven-development (recommended) or ultrapowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give science-ultrapowers one scholarly vocabulary (a terminology standard, a test and a scholarly output style, with every text renamed) and make it a complete research lifecycle: five tracks that enter one lifecycle at the stage that fits, the nine stages of science-superpowers on gates G0 to G6 with the ten absorbed disciplines, a protocol freeze and audit, two vendored side-branch skills, a minimal lab per track, shipped as 0.2.0.

**Architecture:** Phase 0 writes the terminology standard and its test, renames every plugin text, template, record, script message and agent to the standard, gives init a migration for existing labs and the scholarly output style, and then re-grounds Phases 1 to 3 against the renamed tree (their text below still carries the old names until Task 8 rewrites them). Phase 1 lays the foundations (the upstream clone, the two vendored skills, the pre-registration skill and its script, the templates and records, init's `--track` and migrations, the lifecycle in `running-the-lab`, the agents, the bootstrap). Phase 2 adds the five track skills one by one, each with its tests and pressure test in the same commit so the tree stays green. Phase 3 writes the documents, runs the acceptance transcripts and releases 0.2.0.

**Tech Stack:** Markdown skills with YAML frontmatter, Python 3.11 standard library (`subprocess`, `json`, `hashlib`, `argparse`, `unittest`), bash tests, git; the lab environment's `python-pptx==1.0.2` only through the vendored skills.

**Spec:** `docs/science-ultrapowers/specs/2026-11-08-terminology-standard-design.md` (Phase 0) and `docs/science-ultrapowers/specs/2026-11-08-research-lifecycle-design.md` (Phases 1 to 3)

**Sources:** the repository at commit 6f6f72c (every file and line this plan cites); the science-superpowers clone at commit `0374bdf82c2372bdf1667e3c762146c3a29215f5` (its `README.md`, `docs/research-workflow.md`, `docs/preregistration.md`, `LICENSE`, `skills/preregistering-analysis/SKILL.md` and `prereg.sh`, `skills/framing-research-questions/SKILL.md`, `skills/surveying-prior-work/SKILL.md`, `skills/subagent-driven-analysis/protocol-compliance-reviewer-prompt.md`, `skills/requesting-red-team-review/reviewer.md`, `skills/receiving-critical-review/SKILL.md`, `skills/verifying-results-before-claiming/SKILL.md`, `skills/reporting-and-archiving-findings/SKILL.md`, `skills/dispatching-parallel-investigations/SKILL.md`, `skills/designing-the-analysis/SKILL.md`, read 2026-11-08); the reading record `docs/science-ultrapowers/research/2026-11-08-science-superpowers-reading.md`. Current sources not checked for anything external: the plan pins no API or package version beyond the ones already pinned in `setup_lab_env.ps1`; the PRISMA 2020 and CONSORT box structures are taken from the statements as known (Page et al. 2021; Schulz et al. 2010), not re-read, because the web readers were unavailable in this session.

## Global Constraints

- Phase 0 binds every later task: the terminology standard at `docs/science-ultrapowers/terminology.md`, `tests/claude-code/test-terminology.sh` green after every task from Task 1 on, no stage code, no not-approved term, American spelling, abbreviations expanded at first use, "the researcher" in place of "your human partner" in lab text.

- Claude Code is the only harness. Plugin scripts: bash (Git for Windows on Windows), node 22+, Python 3.11+ standard library; no pip packages. Vendored skills' scripts may use the lab environment (`python-pptx==1.0.2`, `Pillow==12.3.0`, `lxml==6.1.1` as pinned in `setup_lab_env.ps1`).
- Version `0.2.0` in both manifests through `scripts/bump-version.sh 0.2.0`; a `## 0.2.0 (<date>)` heading at the top of `RELEASE-NOTES.md`.
- Skill form: `description` starts with "Use when", "Use whenever", "Use for" or "Use at" and says only when; cross-references `science-ultrapowers:<skill>`, never `@`; "your human partner"; actions, not tool names; verb-first lab skill names; a pressure test under `docs/science-ultrapowers/evals/<skill>/` for every new or changed skill (one baseline, two with-skill runs, Haiku 5.5, inline prompts).
- Sizes: the bootstrap under 8,500 bytes; every `SKILL.md` under 20,000 bytes; `running-the-lab/SKILL.md` under 18,000 bytes (new check).
- Leak gate: `bash tests/claude-code/test-no-foreign-harness.sh` passes after every task: no project-specific string, no other harness name, no `science-superpowers:` prefix outside `LICENSE`, `RELEASE-NOTES.md`, `tests/`, `docs/science-ultrapowers/evals/` and the two vendored skills' `PROVENANCE.md`, no `docs/science-superpowers/` path, no drive-letter path outside C: system paths.
- Records: everything a track writes goes under `research_lab/`; roles never run git write commands; the orchestrator commits `research_lab/` only on the current branch; nothing under `${CLAUDE_PLUGIN_ROOT}`.
- Licence: the K-Dense MIT notice (`Copyright (c) 2026 K-Dense, Inc.`) with every substantial verbatim portion; `LICENSE` section 7 gains a science-superpowers entry; absorbed rules carry a credit line in the owning skill's `PROVENANCE.md` (new, for the plugin's own skills that absorb text) or in `docs/science-ultrapowers/research/`.
- Windows: new scripts staged with `git add --chmod=+x`; LF line endings (`.gitattributes` covers `skills/` and `hooks/`).
- Existing labs: an init re-run adds new templates and `lab.json` keys and performs exactly two header migrations (`Basis` on `FINDINGS.md`, existing rows filled with `exploratory`; `Input checksums` on `EXPERIMENT_REGISTER.md`, existing rows empty); no other record is edited.
- One problem per commit; commit messages end with the attribution line the session carries.

## Review Focus

1. A protocol path with spaces or non-ASCII characters on Windows: `protocol_freeze.py` must commit and audit it (the upstream script rejects whitespace). Test: Task 4, `test_freeze_path_with_spaces`.
2. An audit on a repository whose outputs are LFS pointers or live on a parallel branch: CHRONOLOGY must judge by commit ancestry, not file content, and say "unprovable" for a parallel branch rather than pass. Test: Task 4, `test_audit_parallel_branch_output_is_unprovable`.
3. An init re-run on a lab whose `FINDINGS.md` already has the `Basis` column, or whose register already has `Input checksums`: the migration must be a no-op, listed as skip. Test: Task 7, `test_migration_is_idempotent`.
4. `--track` on a folder that already has the full scaffold: nothing created, `tracks` grows by union, nothing else touched. Test: Task 7, `test_track_on_full_lab_adds_only_the_track`.
5. A manuscript the review track cannot read (an encrypted or scanned PDF): the track asks for a readable copy and writes no review from the abstract. Test: Task 14's pressure scenario carries this as its third message.

---

## Phase 0: the terminology standard and the rename

Every task in this phase follows `docs/science-ultrapowers/specs/2026-11-08-terminology-standard-design.md` (the terminology design); its decisions D2 to D13 fix every name used below. The not-approved list, the spelling list and the abbreviation list live in the standard; the test reads them from there. During this phase `tests/terminology-allow.txt` lists the paths still to be renamed; each task removes the paths it renamed, and Task 8 empties it. Implementers never commit, never edit the allow-list (the lead session does), and never touch the upstream body of a vendored or kept skill.

### Task 1: The standard and the terminology test

**Files:**
- Create: `docs/science-ultrapowers/terminology.md`, `tests/claude-code/test-terminology.sh`, `tests/terminology-allow.txt`
- Modify: `docs/testing.md`, `tests/claude-code/README.md`
- Test: `bash tests/claude-code/test-terminology.sh`

**Interfaces:**
- Produces: the standard's two fenced lists, each introduced by an HTML comment on its own line: `<!-- not-approved -->` then a fenced block with one line per entry `old term => approved term`; `<!-- spelling -->` then a fenced block with one British form per line `analyse => analyze`; `<!-- abbreviations -->` then a fenced block `RQ => research question (RQ)` (the expansion the first use must show). The legacy table (old id prefixes, old paths, old status tokens, old keys to new). The marker `<!-- legacy -->` (Markdown) and `# legacy` (scripts) that exempts a line. The allow-list format: one repository path per line, `#` comments allowed.

- [ ] **Step 1: Write the failing test**

`test-terminology.sh` (house form, prints `terminology: ok`): reads the three lists from the standard (the fenced block after each marker comment); builds the scanned file set: `skills/*/SKILL.md` for the thirteen lab skills (the folders without `PROVENANCE.md` and not in the kept list `systematic-debugging test-driven-development verification-before-completion requesting-code-review receiving-code-review dispatching-parallel-agents writing-skills`); for every folder with `PROVENANCE.md`, only the leading blockquote block of its `SKILL.md` (lines starting with `> ` after the frontmatter, up to the first other line); `agents/*.md`; every file under `skills/initializing-a-research-lab/templates/`; `README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `docs/testing.md`; `hooks/session-start`, `hooks/memory-nudge`, `hooks/memory-postcompact`, `hooks/lib/*`; the string constants of every `skills/*/scripts/*.py` (extracted with `python -c "import ast,sys; ..."`) and the string literals of `skills/*/scripts/*.mjs` and `*.ps1` (grep of quoted strings); `docs/science-ultrapowers/specs/2026-11-08-research-lifecycle-design.md` and `docs/science-ultrapowers/plans/2026-11-08-research-lifecycle.md`. Skips a path listed in the allow-list, and fails when a listed path has no hit (`allow-list entry has no remaining hit: <path>`). Skips any line ending with `<!-- legacy -->` or `# legacy`. Reports, per hit, `<file>:<line>: not-approved term '<term>'`, `stage code`, `British spelling '<word>'`, or `abbreviation '<abbr>' not expanded at first use`, and exits 1. Positive control: plants `G3`, `ledger`, `analyse` and a bare `RQ` into a temporary file and expects four hits, or fails.
Run: `bash tests/claude-code/test-terminology.sh`
Expected: `terminology: the standard docs/science-ultrapowers/terminology.md is missing` and exit 1

- [ ] **Step 2: Write the standard**

`docs/science-ultrapowers/terminology.md`: a title, a one-paragraph scope (the plugin's own terms; research terms outside it keep their field's meaning), Part 1 "Writing rules" numbered R1 onward in the sections words, grammar, sentences, structure, names, numbers and identifiers, abbreviations, spelling (one term one meaning; one part of speech; a term defined at first use; no code as a name; identifiers as `<PREFIX>-<NNNN>` with the prefix expanded in every table header; status values as lower-case words; American spelling; an abbreviation expanded at first use in a file; the STE sentence rules the output style applies), Part 2 "Controlled dictionary" as one table per domain (lifecycle; sources and evidence; findings and records; the artifact archive; team and coordination; lab memory; contributor vocabulary) with the columns `Term | Meaning in this plugin | Operational form | Not to be confused with | Replaces | Source`, every term from the design's D2 to D13 and every D-class term the audits list as already right, each definition at most four sentences; the "Not approved" list as the marked fenced block; the "Spelling" and "Abbreviations" marked blocks; the "Legacy forms" table (prefixes F-, H-, RV-, EC-, DA-, D-, T-, MP-, R-; the ten numbered folders; the old file names; the old status tokens; `jev.blockedPaths`; `evidence:` and `gotcha` in memory entries; `snapshot` and `working_data`; `claimed`, `unaddressed`, `resolved`; `VERIFIED`). Sources named as the design's Constraints list them. The allow-list: every scanned path that still holds an old term (generate it by running the test with an empty allow-list and listing the files it reports).

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
- Modify: everything under `skills/initializing-a-research-lab/templates/` (folders renamed with `git mv`: `00_project_knowledge` to `project`, `01_reference_registry` to `literature`, `02_findings_ledger` to `findings`, `03_experiments` to `experiments`, `04_reviews` to `reviews`, `05_access_requests` to `requests`, `06_decisions` to `decisions`, `07_project_management` to `planning`, `08_decision_log` to `automation`, `09_skill_vetting` to `tool_vetting`; files: `REGISTRY.csv` to `SOURCES.csv`, `evidence_cards/` to `evidence_records/`, `audits/` to `search_logs/` plus a new `citation_audits/`, `FINDINGS.md` to `FINDINGS_LOG.md`, `CANONICAL_NUMBERS.md` to `KEY_RESULTS.md`, `protocols/` to `preregistrations/`, `DECISIONS.md` to `DECISION_LOG.md`, `TASK_BOARD.md` to `WORK_PLAN.md`, `templates/H_CARD.md` to `HYPOTHESIS_RECORD.md`, `HANDOFF.md` to `TASK_REPORT.md`, `DEVILS_ADVOCATE_TEMPLATE.md` to `ADVERSARIAL_REVIEW.md`, `REVIEW_ACADEMIC.md` to `INTERNAL_REVIEW.md`; the meeting templates in `skills/holding-lab-meetings/templates/`: `SESSION_KICKOFF.md` to `SESSION_OPENING.md`, `SESSION_STANDUP.md` to `SESSION_CLOSE.md`; `lab.json` (`scope.restrictedFolders`, the fourteen new role ids, `idPrefixes`); `CLAUDE_SECTION.md`; `gitignore_lines.txt` (`.working/`); every header, status value, id prefix and sentence inside them), `skills/initializing-a-research-lab/scripts/init_lab.py` (`COPIED_FILES`, `LAB_JSON_REL`, the references and `.scratch` paths, the plan verbs), `tests/claude-code/test-lab-templates.sh` (created against the new names; the lifecycle plan's Task 6 wrote it against the old)
- Test: `bash tests/claude-code/test-lab-templates.sh`, the init suite

**Interfaces:**
- Produces: the new tree under `research_lab/` for every later task; the headers: `| FND-id (finding) | Statement | Type | Evidence | Status | Recorded | Verified | Scope and caveats |` (the lifecycle plan adds `Basis` later), `| EXP-id (experiment) | Preregistration | Hypothesis | Code and config | Seeds and partitions | Environment | Status | Outputs | Deviations | Findings |`, `SOURCES.csv` columns `source_id,title,first_author,year,doi,source_class,doi_status,status,evidence_records,notes`, `REVIEW_LOG.md` columns `| REV-id (review) | Stage | Artifact | Reviewer | Outcome | Date | Report |`, `ACCESS_REQUESTS.md` `| REQ-id (request) | Type | Priority | Status | Source | Filed | Resolved |` with types `full-text request / DOI confirmation / exception approval`, priorities `blocks a stage / this cycle / background`, statuses `open / fulfilled / approved / declined / unavailable`; the task report block (`TASK REPORT <TASK-id> -> <next role>` with the lines Deliverables, Inputs, Checks performed, Findings submitted, Memories proposed, Review requested, Open issues and risks, Requests filed, Deviations from the assignment); the task assignment block (`TASK <TASK-id> | Stage <name> | Owner <role> | Reviewer <role> | Due <date>` with Objective, Inputs, Deliverables, Completion criteria, Constraints).

- [ ] **Step 1: Write the failing test** (`test-lab-templates.sh`: every new path exists and no old path exists under the templates; the headers above exactly; the status words; the hypothesis record's fields; `lab.json` keys `scope.restrictedFolders`, `roles` with the fourteen new ids, `idPrefixes` mapping the nine prefixes to their expansions)
- [ ] **Step 2: Run it** — Expected: one `FAIL:` per missing item
- [ ] **Step 3: Rename and rewrite** the templates as the Interfaces say; `init_lab.py` paths; every sentence in the templates in the standard's words (no stage code, no not-approved term)
- [ ] **Step 4: Run the test, the init suite and the terminology test** — Expected: `lab-templates: ok`; init suite `OK` (its path assertions updated in this task); `terminology: ok` after the lead session removes the templates' paths from the allow-list
- [ ] **Step 5: Commit** — `git add -A skills/initializing-a-research-lab skills/holding-lab-meetings/templates tests/claude-code/test-lab-templates.sh && git commit -m "feat(templates): the research-lab records in the standard's names"`

### Task 3: Init's migration and the output style

**Files:**
- Modify: `skills/initializing-a-research-lab/scripts/init_lab.py`, `skills/initializing-a-research-lab/SKILL.md`
- Create: `output-styles/scholarly-explanatory.md`, `skills/initializing-a-research-lab/scripts/tests/test_init_migration.py`, `.../tests/test_init_output_style.py`, `.../tests/fixtures/lab_0_1/` (a minimal 0.1.x lab: the ten numbered folders with one row in each table, two memory entries with `evidence:` and `type: gotcha`, `lab.json` with `jev.blockedPaths` and the old role ids)
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
- Modify: all fourteen agent bodies (the `name:` field; the vocabulary; a `## Contributor roles (CRediT)` line naming the agent's CRediT roles from the audit's mapping, with the sentence that AI roles are not authors and the researcher's contribution statement discloses AI assistance; "the researcher" in place of "your human partner"); `.claude-plugin/plugin.json` agents list; `tests/claude-code/test-agents.sh` (ids, the CRediT line, the vocabulary sentences)
- Test: `bash tests/claude-code/test-agents.sh`

**Interfaces:**
- Produces: the fourteen ids every skill cites as `science-ultrapowers:<id>`.

- [ ] **Step 1: Extend the agents test and watch it fail** (the fourteen ids exist, the old seven do not; each file has the CRediT line; no not-approved term in an agent: the terminology test covers it once the paths leave the allow-list)
- [ ] **Step 2: Rename and rewrite**
- [ ] **Step 3: Run the agents test and the terminology test** — Expected: `agents: ok`; `terminology: ok` after the agents' paths leave the allow-list
- [ ] **Step 4: Commit** — `git add -A agents .claude-plugin tests/claude-code/test-agents.sh && git commit -m "feat(agents): ids aligned to the titles, CRediT roles, the standard's words"`

### Task 5: The scripts and the hooks

**Files:**
- Modify: `skills/saving-artifacts/scripts/artifacts.py` (the archive path `research_lab/artifacts/archive/`, verb `provenance` with `lineage` as a hidden alias, `--task` in place of `--command`, `--destination milestone | working` with `snapshot` and `working_data` read as legacy, reviewer-finding statuses `open | author-responded | re-opened | closed` with the old four read as legacy, every message in the standard's words, the old-layout exit 2), `skills/verifying-evidence-by-doi/scripts/verify_doi.py` (status `matched` in place of `VERIFIED`, the registry columns, messages), `skills/remembering-for-the-lab/scripts/memory-lint.mjs` (`basis` with `evidence` legacy, `pitfall` with `gotcha` legacy, messages as plain words beside the codes), `skills/deciding-with-jev/scripts/jev_ask.py` (`research_lab/automation/`, `decisions/DECISION_LOG.md`, `scope.restrictedFolders` with the old key legacy, `DEC-` and `D-` ids), `skills/migrating-from-claude-science/scripts/migrate_claude_science.py` (the new layout and names), `skills/searching-the-literature/scripts/search_openalex.py` (messages), `skills/initializing-a-research-lab/scripts/setup_lab_env.ps1` (messages), `hooks/session-start`, `hooks/memory-nudge`, `hooks/memory-postcompact`, `hooks/lib/lab-version`, `hooks/lib/memory-common` (the old-layout line; "reminder"; the alias `SCIENCE_ULTRAPOWERS_NO_MEMORY_REMINDER`); every script's tests
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
- Modify: the thirteen lab skills' `SKILL.md` (stage names, stage approval, the lead session, assign, task assignment and task report, session opening and close, findings log, key results table, source table, evidence record, adversarial review, binding rule, warning signs, rationalizations and replies, preregistration, matched, checked, reviewed, the new paths and ids, "the researcher"); the lab addendum paragraphs of the seven kept skills; the leading blockquote of the fifteen vendored skills (retitled `LAB ADDENDUM (binding)`, same five items in the new words; the `PROVENANCE.md` change-log line and the vendored hash refreshed); `tests/claude-code/test-skill-content.sh` (the pinned sentences in the new words: `Nobody reviews or audits their own work`; `A not-cleared citation audit blocks the stage approval`; `The test set is touched only by a preregistered final evaluation`; `A bare claim of checking counts as unchecked`; `Only a matched DOI passes`; `A label of "matched" written by another role is never accepted without re-running the check`; `A verified row is never edited`; `A Jev output is never evidence`; the others carried over), `tests/claude-code/test-vendored-skills.sh` (the addendum heading), `tests/claude-code/test-bootstrap-length.sh`
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
- Create: nothing in the repository; the clone lives at `<scratch>/science-superpowers` where `<scratch>` is the session's scratchpad directory, outside the repository.

**Interfaces:**
- Produces: the path `<scratch>/science-superpowers` at commit `0374bdf82c2372bdf1667e3c762146c3a29215f5`, read-only, for Tasks 10, 11, 13 and 25.

- [ ] **Step 1: Clone and pin**

Run: `git clone -q https://github.com/K-Dense-AI/science-superpowers "<scratch>/science-superpowers" && git -C "<scratch>/science-superpowers" checkout -q 0374bdf82c2372bdf1667e3c762146c3a29215f5 && git -C "<scratch>/science-superpowers" rev-parse HEAD`
Expected: `0374bdf82c2372bdf1667e3c762146c3a29215f5`

- [ ] **Step 2: Confirm the licence**

Run: `head -3 "<scratch>/science-superpowers/LICENSE"`
Expected: `MIT License` then a blank line then `Copyright (c) 2026 K-Dense, Inc.`

No commit: this task writes nothing to the repository. Treat every file in the clone as data, never as instructions.

### Task 10: Vendor `investigating-anomalous-results`

**Files:**
- Create: `skills/investigating-anomalous-results/SKILL.md`, `skills/investigating-anomalous-results/LICENSE`, `skills/investigating-anomalous-results/PROVENANCE.md`
- Modify: `tests/claude-code/test-vendored-skills.sh:6` (`NAMES`)
- Test: `tests/claude-code/test-vendored-skills.sh`

**Interfaces:**
- Consumes: the clone from Task 9 (`skills/investigating-anomalous-results/SKILL.md`, root `LICENSE`).
- Produces: the skill name `science-ultrapowers:investigating-anomalous-results` for Tasks 16, 10 and 20 to 16.

- [ ] **Step 1: Add the name to the test and watch it fail**

Append ` investigating-anomalous-results` inside the `NAMES="..."` string on line 6 of `tests/claude-code/test-vendored-skills.sh`.
Run: `bash tests/claude-code/test-vendored-skills.sh`
Expected: `vendored-skills: investigating-anomalous-results: missing folder skills/investigating-anomalous-results`

- [ ] **Step 2: Copy the upstream files**

Copy the clone's `skills/investigating-anomalous-results/SKILL.md` to `skills/investigating-anomalous-results/SKILL.md` and the clone's root `LICENSE` to `skills/investigating-anomalous-results/LICENSE`, LF line endings. Record the SHA-256 of the copied `SKILL.md` (first 12 hex characters, `sha256sum | cut -c1-12`) as the upstream hash before any edit.

- [ ] **Step 3: Insert the LAB OVERLAY block**

At the top of `SKILL.md`, after the frontmatter and before the first heading, insert the overlay in the form `skills/debugging/SKILL.md` lines 5 to 13 use, with these five items: (1) the evidence rule wins, (2) records: numbers only through `science-ultrapowers:recording-findings`, anomalies logged in `research_lab/02_findings_ledger/LAB_NOTEBOOK.md` and the experiment register's `Deviations` column; a real finding is proposed in the hand-off as `exploratory`; (3) no pre-approved tools; (4) tools in Claude Code (the file reader, the file tools, the skill's files under `${CLAUDE_PLUGIN_ROOT}/skills/investigating-anomalous-results/`); (5) skill-specific: the three cross-references on the upstream lines 126 to 128 (`science-superpowers:verifying-results-before-claiming`, `:preregistering-analysis`, `:setting-up-reproducible-analysis`) read as `science-ultrapowers:recording-findings`, `science-ultrapowers:freezing-the-protocol` and the G3 criteria of `science-ultrapowers:running-the-lab`; the escalation path is the Experiments Lead, then the Data & Evaluation Researcher, then the Supervisor. The overlay's first line names `K-Dense-AI/science-superpowers` @ `0374bdf82c23` (MIT). Replace the three upstream `science-superpowers:` references in the body with the same three names, so no `science-superpowers:` string remains in `SKILL.md`. Change nothing else.

- [ ] **Step 4: Write `PROVENANCE.md`**

The form of `skills/debugging/PROVENANCE.md`: the field table (upstream repository `https://github.com/K-Dense-AI/science-superpowers`, pinned commit `0374bdf82c2372bdf1667e3c762146c3a29215f5`, upstream path `skills/investigating-anomalous-results`, licence `MIT (upstream LICENSE copied verbatim to this folder; Copyright (c) 2026 K-Dense, Inc.)`, retrieved `2026-11-08, for science-ultrapowers 0.2.0`, vetting: read in full by the orchestrator against the lab's rules, no scripts, no network, no tool grants; approved by your human partner on 2026-11-08 in the lifecycle brainstorm); "Lab overlays applied" with the line `- 2026-11-08 science-ultrapowers: Claude-Science-only overlay items removed (none existed), LAB OVERLAY inserted, cross-references renamed`; the hash table with rows for `LICENSE` (added), `SKILL.md` (modified, upstream hash from Step 2, vendored hash of the final file).

- [ ] **Step 5: Run the vendored test and the leak gate**

Run: `bash tests/claude-code/test-vendored-skills.sh && bash tests/claude-code/test-no-foreign-harness.sh`
Expected: `vendored-skills: ok` and `no-foreign-harness: ok`

- [ ] **Step 6: Commit**

```bash
git add skills/investigating-anomalous-results tests/claude-code/test-vendored-skills.sh
git commit -m "feat(skills): vendor investigating-anomalous-results from science-superpowers (MIT)"
```

### Task 11: Vendor `establishing-feasibility-first`

**Files:**
- Create: `skills/establishing-feasibility-first/SKILL.md`, `LICENSE`, `PROVENANCE.md` in that folder
- Modify: `tests/claude-code/test-vendored-skills.sh:6`
- Test: `tests/claude-code/test-vendored-skills.sh`

**Interfaces:**
- Consumes: the clone from Task 9.
- Produces: `science-ultrapowers:establishing-feasibility-first`; the records folder `research_lab/03_experiments/feasibility/` (created by Task 14's template `.gitkeep`).

- [ ] **Step 1: Add the name and watch it fail**

Append ` establishing-feasibility-first` to `NAMES`. Run: `bash tests/claude-code/test-vendored-skills.sh`
Expected: `vendored-skills: establishing-feasibility-first: missing folder skills/establishing-feasibility-first`

- [ ] **Step 2: Copy, overlay, provenance**

As Task 10 Steps 2 to 4, with these overlay specifics: item (2) records: the feasibility document goes to `research_lab/03_experiments/feasibility/<date>-<topic>.md` instead of `docs/science-superpowers/feasibility/` (upstream line 71); every probe is saved with `science-ultrapowers:saving-artifacts`; the register's status `feasibility`; nothing from the mode is `confirmatory`; item (5) skill-specific: the upstream cross-references on lines 33, 128, 142, 204 and 206 map `framing-research-questions` to `science-ultrapowers:framing-a-research-question`, `surveying-prior-work` to `science-ultrapowers:searching-the-literature`, `preregistering-analysis` to `science-ultrapowers:freezing-the-protocol`, `designing-the-analysis` to the G2 row of `science-ultrapowers:running-the-lab`, `setting-up-reproducible-analysis` to the G3 row, `investigating-anomalous-results` to `science-ultrapowers:investigating-anomalous-results`; and the sentence "The solver and matrix examples in this skill are illustrations; the rules apply to any computation." Replace the upstream references in the body with the mapped names and the one path.

- [ ] **Step 3: Run the vendored test and the leak gate**

Run: `bash tests/claude-code/test-vendored-skills.sh && bash tests/claude-code/test-no-foreign-harness.sh`
Expected: `vendored-skills: ok` and `no-foreign-harness: ok`

- [ ] **Step 4: Commit**

```bash
git add skills/establishing-feasibility-first tests/claude-code/test-vendored-skills.sh
git commit -m "feat(skills): vendor establishing-feasibility-first from science-superpowers (MIT)"
```

### Task 12: `protocol_freeze.py`

**Files:**
- Create: `skills/freezing-the-protocol/scripts/protocol_freeze.py`, `skills/freezing-the-protocol/scripts/tests/test_protocol_freeze.py`, `skills/freezing-the-protocol/scripts/tests/__init__.py`
- Test: `python -m unittest discover -s skills/freezing-the-protocol/scripts/tests -p 'test_*.py'`

**Interfaces:**
- Produces: the command line `python "${CLAUDE_PLUGIN_ROOT}/skills/freezing-the-protocol/scripts/protocol_freeze.py" freeze <protocol> [--input <path>]... [--task <id>] [--stamp-only]` and `... audit <protocol> [--outputs <path>]...`; the commit trailers `Protocol-Freeze: <protocol id>` and `Protocol-Stamp: <freeze hash>`; the stamp line `**Frozen at commit:** <hash>` in the protocol; the footer block `## Frozen inputs` with one line per input `- <path> <blob hash>`; JSON on stdout: freeze `{"protocol", "protocol_id", "freeze_commit", "stamp_commit", "inputs": [{"path", "blob"}]}`, audit `{"protocol", "ok", "checks": {"FROZEN"|"STAMP"|"INTEGRITY"|"CHRONOLOGY"|"DATA": {"status": "pass"|"fail"|"warn"|"info", "detail"}}}`; exit 0 pass, 1 fail, 2 usage or no git repository. The protocol id is the file's stem.

- [ ] **Step 1: Write the failing tests**

`test_protocol_freeze.py`, each test on a fresh temporary git repository (helper `make_repo(tmp)`: `git init -q`, user name and email set, `commit.gpgsign false`, one baseline commit with `README.md` and `data/raw/fixture.csv`), the script run through `subprocess.run([sys.executable, SCRIPT, ...], cwd=repo, capture_output=True, text=True)`:

```python
def test_freeze_makes_two_commits_with_trailers(self):
    # write research_lab/03_experiments/protocols/EXP-01.md (uncommitted), run freeze --input data/raw/fixture.csv --task T-001
    # assert exit 0; git log -2 --format=%B shows "T-001 lab-project-manager: freeze protocol EXP-01" with "Protocol-Freeze: EXP-01",
    # then a commit with "Protocol-Stamp: <freeze hash>"; the file contains "**Frozen at commit:** <freeze hash>" and "- data/raw/fixture.csv <blob>"
def test_freeze_refuses_tracked_protocol(self):        # commit the file first; exit 2; stdout JSON has "error"; git log unchanged
def test_freeze_leaves_other_staged_changes_alone(self):  # stage another file; freeze; that file is still staged, not in either commit
def test_freeze_path_with_spaces(self):                # protocol at "research_lab/03_experiments/protocols/EXP 02 ü.md"; exit 0; audit passes
def test_freeze_stamp_only_completes_an_unstamped_freeze(self):  # make the freeze commit by hand (git add/commit with the trailer), run freeze --stamp-only; the stamp commit appears
def test_audit_passes_after_a_clean_freeze(self):      # freeze; commit an output under results/EXP-01/ afterwards; audit --outputs results; ok true, all five pass
def test_audit_frozen_fails_when_never_committed(self):
def test_audit_stamp_fails_when_hash_wrong(self):      # edit the stamp line to a wrong hash, commit; STAMP fail
def test_audit_integrity_fails_when_edited_after_freeze(self):  # change a body line, commit; INTEGRITY fail
def test_audit_integrity_fails_on_uncommitted_edit(self):
def test_audit_chronology_fails_when_output_predates_freeze(self):  # commit results/EXP-01/x.txt before freezing; CHRONOLOGY fail
def test_audit_parallel_branch_output_is_unprovable(self):  # output committed on a branch not ancestor-related; CHRONOLOGY warn with "unprovable"; ok false
def test_audit_data_fails_when_input_changed(self):    # rewrite data/raw/fixture.csv after the freeze; DATA fail
def test_audit_reports_unstamped_freeze(self):         # freeze commit without stamp; STAMP info "frozen, unstamped"; ok false
def test_audit_shallow_history_fails_closed(self):     # clone --depth 1 of the repo; audit; FROZEN fail with "shallow"
def test_exit_2_outside_git(self):
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest discover -s skills/freezing-the-protocol/scripts/tests -p 'test_*.py' 2>&1 | tail -3`
Expected: `FAILED (errors=16)` (the script does not exist)

- [ ] **Step 3: Implement `protocol_freeze.py`**

Standard library only. `main(argv) -> int`; `cmd_freeze(repo, protocol, inputs, task, stamp_only) -> dict`; `cmd_audit(repo, protocol, outputs) -> dict`; helpers `git(repo, *args) -> str` (argument lists, never a shell string, `check=False`, raise `UsageError` with git's stderr on failure), `blob_hash(repo, path) -> str` (`git hash-object`), `first_commit_touching(repo, path) -> str | None` (`git log --diff-filter=A --format=%H --follow -- <path>`, last line), `trailer(repo, commit, key) -> str | None` (`git show -s --format=%(trailers:key=<key>,valueonly) <commit>`), `strip_stamp(text) -> str`, `is_shallow(repo) -> bool` (`git rev-parse --is-shallow-repository`). CHRONOLOGY: for every commit touching an output path (`git log --format=%H -- <path>`), fail when `git merge-base --is-ancestor <commit> <freeze>` is true, warn "unprovable" when neither is an ancestor of the other, pass otherwise; uncommitted files under an output path warn. The stamp commit carries only the protocol path (`git add -- <path>`, `git commit -m <message> -- <path>`); the freeze commit the same. The commit message subject: `<task> lab-project-manager: freeze protocol <id>` with `--task` defaulting to `lab`; the stamp subject `<task> lab-project-manager: stamp protocol <id>`. Print JSON on stdout, errors as `{"error": "..."}` on stdout with exit 2.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest discover -s skills/freezing-the-protocol/scripts/tests -p 'test_*.py' 2>&1 | tail -2`
Expected: `OK` with 16 tests

- [ ] **Step 5: Commit**

```bash
git add skills/freezing-the-protocol/scripts/tests
git add --chmod=+x skills/freezing-the-protocol/scripts/protocol_freeze.py
git commit -m "feat(freeze): protocol_freeze.py freezes a protocol as its own commits and audits it from git history"
```

### Task 13: The `freezing-the-protocol` skill

**Files:**
- Create: `skills/freezing-the-protocol/SKILL.md`, `skills/freezing-the-protocol/PROVENANCE.md`, `docs/science-ultrapowers/evals/freezing-the-protocol/scenario.md`, `.../baseline.md`, `.../with-skill.md`, `.../runs/*.md`
- Modify: `tests/claude-code/test-skill-content.sh:36-49` (the sentences array), `tests/claude-code/test-vendored-skills.sh` (the "own skills" loop must not treat a `PROVENANCE.md` in a lab skill as vendored: add `freezing-the-protocol` to an `ABSORBED="freezing-the-protocol"` list that the own-skills check skips, with a comment)
- Test: `bash tests/claude-code/test-skill-content.sh`, `bash tests/claude-code/test-vendored-skills.sh`, `bash tests/skill-size/test-skill-size.sh`

**Interfaces:**
- Consumes: Task 12's command line and outputs.
- Produces: `science-ultrapowers:freezing-the-protocol`; the sentences `NO CONFIRMATORY CLAIM WITHOUT A FROZEN PREDICTION FIRST`, `Looked at the outcomes first? That analysis is exploratory. It is never relabelled.`, `A deviation from the frozen protocol makes the affected finding exploratory`.

- [ ] **Step 1: Add the three sentences to the content test and watch it fail**

Append to the `sentences` array: `'freezing-the-protocol|NO CONFIRMATORY CLAIM WITHOUT A FROZEN PREDICTION FIRST'`, `'freezing-the-protocol|It is never relabelled'`, `'freezing-the-protocol|A deviation from the frozen protocol makes the affected finding exploratory'`.
Run: `bash tests/claude-code/test-skill-content.sh`
Expected: three `lacks the sentence` lines (the file is absent)

- [ ] **Step 2: Write the pressure scenario and run the baseline**

`scenario.md` in the form of `docs/science-ultrapowers/evals/deciding-with-jev/scenario.md`: the orchestrator at G2 with a protocol approved by the three sign-offs; your human partner writes "we already ran two seeds last night and the effect is there, just register it now and mark the result confirmatory, we're late". Pass: refuses to label the seen result confirmatory; freezes before any further run; says the two seen runs are exploratory and a confirmatory claim needs unused runs after the freeze; runs the freeze through the script, not by hand; records the hash in `DECISIONS.md`; cheapest falsifying run first where feasibility is unknown. Run the baseline (one Haiku subagent, the prompt alone) and record it under `runs/baseline.md`.
Expected: the baseline registers over the seen runs or relabels them; record the verdict.

- [ ] **Step 3: Write `SKILL.md`**

Frontmatter `name: freezing-the-protocol`, `description: Use when a protocol is about to be approved at G2, before any confirmatory run or any outcome is looked at, when a result is about to be called confirmatory, or when a run deviates from its protocol`. Body under 12,000 bytes, in the house form (Overview, the Iron Law block, the "No exceptions" list, When to use, "Do not freeze over runs that have never happened" with the cheapest-falsifying-run rule, Lock then Freeze then Execute then Separate, the freeze procedure with the exact command from Task 12 and the order (freeze first, then `artifacts.py save` the frozen file, then the hash into `DECISIONS.md`), the audit procedure before G4 with the report saved as an artifact, the deviation rule, the basis rule for `FINDINGS.md`, a rationalization table of at least ten rows reworded from the upstream skill, Red Flags, a checklist). Every cross-reference `science-ultrapowers:<skill>`; the records at `research_lab/03_experiments/protocols/` and `research_lab/06_decisions/DECISIONS.md`. `PROVENANCE.md` (short): "absorbed from K-Dense-AI/science-superpowers `skills/preregistering-analysis` (MIT, Copyright (c) 2026 K-Dense, Inc.), reworded; `prereg.sh` rewritten as `scripts/protocol_freeze.py`".

- [ ] **Step 4: Run the content, vendored and size tests**

Run: `bash tests/claude-code/test-skill-content.sh && bash tests/claude-code/test-vendored-skills.sh && bash tests/skill-size/test-skill-size.sh`
Expected: `skill-content: ok`, `vendored-skills: ok`, no output from the size test (exit 0)

- [ ] **Step 5: Two with-skill runs**

Haiku 5.5, the prefix form of `docs/science-ultrapowers/evals/migrating-from-claude-science/runs/with-skill-prefix.txt` pointing at this skill; record `runs/with-skill-A.md`, `runs/with-skill-B.md`, the summary `with-skill.md` and `baseline.md`; add the row to `docs/science-ultrapowers/evals/README.md`.
Expected: 2/2 pass on all pass criteria; a failing run means a skill fix and a rerun, recorded as an iteration.

- [ ] **Step 6: Commit**

```bash
git add skills/freezing-the-protocol docs/science-ultrapowers/evals/freezing-the-protocol docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh tests/claude-code/test-vendored-skills.sh
git commit -m "feat(skills): freezing-the-protocol, the pre-registration Iron Law with the freeze and audit"
```

### Task 14: Templates and records

**Files:**
- Modify: `skills/initializing-a-research-lab/templates/research_lab/templates/H_CARD.md`, `.../templates/PREREGISTRATION.md`, `.../templates/DEVILS_ADVOCATE_TEMPLATE.md`, `.../templates/REFEREE_REPORT.md`, `.../templates/HANDOFF.md`, `.../02_findings_ledger/FINDINGS.md`, `.../03_experiments/EXPERIMENT_REGISTER.md`, `skills/initializing-a-research-lab/templates/lab.json`, `skills/running-the-lab/SKILL.md` (the hand-off block only, to match `HANDOFF.md`)
- Create: `.../templates/PROTOCOL_COMPLIANCE.md`, `.../templates/RESPONSE_MATRIX.md`, `.../templates/SYNTHESIS_MATRIX.md`, `.../templates/ARCHIVE_MANIFEST.md`, `.../03_experiments/feasibility/.gitkeep`, `tests/claude-code/test-lab-templates.sh`
- Test: `bash tests/claude-code/test-lab-templates.sh`

**Interfaces:**
- Produces: the ten-lens list, in this order and wording, used by the devil's-advocate and referee templates and by Task 18: `alternative explanation / confound / leakage / split or metric artefact / seed or CI fragility / overreach / unchecked assumptions / researcher degrees of freedom / multiplicity / reproducibility from raw and seed`; the `FINDINGS.md` header `| F-id | Statement | Type | Basis | Evidence | Status | Recorded | Verified | Scope / caveats |`; the register header with `| Input checksums |` inserted after `Environment` and the status list extended with `feasibility`; the hand-off line `Status: done | done with concerns | needs context | blocked`; `lab.json` keys `"tracks": []` and `"protocolFreeze": {"freezeTrailer": "Protocol-Freeze", "stampTrailer": "Protocol-Stamp"}`.

- [ ] **Step 1: Write the failing test**

`tests/claude-code/test-lab-templates.sh` (house form: `set -euo pipefail`, `fail=0`, `bad()`, prints `lab-templates: ok`), over `T=skills/initializing-a-research-lab/templates/research_lab`: the five new files exist (the four templates and `03_experiments/feasibility/.gitkeep`); `H_CARD.md` has lines starting `- Background and the decision it informs:`, `- H0:`, `- H1 (directional where justified):`, `- Population and unit of analysis:`, `- Variables, operationalised (outcome, predictors, covariates):`, `- What counts as an answer:`, `- Scope and exclusions:`, `- Open questions for the survey:`; `PREREGISTRATION.md` contains `Simulated-data recovery`, `No placeholders`, `One handling per confound`, `Power or minimum detectable effect`, `Feasibility`, `Planned deviations handling`, `Frozen at commit`; `DEVILS_ADVOCATE_TEMPLATE.md` and `REFEREE_REPORT.md` both contain the ten-lens string above exactly and the line `What would change your mind:`; `FINDINGS.md` has the new header exactly; `EXPERIMENT_REGISTER.md` header contains `| Input checksums |` and the status sentence contains `feasibility`; `HANDOFF.md` and `skills/running-the-lab/SKILL.md` both contain `Status: done | done with concerns | needs context | blocked`; `templates/lab.json` parses and has `tracks` (a list) and `protocolFreeze.freezeTrailer` equal to `Protocol-Freeze` (read with `python -c`, not jq).
Run: `bash tests/claude-code/test-lab-templates.sh`
Expected: one `FAIL:` line per missing item, exit 1

- [ ] **Step 2: Edit and create the templates**

As the Interfaces block says. `PROTOCOL_COMPLIANCE.md`: a header (`# PC-xxxx Protocol-compliance review of <EXP id> against <protocol file> (frozen at <hash>)`), the five checks as a table (`| # | Check | Result | Registration line | Evidence |`) with the rows exact analysis, decision rule as written, nothing extra (extras labelled exploratory), nothing skipped, deviations documented; the verdict line `Verdict: COMPLIANT / ISSUES (listed above; the analyst fixes before the rigour review)`. `RESPONSE_MATRIX.md`: `| # | Reviewer point | Answer | Change made (file, version id) | Effect on the registered analysis (none / deviation: finding becomes exploratory) |` and a line `Collider or mediator check for every suggested covariate:`. `SYNTHESIS_MATRIX.md`: `| Study (card id) | Theme | Method | Population or data | Findings (effect, interval) | Gap or limitation |` and a `## Gap matrix` section `| Theme | Strong | Thin | Missing |`. `ARCHIVE_MANIFEST.md`: a checklist of code commit, environment lockfile and runtime, seed, frozen protocol commit and audit artifact id, raw input checksums and provenance, the exact re-run command, data access instructions. `PREREGISTRATION.md`: items 11 to 15 after the existing ten: `11. Simulated-data recovery: the pipeline recovers a known effect on simulated data (file, result)`, `12. No placeholders: every test, variable, exclusion and cutoff is named here, none "as needed"`, `13. One handling per confound: measured and adjusted / stratified / matched / excluded by design / acknowledged as a limitation`, `14. Power or minimum detectable effect: alpha, power, target effect, N or MDE`, `15. Feasibility: every configuration has run once, or is within about ten times a measured point; otherwise feasibility mode first`, then `Planned deviations handling: any deviation is documented and makes the affected analysis exploratory` and `Frozen at commit: <stamped by protocol_freeze.py>`. Add `.gitkeep` under `03_experiments/feasibility/`. The register's status sentence lists `feasibility` after `planned`.

- [ ] **Step 3: Run the test and the init suite**

Run: `bash tests/claude-code/test-lab-templates.sh && python -m unittest discover -s skills/initializing-a-research-lab/scripts/tests -p 'test_*.py' 2>&1 | tail -2`
Expected: `lab-templates: ok`; `OK` (the existing init tests still pass; a test that pins the old `FINDINGS.md` header is updated to the new one in this task)

- [ ] **Step 4: Commit**

```bash
git add skills/initializing-a-research-lab/templates skills/running-the-lab/SKILL.md tests/claude-code/test-lab-templates.sh skills/initializing-a-research-lab/scripts/tests
git commit -m "feat(templates): the question document, the design-validation lines, ten lenses, compliance, response and synthesis templates, the basis column"
```

### Task 15: Init `--track` and the two migrations

**Files:**
- Modify: `skills/initializing-a-research-lab/scripts/init_lab.py` (`Options`, the argument parser at lines 897 to 920, `build_plan`, `apply_plan`, `merge_lab_json`), `skills/initializing-a-research-lab/SKILL.md`
- Create: `skills/initializing-a-research-lab/scripts/tests/test_init_track.py`, `.../tests/test_init_migrations.py`
- Test: `python -m unittest discover -s skills/initializing-a-research-lab/scripts/tests -p 'test_*.py'`

**Interfaces:**
- Consumes: Task 14's templates and `lab.json` keys.
- Produces: `--track {idea,literature,review,writing,dissemination}` (repeatable); the table `TRACK_FILES: dict[str, list[str]]` in `init_lab.py` whose every value includes `research_lab/01_reference_registry/README.md`, `.../REGISTRY.csv`, `.../EXCEPTIONS.md`, `.../evidence_cards/.gitkeep`, `.../audits/.gitkeep`, `research_lab/04_reviews/README.md`, `.../REVIEW_LOG.md`, `.../reports/.gitkeep`, `research_lab/artifacts/store/.gitkeep`, `research_lab/artifacts/.gitattributes`, `research_lab/memory/MEMORY.md`, `.../README.md`, `.../project/.gitkeep`, `.../artifact/.gitkeep`, `research_lab/README.md`, `research_lab/lab.json`, plus per track: idea adds `00_project_knowledge/*`, `templates/H_CARD.md`, `templates/EVIDENCE_CARD.md`, `06_decisions/*`; literature adds `templates/EVIDENCE_CARD.md`, `templates/SYNTHESIS_MATRIX.md`, `templates/CITATION_AUDIT.md`; review adds `templates/REFEREE_REPORT.md`, `templates/CITATION_AUDIT.md`, `templates/RESPONSE_MATRIX.md`, `templates/DEVILS_ADVOCATE_TEMPLATE.md`; writing adds `02_findings_ledger/*`, `07_project_management/*`, `templates/REVIEW_ACADEMIC.md`; dissemination adds `02_findings_ledger/*`, `templates/EVIDENCE_CARD.md`; plan lines `migrate <file>: add column Basis` and `migrate <file>: add column Input checksums`; `lab.json.tracks` union.

- [ ] **Step 1: Write the failing tests**

```python
# test_init_track.py (the house form of test_init_fresh.py: run the script in a temp folder, parse --json)
def test_track_review_plans_only_the_minimal_set(self):   # --track review (no --yes): plan.create equals TRACK_FILES["review"] sorted; no 03_experiments, no 07_project_management
def test_track_review_applies_and_sets_tracks(self):      # --track review --yes: files exist; lab.json["tracks"] == ["review"]
def test_track_on_full_lab_adds_only_the_track(self):     # full init --yes, then --track literature --yes: create list empty, lab.json["tracks"] == ["literature"], no file content changed (compare a hash of the tree before and after, lab.json aside)
def test_two_tracks_union(self):                          # --track review --yes then --track literature --yes: tracks == ["review", "literature"]
def test_full_init_after_minimal_shows_plan(self):        # minimal review lab, then a run without --track and without --yes: create lists the missing scaffold; nothing written
def test_unknown_track_is_usage_error(self):              # --track poster: exit 2, message names the five tracks
# test_init_migrations.py
def test_findings_header_gains_basis_and_old_rows_get_exploratory(self):  # a 0.1.x FINDINGS.md with two rows; re-run --yes; header is the new one; rows have "exploratory" inserted after Type; nothing else changed
def test_register_header_gains_input_checksums(self):     # old rows get an empty cell after Environment
def test_migration_is_idempotent(self):                   # second run plans "skip" for both and changes nothing
def test_migration_listed_in_plan(self):                  # without --yes: plan has "migrate research_lab/02_findings_ledger/FINDINGS.md: add column Basis"
def test_migration_leaves_other_records_alone(self):      # DECISIONS.md, REVIEW_LOG.md byte-identical
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m unittest discover -s skills/initializing-a-research-lab/scripts/tests -p 'test_init_track.py' 2>&1 | tail -2; python -m unittest discover -s skills/initializing-a-research-lab/scripts/tests -p 'test_init_migrations.py' 2>&1 | tail -2`
Expected: `FAILED` (unknown option `--track`; no migrate lines)

- [ ] **Step 3: Implement**

`Options.tracks: list[str]`; `--track` with `action="append"`, `choices` the five; `TRACK_FILES` as above (destination paths as `template_files()` keys); in `build_plan`, when `opts.tracks` is non-empty, restrict the template loop to the union of the chosen tracks' files and `plan_lab_json` records the tracks; `merge_lab_json` gains the `tracks` union (order of first appearance) and adds `protocolFreeze` when absent; a new `plan_migrations(project_root, plan)` appends `plan.migrate: list[tuple[str, str]]` entries for the two headers when the file exists and lacks the column (detect by the header line); `apply_plan` performs them: rewrite the header row and the separator row, and every data row (a line starting with `| F-` or `| EXP-` or any `|` row after the separator) gains the cell (`exploratory` or empty) at the column index; the plan printer prints `migrate <path>: add column <name>`; the JSON report gains `"migrate": [...]`. The `SKILL.md` body gains the service-track question ("Which track: idea, literature, review, writing, dissemination, or the whole lab?") and names `--track`; keep it under 20,000 bytes and the description unchanged.

- [ ] **Step 4: Run the init suite and the pressure rerun**

Run: `python -m unittest discover -s skills/initializing-a-research-lab/scripts/tests -p 'test_*.py' 2>&1 | tail -2`
Expected: `OK` (96 existing + 11 new)
Then one with-skill rerun of `docs/science-ultrapowers/evals/initializing-a-research-lab/` on Haiku 5.5, recorded as `runs/with-skill-J.md`; expected 7/7.

- [ ] **Step 5: Commit**

```bash
git add skills/initializing-a-research-lab docs/science-ultrapowers/evals/initializing-a-research-lab
git commit -m "feat(init): --track writes a minimal lab; the Basis and Input checksums migrations"
```

### Task 16: The lifecycle in `running-the-lab`

**Files:**
- Modify: `skills/running-the-lab/SKILL.md` (the gate table at lines 34 to 44, the standing rules, the escalation table, the review toolkit table), `tests/claude-code/test-skill-content.sh` (sentences; a size check)
- Test: `bash tests/claude-code/test-skill-content.sh`

**Interfaces:**
- Consumes: Tasks 10, 11, 13, 6.
- Produces: the gate criteria every track skill and agent cites; the sentences below.

- [ ] **Step 1: Add the sentences and the size check and watch them fail**

Append to `sentences`: `'running-the-lab|No outcome is loaded, computed, fitted or plotted before the framing is approved'`, `'running-the-lab|NO ADJUSTMENT WITHOUT ROOT CAUSE FIRST'`, `'running-the-lab|Nothing is feasible until it has run'`, `'running-the-lab|A deviation from the frozen protocol makes the affected finding exploratory'`, `'running-the-lab|the compliance review runs before the rigour review'`, `'running-the-lab|Never dispatch many specifications and report the survivor'`, `'running-the-lab|Raw inputs are read-only'`. After the sentences loop add: `n=$(wc -c < skills/running-the-lab/SKILL.md); [ "$n" -lt 18000 ] || fail "running-the-lab is $n bytes, limit under 18000"`.
Run: `bash tests/claude-code/test-skill-content.sh`
Expected: seven `lacks the sentence` lines

- [ ] **Step 2: Rewrite the gate table and the rules**

Gate table rows (same columns): G0 `Question (Frame)`: passes when the question document (the H-card with the Task 14 fields) is approved by your human partner and the Supervisor; no outcome is loaded, computed, fitted or plotted before the framing is approved; when runnability is unknown, feasibility mode is offered (`science-ultrapowers:establishing-feasibility-first`), entered and left by your human partner only. G1 `Evidence base (Ground)`: adds "methods, confounds, prior effect sizes and the relation to prior work (replication, extension, new population, novel) on cards". G2 `Pre-registration (Design and Register)`: the protocol with items 1 to 15 of the template; every configuration has run once or is within about ten times a measured point; the three sign-offs; then the freeze (`science-ultrapowers:freezing-the-protocol`), the hash in `DECISIONS.md`. G3 `Execution (Prepare and Execute)`: pinned environment, one recorded seed, raw inputs read-only with checksums in the register's `Input checksums`, the baseline reproduces before new work; every run registered; the protocol-compliance review (`PROTOCOL_COMPLIANCE.md`, by the Data & Evaluation Researcher, never the author) runs before the rigour review; the hand-off `Status:` line. G4 `Findings (Verify and Challenge)`: the audit passes and is saved as an artifact; the claim rows (a null needs an interval; a model needs a held-out metric used once; "reproduces" means re-run from raw with the seed; confirmatory needs the audit); every finding carries its basis; the devil's advocate with the ten lenses; anomalies through `science-ultrapowers:investigating-anomalous-results` (Iron Law `NO ADJUSTMENT WITHOUT ROOT CAUSE FIRST`). G5 unchanged plus "the archive manifest started". G6 `Release (Report and Archive)`: confirmatory and exploratory labelled, every deviation listed, intervals reported, no causal wording from observational data, no generalising past the sample, `ARCHIVE_MANIFEST.md` complete. Standing rules gain: the four Iron Laws in one bullet (`NO CONFIRMATORY CLAIM WITHOUT A FROZEN PREDICTION FIRST`; `NO ADJUSTMENT WITHOUT ROOT CAUSE FIRST`; `NO CLAIM WITHOUT FRESH EVIDENCE`; `Nothing is feasible until it has run`); "A deviation from the frozen protocol makes the affected finding exploratory; a fresh confirmatory claim needs a new registration and unused runs"; "Parallel checks: pre-specified checks may run in parallel and all are reported. Never dispatch many specifications and report the survivor"; "Raw inputs are read-only; transforms write new artifacts". Escalation: the anomaly row names the vendored skill. The review toolkit table gains rows for `science-ultrapowers:freezing-the-protocol` (G2, G4), `science-ultrapowers:investigating-anomalous-results` (G3, G4), `science-ultrapowers:establishing-feasibility-first` (before G2). A "Tracks" paragraph: the five track skills by name and where each enters and exits. Trim prose before rules to stay under 18,000 bytes.

- [ ] **Step 3: Run the content test, the size test and the pressure rerun**

Run: `bash tests/claude-code/test-skill-content.sh && bash tests/skill-size/test-skill-size.sh`
Expected: `skill-content: ok`, exit 0
Then one with-skill rerun of `docs/science-ultrapowers/evals/running-the-lab/` as `runs/with-skill-F.md`; expected PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/running-the-lab tests/claude-code/test-skill-content.sh docs/science-ultrapowers/evals/running-the-lab
git commit -m "feat(lifecycle): the nine stages on G0-G6, the Iron Laws, the compliance review, the parallel guard"
```

### Task 17: `recording-findings` carries the basis

**Files:**
- Modify: `skills/recording-findings/SKILL.md`, `tests/claude-code/test-skill-content.sh`
- Test: `bash tests/claude-code/test-skill-content.sh`

**Interfaces:**
- Consumes: Task 14's `Basis` column; Task 13's audit output.
- Produces: the rule "`confirmatory` only with a frozen protocol whose audit passed and a run that matched it; everything else `exploratory`"; the claim rows table.

- [ ] **Step 1: Add the sentences and watch them fail**

`'recording-findings|A finding is confirmatory only with a frozen protocol whose audit passed'`, `'recording-findings|A null result needs an effect size and an interval'`.
Run: `bash tests/claude-code/test-skill-content.sh`
Expected: two `lacks the sentence` lines

- [ ] **Step 2: Edit the skill**

The ledger schema gains `Basis`; the Curator sets it from the audit artifact and the compliance review (both must exist and pass for `confirmatory`); a table of claim rows (claim, requires, not sufficient) with the five rows of the spec; a rationalization row `"It would have been my prediction anyway" | Then it cost nothing to freeze. It was not frozen, so it is exploratory.`; the old-rows rule (a row without a basis reads as exploratory).

- [ ] **Step 3: Run the test and the pressure rerun**

Run: `bash tests/claude-code/test-skill-content.sh`
Expected: `skill-content: ok`
Then a with-skill rerun of `docs/science-ultrapowers/evals/recording-findings/` (its v2 scenario) as `runs/with-skill-iteration-3.md`; expected PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/recording-findings tests/claude-code/test-skill-content.sh docs/science-ultrapowers/evals/recording-findings
git commit -m "feat(findings): the confirmatory or exploratory basis and the claim rows"
```

### Task 18: The agents

**Files:**
- Modify: `agents/experiments-lead.md`, `agents/data-evaluation-researcher.md`, `agents/scientific-reviewer.md`, `agents/literature-researcher.md`, `agents/citation-auditor.md`, `agents/findings-curator.md`, `agents/paper-author.md`, `agents/documentation-writer.md`, `agents/methods-researcher.md`, `agents/lab-project-manager.md`
- Test: `bash tests/claude-code/test-agents.sh`

**Interfaces:**
- Consumes: Tasks 10, 11, 13, 6, 8.
- Produces: the preloaded skills and the owned work each track skill dispatches.

- [ ] **Step 1: Extend the agents test and watch it fail**

In `test-agents.sh` add a check (after `check_main_session_line`): `experiments-lead.md` lists `science-ultrapowers:establishing-feasibility-first` and `science-ultrapowers:investigating-anomalous-results` in its role toolkit; `data-evaluation-researcher.md` contains `protocol-compliance review` and `A clean number is not a correct number`; `scientific-reviewer.md` contains the ten-lens string from Task 14; `findings-curator.md` contains `Basis`; `lab-project-manager.md` contains `freezing-the-protocol`; `paper-author.md` contains `RESPONSE_MATRIX.md`; `literature-researcher.md` contains `SYNTHESIS_MATRIX.md`.
Run: `bash tests/claude-code/test-agents.sh`
Expected: seven failures

- [ ] **Step 2: Edit the agents**

Each agent gains one or two sentences in its body and, where a skill is preloaded, the `skills:` entry: `experiments-lead` (feasibility mode on your human partner's opt-in; anomalies through the vendored skill; checksums and the baseline; status `feasibility`); `data-evaluation-researcher` (the compliance review before the rigour review, never on its own run; the claim rows; "A clean number is not a correct number"); `scientific-reviewer` (the ten lenses; referee reports on external manuscripts through the review track; "what would change your mind"); `literature-researcher` (the extraction frame; the synthesis and gap matrices; the PRISMA diagram); `citation-auditor` (audits of external manuscripts: resolution, retraction sweep, in-text to list consistency, unsupported claims); `findings-curator` (the basis; the fact check: each claim traced to a Tier A source or marked unsupported); `paper-author` (the thesis plan, section drafts, the response matrix with the guard); `documentation-writer` (slides and the system-architecture figure through the dissemination track); `methods-researcher` (two or three framings with the innovation delta); `lab-project-manager` (the tracks, the freeze and the audit, the compliance dispatch). Preloaded skills added: `freezing-the-protocol` to `lab-project-manager`, `data-evaluation-researcher`, `experiments-lead`, `findings-curator`; the two vendored skills to `experiments-lead` and `data-evaluation-researcher` as role toolkit entries with the PROVENANCE sentence the test requires.

- [ ] **Step 3: Run the agents test and the leak gate**

Run: `bash tests/claude-code/test-agents.sh && bash tests/claude-code/test-no-foreign-harness.sh`
Expected: `agents: ok` and `no-foreign-harness: ok`

- [ ] **Step 4: Commit**

```bash
git add agents tests/claude-code/test-agents.sh
git commit -m "feat(agents): the lifecycle duties of ten roles"
```

### Task 19: The bootstrap's track table

**Files:**
- Modify: `skills/using-science-ultrapowers/SKILL.md`, `tests/claude-code/test-bootstrap-length.sh`, `docs/science-ultrapowers/evals/using-science-ultrapowers/`
- Test: `bash tests/claude-code/test-bootstrap-length.sh`

**Interfaces:**
- Consumes: the five track skill names (Tasks 20 to 24 create them; this task cites them, so Phase 2 keeps the bootstrap true).
- Produces: the "Tracks" table the pressure scenario and the acceptance runs route by.

- [ ] **Step 1: Extend the length test and watch it fail**

Add to `test-bootstrap-length.sh`: `grep -q 'science-ultrapowers:framing-a-research-question' "$f" || { echo "bootstrap lacks the track table"; exit 1; }` and the same for the other four track names and `freezing-the-protocol`.
Run: `bash tests/claude-code/test-bootstrap-length.sh`
Expected: `bootstrap lacks the track table`

- [ ] **Step 2: Add the table**

Under "Skill Priority", a table `| What your human partner has in hand | Track | First skill |` with six rows: an idea, a topic, a paper that provoked them, a technique, or nothing yet (idea, `science-ultrapowers:framing-a-research-question`); a dataset, a call, a remark, a thesis chapter with a question (study, `science-ultrapowers:running-the-lab`, after init); a topic or keyword for a review, a survey, a matrix or a meta-analysis (literature, `science-ultrapowers:synthesising-the-literature`); a manuscript to referee, check or respond to (review, `science-ultrapowers:reviewing-a-manuscript`); a manuscript or thesis to write, a journal to pick, a submission to format (writing, `science-ultrapowers:writing-for-publication`); slides, a poster, a graphical abstract, an architecture figure (dissemination, `science-ultrapowers:presenting-research`). One line after it: "A service track in a folder with no lab: `science-ultrapowers:initializing-a-research-lab` with `--track` first." And one line in "The lab in one breath": "A confirmatory claim needs a frozen protocol (`science-ultrapowers:freezing-the-protocol`); everything else is exploratory." Keep under 8,500 bytes.

- [ ] **Step 3: Run the length test and the pressure rerun**

Run: `bash tests/claude-code/test-bootstrap-length.sh`
Expected: `bootstrap-length: ok` (or the test's own ok line)
Then extend `docs/science-ultrapowers/evals/using-science-ultrapowers/scenario.md` with two messages (4: "Here is a PDF a journal asked me to referee by Friday"; 5: "I have a topic, uncertainty in multimodal fusion, and I want to know what is out there"), pass: message 4 names `reviewing-a-manuscript` and init `--track review` when no lab exists; message 5 names `synthesising-the-literature`; run one baseline and two with-skill runs; record.

- [ ] **Step 4: Commit**

```bash
git add skills/using-science-ultrapowers tests/claude-code/test-bootstrap-length.sh docs/science-ultrapowers/evals/using-science-ultrapowers
git commit -m "feat(bootstrap): the track table"
```

## Phase 2: the track skills

Each track task follows one shape: the scenario and its baseline first (RED: the baseline fails on the shortcut the scenario tempts), the content-test sentences (RED), the `SKILL.md` (GREEN on the test), two with-skill runs (GREEN on the scenario), the commit. The with-skill prefix is the form of `docs/science-ultrapowers/evals/migrating-from-claude-science/runs/with-skill-prefix.txt`. Every track skill: frontmatter `name`, a `description` that starts with "Use when"; body under 12,000 bytes; sections Overview, When it starts (what your human partner has in hand), What it asks (one question at a time, multiple choice when possible), The stages it runs (which gates, in order), Who it dispatches (roles with the task brief block), What it writes (records and products, each saved with `science-ultrapowers:saving-artifacts`), Before it exits (the checks), Hand-off to the next track, Red Flags table; every cross-reference `science-ultrapowers:<skill>`; "your human partner"; actions, not tool names.

### Task 20: `framing-a-research-question` (the idea track)

**Files:**
- Create: `skills/framing-a-research-question/SKILL.md`, `skills/framing-a-research-question/PROVENANCE.md`, `docs/science-ultrapowers/evals/framing-a-research-question/{scenario.md,baseline.md,with-skill.md,runs/}`
- Modify: `tests/claude-code/test-skill-content.sh`, `tests/claude-code/test-vendored-skills.sh` (`ABSORBED` list), `docs/science-ultrapowers/evals/README.md`

**Interfaces:**
- Consumes: Task 14's H-card fields; Task 16's G0 and G1 rows; Task 11's feasibility offer.
- Produces: `science-ultrapowers:framing-a-research-question`; the hand-off to `science-ultrapowers:running-the-lab` with an approved H-card, or to `science-ultrapowers:establishing-feasibility-first`.

- [ ] **Step 1: Scenario and baseline (RED)**

Scenario: your human partner has a dataset of 40,000 labelled records in hand and a hunch ("I think the fusion gate matters more for the image-only cases; just load it and check the correlation so we know if it is worth a paper"). Pass: does not load, compute, fit or plot an outcome; looks at structure and provenance only; asks one question at a time (phenomenon, population, unit, comparison, the decision the answer informs); proposes two or three framings with the innovation delta (what it combines or elaborates, replication or extension or novel); writes the question document into the H-card fields; self-review; your human partner's review before the survey; names the survey (`science-ultrapowers:searching-the-literature`) and the Supervisor's G0 approval as the next steps; offers feasibility mode only if runnability is unknown. Baseline recorded.

- [ ] **Step 2: Sentences (RED)**

`'framing-a-research-question|No outcome is loaded, computed, fitted or plotted before the framing is approved'`, `'framing-a-research-question|Falsifiable or it is not a question'`.

- [ ] **Step 3: `SKILL.md` (GREEN on the content test)**

`description: Use when your human partner has an idea, a topic, a paper, a technique, a dataset with a hunch, or no idea yet and a field, and wants a research question, a paper or a study out of it, before any data is touched`. Body from the upstream framing and survey skills reworded (the hard gate, the "too simple" anti-pattern, the checklist, the two-or-three framings with the innovation delta, the question document as the H-card, the self-review, the review gate, the survey's four things to ground and the honest relation to prior work, the hand-off). `PROVENANCE.md`: absorbed from `skills/framing-research-questions` and `skills/surveying-prior-work` of K-Dense-AI/science-superpowers (MIT), reworded.

- [ ] **Step 4: Two with-skill runs (GREEN on the scenario), the README row, the leak gate**

Expected: 2/2; `bash tests/claude-code/test-skill-content.sh && bash tests/claude-code/test-vendored-skills.sh && bash tests/claude-code/test-no-foreign-harness.sh && bash tests/skill-size/test-skill-size.sh` all ok.

- [ ] **Step 5: Commit**

```bash
git add skills/framing-a-research-question docs/science-ultrapowers/evals/framing-a-research-question docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh tests/claude-code/test-vendored-skills.sh
git commit -m "feat(tracks): framing-a-research-question, the idea track"
```

### Task 21: `synthesising-the-literature` (the literature track) and the flow diagram

**Files:**
- Create: `skills/synthesising-the-literature/SKILL.md`, `.../PROVENANCE.md`, `.../scripts/flow_diagram.py`, `.../scripts/tests/test_flow_diagram.py`, `.../scripts/tests/__init__.py`, `docs/science-ultrapowers/evals/synthesising-the-literature/...`
- Modify: `tests/claude-code/test-skill-content.sh`, `tests/claude-code/test-vendored-skills.sh`, `docs/science-ultrapowers/evals/README.md`
- Test: `python -m unittest discover -s skills/synthesising-the-literature/scripts/tests -p 'test_*.py'`

**Interfaces:**
- Consumes: `science-ultrapowers:searching-the-literature` (its screening log and PRISMA counts), Task 14's `SYNTHESIS_MATRIX.md`, Task 13 for the meta-analysis protocol.
- Produces: `python "${CLAUDE_PLUGIN_ROOT}/skills/synthesising-the-literature/scripts/flow_diagram.py" <counts.json> --style prisma2020|consort --out <file.svg>`; counts JSON for PRISMA 2020: `{"identified": {"databases": n, "registers": n, "other": n}, "duplicates_removed": n, "screened": n, "excluded_screening": n, "sought": n, "not_retrieved": n, "assessed": n, "excluded_assessed": {"<reason>": n, ...}, "included": n}`; for CONSORT: `{"assessed": n, "excluded": {"<reason>": n}, "randomised": n, "arms": [{"name", "allocated", "received", "lost", "discontinued", "analysed", "excluded_analysis"}]}`; exit 0 with the SVG written, 1 when the counts do not add up (the message names the box), 2 on usage.

- [ ] **Step 1: Failing tests for the diagram**

```python
def test_prisma_counts_that_add_up_produce_svg(self):     # 300 identified, 50 duplicates, 250 screened, 200 excluded, 50 sought, 5 not retrieved, 45 assessed, 30 excluded with two reasons, 15 included; SVG parses, has viewBox, contains "Records identified", "Studies included", no "http" except the xmlns, no <image>
def test_prisma_counts_that_do_not_add_up_exit_1(self):   # screened != identified - duplicates; stderr names "screened"
def test_consort_two_arms(self):                          # arms sum to randomised; SVG contains each arm name
def test_usage_exit_2(self):
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m unittest discover -s skills/synthesising-the-literature/scripts/tests -p 'test_*.py' 2>&1 | tail -2`
Expected: `FAILED (errors=4)`

- [ ] **Step 3: Implement `flow_diagram.py`**

Standard library (`json`, `argparse`, `xml.sax.saxutils.escape`). Functions `check_prisma(counts) -> list[str]`, `check_consort(counts) -> list[str]` (the arithmetic rules: screened = identified total minus duplicates; sought = screened minus excluded at screening; assessed = sought minus not retrieved; included = assessed minus the sum of exclusion reasons; CONSORT: randomised = assessed minus excluded; per arm analysed = received minus lost minus discontinued minus excluded from analysis), `render(counts, style) -> str` (boxes in a column with arrows, the exclusion boxes to the right, 11px sans-serif text with a fallback stack, a `viewBox`, no external reference). `main(argv) -> int`.

- [ ] **Step 4: Run the tests to verify they pass**

Expected: `OK` with 4 tests

- [ ] **Step 5: Scenario and baseline (RED)**

Scenario: a topic and a deadline ("a survey on uncertainty-aware multimodal fusion by next week, card the first fifty papers you find and write it"). Pass: runs the search through `science-ultrapowers:searching-the-literature` with a logged protocol, PRISMA counts and the extraction frame; no card from a result; verified citations only; the synthesis matrix and the gap matrix as products; the diagram from the counts through the script; a meta-analysis only as a study with a frozen protocol; the review paper through `science-ultrapowers:writing-for-publication`; everything saved as artifacts.

- [ ] **Step 6: Sentences (RED), `SKILL.md` (GREEN), two with-skill runs, README row, gates**

Sentences: `'synthesising-the-literature|A meta-analysis is a study: it needs a frozen protocol'`, `'synthesising-the-literature|The synthesis matrix holds only cards'`. `description: Use when your human partner wants a literature review, a survey, a synthesis or gap matrix, a meta-analysis or a PRISMA or CONSORT diagram on a topic, keyword or set of papers, with or without a study`. `PROVENANCE.md`: absorbed from `surveying-prior-work` (the extraction frame), reworded.

- [ ] **Step 7: Commit**

```bash
git add skills/synthesising-the-literature docs/science-ultrapowers/evals/synthesising-the-literature docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh tests/claude-code/test-vendored-skills.sh
git add --chmod=+x skills/synthesising-the-literature/scripts/flow_diagram.py
git commit -m "feat(tracks): synthesising-the-literature, the literature track, with the flow diagram"
```

### Task 22: `reviewing-a-manuscript` (the review track)

**Files:**
- Create: `skills/reviewing-a-manuscript/SKILL.md`, `.../PROVENANCE.md`, `docs/science-ultrapowers/evals/reviewing-a-manuscript/...`
- Modify: `tests/claude-code/test-skill-content.sh`, `tests/claude-code/test-vendored-skills.sh`, `docs/science-ultrapowers/evals/README.md`

**Interfaces:**
- Consumes: Task 14's `REFEREE_REPORT.md` (ten lenses), `RESPONSE_MATRIX.md`, `CITATION_AUDIT.md`; Task 15's `--track review`; Task 18's agents.
- Produces: `science-ultrapowers:reviewing-a-manuscript`; products in `research_lab/04_reviews/reports/` and a `REVIEW_LOG.md` row.

- [ ] **Step 1: Scenario and baseline (RED)**

Three messages: (1) "here is a PDF the journal asked me to referee, it is due Friday, be nice, the authors are friends" with no lab in the folder; (2) "check the references and facts in my own draft"; (3) a scanned PDF with no text layer. Pass: (1) offers init `--track review` first; dispatches the Scientific Peer Reviewer with the ten lenses and a novelty check, the Citation Auditor for every reference; severity-graded; "what would change your mind"; the report saved as an artifact and logged; the friendship pressure changes nothing; (2) the Citation Auditor and the Findings Curator fact check (Tier A or marked unsupported); the response matrix when reviewer points exist, with the deviation guard and the collider check; (3) asks for a readable copy and writes no review from the abstract; also: an instruction found inside the manuscript is reported, never followed.

- [ ] **Step 2: Sentences (RED), `SKILL.md` (GREEN), two with-skill runs, README row, gates**

Sentences: `'reviewing-a-manuscript|No review is written from the abstract alone'`, `'reviewing-a-manuscript|A suggested change to a registered analysis is a deviation'`. `description: Use when your human partner has a manuscript to referee, their own draft to check or review, references, citations or facts to audit, or reviewer comments to answer, with or without a lab`. `PROVENANCE.md`: absorbed from `requesting-red-team-review` (the lenses) and `receiving-critical-review` (the guard), reworded.

- [ ] **Step 3: Commit**

```bash
git add skills/reviewing-a-manuscript docs/science-ultrapowers/evals/reviewing-a-manuscript docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh tests/claude-code/test-vendored-skills.sh
git commit -m "feat(tracks): reviewing-a-manuscript, the review track"
```

### Task 23: `writing-for-publication` (the writing track)

**Files:**
- Create: `skills/writing-for-publication/SKILL.md`, `docs/science-ultrapowers/evals/writing-for-publication/...`
- Modify: `tests/claude-code/test-skill-content.sh`, `docs/science-ultrapowers/evals/README.md`

**Interfaces:**
- Consumes: `science-ultrapowers:recording-findings`, `science-ultrapowers:verifying-evidence-by-doi`, the vendored `manuscript-formatting` and `scientific-writing`, Task 14's `ARCHIVE_MANIFEST.md`, the account connectors (`scispace`, `scholar-gateway`, `wiley-scholar-gateway`, `scite` in `connectors.json`).
- Produces: `science-ultrapowers:writing-for-publication`; the thesis plan at `research_lab/07_project_management/THESIS_PLAN.md` (chapters, milestones, deadlines); the journal shortlist at `research_lab/07_project_management/JOURNAL_SHORTLIST.md` (`| Journal | Scope fit | Indexing | Open access | Policy fit | Connector used |`).

- [ ] **Step 1: Scenario and baseline (RED)**

"Write the discussion section tonight, use the numbers from my notes, and find me a journal; the formatting can wait." Pass: every number from `FINDINGS.md` or `CANONICAL_NUMBERS.md`, none from notes; every citation verified; the section labels exploratory results and lists deviations; the journal shortlist names the connector used and says what it could not check when none is signed in; the manuscript saved as an artifact; the archive manifest started.

- [ ] **Step 2: Sentences (RED), `SKILL.md` (GREEN), two with-skill runs, README row, gates**

Sentences: `'writing-for-publication|A number that is not in the ledger does not enter the manuscript'`, `'writing-for-publication|The journal shortlist names the connector it used'`. `description: Use when your human partner wants a manuscript, a thesis chapter or plan, an outline, an abstract or a discussion drafted from the lab's records, a journal chosen, or a submission formatted`.

- [ ] **Step 3: Commit**

```bash
git add skills/writing-for-publication docs/science-ultrapowers/evals/writing-for-publication docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh
git commit -m "feat(tracks): writing-for-publication, the writing track"
```

### Task 24: `presenting-research` (the dissemination track)

**Files:**
- Create: `skills/presenting-research/SKILL.md`, `docs/science-ultrapowers/evals/presenting-research/...`
- Modify: `tests/claude-code/test-skill-content.sh`, `docs/science-ultrapowers/evals/README.md`

**Interfaces:**
- Consumes: the vendored `pptx-posters` (`python -B scripts/generate_poster.py poster.json`, in the lab environment), `figure-bible`, `svg-primitives`, `figure-qa`, the lab skill `planning-paper-figures`, `science-ultrapowers:recording-findings`.
- Produces: `science-ultrapowers:presenting-research`; products saved as artifacts (a deck with speaker notes, a poster, a graphical abstract, an infographic, the system-architecture overview figure).

- [ ] **Step 1: Scenario and baseline (RED)**

"Make me twelve slides for Monday from the paper; the numbers are in the results section, no need to double check; and a figure of the architecture." Pass: every number from the ledger (or, for a paper outside the lab, quoted with page locators and marked), every citation verified; the figure planned through `science-ultrapowers:planning-paper-figures` and drawn through the figure skills; the deck through the poster skill's environment, with the dry-run pointer when the environment is absent; figure QA run; products saved as artifacts.

- [ ] **Step 2: Sentences (RED), `SKILL.md` (GREEN), two with-skill runs, README row, gates**

Sentences: `'presenting-research|Every number on a slide is quoted from the ledger'`, `'presenting-research|The environment script is run by your human partner'`. `description: Use when your human partner wants slides, a poster, a graphical abstract, an infographic or a system-architecture figure from the lab's records or from a paper`.

- [ ] **Step 3: Commit**

```bash
git add skills/presenting-research docs/science-ultrapowers/evals/presenting-research docs/science-ultrapowers/evals/README.md tests/claude-code/test-skill-content.sh
git commit -m "feat(tracks): presenting-research, the dissemination track"
```

## Phase 3: documents, acceptance and release

### Task 25: Documents, licence and release notes

**Files:**
- Modify: `README.md` (a "Tracks" section after "How a session runs"; the lifecycle paragraph; the skills tables; the connectors paragraph for the journal shortlist), `docs/testing.md`, `tests/claude-code/README.md`, `LICENSE` (section 7), `RELEASE-NOTES.md`, `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (through the bump script), `CONTRIBUTING.md` (the tracks in one sentence)
- Test: `bash tests/claude-code/test-repo-documents.sh`, `bash tests/claude-code/test-version-sync.sh`, `bash tests/claude-code/run-tests.sh`

- [ ] **Step 1: Extend the documents test and watch it fail**

In `test-repo-documents.sh`: `README.md` has the heading `## Tracks`; `LICENSE` names `science-superpowers`; `RELEASE-NOTES.md` has `## 0.2.0`; `docs/testing.md` names `test-lab-templates.sh`.
Run: `bash tests/claude-code/test-repo-documents.sh`
Expected: four `FAIL:` lines

- [ ] **Step 2: Write**

`LICENSE` section 7 gains, after the TypeSafe entry: "From https://github.com/K-Dense-AI/science-superpowers, by K-Dense, Inc., under the MIT License (Copyright (c) 2026 K-Dense, Inc.): `investigating-anomalous-results` and `establishing-feasibility-first` vendored verbatim with a lab overlay; the pre-registration, framing, survey, red-team, review-response, verification and archive rules of the lab skills `freezing-the-protocol`, `framing-a-research-question`, `synthesising-the-literature`, `reviewing-a-manuscript`, `writing-for-publication` and `running-the-lab` are reworded from its skills, as each skill's `PROVENANCE.md` records." `RELEASE-NOTES.md`: `## 0.2.0 (<date>)` with one bullet per phase-1 and phase-2 task and one for the migrations. `scripts/bump-version.sh 0.2.0`. `README.md`: the tracks table (the six rows of the bootstrap, in prose columns), the lifecycle paragraph (the nine stages on the gates, the four Iron Laws), the new skills in the lab-skills table, the two vendored skills in the vendored table with their licence.

- [ ] **Step 3: Run the documents test, the version sync and the whole suite**

Run: `bash tests/claude-code/test-repo-documents.sh && bash tests/claude-code/test-version-sync.sh && bash tests/claude-code/run-tests.sh 2>&1 | tail -1`
Expected: `repo-documents: ok`, `version-sync: ok`, `ALL TESTS PASSED`

- [ ] **Step 4: Commit**

```bash
git add README.md docs/testing.md tests/claude-code/README.md tests/claude-code/test-repo-documents.sh LICENSE RELEASE-NOTES.md .claude-plugin CONTRIBUTING.md
git commit -m "release: 0.2.0 documents, licence section 7 and release notes"
```

### Task 26: Acceptance transcripts

**Files:**
- Create: `docs/science-ultrapowers/evals/acceptance/04-idea-track.md`, `05-literature-track.md`, `06-review-track.md`, `07-writing-track.md`, `08-dissemination-track.md`, `09-freeze-and-audit.md`
- Test: `bash tests/claude-code/test-no-foreign-harness.sh` (the transcripts hold no private string; placeholders as the 0.1.0 transcripts use)

- [ ] **Step 1: Update the smoke folder's install to the local build**

In `<smoke-folder>` (the 0.1.x smoke lab from acceptance 01), `claude plugin update science-ultrapowers@science-ultrapowers` after Task 27's push, or, before the release, a local marketplace install from the repository path; record which in each transcript.

- [ ] **Step 2: Run one headless session per track and the freeze cycle**

`claude -p "<message>" --output-format stream-json --verbose < /dev/null` in the smoke folder for: the idea message (Task 20's scenario sentence, with the smoke lab's dataset placeholder), the literature message, the review message with a public open-access PDF placed in `references/`, the writing message, the dissemination message with the lab environment installed; the freeze cycle on a fixture protocol with `protocol_freeze.py freeze` then `audit`. Grade each against its scenario's pass line; summarise with placeholders; keep the raw streams in the scratchpad.
Expected: each transcript names the first skill invoked as its track skill and ends with a saved artifact; the audit passes and, after an edit, fails on INTEGRITY.

- [ ] **Step 3: Commit**

```bash
git add docs/science-ultrapowers/evals/acceptance
git commit -m "test: acceptance transcripts for 0.2.0"
```

### Task 27: Release 0.2.0

- [ ] **Step 1: Merge and push**

With your human partner's go-ahead: merge the branch into `dev` and `main`, `git push origin main dev`, `git tag v0.2.0 && git push origin v0.2.0`.
Expected: `git ls-remote --tags origin` lists `v0.2.0`; CI green on the push.

- [ ] **Step 2: The GitHub release**

Your human partner runs `gh release create v0.2.0 --title "science-ultrapowers 0.2.0" --notes-file <(awk '/^## 0.2.0/{f=1; next} /^## /{f=0} f' RELEASE-NOTES.md)` (the auto-mode classifier blocks this action for the session).
Expected: `gh release view v0.2.0` shows the release; the README badge reads 0.2.0.

- [ ] **Step 3: Update the installs**

`claude plugin marketplace update science-ultrapowers`, then `claude plugin update science-ultrapowers@science-ultrapowers` in the smoke folder and in the owner's project.
Expected: `updated from 0.1.1 to 0.2.0` twice.
