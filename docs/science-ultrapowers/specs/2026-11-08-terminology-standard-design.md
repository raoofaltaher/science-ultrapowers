# Terminology standard and scholarly output style

Status: draft, 2026-11-08. Ticket: none.

## Intent

A PhD researcher reads a skill, an agent's report, a template or the README and meets G0, a ledger, a hand-off, a freeze, an orchestrator, a devil's advocate and nine senses of "verify". The vocabulary came from software teams and from the template the plugin was built on. It is confusing, it is not the language of research, and it shapes what the roles write back: a skill that says "gate" produces reports that say "gate". This design gives the plugin one controlled vocabulary of research terms, each defined once with its source, the way ASD-STE100 gives technical writers one approved word per meaning, and a scholarly output style that applies the same vocabulary and writing rules to every answer the plugin's sessions give.

Success: a researcher reads any plugin text and recognises every term from research practice (preregistration, literature, evidence record, findings log, adversarial review, task report); every term has one meaning and one spelling; codes name nothing; a test refuses a not-approved term before it ships; and the roles write in the same register.

## Goals, non-goals and anti-goals

Goals, true when 0.2.0 ships:

1. A terminology standard at `docs/science-ultrapowers/terminology.md` in two parts, modelled on ASD-STE100: Part 1, the writing rules; Part 2, the controlled dictionary (approved terms with a conceptual definition, the meaning in this plugin, the operational form where one exists, the neighbours it must not be confused with, and the source), followed by the not-approved list with the approved replacement for each.
2. Every plugin text follows it: the thirteen lab skills, the lab addenda on the kept engineering skills and on the vendored skills (their upstream bodies stay verbatim), the fourteen agents, the templates and records, the README and contributor documents, the hooks' printed lines, and the scripts' messages and option names.
3. The seven stages are named Question, Literature, Preregistration, Execution, Results, Reporting, Publication, with no code anywhere; the review that ends a stage is its stage approval.
4. The record folders and files carry plain names; identifiers carry readable prefixes expanded in every table header; status values are lower-case words in one style; the spelling is American English; every abbreviation is expanded at first use.
5. The overloaded words are split: verified (a recomputed finding only), matched (a DOI whose metadata matched), checked (any re-run, with its mechanism), reviewed (a role's judgment only), audit (the citation audit only), record (the noun only).
6. Init migrates an existing lab to the new folder, file and header names in a shown plan, and renames nothing it does not list; the researcher's own data in rows is never edited except the id prefixes in headers.
7. A scholarly output style, `output-styles/scholarly-explanatory.md`, ships in the plugin; init installs it as a new file and prints the one-line settings change; its rules are Part 1 of the standard plus the scholarly register (claims matched to evidence, hedging matched to design, confirmatory and exploratory labelled, numbers from records, terms defined at first use).
8. A test, `tests/claude-code/test-terminology.sh`, fails on any not-approved term, any stage code, any British spelling from the list, and any unexpanded abbreviation from the list, in the plugin's own text.
9. The lifecycle design and plan are rewritten in the standard's vocabulary before the lifecycle tasks run, so the lifecycle is built in the new words from the start.

Non-goals:

- Changing the upstream text of the fifteen vendored skills (their licences and provenance require verbatim copies; only our addendum block changes).
- Changing product and tool names (Claude Code, Claude Science, Jev, Crossref, OpenAlex, DOI, git, Git LFS, PRISMA, CONSORT, CRediT and the connectors).
- Changing the plugin's and the skills' names on the marketplace (`science-ultrapowers`, `saving-artifacts`, `running-the-lab`, and so on); a skill's name is an address, and a rename breaks every installed reference. The one exception is the agent ids, which the researcher sees as role names (goal 3 of the lifecycle design depends on them).
- Rewriting the pressure-test records and the acceptance transcripts under `docs/science-ultrapowers/evals/`; they are history and the test exempts them.
- A general controlled dictionary of English, as ASD-STE100 has; the standard controls the plugin's own terms and the writing rules, not the researcher's prose.

Anti-goals:

- A rename that breaks an existing lab: a researcher updates the plugin and their records stop being found. Every path change ships with its migration and its test.
- A standard nobody reads: the dictionary must be the shortest text that settles each term, and the test is what enforces it, not a reader's memory.
- Losing the devices: the binding rules, the warning signs and the rationalization tables keep their function under their new names.

## Constraints

- Claude Code only; plugin scripts in bash, node 22+ and the Python 3.11+ standard library; nothing under `${CLAUDE_PLUGIN_ROOT}`; the leak gate passes; executable bits on new scripts; LF line endings.
- The standard's form: Part 1 rules numbered R1 to Rn in sections (words, grammar, sentences, structure, names, numbers and identifiers, abbreviations, spelling); Part 2 entries in one table per domain (lifecycle, sources and evidence, findings and records, archive, team and coordination, lab memory, contributor vocabulary), columns: Term | Meaning in this plugin | Operational form | Not to be confused with | Replaces | Source. Definitions of at most four sentences (the FORRT rule). Sources cited by name and year: Parsons et al. 2022 (FORRT glossary), the TOP Guidelines (Center for Open Science), Nosek et al. 2018 (preregistration), the Registered Reports model (COS), OSF registration help, ANSI/NISO Z39.104-2022 (CRediT), PRISMA 2020 (Page et al. 2021), CONSORT 2010 and its pilot and feasibility extension, SPIRIT 2013, CASP checklists, Podsakoff et al. 2016 (concept definitions), Spafford's dissertation guidance (Purdue), CASRAI's operationalization guide, ASD-STE100 Issue 9 (2025), ISO 24495-1:2023, ISO 704.
- The vocabulary decisions of this conversation are binding and listed in D2 to D12 below; the builder adds terms to the dictionary but changes none of these.
- Version 0.2.0 for both the terminology and the lifecycle; one release-notes entry under `## 0.2.0`.
- AGENTS.md changes with the standard: "the researcher" replaces "your human partner" as the deliberate term; "a skill's description says only when to use it" stays; "no new or changed skill without a pressure test" stays; a new rule: "every term is in the terminology standard; `tests/claude-code/test-terminology.sh` enforces the not-approved list".
- The vendored skills' upstream text keeps "your human partner" and its own words; the test scans only our text (the addendum block of a vendored skill is ours).

## Decision record

### D1: A two-part controlled vocabulary with a test, modelled on ASD-STE100
- **Chosen:** one document in two parts (writing rules; a controlled dictionary with a not-approved list), one output style that applies Part 1, one shell test that enforces the not-approved list, and a rename of every plugin text to the dictionary.
- **Why this one:** ASD-STE100 is the proven shape for a controlled vocabulary: "a set of writing rules and a controlled dictionary", "each word has only one meaning and is approved with only one part of speech", technical names allowed outside the dictionary. Evidence: asd-ste100.org About and FAQ pages read 2026-11-08 ("53 writing rules in 9 sections", "approximately 900 words", Issue 9, January 2025). Research has no single equivalent; the closest are discipline vocabularies (ACM CCS, the IEEE Thesaurus) and the open-science glossaries (FORRT), so the plugin needs its own, sourced term by term. Evidence: the pasted standards survey in this conversation; the FORRT glossary page (Parsons et al. 2022, Nature Human Behaviour 6, 312-318). The definition method follows Podsakoff et al. 2016 (conceptual clarity, necessary attributes, differentiation), Spafford (one term one way; define a new term before first use; cite a published definition for a standard term), CASRAI (construct, conceptual definition, operational definition, indicator). Evidence: the Purdue and CASRAI pages read 2026-11-08; the Podsakoff abstract from Crossref.
- **Rejected:** adopting APA Style or the IEEE Editorial Style Manual as the standard, because each is a publication style with no controlled research vocabulary (the APA page read 2026-11-08 lists Paper Format, Citations, Mechanics, Bias-Free Language, Grammar; no terminology section). Rejected: an ISO 704 terminology project, because ISO 704 is the method for terminology work, not a vocabulary; the standard follows its principles (one concept, one designation; definitions by intension) without claiming conformance. Evidence: ISO 704's scope as known; the page was not fetchable.
- **Failure points:** a dictionary that drifts from the text. Mitigation: the test is the dictionary's enforcement, and the not-approved list is generated from the dictionary file by the test itself (one source). A rename that misses a script message or an option name. Mitigation: the audit's inventory is the checklist and the test scans scripts' help strings too. Evidence: the two terminology audits in this session (the `tool-results` record and the second audit).
- **Edge cases:** a research term that also has a software sense in the kept engineering skills (merge, commit, branch, refactor): those skills keep their engineering vocabulary inside their own text; the standard governs lab text and the addenda. My call. A vendored skill's upstream word on the not-approved list (ledger, hand-off): the test exempts upstream bodies by the `LAB OVERLAY` boundary. My call.

### D2: Stage names and stage approval
- **Chosen:** Question, Literature, Preregistration, Execution, Results, Reporting, Publication; the review that ends a stage is its stage approval ("the Preregistration approval"); no stage code anywhere. Evidence: this conversation.
- **Why this one:** one noun each from research practice; Registered Reports show the two halves (Stage 1 before data, Stage 2 after) and the standard says so in the Preregistration entry. Evidence: the COS Registered Reports page read 2026-11-08.
- **Rejected:** keeping codes beside names, because a code is what the researcher objected to. Rejected: the Registered Reports two-stage form alone, because seven approvals carry more information than two. Evidence: this conversation.
- **Failure points:** "Results" collides with a manuscript's results section. Mitigation: the dictionary entry says "the Results stage" in full where the section is near. My call.
- **Edge cases:** the review toolkit table maps vendored skills to stages by name. My call.

### D3: Registration vocabulary
- **Chosen:** preregistration (no hyphen, OSF and COS spelling), register the protocol, a registered protocol, time-stamped, the registration check; the script `preregister.py register | check`; commit trailers `Preregistration:` and `Preregistration-Timestamp:`; the file line `Registered at commit:`. Nothing is called a freeze. Evidence: this conversation; the OSF help page ("a time-stamped, read-only version of your study plan", "a registration is a frozen version of your project that can never be edited"), read 2026-11-08.
- **Why this one:** the act in the standards is registration; "frozen" is OSF's description of the state, not the verb. Evidence: as above.
- **Rejected:** "pre-registration" with the hyphen, because OSF, COS and FORRT write it closed. Evidence: the FORRT entry list and the OSF page. Rejected: "freeze", because it is a software metaphor. Evidence: this conversation.
- **Failure points:** the lifecycle plan is written with freeze vocabulary; it is rewritten before it runs (goal 9). Evidence: `docs/science-ultrapowers/plans/2026-11-08-research-lifecycle.md`.
- **Edge cases:** the registration check's five items keep their machine names in the script's JSON (`registered`, `timestamp`, `unaltered`, `chronology`, `inputs`) and the prose uses the words. My call.

### D4: Folders and files
- **Chosen:** `research_lab/project/` (PROJECT_BRIEF.md), `literature/` (SOURCES.csv, EXCEPTIONS.md, evidence_records/, search_logs/, citation_audits/), `findings/` (FINDINGS_LOG.md, KEY_RESULTS.md, LAB_NOTEBOOK.md), `experiments/` (EXPERIMENT_REGISTER.md, preregistrations/, feasibility/), `reviews/` (REVIEW_LOG.md, reports/), `requests/` (ACCESS_REQUESTS.md), `decisions/` (DECISION_LOG.md, lab_meetings/), `planning/` (WORK_PLAN.md, ROADMAP_STATUS.md, RISK_REGISTER.md), `automation/` (JEV_CALLS.jsonl, thresholds.json), `tool_vetting/`, `templates/`, `artifacts/` (archive/ in place of store/, the four tables), `memory/`, `migration/`, `.working/` in place of `.scratch/`; templates renamed: HYPOTHESIS_RECORD.md, TASK_REPORT.md, ADVERSARIAL_REVIEW.md, INTERNAL_REVIEW.md, SESSION_OPENING.md, SESSION_CLOSE.md, and the rest unchanged. Evidence: this conversation (rename with an init migration).
- **Why this one:** the numbers were sort keys that read as stage codes beside the stage codes; the audit found `02_` findings before `03_` experiments and `08_` and `09_` as support folders. Evidence: the second terminology audit, section 6.
- **Rejected:** keeping the numbers on disk, because a path is text the researcher reads. Rejected: renumbering, because a number stays a code. Evidence: this conversation.
- **Failure points:** every path in skills, agents, scripts, tests and the lifecycle design changes; an existing lab must be migrated. Mitigation: init's migration plan lists every rename (`rename <old> -> <new>`), applies with `--yes`, moves with `git mv` when the lab is tracked, and refuses when both old and new exist; the migrate script writes the new layout; the tests use the new paths. Evidence: `init_lab.py` plan and apply structure (`build_plan`, `apply_plan`).
- **Edge cases:** a lab that renamed a folder by hand: the plan reports it as "unexpected layout" and stops for that folder. My call. The owner's live lab holds an imported Claude Science layout with `claude_code_team/`, which the migration leaves alone. Evidence: acceptance 02.

### D5: Identifiers
- **Chosen:** FND- finding, EVR- evidence record, REV- review, ADV- adversarial review, REQ- request, DEC- decision, TASK- task, HYP- hypothesis, EXP- experiment, PC- stays for a protocol-adherence review renamed `ADH-`; every table header expands its prefix ("FND-id (finding)"); init rewrites headers and templates; existing rows keep their old ids, which the dictionary lists as legacy forms. Evidence: this conversation.
- **Why this one:** a prefix that reads alone needs no key; the audit found F- colliding with Figure and EC- with eligibility criteria. Evidence: the second audit, section 3.
- **Rejected:** keeping short codes with expanded headers, because the codes still collide. Evidence: this conversation.
- **Failure points:** cross-references in old rows ("superseded by F-0041") stay old. Mitigation: the dictionary's legacy table maps old prefixes to new, and the Curator reads both. My call.
- **Edge cases:** scripts that parse ids (`artifacts.py`, `migrate_claude_science.py`, `jev_ask.py` reads a decision id for the gate): each accepts both forms. My call.

### D6: Records vocabulary
- **Chosen:** findings log (FINDINGS_LOG.md, append-only), key results table (KEY_RESULTS.md), source table (SOURCES.csv), evidence record (evidence_records/, EVR-), decision log (DECISION_LOG.md), automation log (`automation/`), work plan (WORK_PLAN.md), experiment register (unchanged), lab notebook (unchanged), review log (unchanged). Evidence: this conversation.
- **Why this one:** "log" is research-record usage (lab notebook, decision log); "register" is reserved for preregistration and the experiment register; "registry" in research is where trials are registered. Evidence: OSF Registries; the audits.
- **Rejected:** "findings register", because of the collision; keeping "ledger" and "canonical", because they are accounting and software words. Evidence: this conversation.
- **Failure points:** `recording-findings` and the Curator agent are dense with "ledger"; the rename is mechanical but the pressure test must rerun. Evidence: `skills/recording-findings/SKILL.md`.
- **Edge cases:** the three vendored skills that carry "ledger" in their own names and scripts (`source_ledger`, `evidence_ledger_template`, `audit_evidence_ledger.py`) keep them; the test exempts upstream text. Evidence: the first audit, pattern P2.

### D7: Archive vocabulary
- **Chosen:** artifact (kept; the ACM and reproducibility term), artifact archive (`artifacts/archive/`; the skill stays `saving-artifacts`), provenance in place of lineage (`artifacts.py provenance`, with `lineage` kept as a hidden alias for one release), `--task` in place of `--command`, the reviewer-finding statuses open / author-responded / re-opened / closed in place of open / claimed / unaddressed / resolved, `--destination milestone | working` in place of `snapshot | working_data`. Evidence: this conversation; W3C PROV and the FAIR principle R1.2 for provenance as known.
- **Why this one:** artifact is what computing research calls the outputs that accompany a paper; provenance is the standard word for where a thing came from. Evidence: the audits.
- **Rejected:** "research output" and "output archive", because they rename the skill, the script and every marker for a word the researcher's field already uses. Evidence: this conversation.
- **Failure points:** the four ledger files (`artifacts.jsonl`, `versions.jsonl`, `dependencies.jsonl`, `verification_checks.jsonl`) are data; their names stay, the prose calls them the archive's tables. My call.
- **Edge cases:** a lab migrated from Claude Science holds `destination: snapshot` rows; the store reads both values. My call.

### D8: Lab memory vocabulary
- **Chosen:** lab memory (kept), pitfall in place of gotcha (`type: pitfall`, with `gotcha` read as a legacy value), reminder in place of nudge (the hooks' names stay as files, their printed lines say reminder, the environment variable gains an alias `SCIENCE_ULTRAPOWERS_NO_MEMORY_REMINDER` with the old name honoured), working notes in place of scratch (`.working/`), consistency check in place of lint (the script name stays `memory-lint.mjs`; its messages and the skill say consistency check), admission criteria in place of the memory gate. Evidence: this conversation.
- **Why this one:** institutional memory is an organisational term; the four small words were the jargon. Evidence: the audits.
- **Rejected:** "lab handbook", because a handbook is a curated document and the memory is a store of single facts. Evidence: this conversation.
- **Failure points:** the memory frontmatter field `evidence: stated | observed | inferred` collides with citation evidence. Mitigation: renamed `basis: stated | observed | inferred`, with `evidence` read as legacy by the consistency check. My call.
- **Edge cases:** memory entries imported from Claude Science carry `type: gotcha`; the consistency check accepts the legacy value and the migration writes the new one. My call.

### D9: Team and coordination vocabulary
- **Chosen:** the researcher (in place of your human partner, the owner, the user, the fifteenth member; the roster row "Principal Researcher (you)" keeps the References & Resources duties), project manager (the Research Project Manager role, in place of orchestrator and main session), assign (in place of dispatch), role (in place of subagent in lab text), independent reviewer (in place of fresh-context), task assignment (in place of task brief), task report (in place of hand-off), session opening and session close (in place of kickoff and stand-up), work plan (in place of task board), completion criteria (in place of acceptance criteria), approval and approver (in place of sign-off), restricted folders (in place of out of scope, blocked folders, blockedPaths, with `lab.json` key `scope.restrictedFolders` and the old key read as legacy), handover summary (in place of where-we-left-off). Agent ids aligned to the titles: `research-project-manager`, `academic-supervisor`, `literature-researcher`, `methods-innovation-researcher`, `data-evaluation-researcher`, `lab-experiments-lead`, `findings-records-curator`, `documentation-writer`, `academic-paper-author`, `academic-reviewer`, `scientific-peer-reviewer`, `citation-reference-auditor`, `research-engineer`, `decision-systems-specialist`; titles unchanged; each agent lists its CRediT roles. Evidence: this conversation; ANSI/NISO Z39.104-2022 (the fourteen CRediT roles, credit.niso.org read 2026-11-08).
- **Why this one:** these are the words a lab uses for the same things; CRediT gives each role a standard anchor. Evidence: the audits; the CRediT page.
- **Rejected:** keeping orchestrator, dispatch and subagent as technical words, because the researcher reads the skills. Evidence: this conversation. Rejected: Lab Director and Internal Reviewer as titles, because the researcher kept every title. Evidence: this conversation.
- **Failure points:** agent ids are addresses: `science-ultrapowers:<id>` in every skill, the manifest's `agents` list, `lab.json.roles`, the hand copies under a project's `.claude/agents/`, and the pressure tests. Mitigation: one rename task with a test over every reference; init's migration rewrites `lab.json.roles` keys and warns on hand copies as it does today. Evidence: `.claude-plugin/plugin.json` agents list; `find_duplicates` in init.
- **Edge cases:** the kept engineering skills say "your human partner" in their upstream text; they are superpowers text under MIT and keep it; only the lab addendum paragraphs change. My call. AGENTS.md's rule flips to "the researcher". Evidence: this conversation.

### D10: Devices and review vocabulary
- **Chosen:** binding rule (in place of Iron Law), warning signs (in place of Red Flags), rationalizations and replies (in place of Common Rationalizations), adversarial review (in place of devil's advocate and red team; ADV- ids; `ADVERSARIAL_REVIEW.md`), critical-appraisal domains (in place of lenses), blocking in place of CRITICAL as the top grade (major and minor stay), cleared / not cleared in place of PASS / FAIL for the citation audit's verdict, protocol-adherence review (in place of protocol-compliance review), stopping rules and pilot runs (in place of kill criteria, campaign and probes), pilot and feasibility study (in place of feasibility mode). Evidence: this conversation; FORRT entries "Adversarial collaboration" and "Red Teams" read 2026-11-08; CASP checklists; the CONSORT extension for pilot and feasibility trials and SPIRIT's stopping guidelines as known.
- **Why this one:** each is the research-practice name for the same device. Evidence: as above.
- **Rejected:** keeping the superpowers device names, because the register must be scholarly throughout. Evidence: this conversation.
- **Failure points:** `test-skill-content.sh` pins sentences that contain old words; it changes in the same task. Evidence: `tests/claude-code/test-skill-content.sh` lines 36 to 49.
- **Edge cases:** the vendored skills keep "Iron Law" and "Red Flags" in their upstream text. My call.

### D11: The overloaded words
- **Chosen:** verified only for a recomputed finding; matched for a DOI whose metadata matched (verifier status `matched`); checked for any re-run with its mechanism named; reviewed for a role's judgment; audit only for the citation audit; record as the noun for a row; the five source checks named resolve-and-match, integrity, peer review, read, record; source statuses as lower-case words (citable, citable by exception, metadata matched, awaiting full text, awaiting approval, candidate, excluded: preprint, excluded: retracted, rejected: mismatch); request statuses open, fulfilled, approved, declined, unavailable; request types full-text request, DOI confirmation, exception approval; priorities blocks a stage, this cycle, background. Evidence: this conversation; the first audit, section 3.
- **Why this one:** one word, one meaning, is Part 1's first rule and the one ASD-STE100 holds above all. Evidence: the ASD-STE100 FAQ ("each word has only one meaning").
- **Rejected:** fixing only verify and check, because review and record are as overloaded. Evidence: this conversation.
- **Failure points:** `verify_doi.py` prints `VERIFIED` and tests pin it; the status becomes `matched` with `VERIFIED` accepted by readers of old cards for one release. My call. The source table's `lab_status` column holds the old tokens in existing labs; init migrates the values in a shown plan. My call.
- **Edge cases:** "verification record" in the task report becomes "checks performed". My call.

### D12: Spelling, abbreviations, status style
- **Chosen:** American English with one dictionary (analyze, behavior, license, artifact, judgment, organize, summarize, prioritize); a list of British forms the test refuses in plugin text (analyse, behaviour, licence, artefact, judgement, organise, summarise, prioritise, centre, colour); every abbreviation expanded at first use in a file (RQ, ECE, CI, PRISMA, LFS, CRediT, IMRaD, DOI stays as the name of the identifier); status values lower-case words everywhere, machine tokens only inside scripts' JSON. Evidence: this conversation; APA and IEEE are American; ASD-STE100 follows American spelling (the FAQ: Merriam-Webster).
- **Why this one:** one dictionary ends the split the audit measured (analyse 122 against analyze 39). Evidence: the first audit, pattern P10.
- **Rejected:** British English, because the three reference standards are American. Evidence: this conversation.
- **Failure points:** `LICENSE` and the licence text use "license"; the repository documents switch to the American noun. My call. Vendored and kept upstream text keeps its spelling; the test exempts it. My call.
- **Edge cases:** proper names keep their spelling (Centre for Open Science is "Center"; Programme Officer in a quoted guide stays). My call.

### D13: The scholarly output style
- **Chosen:** `output-styles/scholarly-explanatory.md`, frontmatter `name: Scholarly Explanatory`, `keep-coding-instructions: true`; the body: the session is a research assistant working with the researcher; Part 1 of the standard as writing rules; the scholarly register (claims matched to the design: association against causation, sample against population; hedging words matched to evidence; confirmatory and exploratory labelled; every number from the findings log or the key results table; every citation from a verified source; a term defined at first use; an abbreviation expanded at first use); a short "Note" block before and after a change, in place of STE Explanatory's "Insight" block, with at most three points, specific to the lab or the work. Init copies the file to `.claude/output-styles/scholarly-explanatory.md` when absent and prints `"outputStyle": "Scholarly Explanatory"` as the settings line to merge. Evidence: `output-styles/ste-explanatory.md` and `skills/init/scripts/init.mjs` in ultrapowers 2.3.0 (the file target and the `outputStyle` setting), read 2026-11-08; this conversation.
- **Why this one:** the same mechanism the researcher already uses, with the research register in place of the engineering one. Evidence: as above.
- **Rejected:** writing the style into `CLAUDE_SECTION.md` only, because a style applies to every answer and a section only to the lab's work. My call.
- **Failure points:** a style that repeats the skills' rules verbatim doubles the context. Mitigation: the style carries the rules and the register, never the lab's procedures. My call.
- **Edge cases:** a project that already has an output style: init writes nothing and says so. Evidence: init's skip-if-present rule.

### D14: One release, terminology first
- **Chosen:** the rename and the standard are phase 0 of the lifecycle plan; the lifecycle design and plan are rewritten in the new vocabulary at the end of phase 0, before any lifecycle task runs; one release 0.2.0. Evidence: this conversation ("EVERYTHING NOW").
- **Why this one:** the researcher's choice; the lifecycle is then built once, in the right words.
- **Rejected:** terminology as 0.2.0 and the lifecycle as 0.3.0, because the researcher wants one release. Evidence: this conversation.
- **Failure points:** a long branch; the ledger and the task lines are the recovery. Evidence: the lifecycle design D6.
- **Edge cases:** the two phase-0 pressure reruns on skills the lifecycle changes again later are run once more then. My call.

## Architecture

1. **The standard** (`docs/science-ultrapowers/terminology.md`): Part 1 rules; Part 2 dictionary by domain; the not-approved list; the legacy table (old id prefixes, old paths, old status tokens, old key names). Interface: the test reads the not-approved list and the British-spelling list from this file (a fenced block each, marked `<!-- not-approved -->` and `<!-- spelling -->`).
2. **The test** (`tests/claude-code/test-terminology.sh`): scans the plugin's own text (lab skills' full bodies; the addendum block of every vendored and kept skill up to its end marker; agents; templates; README, CONTRIBUTING, AGENTS.md, docs/testing.md; hooks; scripts' help and message strings through a small extractor) for the not-approved terms, the stage codes (`\bG[0-6]\b`), the British forms, and an unexpanded abbreviation (first occurrence in a file not followed by its expansion in parentheses, for the listed abbreviations). Exempts `docs/science-ultrapowers/evals/`, `LICENSE`, `RELEASE-NOTES.md`, the research and reviews records, and upstream bodies.
3. **The rename** across skills, agents, templates, records, hooks and scripts, in the dictionary's words, with the engineering skills' and vendored skills' upstream bodies untouched.
4. **Init's migration** (`init_lab.py`): `rename` plan lines for folders and files, header rewrites (id prefixes, status tokens, column names), `lab.json` key renames (`jev.blockedPaths` to `scope.restrictedFolders`, `roles` keys to the new agent ids), the output-style file, all shown before `--yes`.
5. **The migrate script** writes the new layout for a Claude Science import.
6. **The output style** file and its install.
7. **The lifecycle design and plan**, rewritten in the dictionary's words.

## Components

- `docs/science-ultrapowers/terminology.md` (new): about 300 dictionary entries at most; Part 1 about forty rules.
- `tests/claude-code/test-terminology.sh` (new), `tests/claude-code/test-skill-content.sh` (sentences updated), `tests/claude-code/test-agents.sh` (ids), `tests/claude-code/test-no-foreign-harness.sh` (unchanged), `tests/claude-code/run-tests.sh` picks the new test up by its name.
- Skills: the thirteen lab skills rewritten in place (names unchanged); the lab addendum paragraphs of the seven kept skills; the `LAB OVERLAY` blocks of the fifteen vendored skills (now titled `LAB ADDENDUM (binding)`, with `test-vendored-skills.sh` updated); `skills/initializing-a-research-lab/templates/` (every folder, file, header and status value); `skills/saving-artifacts/scripts/artifacts.py` (`provenance`, `--task`, `--destination milestone|working`, the reviewer-finding statuses, messages), `skills/remembering-for-the-lab/scripts/memory-lint.mjs` (messages, `basis` field, legacy `evidence` and `gotcha`), `skills/verifying-evidence-by-doi/scripts/verify_doi.py` (`matched` status; `VERIFIED` read as legacy), `skills/migrating-from-claude-science/scripts/migrate_claude_science.py` (the new layout and names), `skills/deciding-with-jev/scripts/jev_ask.py` (decision id forms, restricted folders key), `skills/initializing-a-research-lab/scripts/init_lab.py` (the migration, the output style).
- Agents: fourteen files renamed and rewritten; `.claude-plugin/plugin.json` agents list.
- Hooks: `session-start`, `memory-nudge`, `memory-postcompact`, `lib/lab-version` printed lines.
- `output-styles/scholarly-explanatory.md` (new).
- Documents: README, CONTRIBUTING, AGENTS.md, docs/testing.md, RELEASE-NOTES 0.2.0 entry (one, shared with the lifecycle).
- The lifecycle design and plan rewritten.

## Data flow

Text in, text out: the standard is read by people and by the test; the test reads the plugin's files; init reads an existing lab's layout and writes the renamed layout and headers; the migrate script reads a Claude Science copy and writes the new layout; the output style is read by Claude Code from the project's `.claude/output-styles/`. No new trust boundary: the standard is plugin text; init's migration touches only the lab's own files after a shown plan.

## Error handling

- The test prints one line per offending term with file and line, and exits 1; it never edits.
- Init's migration refuses a rename when the target exists, reports a hand-renamed folder as unexpected and stops for it, and performs nothing without `--yes`.
- A script that meets a legacy value (old id prefix, `VERIFIED`, `gotcha`, `evidence:`, `snapshot`, `jev.blockedPaths`) reads it and writes the new form; it never fails on a legacy value in this release.
- The output-style install writes nothing when the file exists and says so.

## Testing

- `test-terminology.sh` (new): the not-approved list, the stage codes, the British forms, the abbreviations; a self-check that plants one term of each kind and expects a failure (as the leak gate does).
- Unit tests: init migration (`test_init_migration.py`: every rename, the header rewrites, idempotence, the refusal on an existing target, the unexpected-layout stop, `lab.json` key renames, the output-style install and skip); `artifacts.py` (the `provenance` verb, the `--task` flag, the legacy `lineage` alias, the status renames, the legacy `snapshot` value); `verify_doi.py` (`matched`, legacy `VERIFIED` on read); `memory-lint.mjs` (`basis`, legacy `evidence` and `gotcha`); `migrate_claude_science.py` (the new layout on the fixture); `jev_ask.py` (both id forms, both keys).
- Shell tests: `test-skill-content.sh` with the new sentences; `test-agents.sh` with the new ids and the CRediT line; `test-vendored-skills.sh` with the addendum heading; `test-lab-templates.sh` (from the lifecycle plan, written against the new names); `test-repo-documents.sh` with the output style file and the standard present.
- Pressure tests: every lab skill is rewritten, so every one reruns (one with-skill run each on Haiku 5.5, recorded as a new iteration); the standard's own pressure test is the test file.
- Acceptance: an init migration on a copy of the 0.1.x smoke lab and on a copy of the owner's live lab, with the plan recorded and the diff summarised.

## Left to the builder

- The exact wording of each dictionary entry, within the four-sentence rule and the decisions above.
- The exact list of Part 1 rules, within the sections named in Constraints, and their numbering.
- The extractor that collects scripts' message strings for the test (a Python one-liner over string literals is enough).
- The order of the rename tasks inside phase 0, as long as the standard and the test land first and the lifecycle rewrite lands last.

## Definition of done

1. `docs/science-ultrapowers/terminology.md` exists in the two-part form with every decided term and its source; `tests/claude-code/test-terminology.sh` passes on the tree and fails on each planted term.
2. No stage code, no not-approved term and no British form from the list remains in the plugin's own text; every abbreviation on the list is expanded at first use.
3. A fresh lab has the new folders, files, headers and ids; init's migration on a copy of a 0.1.x lab produces the same layout with the rows' data unchanged; both are tested.
4. The fourteen agents carry the new ids and their CRediT roles; every reference resolves; the manifest lists them.
5. The output style ships and installs; the README documents it.
6. Every lab skill's pressure test has a passing with-skill rerun on the rewritten text.
7. The lifecycle design and plan are rewritten in the standard's vocabulary and the plan's self-review passes.

## Repositories in scope

`.` (the science-ultrapowers repository). The owner's live lab is a migration test target only when the owner runs it.

## Assumption ledger

| # | Question | Chosen answer | Confidence | Reason |
|---|---|---|---|---|
| 1 | Do the vendored and kept skills' upstream bodies keep their words and spelling? | Yes; only our addendum changes; the test exempts upstream text | High | Licences and provenance hashes require verbatim copies (D1, D9, D10, D12). |
| 2 | How do scripts treat legacy values? | Read old, write new, never fail, for this release | Medium | A researcher's lab must keep working through the update (D5, D7, D8, D11). |
| 3 | The memory field `evidence` | Renamed `basis` | Medium | It collided with citation evidence (D8). |
| 4 | "Results" against the manuscript's results section | "the Results stage" in full where the section is near | Medium | The only collision the stage names leave (D2). |
| 5 | The verifier's status word | `matched`, `VERIFIED` read as legacy | Medium | "Verified" is reserved for findings (D11). |
| 6 | The style's note block | "Note", at most three points, before and after a change | Medium | Mirrors STE Explanatory's Insight block without its name (D13). |
| 7 | Where the test reads its lists | Fenced blocks in the standard, marked with comments | Medium | One source for the dictionary and the test (D1). |
| 8 | Skill names stay | Yes, all; only agent ids change | High | A skill name is an address on the marketplace (Non-goals). |
| 9 | The kept engineering skills' own vocabulary (merge, refactor) | Stays inside those skills | High | They describe software work (D1). |
| 10 | Proper names keep their spelling | Yes | High | Center for Open Science, PRISMA, CRediT are names (D12). |
