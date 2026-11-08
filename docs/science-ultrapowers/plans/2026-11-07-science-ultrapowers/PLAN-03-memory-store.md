# PLAN-03: Memory Store Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ultrapowers:subagent-driven-development (recommended) or ultrapowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the lab Claude Science's memory model (entity scopes, evidence tags, the not-to-save rules, a session scratchpad) with ultrapowers' mechanics (one fact per file in git, an index with a hard budget, a four-criteria gate, a lint script, a prompt nudge and a post-compaction rescue hook), keeping the role that learned each fact.

**Architecture:** A `research_lab/memory/` store (`MEMORY.md` index, `project/` and `artifact/<id>/` entry folders), a node lint script with the ultrapowers codes plus five new frontmatter codes and one content code, two bash hooks sharing a small library, and the `remembering-for-the-lab` discipline skill. No service, no database.

**Tech Stack:** node 22+ (`memory-lint.mjs`, `node --test`), bash hooks through `hooks/run-hook.cmd`, Markdown with YAML-like frontmatter (parsed line-wise, no YAML library).

**Spec:** `docs/science-ultrapowers/specs/2026-11-07-science-ultrapowers-design.md` — G9, D5, D10, Components "remembering-for-the-lab", Error handling, Testing.

**Sources:** Claude Science system prompt sections "Memory" (entities `profile`, `project:<pid>`, `artifact:<aid>`, `frame`; evidence `stated|observed|inferred`; `search_memory` before acting; "use sparingly, prefer replace") and "What NOT to save as memory", read 2026-11-07 from the local Claude Science database; ultrapowers 2.3.0 `skills/team-memory/SKILL.md`, `skills/team-memory/scripts/memory-lint.mjs`, `hooks/team-memory-nudge`, `hooks/team-memory-postcompact`, `hooks/lib/team-memory-common` (read from `<user-profile>\.claude\plugins\cache\ultrapowers\ultrapowers\2.3.0\`); Claude Code hooks reference (UserPromptSubmit and SessionStart `compact` context injection; `source` field). Not checked: none.

## Global Constraints

- Store root `research_lab/memory/`; index `research_lab/memory/MEMORY.md`; entries under `project/` and `artifact/<artifact_id>/`; `README.md` beside the index. Nothing else at the store root.
- Entry frontmatter, exact keys and order: `name`, `description`, `metadata` with nested `type` (`gotcha|decision|lesson|directive|vocabulary`), `entity` (`project` or `artifact:<id>`), `evidence` (`stated|observed|inferred`), `learned_by` (a role name or `unknown`), `origin` (`agent|extractor|user|import`), then `date` (`YYYY-MM-DD`), then optional `note`. `name` equals the file name without `.md`. Body: the fact (one to three sentences), `**Why:**`, `**How to apply:**`.
- Index line: `- [<name as title>](<dir>/<file>.md) — <one-line hook> (<YYYY-MM>)`; updates fold into the line as `**UPDATED YYYY-MM-DD: ...**`.
- Budget `memory.indexBudget` from `research_lab/lab.json` (default 150); `memory.rediscoveryMinutes` (default 15); `memory.trailer` (default `Memory-Ref`).
- Profile-scope facts (about your human partner) are never stored in the project; the skill points at Claude Code user memory.
- Session scratchpad `research_lab/.scratch/<YYYY-MM-DD>-<session>/<role>.md`, git-ignored (PLAN-06 writes the ignore line), deleted by the stand-up.
- Hooks print nothing and exit 0 unless a store exists at or above the working directory; they never write.
- Skill writing follows PLAN-01's Global Constraints.

## Review Focus

1. A memory whose body is only `F-0031` or `see D-0107` duplicates a record; Task 2's lint test asserts `RECORD_ONLY` on such a body.
2. A compaction hook that fires on `startup` would nag at every session start: Task 3's test feeds `{"source":"startup"}` and asserts empty output.
3. A fact about a person ("the supervisor prefers…") is a profile-scope leak: Task 2's lint flags `entity: profile` as `FM_ENTITY`, and the skill's gate refuses it.
4. An index line whose link points at a file in the wrong entity folder (an `artifact:` entry under `project/`): Task 2's test asserts `FM_ENTITY_DIR`.
5. The hook library's `find_memory_store` must stop at the filesystem root and must find the store from a nested working directory: Task 3's test runs from `<repo>/src/deep` and from a temp dir with no store.

---

### Task 1: Port `memory-lint.mjs` with the new schema

**Files:**
- Create: `skills/remembering-for-the-lab/scripts/memory-lint.mjs`, `skills/remembering-for-the-lab/scripts/tests/memory-lint.test.mjs`, `skills/remembering-for-the-lab/scripts/tests/fixtures/` (built by the test at run time, not committed)

**Interfaces:**
- Produces: `node skills/remembering-for-the-lab/scripts/memory-lint.mjs <store> [--budget N]`; exit 0 clean, else one line per finding `<CODE> <path>: <message>` and exit 1. Codes: `BUDGET`, `DANGLING`, `ORPHAN`, `STRAY`, `FM_MISSING`, `FM_KEYS`, `FM_NAME`, `FM_TYPE`, `FM_ENTITY`, `FM_ENTITY_DIR`, `FM_EVIDENCE`, `FM_LEARNED_BY`, `FM_ORIGIN`, `FM_DATE`, `WIKILINK`, `NEAR_DUP`, `RECORD_ONLY`. When `--budget` is absent the script reads `../lab.json` relative to the store (`memory.indexBudget`), else 150.

- [ ] **Step 1: Write the failing tests**

`memory-lint.test.mjs` (node `test`, builds a temp store per case with a helper `writeStore(dir, {index, entries})`):
- `clean store exits 0` (two valid entries, one `project/`, one `artifact/abc123/`, both indexed).
- `BUDGET when index lines exceed budget` (`--budget 2`, three entries).
- `DANGLING index link to missing file`.
- `ORPHAN entry without index line`.
- `STRAY file at store root` (`notes.md`).
- `FM_KEYS when metadata lacks learned_by`.
- `FM_TYPE on unknown type`; `FM_EVIDENCE on unknown evidence`; `FM_ORIGIN on unknown origin`; `FM_LEARNED_BY when empty`.
- `FM_ENTITY on profile`; `FM_ENTITY_DIR when entity artifact:x lives under project/`.
- `FM_DATE on 2026/11/07`.
- `WIKILINK to missing name`; `NEAR_DUP on names differing by trailing s`.
- `RECORD_ONLY when the body is just a record id` (bodies `F-0031`, `see D-0107.`, `EC-0042`).
- `budget read from lab.json when --budget absent` (`lab.json` with `memory.indexBudget: 1`, two entries → `BUDGET`).

- [ ] **Step 2: Run them to see them fail**

Run: `node --test skills/remembering-for-the-lab/scripts/tests/*.test.mjs`
Expected: every test fails with `Cannot find module .../memory-lint.mjs`.

- [ ] **Step 3: Port the script**

Copy ultrapowers' `memory-lint.mjs` and change: entry folders `project` and `artifact/*` (recursive one level under `artifact/`) instead of `gotchas|decisions|subsystems`; the frontmatter schema and codes above (`RECORD_ONLY` matches a body whose non-blank text, after removing `**Why:**`/`**How to apply:**` lines, is only record ids `^(see\s+)?(F|D|EC|RV|T|REQ|EXP|H)-\d+\.?$` case-insensitive); budget from `lab.json` as described. Keep the output format and the exit codes.

- [ ] **Step 4: Run the tests**

Expected: all pass.

- [ ] **Step 5: Commit**

Run: `git add skills/remembering-for-the-lab && git commit -m "feat(memory): port memory-lint with entity scopes, evidence tags, learned_by and RECORD_ONLY"`

### Task 2: Store templates and the `remembering-for-the-lab` skill

**Files:**
- Create: `skills/remembering-for-the-lab/SKILL.md`, `skills/remembering-for-the-lab/templates/MEMORY.md`, `skills/remembering-for-the-lab/templates/README.md`, `skills/remembering-for-the-lab/templates/entry.md`

**Interfaces:**
- Produces: the three templates PLAN-06 `init` copies into `research_lab/memory/` (`MEMORY.md` with the header, the four criteria, the never-store list, the index line format and empty `## Project` and `## Artifacts` headings; `README.md` with the contract; `entry.md` with the exact frontmatter skeleton)

- [ ] **Step 1: Write the templates**

`MEMORY.md`: title `# Lab memory: index`, two lines of purpose, the four criteria (verified, durable, expensive at `rediscoveryMinutes`, not derivable: not in code, docs, specs, git history, **or the lab records: findings, decisions, registry, artifact store**), the never-store list (secrets, tokens, credentials, URLs embedding auth, personal data, facts about people, anything derivable from the records or the artifact store), the index line format, then `## Project` and `## Artifacts` headings with no lines. `README.md`: layout, entry format (frontmatter block verbatim), when to write, the scopes (`project`, `artifact:<id>`; profile facts go to Claude Code user memory; the session scratchpad path), the stand-up as the gating moment. `entry.md`: the frontmatter skeleton with `<placeholders>` and the body skeleton.

- [ ] **Step 2: Lint an index built from the template**

Run: in a temp dir, create `research_lab/memory/` with the two templates and `project/`, `artifact/` folders; `node skills/remembering-for-the-lab/scripts/memory-lint.mjs <that store>`
Expected: exit 0.

- [ ] **Step 3: Write `SKILL.md`**

Frontmatter: `name: remembering-for-the-lab`; `description: Use when a role or your human partner learns a verified, durable, expensive-to-rediscover fact about the project that no lab record holds, when deciding whether the lab already hit a problem, before dispatching a role on a topic the lab may have met before, or when asked to prune or lint the lab memory`. Body, superpowers form, under 500 words: `## Overview` (core principle: *Records hold what happened; memory holds what the records cannot tell you.*); `## The Iron Law` code block `SEARCH MEMORY BEFORE DISPATCHING; GATE BEFORE WRITING; NEVER STORE WHAT A RECORD ALREADY SAYS`; `## Scopes and tags` table (`project`, `artifact:<id>`, profile → user memory, scratchpad → `research_lab/.scratch/`; `evidence` meanings from Claude Science: stated and observed are load-bearing, inferred is a hypothesis); `## remember` steps (the four-criteria gate; the never-store list; check the index; distil; write the file from `templates/entry.md`; add the index line; budget check; lint; the orchestrator commits under the lab's commit rule with the `Memory-Ref` trailer); `## recall` ladder (index, grep the store, grep the records `DECISIONS.md` / `FINDINGS.md` / `LAB_NOTEBOOK.md` / `REVIEW_LOG.md`, `git log --grep`, write back hard-won answers); `## Who writes` (roles propose memories in the hand-off `Memories proposed:` line as `type | evidence | text`; the orchestrator gates and writes; nothing is written mid-task by a subagent); `## prune` and `## lint` (the command and the code table, including the new codes); `## Red Flags` table (at least: "useful context for the next session" → scratchpad or task record; "it's in a decision, but a note saves time" → RECORD_ONLY; "the supervisor said they prefer…" → profile, not here; "fairly sure" → inferred, verify first; "the index is only a little over").

- [ ] **Step 4: Run the gate and commit**

Run: `bash tests/claude-code/test-no-foreign-harness.sh`
Expected: `no-foreign-harness: ok`.
Run: `git add skills/remembering-for-the-lab && git commit -m "feat(memory): remembering-for-the-lab skill and store templates"`

### Task 3: Nudge and post-compaction hooks

**Files:**
- Create: `hooks/lib/memory-common`, `hooks/memory-nudge`, `hooks/memory-postcompact`
- Modify: `hooks/hooks.json`
- Test: `tests/claude-code/test-memory-hooks.sh`

**Interfaces:**
- Consumes: PLAN-01 `hooks/run-hook.cmd`, `hooks/hooks.json`
- Produces: `hooks/hooks.json` with three entries: SessionStart `startup|clear|compact` → `session-start`; SessionStart `compact` → `memory-postcompact`; UserPromptSubmit → `memory-nudge`; both new hooks print `{"hookSpecificOutput":{"hookEventName":"<event>","additionalContext":"…"}}` only when `find_memory_store` finds `research_lab/memory/MEMORY.md` at or above the hook's `cwd`

- [ ] **Step 1: Write the failing test**

`tests/claude-code/test-memory-hooks.sh`: builds a temp repo with `research_lab/memory/MEMORY.md` and a nested `src/deep/`; asserts: (a) `echo '{"cwd":"<tmp>/src/deep"}' | bash hooks/memory-nudge` prints JSON whose `additionalContext` contains `remembering-for-the-lab` and the store path; (b) from a temp dir without a store the output is empty and the exit code 0; (c) `echo '{"cwd":"<tmp>","source":"compact"}' | bash hooks/memory-postcompact` prints JSON containing `compacted`; (d) with `"source":"startup"` the output is empty; (e) `SCIENCE_ULTRAPOWERS_NO_MEMORY_NUDGE=1` makes (a) print nothing; (f) `jq -e '.hooks.UserPromptSubmit[0].hooks[0].command | test("memory-nudge")' hooks/hooks.json` and `jq -e '.hooks.SessionStart[1].matcher == "compact"' hooks/hooks.json` succeed. Prints `memory-hooks: ok`.

- [ ] **Step 2: Run it to see it fail**

Expected: `bash: hooks/memory-nudge: No such file or directory`.

- [ ] **Step 3: Port the library and the two hooks**

`hooks/lib/memory-common`: copy ultrapowers' `team-memory-common` and rename `nudge_off` to read `SCIENCE_ULTRAPOWERS_NO_MEMORY_NUDGE`, `find_memory_store` to look for `research_lab/memory/MEMORY.md` walking up from `cwd` to the root and print the store directory, `emit_context <event> <text>` to print the Claude Code `hookSpecificOutput` shape only. `hooks/memory-nudge` and `hooks/memory-postcompact`: copy ultrapowers' two hooks with the library name, the skill name `science-ultrapowers:remembering-for-the-lab`, and the text: nudge `Lab memory: if this session verified a durable, expensive-to-rediscover fact that no lab record holds, propose it in the hand-off or save it with science-ultrapowers:remembering-for-the-lab (store: <path>).`; post-compaction `Context was just compacted. If lab-worthy learnings surfaced earlier and are not yet saved to <path>, save them now with science-ultrapowers:remembering-for-the-lab.` Add the two `hooks.json` entries.

- [ ] **Step 4: Run the test and the session-start test**

Run: `bash tests/claude-code/test-memory-hooks.sh && bash tests/claude-code/test-session-start.sh`
Expected: both `ok`.

- [ ] **Step 5: Commit**

Run: `git add hooks tests/claude-code/test-memory-hooks.sh && git commit -m "feat(memory): prompt nudge and post-compaction rescue hooks"`

## Execution record (2026-11-07/08)

Executed by an Opus 5.5 orchestrator, with Sonnet 5.5 and Haiku 5.5 implementers per task and per fix pass; the orchestrator wrote the prose (templates, skill) and the briefs, and reviewed every diff. The final whole-branch review was by a fresh Fable 5.1 reviewer: 0 Critical, 4 Important and 17 Minor findings, all fixed, none deferred. Branch `plan-03-memory-store`, cut from `dev` (main + PLAN-01 + PLAN-02), commits `5bd792b..`. Deviations from the tasks above, each ruled with the spec as the authority:

- R2: Task 1 also committed a frontmatter-only SKILL.md (the gate requires one per skill folder).
- R3: test ids avoid `D-00NN` (the gate rejects it under skills/).
- R4: lint fixtures live in OS temp dirs, not a `fixtures/` folder.
- R5: BUDGET counts every MEMORY.md line, so the template header stays at 18 lines.
- R6: frontmatter keys are checked in order, with an optional `note:` last.
- R7: `learned_by` must be kebab-case or `unknown`.
- R8: `profile` is FM_ENTITY; FM_ENTITY_DIR is checked both ways.
- R9: RECORD_ONLY also covers index-line hooks.
- R10: STRAY covers misplaced files and folders inside `project/` and `artifact/`; dotfiles are ignored.
- R11: the never-store list is the plan's list plus spec D5's.
- R12: the remembering-for-the-lab pressure test the spec requires was added. It ran five rounds (`docs/science-ultrapowers/evals/remembering-for-the-lab/`):
  - v1: did not discriminate on the gate.
  - v2: baselines 0/3, with the skill 3/3.
  - v3 and v4: refactor checks, 2/2 each.
  - "Never store artifacts" became "artifact contents", so artifact-scoped memories are reachable.
- R17: the lint's main-module guard compares real paths. Through a junction it had exited 0 without linting, and the bug is inherited from ultrapowers.
- R13–R16 and R24: the hooks are Claude-Code-only. `find_memory_store` walks the logical path first, giving a relative path, and falls back to the physical path, printing an absolute path, only when a junction or symlink makes them differ. `emit_json` is session-start's EPIPE-proof body.
- R25: new lint code NO_FACT (18 codes). RECORD_ONLY also catches id lists and named records ("D-0124 and F-0031", "See decision D-0124").
- R26–R28: misconfigured `lab.json` budgets are reported; usage errors exit 2; `./` and case-different index links are matched.
- R30: the off switch `SCIENCE_ULTRAPOWERS_NO_MEMORY_NUDGE` keeps the hooks on for empty, 0, false, no and off.
- R31: `date` is the last verification day.
- R32: the nudge text says "gate it and save it".
- R33: PLAN-07's memory import was aligned with this lint: kebab-case `learned_by`, slug de-duplication, and record-only rows sent to a prune list.
