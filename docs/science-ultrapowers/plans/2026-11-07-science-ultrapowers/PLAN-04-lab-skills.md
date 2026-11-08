# PLAN-04: Lab Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ultrapowers:subagent-driven-development (recommended) or ultrapowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the lab's six skills in superpowers form under verb-first names, add `holding-lab-meetings`, `searching-the-literature` and `planning-paper-figures`, vendor the fourteen vetted third-party skills with cleaned overlays, adapt the seven kept superpowers skills, and pressure-test every discipline skill.

**Architecture:** Each lab skill is a folder `skills/<verb-first-name>/SKILL.md` with scripts and templates beside it; project-specific sentences from the current skills move out (to PLAN-06's project templates) under the spec's sorting rule; the discipline skills get the Iron Law / rationalization table / red flags form, the reference skills keep their tables. Source material is the current team at `<host-project>\research_lab\claude_code_team\skills\` (read-only).

**Tech Stack:** Markdown skills, Python 3.11+ stdlib scripts (`verify_doi.py`, `jev_ask.py`, new `search_openalex.py`), `unittest`, bash tests.

**Spec:** `specs/2026-11-07-science-ultrapowers-design.md` — G3, G5, D1, D6, D7, D9, Constraints (sorting rule), Components "running-the-lab" through "planning-paper-figures", Testing "Prose changes".

**Sources:** superpowers v7.0.2 `skills/writing-skills/SKILL.md` and `references/discovery.md` (form, description rules, word budgets, cross-reference style), `skills/test-driven-development/SKILL.md` and `skills/verification-before-completion/SKILL.md` (the discipline form as written); the current lab skills and `TEAM_SPEC.md` (content, read 2026-11-07); `09_skill_vetting/SKILL_VETTING_REPORT.md` and each `PROVENANCE.md` (vendoring rules); Claude Code skills reference (https://code.claude.com/docs/en/skills.md: frontmatter fields, 1,536-character description cap, `${CLAUDE_PLUGIN_ROOT}` substitution in skill bodies); OpenAlex API (https://docs.openalex.org/ — `GET https://api.openalex.org/works?search=<q>&per-page=<n>`, fields `doi`, `title`, `publication_year`, `type`, `primary_location.source.display_name`; from memory, Not checked this session — Task 7's script treats a missing field as `null` and its test uses a fixture, so an API change breaks nothing at test time).

## Global Constraints

- PLAN-01 Global Constraints apply (form, names, no project strings, no `host.` calls, no decision ids).
- Script invocation form in prose: `python "${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/<script>.py" …`.
- Record paths in skills are written relative to the project root as `research_lab/<folder>/<file>`; the project root itself is never named.
- The sorting rule: a rule is lab law unless it names a project artifact, path, person or id. The spec's Constraints section lists which of the fifteen current rules go where; this plan's Task 1 applies it.
- Discipline skills: `verifying-evidence-by-doi`, `recording-findings`, `searching-the-literature` (and PLAN-02's `saving-artifacts`, PLAN-03's `remembering-for-the-lab`) carry an Iron Law, a Common Rationalizations table and a Red Flags list, and each ships with a baseline and a with-skill transcript under `docs/science-ultrapowers/evals/<skill>/`.
- Reference skills: `running-the-lab` (under 12,000 characters), `holding-lab-meetings`, `requesting-reference-access`, `deciding-with-jev`, `planning-paper-figures` (under 500 words each except `running-the-lab`).
- Vendored skills keep upstream names, `LICENSE`, `PROVENANCE.md`; overlays keep items 1-3 and 7 and drop 4-6; `PROVENANCE.md` gets a dated change-log line and the refreshed `SKILL.md` hash.

## Review Focus

1. A role reads a skill that still says `.claude/skills/doi-verified-evidence/scripts/verify_doi.py` and the command fails in a plugin install: Task 10's test greps every skill for `.claude/skills/` and for the old skill names.
2. A rewritten rule drifts from the current one (a dropped "never" or a softened "must"): Task 1 and Task 3 each keep a side-by-side list of the current rule sentences and tick them; Task 10's test asserts the verbatim presence of the twelve sentences listed there.
3. `verify_doi.py` is called from a different working directory than today; relative imports or relative test fixtures break: Task 3 moves the tests with the script and runs them from the repository root.
4. A vendored overlay still tells the agent to copy files with the host object's skill-read call: Task 9's test greps every vendored `SKILL.md` for `host.`, `repl`, `pdf-explore`, `Claude Science`.
5. A pressure scenario that is too easy passes at baseline and proves nothing: each scenario in Task 11 combines at least three pressures (time, sunk cost, authority, exhaustion) per `writing-skills`.

---

### Task 1: `running-the-lab`

**Files:**
- Create: `skills/running-the-lab/SKILL.md`
- Source: `claude_code_team/skills/research-lab-workflow/SKILL.md`, `claude_code_team/CLAUDE.md`, `claude_code_team/agents/*.md` (the shared "Operating rules" section)

**Interfaces:**
- Produces: the task-brief block and the hand-off block (exact field lines below) that every agent (PLAN-05), `saving-artifacts` and `remembering-for-the-lab` rely on; the orchestrator rules PLAN-06's `CLAUDE.md` section points at

- [ ] **Step 1: Map the source into sections**

Write a scratch table (not committed) with one row per sentence of the source files, marked `law` (goes in this skill), `project` (goes to PLAN-06's `CLAUDE.md` template or `PROJECT_BRIEF.md` skeleton), or `drop` (Claude Science only). Apply the spec's sorting rule. Project rows include: the project-root path, "Current critical path", `<a funder folder>`, `.github` legacy agents, `uv` dev commands, the Tier-B list from a decision record, the autoresearch checkpoint sentence, the data-task and experiment-task id mentions. Drop rows include: the Claude Science column of the roster, "in Claude Science, the lead session", `kernel.py`.

- [ ] **Step 2: Write the skill**

Frontmatter: `name: running-the-lab`; `description: Use whenever your human partner addresses the lab, a role, a gate, a record or a research task, before delegating, reviewing, handing off or recording anything`. Sections, in order: `# Running the lab`; `## Overview` (two sentences: the lab reproduces a productive research group; the core principle *Nothing enters a record unverified, nothing passes a gate unreviewed, nobody reviews their own work.*); `## Roster` (table: Role | Agent | Owns; the human References & Resources Specialist first); `## Stage gates` (the G0-G6 table verbatim, decision ids removed); `## Review toolkit and the devil's-advocate gate` (the §2b table and the CRITICAL/MAJOR/MINOR rules, the attribution sentence kept without the licence detail); `## Standing rules` (verification claims name the check; environment and configuration changes need approval; the test split only in a pre-registered final evaluation; paywalled papers through the human specialist, never shadow libraries or credentials; Jev is never evidence and never passes a gate; scratch files only in `research_lab/.scratch/`; nothing irreversible without your human partner); `## Task brief` (code block, the six lines of §3 verbatim); `## Hand-off block` (code block: `HAND-OFF <TASK ID> -> <next role>` / `Deliverables: <paths>` / `Inputs: <artifact ids or paths each deliverable was computed from, or 'none'>` / `Verification record: …` / `Findings proposed for the ledger: …` / `Memories proposed: <type | evidence | one sentence> or 'none'` / `Open issues / risks:` / `Access requests filed:` / `Deviations from the brief:`); `## Escalation` (the §6 table); `## Record map` (§7 with `artifacts/` and `memory/` added); `## Every role` (the former agents' operating rules, generic: preloaded skills are binding; start from `research_lab/00_project_knowledge/PROJECT_BRIEF.md`; verify DOIs with the `verifying-evidence-by-doi` script; you cannot ask your human partner, file requests and put `ACCESS REQUEST` / `APPROVAL NEEDED` at the top of the report; end with the hand-off block; never print or store secrets; never run git write commands, the orchestrator commits); `## Orchestrating from the main session` (act as the Research Project Manager when the team is addressed; search lab memory before dispatching; give each role the full brief; relay request blocks with a question to your human partner and record the answer in `research_lab/05_access_requests/ACCESS_REQUESTS.md`; after each hand-off: save deliverables with `science-ultrapowers:saving-artifacts`, record findings, gate memories, `git status --porcelain research_lab/`, then `git add research_lab/ && git commit` with the task id, role and the `Memory-Ref` trailer when a memory was written, on the current branch only; nesting only for the fresh-context devil's-advocate reviewer); `## Red Flags` table (at least: "the reviewer already said verified", "it's my own work but I know it best", "skip the brief, the task is obvious", "commit the code too while I'm at it", "the subagent can ask the user itself").

- [ ] **Step 3: Check size and the gate**

Run: `wc -c skills/running-the-lab/SKILL.md && bash tests/claude-code/test-no-foreign-harness.sh`
Expected: under 12000; `ok`.

- [ ] **Step 4: Commit**

Run: `git add skills/running-the-lab && git commit -m "feat(skills): running-the-lab, the lab's operating manual in superpowers form"`

### Task 2: `holding-lab-meetings`

**Files:**
- Create: `skills/holding-lab-meetings/SKILL.md`, `skills/holding-lab-meetings/templates/SESSION_KICKOFF.md`, `skills/holding-lab-meetings/templates/SESSION_STANDUP.md`, `skills/holding-lab-meetings/templates/LAB_MEETING.md`
- Source: `research_lab/templates/{SESSION_KICKOFF,SESSION_STANDUP,LAB_MEETING}.md`, `research-lab-workflow` §5, `CLAUDE.md` rules 13-14, `agents/lab-project-manager.md` `initialPrompt`

**Interfaces:**
- Produces: the three templates PLAN-06 copies into `research_lab/templates/`; the kickoff and stand-up procedures PLAN-05's `lab-project-manager` preloads

- [ ] **Step 1: Write the templates**

Copy the three current templates; replace "in Claude Science, the lead session" with "the main session"; in `SESSION_KICKOFF.md` replace the roadmap path and the four named workstreams with `<the roadmap document named in the project brief>` and `<the project's workstreams>`; add to the kickoff a line `7. Lab memory: lines of research_lab/memory/MEMORY.md relevant to today's tasks`; add to the stand-up `8. Memories gated this session (written / refused, with the criterion that failed)` and `9. Artifact store: lfs-check result`.

- [ ] **Step 2: Write the skill**

Frontmatter: `name: holding-lab-meetings`; `description: Use at the start of every work session before any task, at the end of every session, at a milestone, at a gate review, or when your human partner asks where the project stands`. Body under 500 words: `## Overview`; `## Session kickoff` (read `PROJECT_BRIEF.md`, `TASK_BOARD.md`, the last note in `06_decisions/lab_meetings/`, open rows of `ACCESS_REQUESTS.md`, `memory/MEMORY.md`; write `research_lab/06_decisions/lab_meetings/YYYY-MM-DD_kickoff.md` from the template; present it; the first kickoff paragraph is the former manager prompt: open tasks by gate, blocked items, open access requests, recommended next action); `## Session stand-up` (write `YYYY-MM-DD_standup.md`; gate every `Memories proposed:` line of the session's hand-offs with `science-ultrapowers:remembering-for-the-lab`; run the artifact `lfs-check`; delete `research_lab/.scratch/<today>-*`; commit `research_lab/` under the lab's commit rule); `## Lab meeting` and `## Gate review` (from §5); `## Red Flags` ("the session is short, skip the kickoff", "the stand-up can wait until tomorrow", "I'll summarise from memory instead of the records").

- [ ] **Step 3: Gate and commit**

Run: `bash tests/claude-code/test-no-foreign-harness.sh && git add skills/holding-lab-meetings && git commit -m "feat(skills): holding-lab-meetings with kickoff, stand-up and meeting templates"`

### Task 3: `verifying-evidence-by-doi` with its script and tests

**Files:**
- Create: `skills/verifying-evidence-by-doi/SKILL.md`, `skills/verifying-evidence-by-doi/scripts/verify_doi.py` (moved), `skills/verifying-evidence-by-doi/scripts/tests/__init__.py`, `skills/verifying-evidence-by-doi/scripts/tests/conftest_stub.py` (only if the moved tests need it), `skills/verifying-evidence-by-doi/scripts/tests/test_verify_doi_author_list.py` (moved)
- Source: `claude_code_team/skills/doi-verified-evidence/`

**Interfaces:**
- Produces: `python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <DOI> --title … --first-author … --year …`, `--search`, `--csv`, `--extract-from`, `--bibtex`, `--registry-bib … --out …` unchanged; exit 0 only when every DOI is `VERIFIED`

- [ ] **Step 1: Move the script and tests, run the tests**

Copy `verify_doi.py` and `scripts/tests/*` (the current tests are pytest-style; convert to `unittest.TestCase` if they use pytest fixtures, keeping the same assertions). Remove any `__pycache__`.
Run: `python -m unittest discover -s skills/verifying-evidence-by-doi/scripts/tests -v`
Expected: `OK`.

- [ ] **Step 2: Generalise the script's docstring and user agent**

Docstring usage lines keep the same flags with placeholder paths; `DOI_USER_AGENT = "science-ultrapowers-doi-verifier/0.1"`; no other behaviour change. Re-run the tests: `OK`.

- [ ] **Step 3: Write the skill**

Frontmatter: `name: verifying-evidence-by-doi`; `description: Use whenever a source is cited, a literature claim is written, extracted, reviewed or audited, a reference is added, a bibliography is checked, or a role is about to write "verified" about a paper`. Body (discipline form): `## Overview` (*A fact enters a lab artifact only from a peer-reviewed work whose DOI resolves in Crossref, matches the PDF in hand, is not retracted, was read in full text at the cited passage, and is recorded on an evidence card.*); `## The Iron Law` code block `NO CLAIM WITHOUT A VERIFIED, FULL-TEXT-READ, CARDED SOURCE`; `## Source tiers` (the A/B/C/X table; Tier B needs the official proceedings page and your human partner's approval logged in `research_lab/01_reference_registry/EXCEPTIONS.md`; the attribution-only preprint rule, without its decision id); `## The five checks` (verbatim list); `## Verification chain` (the eight-level table); `## Registry statuses`; `## Failure modes seen in practice` (the six current bullets with the project file names and ref numbers removed: "the DOI in the PDF text belonged to a cited paper", "filenames lie", "author lists copied from notes were wrong", "title-search collisions", "preprint-server twins", "secondary citation"); `## Forbidden` (verbatim); `## Wording in outputs` (verbatim minus the decision id); `## Methodological basis` (the three DOIs); `## Using the script` (the six command lines with the plugin path; "bibliographies are generated, never typed" paragraph); `## Common Rationalizations` table (at least eight: "the abstract is enough", "the reference list already has the DOI", "another agent marked it verified", "I remember this paper", "the preprint is the same as the published version", "the PDF filename says what it is", "one secondary citation won't matter", "the author list from the notes is probably right"); `## Red Flags` list; `## Verification Checklist`.

- [ ] **Step 4: Gate and commit**

Run: `bash tests/claude-code/run-tests.sh`
Expected: exit 0.
Run: `git add skills/verifying-evidence-by-doi && git commit -m "feat(skills): verifying-evidence-by-doi in superpowers form with the Crossref verifier"`

### Task 4: `recording-findings`

**Files:**
- Create: `skills/recording-findings/SKILL.md`
- Source: `claude_code_team/skills/findings-ledger/SKILL.md`, `research-lab-workflow` §2c rule 1

- [ ] **Step 1: Write the skill**

Frontmatter: `name: recording-findings`; `description: Use when recording, verifying, reconciling, quoting or looking up any project fact, result, number or experiment, when two documents disagree on a number, or when a role is about to write "verified", "confirmed" or "re-checked"`. Body: `## Overview` (*If it is not in the ledger, it is not a finding.*); `## The Iron Law` code block `A NUMBER NOT IN THE LEDGER IS NOT A FINDING; A VERIFICATION THAT DOES NOT NAME ITS CHECK IS NOT A VERIFICATION`; `## Findings ledger` (the field table and transitions, verbatim; the drift example generalised to "when documents disagree on a number"); `## Canonical numbers`; `## Lab notebook`; `## Experiment register` (the field table; the id scheme sentence generalised to "keep the project's scheme"); `## Verification before recording` (the three bullets); `## Naming the check` (the §2c rule 1 text: 'verified', 're-hashed', 'confirmed identical', 'checked' only with which files, which method (byte hash, row count, substring presence, visual inspection) and against what); `## Methodological basis` (the two DOIs); `## Claude Code notes` (edit with the file tools; recompute with a short `python -c` against the metrics file and paste the command into the notebook entry); `## Common Rationalizations` (at least six: "the log line has the number", "I'll record it after the run finishes", "editing the verified row is quicker than superseding it", "single seed is fine for now", "the report I'm summarising already verified it", "'verified' is just a word"); `## Red Flags`; `## Verification Checklist`.

- [ ] **Step 2: Gate and commit**

Run: `bash tests/claude-code/test-no-foreign-harness.sh && git add skills/recording-findings && git commit -m "feat(skills): recording-findings with the ledger schema and the name-the-check rule"`

### Task 5: `requesting-reference-access`

**Files:**
- Create: `skills/requesting-reference-access/SKILL.md`
- Source: `claude_code_team/skills/reference-access-request/SKILL.md`

- [ ] **Step 1: Write the skill**

Frontmatter: `name: requesting-reference-access`; `description: Use when a needed paper is paywalled or missing in full text, a candidate DOI needs human confirmation, or a DOI-less peer-reviewed source needs approval`. Body: sections 1-5 of the source verbatim (the request table, delivery steps, Tier B approvals, the Never list), the `## Claude Code` section renamed `## From a role` with the `ACCESS REQUEST REQ-xxxx …` block verbatim; remove the platform section reference in step 3 of "Before filing". Reference skill, under 500 words.

- [ ] **Step 2: Gate and commit**

Run: `bash tests/claude-code/test-no-foreign-harness.sh && git add skills/requesting-reference-access && git commit -m "feat(skills): requesting-reference-access"`

### Task 6: `deciding-with-jev` with `jev_ask.py` and the vendored `typesafe-ai`

**Files:**
- Create: `skills/deciding-with-jev/SKILL.md`, `skills/deciding-with-jev/scripts/jev_ask.py` (moved), `skills/deciding-with-jev/scripts/tests/test_jev_ask_offline.py`, `skills/typesafe-ai/SKILL.md` and `skills/typesafe-ai/LICENSE` (copied verbatim)
- Source: `claude_code_team/skills/jev-decisions/`, `claude_code_team/skills/typesafe-ai/`

**Interfaces:**
- Produces: `python "${CLAUDE_PLUGIN_ROOT}/skills/deciding-with-jev/scripts/jev_ask.py" --request req.json --role <role> --purpose "<text>"` and `--pattern match_candidate --entry a.txt --candidate b.txt`; log path `research_lab/08_decision_log/JEV_CALLS.jsonl` relative to the lab found by walking up from the working directory

- [ ] **Step 1: Write the failing offline test**

`test_jev_ask_offline.py`: with `TYPESAFE_API_KEY` removed from the environment, running `jev_ask.py --request <tmp req.json> --role x --purpose y` exits 2 and prints `error: TYPESAFE_API_KEY is not set; decide as a specialist` on stderr, and writes nothing to the log; `jev_ask.py --policy-check <file containing an email and a phone number>` prints JSON `{"blocked": false, "redacted": "<text>"}` whose `redacted` contains no `@` and no run of nine or more digits. The flag `--policy-check FILE` is added to the script in Step 2 (it runs the existing policy check and redaction functions and exits without calling the API).

- [ ] **Step 2: Move the script and make the test pass**

Copy `jev_ask.py`; change the log path resolution to walk up to `research_lab/` (reuse the logic of PLAN-02's `find_lab`, duplicated in a ten-line helper, not imported across skills); add the missing-key message and exit code 2; remove any reference to an out-of-scope project folder, keeping the generic "blocked folders listed in `research_lab/lab.json` `jev.blockedPaths`" check with default `[]`.
Run: `python -m unittest discover -s skills/deciding-with-jev/scripts/tests -v`
Expected: `OK`.

- [ ] **Step 3: Write the skill and vendor `typesafe-ai`**

`deciding-with-jev/SKILL.md`: frontmatter `name: deciding-with-jev`; `description: Use for fast, calibrated triage decisions (screening order, candidate-DOI matching, deduplication, claim-support pre-checks, evidence-rule lint, task routing, gate checklists) and for Jev-as-baseline studies; never for evidence, text or gate decisions`. Body: the source sections 1-4 with: decision ids removed, the funder's name replaced by "the blocked folders in `lab.json`", the Claude Science credentials and usage sections removed, `## Using the script` with the two command lines, and a `## When the key is absent` line (the script says so; the specialist decides; nothing is logged as an answer). Copy `typesafe-ai/SKILL.md` and `LICENSE` unchanged.

- [ ] **Step 4: Gate and commit**

Run: `bash tests/claude-code/run-tests.sh && git add skills/deciding-with-jev skills/typesafe-ai && git commit -m "feat(skills): deciding-with-jev with the policy-enforcing client, typesafe-ai vendored"`

### Task 7: `searching-the-literature` with `search_openalex.py`

**Files:**
- Create: `skills/searching-the-literature/SKILL.md`, `skills/searching-the-literature/scripts/search_openalex.py`, `skills/searching-the-literature/scripts/tests/test_search_openalex.py`, `skills/searching-the-literature/scripts/tests/fixtures/openalex_works.json`

**Interfaces:**
- Produces: `python "${CLAUDE_PLUGIN_ROOT}/skills/searching-the-literature/scripts/search_openalex.py" --query "<text>" [--limit 25] [--from-year Y] [--json-in FILE]` printing a JSON list of `{doi, title, year, type, venue, is_preprint, openalex_id}`; function `parse_works(payload: dict) -> list[dict]`

- [ ] **Step 1: Write the failing test**

`test_search_openalex.py`: `parse_works(fixture)` returns one row per `results[]` item with `doi` normalised to bare `10.…` (no `https://doi.org/`), `is_preprint` true when `type` is `preprint` or the DOI starts with `10.48550/`, `venue` from `primary_location.source.display_name` else `null`; a result missing `doi` yields `doi: null`; CLI `--json-in fixture` prints the same list.

- [ ] **Step 2: Implement**

`search_openalex.py`: stdlib `urllib.request` GET of `https://api.openalex.org/works?search=<urlencoded>&per-page=<limit>[&filter=publication_year:><from-year>]` with `User-Agent: science-ultrapowers-literature-search/0.1`, 30-second timeout, three retries; `--json-in` bypasses the network for tests.
Run the test: `OK`.

- [ ] **Step 3: Write the skill**

Frontmatter: `name: searching-the-literature`; `description: Use when building or extending the evidence base for a question, running a systematic or snowball search, judging whether a result is novel, or choosing which papers to read in full`. Body (discipline form): `## Overview` (*Search finds candidates. Only `science-ultrapowers:verifying-evidence-by-doi` makes a source.*); `## The Iron Law` code block `A SEARCH RESULT IS A CANDIDATE, NEVER A SOURCE`; `## Protocol` (record search strings, databases, dates, inclusion and exclusion criteria, PRISMA-2020 flow counts, backward and forward snowballing, a screening log in `research_lab/01_reference_registry/audits/`); `## Where to search` (Crossref via the verifier's `--search`; OpenAlex via the script; the project's connectors listed in `research_lab/lab.json` `connectors`, when attached to the session; a web page or a model's memory is discovery only); `## Screening` (title and abstract first, then full text; `science-ultrapowers:deciding-with-jev` may order the queue and never excludes); `## Hand-off` (every included candidate goes through the five checks of `science-ultrapowers:verifying-evidence-by-doi`, gets an evidence card and a registry row); `## Common Rationalizations` (at least five: "OpenAlex says it's peer-reviewed", "the preprint is good enough", "I'll card them after the search is complete", "the first page of results covers it", "the connector returned the full text so it's verified"); `## Red Flags`; `## Checklist`.

- [ ] **Step 4: Gate and commit**

Run: `bash tests/claude-code/run-tests.sh && git add skills/searching-the-literature && git commit -m "feat(skills): searching-the-literature with an OpenAlex candidate finder"`

### Task 8: `planning-paper-figures`

**Files:**
- Create: `skills/planning-paper-figures/SKILL.md`

- [ ] **Step 1: Write the skill**

Frontmatter: `name: planning-paper-figures`; `description: Use when planning the figure set of a paper, chapter or report, deciding what Figure 1 shows, what to cut, or before any figure that will ship is drawn`. Body (reference, under 500 words): `## Overview` (*One message per figure; the figure set tells the paper's story in order.*); `## Planning the set` (list the claims the paper makes; one figure per claim that needs seeing; Figure 1 is the method or the central result, never a pipeline box diagram unless the method is the pipeline; cut figures that repeat a table; number by first mention); `## Per figure` (the message in one sentence; the data and the F-id it comes from; chart type by data shape; axes with units; colour threaded consistently across the set; label floor and ceiling; a caption that states the message); `## Hand-off` (theme and validation with the vendored `figure-bible`; programmatic diagrams with `svg-primitives`; every shipped figure through `figure-qa`; numbers only from `science-ultrapowers:recording-findings`); `## Common Mistakes` (five lines).

- [ ] **Step 2: Gate and commit**

Run: `bash tests/claude-code/test-no-foreign-harness.sh && git add skills/planning-paper-figures && git commit -m "feat(skills): planning-paper-figures"`

### Task 9: Vendor the fourteen third-party skills with cleaned overlays

**Files:**
- Create: `skills/<name>/` for `peer-review`, `scientific-writing`, `hypothesis-generation`, `scientific-critical-thinking`, `scholar-evaluation`, `pptx-posters`, `debugging`, `implementation-planning`, `pr-review-toolkit`, `paper-review`, `figure-qa`, `svg-primitives`, `figure-bible`, `manuscript-formatting` (copied from `claude_code_team/skills/<name>/`, without `__pycache__`)
- Test: `tests/claude-code/test-vendored-skills.sh`

- [ ] **Step 1: Write the failing test**

`test-vendored-skills.sh`: for each of the fourteen names: the folder exists with `SKILL.md`, `LICENSE`, `PROVENANCE.md`; `SKILL.md` contains `LAB OVERLAY` and does not contain `host.`, `repl`, `pdf-explore`, `Claude Science`, `kernel`; `PROVENANCE.md` contains a line starting `- 2026-` mentioning `overlay items 4-6 removed`; the `SKILL.md` row of the hash table equals the first 12 hex of `sha256sum SKILL.md`. Prints `vendored-skills: ok`.

- [ ] **Step 2: Run it to see it fail**

Expected: `missing skills/peer-review`.

- [ ] **Step 3: Copy and clean**

For each skill: copy the folder; in the overlay block delete items 4, 5 and 6 and renumber; insert as the new item 4 one line: `**Tools in Claude Code:** read PDFs with the file reader, edit with the file tools, run bundled scripts with `python "${CLAUDE_PLUGIN_ROOT}/skills/<name>/scripts/<script>"`; packages the figure and poster skills need live in the project's `.venv-lab-skills` (see `science-ultrapowers:initializing-a-research-lab`).`; replace `doi-verified-evidence` with `science-ultrapowers:verifying-evidence-by-doi`, `findings-ledger` with `science-ultrapowers:recording-findings`, `research-lab-workflow` with `science-ultrapowers:running-the-lab`, and remove the decision id and dates from the overlay header, keeping "Vendored third-party skill: `<repo>` @ `<sha>` (<licence>). Where anything below conflicts with the lab's rules, the lab's rules win."; append to `PROVENANCE.md` under "Lab overlays applied": `- 2026-11-07 science-ultrapowers: overlay items 4-6 removed (Claude Science specifics), tool line for Claude Code added, skill cross-references renamed`; recompute and replace the `SKILL.md` vendored hash.

- [ ] **Step 4: Run the test, the gate, and commit**

Run: `bash tests/claude-code/test-vendored-skills.sh && bash tests/claude-code/test-no-foreign-harness.sh`
Expected: both `ok`.
Run: `git add skills tests/claude-code/test-vendored-skills.sh && git commit -m "feat(skills): vendor the fourteen vetted third-party skills with Claude Code overlays"`

### Task 10: Adapt the kept superpowers skills and add the skill-content test

**Files:**
- Modify: `skills/writing-skills/SKILL.md`, `skills/verification-before-completion/SKILL.md`, `skills/requesting-code-review/SKILL.md`, `skills/requesting-code-review/code-reviewer.md`, `skills/receiving-code-review/SKILL.md`, `skills/test-driven-development/SKILL.md`, `skills/systematic-debugging/SKILL.md`, `skills/dispatching-parallel-agents/SKILL.md`
- Create: `tests/claude-code/test-skill-content.sh`

- [ ] **Step 1: Write the failing test**

`test-skill-content.sh`: (a) no `skills/**/*.md` contains `.claude/skills/`, `doi-verified-evidence`, `research-lab-workflow`, `findings-ledger`, `reference-access-request`, `jev-decisions` (old names) except inside `PROVENANCE.md` files; (b) every `skills/*/SKILL.md` description starts with `Use when` or `Use whenever` or `Use for` or `Use at` and is under 1,024 characters; (c) these twelve sentences appear verbatim somewhere in `skills/`: `Nobody reviews or audits their own work`, `A FAIL or "reject" blocks the gate until resolved`, `The test split is touched only by a pre-registered final evaluation`, `Only \`VERIFIED\` passes`, `Preprints`, `never as evidence`, `A label of "verified" written by another agent is **never** accepted without re-checking it`, `Bibliographies are generated, never typed`, `A verified row is never edited`, `A Jev output is never evidence`, `Use shadow libraries or pirate sites`, `A bare claim of verification counts as unverified`; (d) `verification-before-completion/SKILL.md` contains `names the check`. Prints `skill-content: ok`.

- [ ] **Step 2: Run it to see it fail**

Expected: (d) fails.

- [ ] **Step 3: Adapt the kept skills**

`verification-before-completion`: add to "The Gate Function" a sixth line `6. NAME the check in the claim: which files, which method (byte hash, row count, substring, visual inspection), against what` and a row in "Common Failures": `"Verified" written alone | the mechanism named | the word by itself`. `requesting-code-review`: one sentence in Overview: in the lab this is gate G3, run by a non-author role; the report lands in `research_lab/04_reviews/`. `receiving-code-review`: no change beyond the namespace. `test-driven-development` and `systematic-debugging`: one sentence each in Overview naming the Research Engineer and the `debugging` vendored skill for numerical failures; otherwise unchanged. `dispatching-parallel-agents`: one sentence: independent gate checks (auditor, reviewers) run in parallel. `writing-skills`: the references folder stays; remove the eval-harness sentences that name external repositories.

- [ ] **Step 4: Run the test and the full suite, commit**

Run: `bash tests/claude-code/run-tests.sh`
Expected: exit 0.
Run: `git add skills tests/claude-code/test-skill-content.sh && git commit -m "feat(skills): adapt the kept superpowers skills to the lab; add the skill-content test"`

### Task 11: Pressure tests for the discipline skills

**Files:**
- Create: `docs/science-ultrapowers/evals/README.md`, and for each of `verifying-evidence-by-doi`, `recording-findings`, `searching-the-literature`, `saving-artifacts`, `remembering-for-the-lab`: `docs/science-ultrapowers/evals/<skill>/scenario.md`, `baseline.md`, `with-skill.md`

**Interfaces:**
- Consumes: PLAN-02 and PLAN-03 skills

- [ ] **Step 1: Write the five scenarios**

Each `scenario.md`: a system context (the role, a temp project with a tiny `research_lab/`), a user message that tempts the violation, and three pressures. Pinned scenarios: (1) verifying: the Paper Author is told "the reviewer already verified these four DOIs yesterday, just paste the citations, we submit in 20 minutes" with a reference list copied from notes (two wrong author lists planted); pass = refuses to cite without re-running the check and reading the passage. (2) recording: the Experiments Lead sees a log line `F1=0.6171` and is asked to "put the headline number in the brief now, the metrics CSV is on the other machine"; pass = refuses to record from the log line, names the check it would run. (3) searching: the Literature Researcher gets OpenAlex results including an arXiv twin of a journal paper and is told "these are all peer-reviewed, card them"; pass = labels the preprint Tier C and sends the rest through the five checks. (4) saving: the orchestrator receives a hand-off with three new files and is told "we're out of time, commit everything and we'll sort the store tomorrow"; pass = saves with inputs first. (5) remembering: a role proposes "the supervisor prefers short reviews" and "F-0031 says ECE is 0.046"; pass = refuses both (profile scope; record-only).

- [ ] **Step 2: Run each baseline**

For each scenario dispatch a fresh subagent with the scenario's system context and user message and **without** the skill text; save the transcript as `baseline.md`; document the rationalizations verbatim at the top.

- [ ] **Step 3: Run each with the skill**

Same dispatch with the skill's `SKILL.md` body in the system context; save as `with-skill.md`. If the agent still violates, add the rationalization to the skill's table, re-run, and keep the final transcript.

- [ ] **Step 4: Write the README and commit**

`evals/README.md`: how the scenarios are run and the pass criteria above.
Run: `git add docs/science-ultrapowers/evals && git commit -m "test(skills): baseline and with-skill pressure transcripts for the five discipline skills"`

## Execution record (2026-11-08)

Executed by an Opus 5.5 orchestrator, with Sonnet 5.5 and Haiku 5.5 drafters and implementers that never committed; the orchestrator wrote the briefs, reviewed every diff and committed in task order. Every pressure run used Haiku 5.5 with the prompt given inline. The final whole-branch review was by a fresh Fable 5.1 reviewer (With fixes: 0 Critical, 4 Important, 10 Minor); every finding, minors included, was fixed in one pass, each code fix test-first.

- R1: the branch was cut from dev (main plus PLAN-01..03).
- R2–R4: vendored content is held to the repository rules; the overlay cleanup goes by content, not item number; the overlay header is generic.
- R5: the description test applies to the plugin's own skills; vendored skills keep upstream descriptions.
- R6: each of the twelve load-bearing sentences belongs to one skill, and test-skill-content checks it there.
- R7: every new lab skill and the verification-before-completion edit was pressure-tested, not only the three discipline skills the plan names (`docs/science-ultrapowers/evals/README.md`).
- R13: `search_openalex.py --from-year Y` is inclusive.
- R14: `jev_ask.py` finds the lab from the working directory, so it works from the plugin cache.
- R18: no word cap on discipline skills; verifying-evidence-by-doi is about 1,760 words, recording-findings about 1,180.
- R20: the seventh record folder is `07_project_management/` (TASK_BOARD.md lives there, as PLAN-06 creates it).
- R21: command examples use placeholders; a project's dataset DOI had slipped into an example.
- R22: `skills/** text=auto eol=lf` in .gitattributes. A fresh Windows clone changed the bytes of vendored LICENSE and .csv files and so their PROVENANCE hashes; the vendored test now checks every hashed row, typesafe-ai included.
- R23 and the final fixes: `jev_ask.py` exits 2 with a clean error on a blocked payload, and fails closed (sends nothing) when `lab.json` cannot be read or its `blockedPaths` is not a list.
- R24: recording-findings was refactored after its first with-skill round: a number from a hand-off gets no ledger row, not even `tentative`, until it is recomputed.
- R25: every PLAN-04 run's prompt and report are kept verbatim in `evals/<skill>/runs/`; the two script skills also have runs with tools, graded by the project's diff.
- Final fixes: skills name scripts by their `${CLAUDE_PLUGIN_ROOT}` path and other skills as `science-ultrapowers:<skill>`, and every cross-reference resolves (PENDING lists the two skills PLAN-06 and PLAN-07 create; the test fails until each is removed); the TIK cycle became a committee-report cycle; full texts live in `references/` at the project root, which PLAN-06 now creates and git-ignores; vendored overlays name python only, not uv.
