<p align="center">
  <img src="assets/science-ultrapowers-small.svg" alt="science-ultrapowers logo" width="420">
</p>

<p align="center">
  <a href="https://github.com/raoofaltaher/science-ultrapowers/releases/latest"><img src="https://img.shields.io/github/v/release/raoofaltaher/science-ultrapowers?style=for-the-badge&label=release&color=8e09fa&labelColor=2d0789&cacheSeconds=300" alt="Latest release" height="40"></a>
</p>

<p align="center">
  🙏 <a href="https://github.com/raoofaltaher/science-ultrapowers/discussions/new?category=q-a">Ask a question</a>
  &nbsp;·&nbsp;
  💡 <a href="https://github.com/raoofaltaher/science-ultrapowers/discussions/new?category=ideas">Suggest an idea</a>
  &nbsp;·&nbsp;
  🙌 <a href="https://github.com/raoofaltaher/science-ultrapowers/discussions/new?category=show-and-tell">Show what you built</a>
  &nbsp;·&nbsp;
  🐛 <a href="https://github.com/raoofaltaher/science-ultrapowers/issues/new/choose">Report a bug</a>
  &nbsp;·&nbsp;
  💬 <a href="https://github.com/raoofaltaher/science-ultrapowers/discussions">Join the discussion</a>
</p>

<p align="center">
  🌐 <a href="https://raoofaltaher.com">raoofaltaher.com</a>
  &nbsp;·&nbsp;
  🧰 <a href="https://github.com/raoofaltaher/ultrapowers">Ultrapowers, the engineering sibling</a>
</p>

# science-ultrapowers

science-ultrapowers is a research-lab methodology for Claude Code. It has fourteen research roles, a lifecycle of seven stages from Question to Publication (each ending in a stage approval), five tracks that enter the lifecycle where your work begins, a DOI-verified evidence rule, a versioned artifact archive and lab memory, and it can continue a project that began in Claude Science.

You talk to the lab in plain words. The lead session, your own session, acts as the Research Project Manager: it assigns the roles, collects their task reports and relays their questions to you. Nothing enters a record without its check, nothing wins a stage approval unreviewed, and nobody reviews their own work.

Built from obra/superpowers v7.0.2 (MIT) as the template; see LICENSE.

## Table of contents

