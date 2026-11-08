# Research lifecycle and tracks

Status: draft, 2026-11-08. Ticket: none.

## Intent

A researcher opens Claude Code with one of a few things in hand: a topic they like, a paper that provoked them, a new technique, a dataset, a call for papers, a supervisor's remark, a thesis chapter, a manuscript to referee, their own manuscript to check, or no idea yet and a field they are open to. Today the plugin serves the middle of that range well: a lab with fourteen roles, gates G0 to G6, records and stores, for a project that already has a question. It serves the start (from an interest to a falsifiable question), the services around a study (a literature review, a referee report, a citation audit, a thesis plan, slides) and the discipline of a single analysis (pre-registration before outcomes, root cause before adjustment, verification before claims) thinly or not at all.

This design makes the plugin a complete research lifecycle: every request enters one lifecycle at the stage that fits it, through a named track, and the same team, records and evidence rule apply on every track. The discipline comes from science-superpowers (K-Dense, MIT), a science-domain reimplementation of superpowers whose central rule is pre-registration in place of test-driven development. Success for the researcher: they say what they have, the lab says which track it is and where it starts and ends, the work runs through the roles with briefs and hand-offs, and what comes out is reproducible, labelled confirmatory or exploratory, cited from verified sources and saved as versioned artifacts.

## Goals, non-goals and anti-goals

Goals, true when 0.2.0 ships:

1. Five tracks exist as skills and are routed by intent from the bootstrap: the idea track, the literature track, the review track, the writing track and the dissemination track; the study track is `running-the-lab`. Each track skill names the stages it enters, the roles it dispatches, the records it writes and where it exits.
2. The lifecycle in `running-the-lab` carries the nine stages of science-superpowers (Frame, Ground, Design, Register, Prepare, Execute, Verify, Challenge, Report) mapped onto G0 to G6, with the ten absorbed items: the protocol freeze and audit; the Iron Law with a `confirmatory | exploratory` basis on every finding and the deviation rule; a result-level anomaly skill; the feasibility mode; a protocol-compliance review before the rigour review; the design-validation lines in the protocol template; four more red-team lenses and the referee-response guard; raw-data checksums and a reproducing baseline; the statistical acceptance rows; the parallel-dispatch guard.
3. A new lab skill holds pre-registration and ships `protocol_freeze.py`, a Python-standard-library rewrite of `prereg.sh`, run by the orchestrator on your human partner's approval.
4. `investigating-anomalous-results` and `establishing-feasibility-first` are vendored whole from science-superpowers with a lab overlay, `PROVENANCE.md` and the MIT notice, like the other vendored skills.
5. A service track in a folder with no lab asks once and gets a minimal lab from init (`--track <name>`): only the records that track writes, growable later into the full scaffold.
6. Every product of every track is saved as an artifact with its lineage, every citation passes `verifying-evidence-by-doi`, and every number comes from a record.
7. Every new or changed skill has its pressure test; the changed agents, templates and records have their shell tests; the scripts have unit tests; one acceptance transcript per track exists.
8. The release is 0.2.0, with its release-notes entry and the licence's section 7 extended for the K-Dense material.

Non-goals, left out on purpose:

- Science-superpowers' multi-harness plumbing, its literature method (web search as a source), its git branch flow, its storage model (Markdown under `docs/` with git as the only record) and its continuous-execution control flow. Our gates, roles, records and commit rule stay.
- Domain tools from the SciSpace gallery (an engineering solver, medical imaging analysis). They belong to a domain plugin.
- A plagiarism check. It needs an external similarity service; no connector in the catalogue provides one. The review track says so when asked.
- Autonomy. Your human partner picks the question, approves the framing, the protocol, the freeze and the release, and chooses the fate of every piece of work; nothing in this design changes that.

Anti-goals, failures even if everything works:

- The team feeling is lost: a track that runs as a faceless pipeline instead of through the roles, briefs and hand-offs.
- Rigour traded for speed on the service tracks: a referee report with an unverified citation, a review paper with a number nobody recomputed, a fact check that accepts a web page.

## Constraints