- [Install](#install)
- [Start a lab](#start-a-lab)
- [Continue from Claude Science](#continue-from-claude-science)
- [The team](#the-team)
- [How a session runs](#how-a-session-runs)
- [Tracks](#tracks)
- [The records and the archive](#the-records-and-the-archive)
- [Scholarly output style](#scholarly-output-style)
- [Skills](#skills)
- [Connectors](#connectors)
- [Testing](#testing)
- [License](#license)

## Install

Claude Code is the only supported harness.

Register the marketplace, then install the plugin:

```
claude plugin marketplace add raoofaltaher/science-ultrapowers
claude plugin install science-ultrapowers@science-ultrapowers --scope project
```

Inside a session, `/plugin marketplace add raoofaltaher/science-ultrapowers` and then `/plugin install science-ultrapowers@science-ultrapowers` do the same. Project scope records the plugin in the project, so everyone who opens it gets the lab.

To move an existing install to a new release, update the marketplace and then the plugin, and restart Claude Code:

```
claude plugin marketplace update science-ultrapowers
claude plugin update science-ultrapowers@science-ultrapowers
```

Inside a session, `/plugin marketplace update science-ultrapowers` and `/plugin update science-ultrapowers@science-ultrapowers` do the same. After an update, run `science-ultrapowers:initializing-a-research-lab` once in each lab: it shows what the new release adds or migrates, and applies it with `--yes`.

If your access to the repository comes through your own credentials, run `gh auth setup-git` once. Claude Code then updates the plugin in the background with those credentials.

Requirements:

- Git for Windows, or bash on macOS and Linux.
- Python 3.11 or later. The scripts use the standard library only.
- node 22 or later.
- git-lfs, for the artifact archives of your projects.
- PowerShell 7 (`pwsh`), only for the optional environment script `setup_lab_env.ps1`.
- `jq`, for development of the plugin only.

## Start a lab

Ask for a research lab in a project, or ask for research work in a folder that has no `research_lab/`. The `science-ultrapowers:initializing-a-research-lab` skill takes over.

It asks once:

- the lab's name, short name and a one or two sentence description;
- the Git Large File Storage (LFS) threshold, 10 MB by default;
- which connectors to set up (see [Connectors](#connectors));
- the restricted folders no role may open (`--out-of-scope`);
- whether to prepare the figure and poster environment;
- whether to write permission rules, default no;
- whether you want a minimal lab for one track instead of the full lab (`--track idea|literature|review|writing|dissemination`, repeatable; see [Tracks](#tracks)).

It then writes only what the project lacks, and never overwrites a file:

- `research_lab/`: the project brief, the findings log, the key results table, the source table, the decision log, the work plan, the templates, the artifact archive and lab memory;
- the Scholarly Explanatory output style, in `.claude/output-styles/scholarly-explanatory.md` (see [Scholarly output style](#scholarly-output-style));
- a lab section in `CLAUDE.md` (`.claude/CLAUDE.md` if that is the only one);
- `.mcp.json`, when you chose connectors;
- the lines the lab needs in `.gitattributes` and `.gitignore`;
- `research_lab/lab.json`, which records the lab's name, roles, thresholds and connectors.

The script first prints its plan. You read it, and it writes only after your yes. A re-run adds what is new and updates `lab.json`.

A lab begun with release 0.1 is migrated by running `science-ultrapowers:initializing-a-research-lab` again. The skill shows its plan first. It renames the folders and files, rewrites the headers and status words, adds the `Basis` column to the findings log (existing rows read `exploratory`) and the `Input checksums` column to the experiment register (existing rows stay empty), and writes `research_lab/migration/HANDOVER_SUMMARY.md`. Release 0.2.0 renamed the agent ids and two JSON keys; [RELEASE-NOTES.md](RELEASE-NOTES.md) lists them.

After the write, fill in `research_lab/project/PROJECT_BRIEF.md`, approve `.mcp.json` when Claude Code asks, then sign in to each connector with `/mcp`. The environment script (`setup_lab_env.ps1`) prepares the figure and poster tools and the Jev key. You see its `-DryRun` output first, and you run it yourself. It asks before each change.

## Continue from Claude Science

If a Claude Science data directory exists on the machine, the `science-ultrapowers:migrating-from-claude-science` skill continues one project in the lab. Quit Claude Science first. Run the dry run first. It writes only a report, and you say yes to that report before the real run.

It imports:

- the project's memories;
- the Claude Science profiles, as a diff against the lab's agents;
- every artifact version, with its dependencies and reviewer verdicts;
- the handover summary for the next session opening;
- checklists for connectors, secret names, permissions and skills state;
- optionally, the chat transcripts, one JSON file per session (`--transcripts`).

It never opens the live database, never reads a secret and never changes an agent file. Secrets are listed by name only, and you set their values in the environment.

Read `research_lab/migration/MIGRATION_REPORT.md`, then the files beside it: `PROFILE_DIFF.md`, `PROFILE_MEMORIES.md`, `SUPERSEDED_MEMORIES.md`, `PRUNE_CANDIDATES.md`, `ENV_CHECKLIST.md`, `CONNECTORS.md`, `PERMISSIONS.md`, `SKILLS.md`, `SKILLS_DRIFT.md`, `HANDOVER_SUMMARY.md` and `WARNINGS.md`. Imported code cells, environment records, check evidence and transcripts are copied verbatim. They can hold pasted secrets or personal data, so review them before any public push.

## The team

Fourteen agents run the roles. You are the fifteenth: the Principal Researcher. You supply full texts, approve sources that have no DOI and give the final release. Assign a role as `science-ultrapowers:<agent>`.

| Role | Agent | Owns |
|---|---|---|
| Research Project Manager | `research-project-manager` | Work plan, stage approvals, risks, decisions, lab-meeting minutes |
| Academic Supervisor | `academic-supervisor` | Scientific direction, the Question, Literature, Preregistration and Results approvals, integrity, the Publication approval |
| Literature Researcher | `literature-researcher` | Search, evidence records, the source table |
| Methods & Innovation Researcher | `methods-innovation-researcher` | Hypotheses, method formulation and mathematics, ablation design |
| Data & Evaluation Researcher | `data-evaluation-researcher` | Data validity, evaluation protocols, statistics |
| Lab & Experiments Lead | `lab-experiments-lead` | Runs, the experiment register, reproducibility, compute |
| Findings & Records Curator | `findings-records-curator` | The findings log, the key results table, the lab notebook |
| Documentation Writer | `documentation-writer` | Documentation, model cards, datasheets, experiment reports |
| Academic Paper Author | `academic-paper-author` | Manuscripts, thesis chapters, claim-evidence maps |
| Academic Reviewer | `academic-reviewer` | Internal review of proposals, chapters, reports and manuscripts |
| Scientific Peer Reviewer | `scientific-peer-reviewer` | Referee-style review, the adversarial review |
| Citation & Reference Auditor | `citation-reference-auditor` | Citation audits, retraction checks, cleared or not cleared at each stage |
| Research Engineer | `research-engineer` | Code changes with tests and quality checks |
| Decision Systems Specialist | `decision-systems-specialist` | The Jev decision layer, calibration, the automation log and the thresholds |

## How a session runs

1. **Session opening.** Before any task, the Research Project Manager reads the project brief, the work plan, the last lab-meeting note, the open requests and lab memory. It presents a short status and a recommended next action.
2. **Task assignments.** Every assignment is a written block: task id, stage, owner, reviewer, due date, objective, inputs, deliverables, completion criteria, restricted folders and constraints. A free-form paragraph is not a task assignment.
3. **Task reports.** Every role ends every task with a task report: deliverables, inputs, the checks performed, findings submitted and memories proposed, review requests, open issues and risks, and deviations. A return without one has not delivered.
4. **Records.** After each task report the lead session saves the deliverables to the artifact archive. The Findings & Records Curator recomputes each submitted finding from its file. The lead session applies the admission criteria to proposed memories, assigns any requested review, then commits `research_lab/` only. You commit your code.
5. **Session close.** At the end of every session the lab applies the admission criteria to the remaining memory proposals, runs `lfs-check`, writes the session close note, clears the working notes folder (`research_lab/.working/`) and commits.

Nothing skips a stage approval. Independent checks run in parallel, and each stage approval is logged in `research_lab/decisions/DECISION_LOG.md`.

| Stage | Approved when |
|---|---|
| Question | The question document is approved by you and then by the Academic Supervisor. It is the hypothesis record: a research question (RQ) link, a falsifiable prediction, the null and alternative hypotheses, the variables, what counts as an answer, prior-work evidence records and a statement of its contribution relative to prior work. |
| Literature | The search plan, the search logs, the Preferred Reporting Items for Systematic reviews and Meta-Analyses (PRISMA) 2020 counts, the evidence records and the source table rows exist. |
| Preregistration | The protocol holds hypothesis, design, metrics, seeds, test, stopping rules, splits, compute budget and the design-validation items. After the three approvals the lead session registers it at a commit with `preregister.py`. |
| Execution | Every run is registered with its commit, config hash, seeds, environment, input checksums, artifacts and deviations, and a protocol-adherence review compares the runs with the protocol. |
| Results | The registration check is clear. The analysis against the registered protocol, with effect sizes, a confidence interval (CI) for each and the tests, is recorded in findings log rows, each with its basis: confirmatory or exploratory. |
| Reporting | Documentation, model cards and datasheets are updated from the findings log and the source table, and the archive manifest is started. |
| Publication | A manuscript or thesis chapter is ready to leave the lab, after the full citation audit and the referee reports. |

The stages carry the nine phases of the K-Dense-AI/science-superpowers research workflow as their criteria: Frame, Ground, Design, Register, Prepare, Execute, Verify, Challenge and Report. Four binding rules hold at every stage:

- `NO CONFIRMATORY CLAIM WITHOUT A REGISTERED PREDICTION FIRST`. A result is confirmatory only when its protocol was registered before the outcome was seen and `preregister.py check` is clear. Everything else is exploratory, and a deviation from the protocol makes the affected finding exploratory.
- `NO ADJUSTMENT WITHOUT ROOT CAUSE FIRST`. An anomalous result goes through `science-ultrapowers:investigating-anomalous-results` before anyone changes the code, the data or the protocol.
- `NO CLAIM WITHOUT FRESH EVIDENCE`. A claim that a result is checked, reproduced or passing rests on a check run now, and the claim names its mechanism: which files, which method, against what.
- `Nothing is feasible until it has run`. When runnability is unknown, `science-ultrapowers:establishing-feasibility-first` runs a pilot and feasibility study before the Preregistration approval.

At the Results and Publication stages an independent assignment of the Scientific Peer Reviewer, with no access to the author's reasoning, also writes the strongest case against each primary claim. A blocking objection stops the stage approval.

The evidence rule, in three lines:

- A fact enters a record only from a peer-reviewed work whose DOI resolves in Crossref, read in full text at the cited passage and recorded in an evidence record.
- Preprints, web pages, lab notes and memory are never evidence. A work without a DOI needs your approval first.
- Every level re-runs the check. Nobody accepts another agent's "verified".

## Tracks

A track enters the lifecycle at the stage that fits what you hold. The session primer routes your first message to the right track. A service track (literature, review, writing or dissemination) in a folder with no `research_lab/` starts with `science-ultrapowers:initializing-a-research-lab` and `--track <track>`, which writes a minimal lab for that track, then runs the track skill.

| What you have in hand | Track | First skill | Where it ends |
|---|---|---|---|
| An idea, a topic, a paper that provoked you, a technique, a supervisor's remark, a dataset with a hunch, or nothing yet | idea | `science-ultrapowers:framing-a-research-question` | The Question approval: a hypothesis record and a survey of prior work, handed to the study track or to a pilot and feasibility study. |
| A framed question with a dataset, a call for papers, or a thesis chapter | study | `science-ultrapowers:running-the-lab`, after init | The full lifecycle, from the Question stage to the Publication approval. |
| A topic or keyword for a review, a survey, a matrix or a meta-analysis | literature | `science-ultrapowers:synthesizing-the-literature` | The Literature approval: a logged search, evidence records, a synthesis matrix, a gap matrix and a flow diagram. A review paper or a meta-analysis may follow. |
| A manuscript to referee, check or respond to | review | `science-ultrapowers:reviewing-a-manuscript` | A report in `research_lab/reviews/reports/`, written by independent roles. No review is written from the abstract alone. |
| A manuscript or thesis to write, a journal to pick, a submission to format | writing | `science-ultrapowers:writing-for-publication` | The Publication approval, with the manuscript saved as an artifact and the archive manifest complete. |
| Slides, a poster, a graphical abstract, an architecture figure | dissemination | `science-ultrapowers:presenting-research` | A deck, a poster or a figure saved as an artifact, with every number quoted from the findings log. |

A lab set up for one track holds the files every track uses: the decision log, the request queue, the work plan, the task report template, the three meeting templates (session opening, session close, lab meeting), the literature and review folders, the artifact archive, lab memory and `.working/`. Each track adds its own templates. Init without `--track` adds the rest of the lab.

Every track writes only under `research_lab/`. The roles never run git write commands, and the lead session commits `research_lab/` only. The evidence rule and the four binding rules hold in every track.

## The records and the archive

The lab keeps its records under `research_lab/`. Each record has one path and one owner.

- **The findings log:** `research_lab/findings/FINDINGS_LOG.md`, one row for each finding, each with its basis: confirmatory or exploratory.
- **The preregistrations:** `research_lab/experiments/preregistrations/`, each registered at a commit and checked through `python "${CLAUDE_PLUGIN_ROOT}/skills/preregistering-the-protocol/scripts/preregister.py"` (`register`, then `check`).
- **The key results table:** `research_lab/findings/KEY_RESULTS.md`, the numbers a document may quote.
- **The source table and the evidence records:** `research_lab/literature/SOURCES.csv` and `research_lab/literature/evidence_records/`.
- **The decision log:** `research_lab/decisions/DECISION_LOG.md`, with every stage approval.
- **The work plan:** `research_lab/planning/WORK_PLAN.md`.
- **The artifact archive:** `research_lab/artifacts/archive/`, described below.
- **Lab memory:** `research_lab/memory/`, described below.

### The artifact archive

`research_lab/artifacts/` holds every deliverable the lab keeps. It is committed to git.

- `archive/<artifact id>/v<NNN>_<name>`: byte-exact copies, one per version.
- `artifacts.jsonl`, `versions.jsonl`, `dependencies.jsonl`, `verification_checks.jsonl`: the archive's tables.
- `.gitattributes`: one LFS line for each stored file at or above the threshold.

Every save is a full copy. Versions chain, each version records its inputs, and reviewer findings attach to the judged version. The workspace holds working notes. The archive is the record.

Run the verbs through `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py"`:

| Verb | Use |
|---|---|
| `save` | Store files as artifact versions, with their inputs (`--role`, `--task`, `--inputs`). |
| `link` | Record a project file without copying it. |
| `search` | Find prior work before recomputing it. |
| `path` | Print where a version's bytes are. |
| `provenance` | Show a version's inputs and checks. |
| `graph` | Show a version's full ancestry. |
| `findings` | Attach, list or review a reviewer's finding (`findings add`, `findings list`, `findings review`). |
| `respond` | The author answers a reviewer finding. |
| `resolve` | Turn `{{artifact:<id>}}` markers into relative links. |
| `lfs-check` | Report stored copies that lack an LFS line, and the LFS total. |

### Lab memory

`research_lab/memory/` holds one fact per file, indexed by `MEMORY.md`.

- `project/<name>.md`: a fact about the project.
- `artifact/<artifact id>/<name>.md`: a fact about reading one artifact.
- `README.md`: the entry format.

Records hold what happened. Memory holds what the records cannot tell you.

- **The admission criteria.** A fact is saved only when it is verified, durable, expensive to rediscover and not derivable from code, docs, git history or the lab records. All four, or nothing is saved. Only the lead session writes.
- **The consistency check.** `node "${CLAUDE_PLUGIN_ROOT}/skills/remembering-for-the-lab/scripts/memory-lint.mjs" research_lab/memory` checks the index budget (`memory.indexBudget` in `lab.json`, 150 lines by default), the frontmatter, dangling and orphan entries and near-duplicates. Exit 0 is clean.
- **The hooks.** The `session-start` hook loads the session primer. The `memory-nudge` and `memory-postcompact` hooks print one reminder line when lab memory exists, on each prompt and after context compaction. They write nothing. `SCIENCE_ULTRAPOWERS_NO_MEMORY_REMINDER=1` turns the two memory hooks off.

### The LFS rule

A stored file at or above `lfs.thresholdMB` in `lab.json` (10 MB by default) gets an LFS line in `research_lab/artifacts/.gitattributes`. Install git-lfs and run `git lfs install` in the project. Run `lfs-check` at every session close. A save warns when the LFS total passes `lfs.budgetWarnMB` (800 MB by default). The plugin repository itself uses no LFS.

## Scholarly output style

The plugin ships the output style `output-styles/scholarly-explanatory.md`. The lab set-up installs it to `.claude/output-styles/scholarly-explanatory.md` in the project and prints the settings line `"outputStyle": "Scholarly Explanatory"` for `.claude/settings.json`.

The style makes the lead session write plain, disciplined scholarly English. It matches each claim to the design and hedges it to the evidence. It takes every number from the findings log or the key results table and every citation from a matched source.

The terminology standard, `docs/science-ultrapowers/terminology.md`, fixes the plugin's terms and its writing rules.

## Skills

### Lab skills

| Skill | Use it to |
|---|---|
| `using-science-ultrapowers` | Start every conversation by finding and invoking the right skill. |
| `initializing-a-research-lab` | Start, join, migrate or upgrade a lab in a project. |
| `migrating-from-claude-science` | Continue a Claude Science project in the lab. |
| `running-the-lab` | Address the lab, a role or a stage: the roster, the lifecycle and its binding rules, stage approvals, task assignments and task reports. The study track. |
| `holding-lab-meetings` | Open each session, close it, review a stage. |
| `verifying-evidence-by-doi` | Check a source before anyone cites it. |
| `searching-the-literature` | Build the evidence base with a systematic or snowball search. |
| `recording-findings` | Record, verify and quote findings and key results. |
| `saving-artifacts` | Save, link, search and review the lab's deliverables. |
| `remembering-for-the-lab` | Apply the admission criteria, save, recall, prune and check the lab memory. |
| `requesting-reference-access` | File a request for a paywalled paper or an exception approval. |
| `planning-paper-figures` | Plan the figure set of a paper before any figure is drawn. |
| `deciding-with-jev` | Use Jev for fast, calibrated prioritization, never for evidence or stage approvals. |
| `preregistering-the-protocol` | Register a protocol at a commit before any outcome is seen, then run the registration check (`preregister.py`). |
| `framing-a-research-question` | The idea track: turn an interest into a falsifiable question, a hypothesis record and a survey of prior work. |
| `synthesizing-the-literature` | The literature track: a logged search, a synthesis matrix, a gap matrix and a PRISMA 2020 or Consolidated Standards of Reporting Trials (CONSORT) flow diagram. |
| `reviewing-a-manuscript` | The review track: referee a manuscript, check a draft, audit its references or answer reviewer comments. |
| `writing-for-publication` | The writing track: draft a manuscript or thesis chapter from the records, shortlist journals and format a submission. |
| `presenting-research` | The dissemination track: slides, posters, graphical abstracts and architecture figures from the records. |

### Kept engineering skills

| Skill | Use it to |
|---|---|
| `systematic-debugging` | Find the root cause before proposing a fix. |
| `test-driven-development` | Write the test before the implementation. |
| `verification-before-completion` | Run the checks before claiming that work is done. |
| `requesting-code-review` | Ask a non-author to review finished work. |
| `receiving-code-review` | Weigh review feedback with rigor, not blind agreement. |
| `dispatching-parallel-agents` | Assign independent tasks in parallel. |
| `writing-skills` | Create and pressure-test a skill. |

### Adopted third-party skills

Each carries a lab addendum, its upstream license and a `PROVENANCE.md` that records the source, the pinned commit and the vetting. The two skills from K-Dense-AI/science-superpowers, `investigating-anomalous-results` and `establishing-feasibility-first`, are reworded in full into the plugin's terminology standard, with every rule kept; their `PROVENANCE.md` records it. The evidence rule overrides anything an adopted skill says.

| Skill | Upstream | License |
|---|---|---|
| `debugging` | neuromechanist/research-skills | BSD-3-Clause |
| `figure-bible` | neuromechanist/research-skills | BSD-3-Clause |
| `figure-qa` | neuromechanist/research-skills | BSD-3-Clause |
| `implementation-planning` | neuromechanist/research-skills | BSD-3-Clause |
| `manuscript-formatting` | neuromechanist/research-skills | BSD-3-Clause |
| `paper-review` | neuromechanist/research-skills | BSD-3-Clause |
| `pr-review-toolkit` | neuromechanist/research-skills | BSD-3-Clause |
| `svg-primitives` | neuromechanist/research-skills | BSD-3-Clause |
| `hypothesis-generation` | K-Dense-AI/claude-scientific-writer | MIT |
| `peer-review` | K-Dense-AI/claude-scientific-writer | MIT |
| `pptx-posters` | K-Dense-AI/claude-scientific-writer | MIT |
| `scholar-evaluation` | K-Dense-AI/claude-scientific-writer | MIT |
| `scientific-critical-thinking` | K-Dense-AI/claude-scientific-writer | MIT |
| `scientific-writing` | K-Dense-AI/claude-scientific-writer | MIT |
| `investigating-anomalous-results` | K-Dense-AI/science-superpowers | MIT |
| `establishing-feasibility-first` | K-Dense-AI/science-superpowers | MIT |
| `typesafe-ai` | TypeSafe AI documentation skill (docs.typesafe.ai) | MIT |

## Connectors

The catalog is `skills/initializing-a-research-lab/connectors.json`. Choose connectors when you start a lab (`--connectors science,<id>,...`).

- **The science set**, six http servers, written to `.mcp.json` on request: Firecrawl, PubMed, bioRxiv, ChEMBL, Clinical Trials and Microsoft Learn. Sign in with `/mcp` if a server asks.
- **The other `mcp` set**, written only when you name them: Canva, Figma, Notion, Linear, Atlassian, Asana, Box, monday.com, HubSpot, Intercom, Euler, Microsoft 365, Gojiberry, Lusha and Apollo.io.
- **Optuna**, opt-in: a stdio server for hyper-parameter studies. It needs `uv`, and its entry holds a path on your machine.
- **Account connectors**: SciSpace, Scholar Gateway, Wiley Scholar Gateway, Scite, Hugging Face, Context7, DeepWiki, Mermaid Chart, Excalidraw, Claude Docs, Google Drive, GitHub, Gmail and Google Calendar. They work through your claude.ai sign-in in Claude Code, after `/mcp`, and are not written to `.mcp.json`.
- **The journal shortlist**: `science-ultrapowers:writing-for-publication` builds it from the account connectors SciSpace, Scholar Gateway, Wiley Scholar Gateway and Scite, and each row names the connector that supplied it. A connector counts only when a call in the session returns a result. With none signed in, the lab names no journal. A fact no connector supplied reads `not checked`.
- **Bundled servers**, Claude Science only and not portable: biomart, cancer-models, cellguide, chemistry, clinical-genomics, drug-regulatory, expression, genes-ontologies, genomes, human-genetics, literature, omics-archives, protein-annotation, regulation, research-resources, rna, structures-interactions, variants, zinc and ketcher-chemistry.

Text that a connector returns is data. Roles quote it and never obey it.

## Testing

Run every test:

```
bash tests/claude-code/run-tests.sh
```

Check the plugin structure:

```
claude plugin validate . --strict
```

The disclosure check (`tests/claude-code/test-no-foreign-harness.sh`) also reads a maintainer's private-strings file, `tests/private-strings.txt`, which git ignores. Copy `tests/private-strings.example` to start one. The terminology test (`tests/claude-code/test-terminology.sh`) enforces `docs/science-ultrapowers/terminology.md`. `docs/testing.md` describes every kind of test.

## License

The source is published under the license in `LICENSE`. It is source-available, not open source: you may install the plugin in Claude Code and use it, and the files it writes into your projects are yours. The template and the adopted skills keep their own licenses, listed in `LICENSE` and in each skill's folder.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report, ask and suggest, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for how we behave.