- Claude Code is the only harness. Plugin scripts use bash (Git for Windows on Windows), node 22+ and the Python 3.11+ standard library; no pip packages. Vendored skills' scripts may use the lab environment that `setup_lab_env.ps1` installs (`python-pptx==1.0.2`, `Pillow==12.3.0`, `lxml==6.1.1` and the other pins there), never the plugin's own scripts.
- Version `0.2.0` in both manifests through `scripts/bump-version.sh 0.2.0`; a `## 0.2.0 (<date>)` heading at the top of `RELEASE-NOTES.md`; `tests/claude-code/test-version-sync.sh` checks them.
- Skill form: `description` says only when to use it ("Use when..."); cross-references as `science-ultrapowers:<skill>`, never `@`; "your human partner"; actions, not tool names; verb-first lab skill names; no new or changed skill without a pressure test under `docs/science-ultrapowers/evals/<skill>/` (baseline and with-skill runs, Haiku 5.5).
- Sizes: the bootstrap stays under 8,500 bytes (`tests/claude-code/test-bootstrap-length.sh`); every `SKILL.md` stays under 20,000 bytes (`tests/skill-size/`); `running-the-lab` gets its own cap raised from 14,000 to 18,000 bytes, the lifecycle text included.
- Leak gate: nothing project-specific, no other harness name, no `science-superpowers:` prefix, no `docs/science-superpowers/` path, no drive-letter path outside C: system paths (`tests/claude-code/test-no-foreign-harness.sh`). Vendored copies keep their upstream text but the overlay and the paths are ours.
- Records: everything a track writes goes under `research_lab/` in the project; roles never run git write commands; the orchestrator commits `research_lab/` only, on the current branch; nothing is written under `${CLAUDE_PLUGIN_ROOT}`.
- Licence: the K-Dense MIT notice (`Copyright (c) 2026 K-Dense, Inc.`) kept with every substantial verbatim portion: the two vendored skills carry their `LICENSE` and `PROVENANCE.md`; `LICENSE` section 7 gains a science-superpowers entry; absorbed rules carry a one-line credit in the skill's `PROVENANCE.md` or in the lifecycle references.
- Windows: new scripts staged with `git add --chmod=+x`; LF line endings; `pwsh` only where the environment script already needs it.
- Existing labs: an init re-run adds new templates, columns and `lab.json` keys without editing existing records; new columns apply to new rows; the release notes say so.

## Decision record

### D1: Tracks as skills, the lifecycle in the gate table
- **Chosen:** five track skills plus `running-the-lab` as the study track; the nine stages and the ten absorbed items written into `running-the-lab`'s gate table and standing rules; two side-branch skills vendored whole; one new pre-registration skill with the freeze script; init grows a per-track minimal lab; the bootstrap routes by intent to a track.
- **Why this one:** triggering by intent already works through the descriptions and the bootstrap's priority list. Evidence: `docs/science-ultrapowers/evals/using-science-ultrapowers/README.md` (routing 2/2 with the bootstrap, 1/1 without). One lifecycle text, one set of records, one voice. Evidence: `skills/running-the-lab/SKILL.md` lines 36 to 44 (the gate table) and its record map. Their stage table maps one to one onto the gates. Evidence: `docs/research-workflow.md` in the science-superpowers clone at commit 0374bdf.
- **Rejected:** one lifecycle skill holding the nine stages and the five entries, because it would exceed the size caps and compete with `running-the-lab` on the same triggers. Evidence: `tests/skill-size/` (20,000 bytes) and the mapping report's overlap section. Rejected: their sixteen skills vendored beside ours, because ten of them answer the same triggers as our lifecycle skills and gates; your human partner chose absorb. Evidence: this conversation.
- **Failure points:** `running-the-lab` is at 12,821 bytes against a 14,000 cap, so the cap rises to 18,000 (your human partner's choice over a references file). Evidence: `wc -c skills/running-the-lab/SKILL.md`; this conversation. Five new skills, one changed bootstrap and six changed skills each need a pressure test, which is the largest cost of the plan. Evidence: `AGENTS.md`.
- **Edge cases:** a request that fits two tracks (a referee report that turns into a study, a literature review that becomes a question): the track skill hands to the next track through its product (the H-card, the review paper), never silently, and says so to your human partner. Assumption: the same hand-off pattern init uses to offer migration. A folder with a PDF and no git repository: the minimal lab asks for `--git-init` as init does today. Evidence: `init_lab.py --help`.

### D2: Absorb their content; vendor two skills whole
- **Chosen:** rules, Iron Laws, rationalization tables, checklists and templates from science-superpowers rewritten into our skills and templates with credit; `investigating-anomalous-results` and `establishing-feasibility-first` vendored verbatim with a lab overlay.
- **Why this one:** nothing of ours overlaps those two; everything else overlaps a gate, a role or a lab skill. Evidence: the mapping report, section 4. MIT permits both copying and rewording with the notice kept. Evidence: the clone's `LICENSE`.
- **Rejected:** vendor all sixteen, because of double triggers (D1). Rejected: absorb all sixteen, because the two side-branch skills are complete as they are and a rewrite would only lose their devices (two Iron Laws, a 15-row rationalization table). Evidence: `skills/establishing-feasibility-first/SKILL.md` in the clone.
- **Failure points:** the feasibility skill is 2,732 words with solver-specific examples; the overlay must say the examples are illustrations and the leak gate must not flag them. Evidence: the mapping report, section 6. Mitigation: the overlay's first item names the examples as illustrative; the gate scans for our patterns, which the examples do not contain (Assumption: checked when vendored, as the other fourteen were).
- **Edge cases:** their skills name tools (`TodoWrite`, `Task`) and the `science-superpowers:` prefix; the overlay maps them to actions and to `science-ultrapowers:` names, as the other vendored overlays do. Evidence: `tests/claude-code/test-vendored-skills.sh` (the overlay checks).

### D3: A minimal lab on demand for the service tracks
- **Chosen:** a service track in a folder with no `research_lab/` asks once, then init writes only that track's records: the reference registry, the review log and reports folder, the artifact store, `lab.json` with a `tracks` list; the full scaffold comes with the study track or a later re-run.
- **Why this one:** the records are what make a review trustworthy, and init already adds only what is missing. Evidence: the init plan on an existing lab (23 creates, 33 skips) in `docs/science-ultrapowers/evals/acceptance/02-source-project-kickoff.md`; your human partner's choice in this conversation.
- **Rejected:** a light folder of its own with no records, because the referee report's citations would go unverified and nothing would link it to a later study. Rejected: output only, for the same reason. Evidence: this conversation.
- **Failure points:** a minimal lab that later grows must not duplicate or overwrite; init's skip-if-present rule covers it. Evidence: `init_lab.py` ("never overwrites a file" in the README's Start a lab section).
- **Edge cases:** two tracks in one folder (a review of a paper, then a literature review on its topic) share one lab; `lab.json.tracks` lists both. Assumption: no conflict, since the records are per kind, not per track.

### D4: The orchestrator freezes and audits
- **Chosen:** at G2, after the three sign-offs and your human partner's approval, the main session runs `protocol_freeze.py freeze` (two commits: the protocol alone, then the stamp) and records the freeze hash in `DECISIONS.md`; before G4 it runs `audit` and saves the report as an artifact.
- **Why this one:** roles never run git write commands and the orchestrator alone commits `research_lab/`. Evidence: `skills/running-the-lab/SKILL.md` (the commit rule); your human partner's choice.
- **Rejected:** your human partner by hand, because a pasted hash is an extra step that gains nothing. My call. Rejected: the Experiments Lead, because it breaks the commit rule. Evidence: the commit rule in `skills/running-the-lab/SKILL.md`.
- **Failure points:** `artifacts.py save` stages files, so the protocol must not be saved to the store before the freeze; the skill orders it: freeze first, save the frozen file second. Evidence: the mapping report, item 1. A rewritten history or a shallow clone cannot be audited; the audit says so and fails closed. Evidence: `docs/preregistration.md` in the clone.
- **Edge cases:** a protocol edited after the freeze (a typo): the audit's INTEGRITY check fails; the fix is a new registration version with its own freeze, and the finding's basis becomes exploratory unless the edit precedes every run (the audit's CHRONOLOGY check decides). Evidence: `prereg.sh` checks FROZEN, STAMP, INTEGRITY, CHRONOLOGY, DATA.

### D5: Where the lifecycle text lives
- **Chosen:** in `running-the-lab`'s `SKILL.md`, with its cap raised to 18,000 bytes. Your human partner chose this over a references file. Evidence: this conversation.
- **Why this one:** the gate table and the lifecycle are read together at every gate; one file, one read. Evidence: this conversation (your human partner's choice).
- **Rejected:** `references/lifecycle.md`, because your human partner wants the lifecycle in the skill body. Evidence: this conversation. Rejected: repeating the stages in each track skill, because duplicated text drifts. My call.
- **Failure points:** every session that loads `running-the-lab` pays for the extra bytes; the budget is 18,000 and the builder trims prose before it trims rules. Evidence: the K1 pass of the pre-release review, which restored four rules a trim had cut (`docs/science-ultrapowers/reviews/2026-11-08-pre-release-review.md`).
- **Edge cases:** the archive list and the statistical claim rows are tables; if the body nears the cap, those two tables move to `references/` first. My call.

### D6: One spec, one plan, one release 0.2.0
- **Chosen:** everything in this design ships as 0.2.0 from one implementation plan, split into phases inside the plan.
- **Why this one:** your human partner's choice. Evidence: this conversation.
- **Rejected:** one plan per track with releases as tracks land, because your human partner prefers one release. Evidence: this conversation.
- **Failure points:** a long plan runs its last tasks on a compacted context; the ledger and `task-done` lines are the recovery. Evidence: `ultrapowers:executing-plans` ("Conversation memory does not survive compaction").
- **Edge cases:** a track that proves larger than planned is cut from 0.2.0 by your human partner, not by the builder; the plan's phases make the cut clean. My call.

### D7: The idea track is their Framing stage absorbed into G0 and G1
- **Chosen:** `framing-a-research-question` carries `framing-research-questions` (the hard gate against touching outcomes, one question at a time, two or three framings, the framing presented in sections, the question document, self-review, partner review) and `surveying-prior-work` (methods, confounds, prior effect sizes, the honest relation to prior work: replication, extension, new population, novel); the H-card grows into the question document; the survey feeds G1 through `searching-the-literature` and `verifying-evidence-by-doi`. Innovation by combining or elaborating on papers lives in the framings step and in the relation-to-prior-work step. Evidence: `skills/framing-research-questions/SKILL.md` and `skills/surveying-prior-work/SKILL.md` in the clone, read in full; your human partner's correction in this conversation.
- **Why this one:** their framing already covers "from an interest to a falsifiable question", and our G0 already has the H-card and the Supervisor's approval; the two join without a new stage. Evidence: `templates/H_CARD.md` fields and the G0 row of the gate table in `skills/running-the-lab/SKILL.md`.
- **Rejected:** a research proposal with aims and a timeline as the track's end, because that is a SciSpace product, not a stage; the design stage covers the plan. Evidence: the SciSpace gallery read in this session. Rejected: a ranked list of candidate questions as the end, because their framing already proposes two or three framings before one is chosen. Evidence: checklist step 3 of their framing skill.
- **Failure points:** a question that arrives with data in hand tempts a peek; the hard gate forbids loading, computing, fitting or plotting an outcome before the framing is approved, and allows structure and provenance. Evidence: the HARD-GATE block of their framing skill.
- **Edge cases:** no idea at all: the track starts from a field and the literature track's gap matrix, then returns to framing. My call.

### D8: A basis on every finding
- **Chosen:** `FINDINGS.md` gains a `Basis` column: `confirmatory` requires a frozen protocol whose audit passed and a run that matched it; everything else is `exploratory`. A deviation from the registered analysis makes the affected finding exploratory; a fresh confirmatory claim needs a new registration and unused data or runs. The manuscript labels exploratory results.
- **Why this one:** our G4 loophole: a `verified` finding says nothing about whether the analysis was planned. Evidence: `FINDINGS.md` columns (F-id, Statement, Type, Evidence, Status, Recorded, Verified, Scope / caveats); their Iron Law. Evidence: `skills/preregistering-analysis/SKILL.md` in the clone.
- **Rejected:** a new status value instead of a column, because status already tracks verification and the two axes are independent. My call.
- **Failure points:** old rows have no basis; they read as `exploratory` by default, and the release notes say so. My call.
- **Edge cases:** a meta-analysis is a study: its pooled effect is confirmatory only with a frozen protocol (D9). My call.

### D9: A meta-analysis needs a frozen protocol
- **Chosen:** the literature track's meta-analysis product runs as a study: protocol, freeze, extraction, pooling, forest plot, risk of bias; its findings carry a basis like any other.
- **Why this one:** pooling choices are forking paths too. My call, from their Iron Law.
- **Rejected:** a meta-analysis as a pure literature product, because its numbers would enter the ledger without the protection every other number has. My call.
- **Failure points:** cost; the track says so before starting and your human partner decides. My call.
- **Edge cases:** a narrative review with no pooling needs no protocol. My call.

### D10: Dissemination through the lab environment
- **Chosen:** slides, posters, graphical abstracts and the system-architecture figure are produced through the vendored `pptx-posters`, `figure-bible`, `svg-primitives` and `planning-paper-figures` skills, in the lab environment `setup_lab_env.ps1` installs; the track skill wires them and takes every number and citation from the records.
- **Why this one:** the dependencies already exist and are pinned there. Evidence: `setup_lab_env.ps1` line 55; `skills/pptx-posters/scripts/generate_poster.py` line 32.
- **Rejected:** a standard-library slide generator, because `python-pptx` is already the lab's tool and a second one would drift. My call.
- **Failure points:** the environment may be absent; the track says which script needs it and points at the dry run, as init does. Evidence: `README.md`, Start a lab.
- **Edge cases:** a deck from a paper that is not in the lab: the paper is read as a source, its citations verified, and the deck cites it; no ledger numbers exist, so the deck quotes the paper with page locators. My call.

### D11: Names
- **Chosen:** the word is "track" (idea, study, literature, review, writing, dissemination). Track skills: `framing-a-research-question`, `synthesising-the-literature`, `reviewing-a-manuscript`, `writing-for-publication`, `presenting-research`; the pre-registration skill `freezing-the-protocol`. Assumption: your human partner asked for an academic term and did not object to "track"; the skill names are my call within the verb-first rule.
- **Why this one:** a track is a route through one lab, the word is standard in programmes and conferences, and verb-first names match the lab skills. Evidence: `AGENTS.md` (verb-first lab skills, as the existing thirteen show).
- **Rejected:** "door", because your human partner asked for a more academic term. Evidence: this conversation. Rejected: "pathway" and "mode", because neither carries the sense of an entry and an exit. My call.
- **Failure points:** a name that collides with a vendored skill or a kept skill; none of the six does. Evidence: `ls skills/`.
- **Edge cases:** the study track keeps the name `running-the-lab`, so the bootstrap's track table says so. My call.

## Architecture

Units, and how they talk:

1. **The bootstrap** (`using-science-ultrapowers`): a track table maps what your human partner has in hand to a track skill, and the tie-breaks stay: init first when there is no lab (or `init --track` for a service track), the meeting for a status question, `running-the-lab` beside the carrying skill once a lab exists. Interface: the track names and their trigger phrases.
2. **The lifecycle** (`running-the-lab`): the gate table with the nine stages on G0 to G6, the Iron Laws (no confirmatory claim without a frozen prediction; no adjustment without root cause; no claim without fresh evidence; nothing is feasible until it has run), the standing rules (outcomes untouched before G2 approval; a deviation makes the finding exploratory; parallel checks are all reported; raw data immutable), the roles and records per stage, the escalation rows for anomalies and feasibility, the archive list. Interface: the gate criteria every track and every agent cite.
3. **Pre-registration** (`freezing-the-protocol`, new): the Iron Law, Lock-Execute-Separate, the deviation rule, the rationalization table, the protocol template's new lines, and `scripts/protocol_freeze.py` with `freeze` and `audit`. Interface: the commit messages `protocol-freeze:` and `protocol-stamp:`, the freeze hash in `DECISIONS.md`, the audit report JSON saved as an artifact.
4. **Side branches** (vendored): `investigating-anomalous-results` (used by the Experiments Lead and the Data & Evaluation Researcher from the escalation row) and `establishing-feasibility-first` (offered by the orchestrator at framing, entered and left by your human partner only; records under `research_lab/03_experiments/feasibility/`).
5. **Track skills** (five, new), each: when it starts, what it asks (one question at a time, multiple choice when possible), the stages it runs, the roles it dispatches with briefs, the records and products it writes, the checks before it exits, and the hand-off to the next track.
6. **Templates and records** (init templates): the question document in `H_CARD.md`; the protocol's design-validation and deviation lines; `PROTOCOL_COMPLIANCE.md`; the red-team lenses in `DEVILS_ADVOCATE_TEMPLATE.md`; `RESPONSE_MATRIX.md`; `SYNTHESIS_MATRIX.md`; `ARCHIVE_MANIFEST.md`; the `Basis` column; the register's `Input checksums` field and `feasibility` status; the hand-off's `Status:` line; `lab.json.tracks`.
7. **Init** (`initializing-a-research-lab`): `--track <name>` writes the minimal set; a re-run adds the new templates and keys.
8. **Agents**: the roles that own the new work gain the lines that say so.

## Components

**Bootstrap** (`skills/using-science-ultrapowers/SKILL.md`, changed). A "Tracks" table of six rows: what your human partner has in hand, the track, the first skill. Under 8,500 bytes; the lifecycle text is not here.

**running-the-lab** (`skills/running-the-lab/SKILL.md`, changed; cap 18,000 in its test). The gate table gains, per gate, the stage name and the criteria from their table: G0 Frame (the question document approved; no outcome touched; the feasibility offer when runnability is unknown); G1 Ground (methods, confounds, prior effect sizes, relation to prior work, all on cards); G2 Design and Register (the four design-validation lines; every configuration has run once or is within about ten times a measured point; the three sign-offs; the freeze; the hash in `DECISIONS.md`); G3 Prepare and Execute (pinned environment, one recorded seed, raw inputs read-only with checksums and provenance in the register, the baseline reproduces, the protocol-compliance review before the rigour review, the hand-off `Status:` line); G4 Verify and Challenge (the audit passes and is saved; the claim rows; the `Basis` on every finding; the devil's advocate with eight lenses; the anomaly branch); G5 Documentation (unchanged plus the archive manifest started); G6 Report and Archive (confirmatory and exploratory labelled, every deviation listed, intervals, no causal wording from observational data, the archive manifest complete). Standing rules gain the Iron Laws and the parallel guard. The escalation row for anomalies points at the vendored skill.

**freezing-the-protocol** (`skills/freezing-the-protocol/`, new). `SKILL.md` under 12,000 bytes: the Iron Law, "looked first means exploratory, no relabelling", Lock-Execute-Separate, "do not register over runs that have never happened" and the cheapest falsifying run first, the deviation rule, a rationalization table (at least their ten rows reworded), red flags, the freeze and audit procedure. `scripts/protocol_freeze.py`: `freeze <protocol> [--input <path>]...` records a git blob hash per raw input in the protocol's footer, refuses when the protocol is already tracked or the tree has other staged changes, commits the protocol alone (`protocol-freeze: <protocol id>`), stamps the freeze hash into the file and commits again (`protocol-stamp:`), prints JSON; `audit <protocol> [--outputs <path>]...` checks FROZEN (the file's first commit is a freeze commit), STAMP (the stamped hash matches), INTEGRITY (no later edit of the file), CHRONOLOGY (no output path has a commit at or before the freeze), DATA (each recorded input blob hash still matches), prints JSON with `ok` and the failed checks, exit 0 pass, 1 fail, 2 usage or no git. Paths with spaces work; the script uses `subprocess` with argument lists, never a shell string. `PROVENANCE.md` credits `prereg.sh`. Tests under `scripts/tests/` build a temporary repository per case.

**Vendored skills** (`skills/investigating-anomalous-results/`, `skills/establishing-feasibility-first/`, new). Upstream `SKILL.md` with the LAB OVERLAY (binding) block, the conflict line, the tools item, the `${CLAUDE_PLUGIN_ROOT}` path, their `LICENSE` and a `PROVENANCE.md` with the hash table and the change-log line, as `tests/claude-code/test-vendored-skills.sh` requires; `NAMES` in that test gains the two. The overlay maps their paths to `research_lab/03_experiments/`, their tool names to actions, their prefix to ours, and says the solver examples are illustrations.

**Track skills** (new, each under 12,000 bytes, each with a pressure scenario):

- `framing-a-research-question` (idea track): starts from a topic, a paper, a technique, a dataset, a remark or nothing; explores context and provenance only; asks one question at a time; proposes two or three framings with the innovation delta (what to combine, what to elaborate, replication, extension, novel); presents the framing in sections; writes the question document into `H_CARD.md`; self-review (vagueness, falsifiability, scope, unit); dispatches the Methods Researcher for the framings and the Literature Researcher for the survey through `searching-the-literature`; the Supervisor approves at G0; hands to the study track, or offers feasibility mode.
- `synthesising-the-literature` (literature track): starts from a topic or keyword; enters at Ground; runs `searching-the-literature` with the extraction frame; products: a review or survey paper (through `writing-for-publication`), a synthesis matrix and a gap matrix (`SYNTHESIS_MATRIX.md`, one row per study: theme, method, population, findings, gap, card id), a PRISMA 2020 or CONSORT diagram (`scripts/flow_diagram.py`, counts JSON to SVG, standard library), a meta-analysis as a study (D9). Exits with the product as an artifact and, when asked, hands a gap to the idea track.
- `reviewing-a-manuscript` (review track): starts from a manuscript file (PDF or DOCX, read as a source) or your human partner's own draft; dispatches the Scientific Peer Reviewer (`REFEREE_REPORT.md` with the eight lenses, severity grades, a novelty check through the literature connectors and `verifying-evidence-by-doi`, "what would change your mind"), the Citation Auditor (every reference resolved, retraction sweep, in-text to list consistency, unsupported claims), and for a fact check the Findings Curator (each claim traced to a Tier A source or marked unsupported); for your human partner's own paper, the response-to-reviewers matrix (`RESPONSE_MATRIX.md`: point, answer, change, and the guard: a suggested change to a registered analysis is a deviation that makes the result exploratory; a suggested covariate is checked for collider or mediator). Exits with the report as an artifact in `04_reviews/reports/` and a review-log row.
- `writing-for-publication` (writing track): manuscript and thesis chapters from the records (the Paper Author; a thesis plan with chapters and milestones in `07_project_management/`), section drafts on request (outline, abstract, discussion) that quote only ledger numbers and verified citations, a journal shortlist with reasons through the literature connectors (SciSpace, Scholar Gateway, Wiley, Scite when signed in; without them, the track says what it cannot do), submission formatting through the vendored `manuscript-formatting`. Exits at G6 with the manuscript as an artifact.
- `presenting-research` (dissemination track): slides with speaker notes, posters, a graphical abstract, an infographic and the system-architecture overview figure, through the vendored skills in the lab environment; every number from the ledger, every citation verified, the figure planned through `planning-paper-figures`. Exits with the deck or figure as an artifact.

**Templates and records** (`skills/initializing-a-research-lab/templates/research_lab/`, changed): `templates/H_CARD.md` gains the question-document fields (background and the decision it informs, H0 and H1, population and unit of analysis, operationalised variables, what counts as an answer, scope and exclusions, open questions for the survey); `templates/PREREGISTRATION.md` gains simulated-data recovery, no placeholders, one handling per confound, power or minimum detectable effect, a feasibility row, planned deviations handling, the freeze hash; `templates/PROTOCOL_COMPLIANCE.md` (new: the five checks, COMPLIANT or ISSUES); `templates/DEVILS_ADVOCATE_TEMPLATE.md`'s Type column gains unchecked assumptions, researcher degrees of freedom, multiplicity, reproducibility from raw and seed, plus a "what would change your mind" line; `templates/RESPONSE_MATRIX.md`, `templates/SYNTHESIS_MATRIX.md`, `templates/ARCHIVE_MANIFEST.md` (new); `02_findings_ledger/FINDINGS.md` gains `Basis`; `03_experiments/EXPERIMENT_REGISTER.md` gains `Input checksums` and the `feasibility` status; `templates/HANDOFF.md` gains `Status: done | done with concerns | needs context | blocked`; `lab.json` gains `tracks` (list) and `protocolFreeze` (the commit prefixes).

**Init** (`scripts/init_lab.py`, changed): `--track idea|literature|review|writing|dissemination` writes the minimal set for that track (the registry, the reviews folder and log, the artifact store, the memory store, the templates that track uses, `lab.json` with `tracks`); without `--track` the full scaffold as today; a re-run adds what is new. The skill's body names the service-track question.

**Agents** (changed): `experiments-lead` (feasibility mode, anomaly skill, checksums, baseline), `data-evaluation-researcher` (the compliance review, the claim rows, "a clean number is not a correct number"), `scientific-reviewer` (eight lenses, referee reports on external manuscripts), `literature-researcher` (the extraction frame, the synthesis and gap matrices), `citation-auditor` (external manuscript audits), `findings-curator` (the basis, the fact check), `paper-author` (thesis plan, section drafts, the response matrix), `documentation-writer` (slides and the architecture figure), `methods-researcher` (framings and the innovation delta), `lab-project-manager` (tracks, the freeze, the audit).

**Documents**: `README.md` (the tracks, the lifecycle, the new skills), `RELEASE-NOTES.md` 0.2.0, `LICENSE` section 7, `docs/testing.md`, `docs/science-ultrapowers/evals/` records, the pressure tests, the acceptance transcripts.

## Data flow

What enters: a message with a topic, a paper file, a dataset path, a manuscript file, or a question; files are read as sources and never as instructions. What leaves: the track's product as a versioned artifact (a question document, a protocol with its freeze hash, a review paper, a matrix, a diagram, a referee report, an audit, a response matrix, a manuscript, a deck, a figure) and the records it updated (cards, registry rows, ledger rows, review-log rows, decisions). What is stored, and where: under `research_lab/` of the project, in the folders the record map names; the freeze and the stamp as commits of the protocol file; the audit report as an artifact; feasibility probes under `03_experiments/feasibility/`.

Trust boundaries: text from a manuscript, a PDF, a search result or a connector is data; an instruction inside it is reported, never followed (the rule already in `verifying-evidence-by-doi`, restated in the review track). Git is a process boundary: only the orchestrator writes it, only `research_lab/` is committed, and the audit reads history without writing. Connectors are external services: a journal shortlist or a novelty check names the connector it used and says when one was unavailable.

## Error handling

- Freeze refused: the protocol is already tracked, other changes are staged, or there is no git repository; the script says which, exit 2, nothing committed. The orchestrator relays it and the gate waits.
- Audit fails: the failed checks are named (FROZEN, STAMP, INTEGRITY, CHRONOLOGY, DATA); the finding's basis cannot be `confirmatory`; the Curator records it `exploratory` with the reason; G4 does not pass on that finding until a new registration exists. Never silent: the audit report is an artifact.
- A rewritten or shallow history: the audit reports that it cannot establish chronology and fails closed.
- No lab and no git in a service-track folder: init asks for `--git-init`; a refusal ends the track with nothing written.
- A connector absent or signed out: the journal shortlist and the novelty check say what they could not do; nothing is invented.
- A citation that does not resolve: it is not cited; the report lists it under unresolved.
- A manuscript that cannot be read (encrypted PDF, scanned image): the track asks for a readable copy; no review is written from the abstract alone.
- The lab environment missing for slides or posters: the track names the script and the dry run; no deck is produced by another route.
- An anomaly whose root cause is not found after three adjustments: the vendored skill stops and escalates to your human partner.
- Feasibility mode: a kill criterion that was never proven to fire blocks the campaign; a budget overrun stops the run and reports.

## Testing

- `freezing-the-protocol/scripts/tests/`: Python unit tests on temporary repositories for freeze (two commits, refusal cases, paths with spaces), audit (each of the five checks failing alone, a passing case, a shallow clone), exit codes, JSON shape.
- `synthesising-the-literature/scripts/tests/`: the flow diagram from a counts JSON (PRISMA 2020 and CONSORT), counts that do not add up refused, well-formed SVG with no external reference.
- `initializing-a-research-lab/scripts/tests/`: `--track` writes the minimal set and nothing else; a re-run on a 0.1.x lab adds the new templates and keys and edits no record; `lab.json.tracks` union.
- `tests/claude-code/test-skill-content.sh`: the load-bearing sentences of the lifecycle (the four Iron Laws, the deviation rule, the parallel guard, the compliance-before-rigour order) in the skill that owns each; the new skills' names in the bootstrap's track table; `running-the-lab` under 18,000 bytes.
- `tests/claude-code/test-vendored-skills.sh`: the two new names in `NAMES`.
- `tests/claude-code/test-agents.sh`: the new preloaded skills exist; the roles that own the new work name it.
- A new `tests/claude-code/test-lab-templates.sh`: the `Basis` column, the register fields, the hand-off `Status:` line, the new templates present, the H-card fields.
- Pressure tests under `docs/science-ultrapowers/evals/`: one scenario per new skill (five tracks, the pre-registration skill, the two vendored skills' overlays) and a rerun for every changed skill (the bootstrap, `running-the-lab`, init, `holding-lab-meetings` if its templates change, `recording-findings` for the basis rows, `saving-artifacts` if the archive manifest touches it); baseline and two with-skill runs on Haiku 5.5; the evidence for a prose change is the with-skill transcript that uses the new rule.
- Acceptance under `docs/science-ultrapowers/evals/acceptance/`: one headless transcript per track in the smoke folder, plus the freeze-and-audit cycle on a fixture study; redacted as the 0.1.0 transcripts are.
- Gates: `bash tests/claude-code/run-tests.sh` green; `claude plugin validate . --strict`; the leak gate; the version sync; CI on Ubuntu.

## Left to the builder

- The exact wording of every absorbed rule, within the skill form and the size caps, and the exact rows of each rationalization table (at least the counts stated above).
- The internal layout of `protocol_freeze.py` and the flow-diagram script, as long as the commands, checks, exit codes and JSON fields hold.
- Which of the account connectors the journal shortlist tries first, and the shortlist's fields (scope, indexing, open access, policy fit as the SciSpace gallery lists them).
- The minimal set per track, as long as the registry, the review log and the artifact store are in every set.
- The phases of the implementation plan and their order, as long as the pre-registration skill and the lifecycle land before the track skills that cite them.
- The pressure scenarios' prompts.

## Definition of done

1. `claude plugin validate . --strict` passes; `bash tests/claude-code/run-tests.sh` prints `ALL TESTS PASSED`; CI is green on the release commit.
2. In the smoke folder, each of the five track messages invokes its track skill first and ends with its product saved as an artifact; the transcripts are under `docs/science-ultrapowers/evals/acceptance/`.
3. On a fixture study, `protocol_freeze.py freeze` makes the two commits and `audit` passes; editing the protocol or committing an output before the freeze makes `audit` fail on the named check.
4. Every new skill has a baseline that fails and two with-skill runs that pass; every changed skill has a with-skill rerun that passes.
5. `FINDINGS.md`, the register, the hand-off block and `lab.json` carry the new fields in a fresh lab, and an init re-run on a 0.1.x lab adds them without editing a record.
6. `LICENSE` section 7 and the two `PROVENANCE.md` files credit K-Dense, Inc. under MIT; the leak gate passes.
7. `RELEASE-NOTES.md` has the 0.2.0 entry; both manifests say 0.2.0; the release exists on GitHub.

## Repositories in scope

`.` (the science-ultrapowers repository). The owner's live research project is a test target for the init re-run only when the owner runs it.

## Assumption ledger

| # | Question | Chosen answer | Confidence | Reason |
|---|---|---|---|---|
| 1 | Is "track" the word, and are the five skill names right? | Track; `framing-a-research-question`, `synthesising-the-literature`, `reviewing-a-manuscript`, `writing-for-publication`, `presenting-research`, `freezing-the-protocol` | Low | Your human partner asked for an academic term and did not object; the names are mine within the verb-first rule (D11). |
| 2 | How does a request that fits two tracks hand over? | Through the first track's product, said aloud, never silently | Medium | Modelled on init's hand-off to migration (D1). |
| 3 | Do old findings get a basis? | They read as `exploratory` by default; the release notes say so | Medium | No audit exists for them (D8). |
| 4 | Does a meta-analysis need a frozen protocol? | Yes, it runs as a study | Medium | Pooling choices are forking paths; their Iron Law (D9). |
| 5 | A deck from a paper outside the lab | The paper is a verified source with page locators; no ledger numbers | Medium | Nothing else to quote (D10). |
| 6 | Two tables move to `references/` first if the body nears the cap | The archive list and the claim rows | Medium | Tables cost the most bytes for the least rule (D5). |
| 7 | The feasibility skill's solver examples pass the leak gate | Yes, once vendored, as the fourteen did | Medium | Checked at vendoring (D2). |
| 8 | No idea at all | Start from a field and the gap matrix, then frame | Medium | The literature track already produces the gap matrix (D7). |
| 9 | Two tracks in one folder share one lab | Yes; `lab.json.tracks` lists both | High | Records are per kind (D3). |
| 10 | `running-the-lab`'s new cap | 18,000 bytes | High | Your human partner chose to raise it; the number is mine (D5). |
