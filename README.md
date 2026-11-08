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

science-ultrapowers is a research-lab methodology for Claude Code. It has fourteen research roles, stage gates G0-G6, a DOI-verified evidence rule, a versioned artifact store and lab memory, and it can continue a project that began in Claude Science.

You talk to the lab in plain words. The main session acts as the Research Project Manager: it briefs the roles, collects their hand-offs and relays their questions to you. Nothing enters a record without its check, nothing passes a gate unreviewed, and nobody reviews their own work.

Built from obra/superpowers v7.0.2 (MIT) as the template; see LICENSE.

## Table of contents

- [Install](#install)
- [Start a lab](#start-a-lab)
- [Continue from Claude Science](#continue-from-claude-science)
- [The team](#the-team)
- [How a session runs](#how-a-session-runs)
- [The stores](#the-stores)
- [Skills](#skills)
- [Connectors](#connectors)
- [Testing](#testing)
- [Licence](#licence)

## Install

Claude Code is the only supported harness.

Register the marketplace, then install the plugin:

```
claude plugin marketplace add raoofaltaher/science-ultrapowers
claude plugin install science-ultrapowers@science-ultrapowers --scope project
```

Inside a session, `/plugin marketplace add raoofaltaher/science-ultrapowers` and then `/plugin install science-ultrapowers@science-ultrapowers` do the same. Project scope records the plugin in the project, so everyone who opens it gets the lab.

If your access to the repository comes through your own credentials, run `gh auth setup-git` once. Claude Code then updates the plugin in the background with those credentials.

Requirements:

- Git for Windows, or bash on macOS and Linux.
- Python 3.11 or later. The scripts use the standard library only.
- node 22 or later.
- git-lfs, for the artifact stores of your projects.
- PowerShell 7 (`pwsh`), only for the optional environment script `setup_lab_env.ps1`.
- `jq`, for development of the plugin only.

## Start a lab

Ask for a research lab in a project, or ask for research work in a folder that has no `research_lab/`. The `science-ultrapowers:initializing-a-research-lab` skill takes over.

It asks once:

- the lab's name, short name and a one or two sentence description;
- the Git LFS threshold, 10 MB by default;
- which connectors to set up (see [Connectors](#connectors));
- the folders no role may open (`--out-of-scope`);
- whether to prepare the figure and poster environment;
- whether to write permission rules, default no.

It then writes only what the project lacks, and never overwrites a file:

- `research_lab/`: the briefs, registries, ledgers, templates, the artifact store and the memory store;
- a lab section in `CLAUDE.md` (`.claude/CLAUDE.md` if that is the only one);
- `.mcp.json`, when you chose connectors;
- the lines the lab needs in `.gitattributes` and `.gitignore`;
- `research_lab/lab.json`, which records the lab's name, roles, thresholds and connectors.

The script first prints its plan. You read it, and it writes only after your yes. A re-run adds what is new and updates `lab.json`.

After the write, fill in `research_lab/00_project_knowledge/PROJECT_BRIEF.md`, approve `.mcp.json` when Claude Code asks, then sign in to each connector with `/mcp`. The environment script (`setup_lab_env.ps1`) prepares the figure and poster tools and the Jev key. You see its `-DryRun` output first, and you run it yourself. It asks before each change.

## Continue from Claude Science

If a Claude Science data directory exists on the machine, the `science-ultrapowers:migrating-from-claude-science` skill continues one project in the lab. Quit Claude Science first. Run the dry run first. It writes only a report, and you say yes to that report before the real run.

It imports:

- the project's memories;
- the Claude Science profiles, as a diff against the lab's agents;
- every artifact version, with its dependencies and reviewer verdicts;
- the where-we-left-off summary for the next kickoff;
- checklists for connectors, secret names, permissions and skills state;
- optionally, the chat transcripts, one JSON file per session (`--transcripts`).

It never opens the live database, never reads a secret and never changes an agent file. Secrets are listed by name only, and you set their values in the environment.

Read `research_lab/migration/MIGRATION_REPORT.md`, then the files beside it: `PROFILE_DIFF.md`, `PROFILE_MEMORIES.md`, `SUPERSEDED_MEMORIES.md`, `PRUNE_CANDIDATES.md`, `ENV_CHECKLIST.md`, `CONNECTORS.md`, `PERMISSIONS.md`, `SKILLS.md`, `SKILLS_DRIFT.md`, `WHERE_WE_LEFT_OFF.md` and `WARNINGS.md`. Imported code cells, environment snapshots, check evidence and transcripts are copied verbatim. They can hold pasted secrets or personal data, so review them before any public push.

## The team

Fourteen agents run the roles. You are the fifteenth: you supply full texts, approve Tier-B sources and give the final release. Dispatch a role as `science-ultrapowers:<agent>`.

| Role | Agent | Owns |
|---|---|---|
| Research Project Manager | `lab-project-manager` | Task board, gates, risks, decisions, lab-meeting minutes |
| Academic Supervisor | `academic-supervisor` | Scientific direction, G0 and G2 approvals, integrity, release sign-off |
| Literature Researcher | `literature-researcher` | Search, evidence cards, the reference registry |
| Methods & Innovation Researcher | `methods-researcher` | Hypotheses, method formulation and mathematics, ablation design |
| Data & Evaluation Researcher | `data-evaluation-researcher` | Data validity, evaluation protocols, statistics |
| Lab & Experiments Lead | `experiments-lead` | Runs, the experiment register, reproducibility, compute |
| Findings & Records Curator | `findings-curator` | The findings ledger, canonical numbers, the lab notebook |
| Documentation Writer | `documentation-writer` | Documentation, model cards, datasheets, experiment reports |
| Academic Paper Author | `paper-author` | Manuscripts, thesis chapters, claim-evidence maps |
| Academic Reviewer | `academic-reviewer` | Internal review of proposals, chapters, reports and manuscripts |
| Scientific Peer Reviewer | `scientific-reviewer` | Referee-style review, the devil's-advocate check |
| Citation & Reference Auditor | `citation-auditor` | Citation audits, retraction sweeps, PASS or FAIL per gate |
| Research Engineer | `research-engineer` | Code changes with tests and quality gates |
| Decision Systems Specialist | `decision-systems-specialist` | The Jev decision layer, calibration, the decision log |

## How a session runs

1. **Kickoff.** Before any task, the Research Project Manager reads the project brief, the task board, the last lab-meeting note, the open access requests and the lab memory. It presents a short status and a recommended next action.
2. **Task briefs.** Every delegation is a written brief: task id, gate, owner, reviewer, due date, objective, inputs, deliverables, acceptance criteria and constraints. A free-form paragraph is not a brief.
3. **Hand-off blocks.** Every role ends every task with a hand-off block: deliverables, inputs, a verification record, proposed findings and memories, review requests, open risks and deviations. A return without one has not delivered.
4. **Records.** After each hand-off the orchestrator saves the deliverables to the artifact store. The Findings & Records Curator recomputes each proposed finding from its file. The orchestrator gates proposed memories, dispatches any requested review, then commits `research_lab/` only. You commit your code.
5. **Stand-up.** At the end of every session the lab gates the remaining memory proposals, runs `lfs-check`, writes the stand-up note, clears the scratch folder and commits.

Nothing skips a gate. Independent checks run in parallel, and each gate decision is logged in `research_lab/06_decisions/DECISIONS.md`.

| Gate | What passes it |
|---|---|
| G0 Question | An H-card exists: a research-question link, a falsifiable prediction, prior-work evidence cards and a novelty delta. |
| G1 Evidence base | The search protocol, screening log, PRISMA-style counts, evidence cards and registry rows exist. |
| G2 Pre-registration | The protocol is filed with hypothesis, design, metrics, seeds, test, stopping rules, splits and compute budget. |
| G3 Execution | Every run is registered with its commit, config hash, seeds, environment, artifacts and deviations. |
| G4 Findings | The analysis against the protocol, with effect sizes, confidence intervals and tests, is recorded in ledger entries. |
| G5 Documentation | Documentation, model cards and datasheets are updated from the ledger and the registry. |
| G6 Release | A manuscript or thesis chapter is ready to leave the lab, after the full citation audit and the referee reports. |

At G4 and G6 a fresh-context dispatch of the Scientific Peer Reviewer also writes the strongest case against each headline claim. A CRITICAL objection blocks the gate.

The evidence rule, in three lines:

- A fact enters a record only from a peer-reviewed work whose DOI resolves in Crossref, read in full text at the cited passage and recorded on an evidence card.
- Preprints, web pages, lab notes and memory are never evidence. A work without a DOI needs your approval first.
- Every level re-runs the check. Nobody accepts another agent's "verified".

## The stores

### Artifact store

`research_lab/artifacts/` holds every deliverable the lab keeps. It is committed to git.

- `store/<artifact id>/v<NNN>_<name>`: byte-exact copies, one per version.
- `artifacts.jsonl`, `versions.jsonl`, `dependencies.jsonl`, `verification_checks.jsonl`: the ledgers.
- `.gitattributes`: one LFS line for each stored file at or above the threshold.

Every save is a full copy. Versions chain, each version records its inputs, and reviewer verdicts attach to the judged version. The workspace is scratch. The store is the record.

Run the verbs through `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py"`:

| Verb | Use |
|---|---|
| `save` | Store files as artifact versions, with their inputs. |
| `link` | Record a project file without copying it. |
| `search` | Find prior work before recomputing it. |
| `path` | Print where a version's bytes are. |
| `lineage` | Show a version's inputs and checks. |
| `graph` | Show a version's full ancestry. |
| `check` | Attach, list or review a reviewer's verdict (`check add`, `check list`, `check review`). |
| `mark-addressed` | The author says a check is fixed. |
| `resolve` | Turn `{{artifact:<id>}}` markers into relative links. |
| `lfs-check` | Report stored copies that lack an LFS line, and the LFS total. |

### Memory store

`research_lab/memory/` holds one fact per file, indexed by `MEMORY.md`.

- `project/<name>.md`: a fact about the project.
- `artifact/<artifact id>/<name>.md`: a fact about reading one artifact.
- `README.md`: the entry format.

Records hold what happened. Memory holds what the records cannot tell you.

- **The gate.** A fact is saved only when it is verified, durable, expensive to rediscover and not derivable from code, docs, git history or the lab records. All four, or nothing is saved. Only the orchestrator writes.
- **The lint.** `node "${CLAUDE_PLUGIN_ROOT}/skills/remembering-for-the-lab/scripts/memory-lint.mjs" research_lab/memory` checks the index budget (`memory.indexBudget` in `lab.json`, 150 lines by default), the frontmatter, dangling and orphan entries and near-duplicates. Exit 0 is clean.
- **The hooks.** The `session-start` hook loads the bootstrap. The `memory-nudge` and `memory-postcompact` hooks print one reminder line when a lab memory store exists, on each prompt and after context compaction. They write nothing. `SCIENCE_ULTRAPOWERS_NO_MEMORY_NUDGE=1` turns the two memory hooks off.

### The LFS rule

A stored file at or above `lfs.thresholdMB` in `lab.json` (10 MB by default) gets an LFS line in `research_lab/artifacts/.gitattributes`. Install git-lfs and run `git lfs install` in the project. Run `lfs-check` at every stand-up. A save warns when the LFS total passes `lfs.budgetWarnMB` (800 MB by default). The plugin repository itself uses no LFS.

## Skills

### Lab skills

| Skill | Use it to |
|---|---|
| `using-science-ultrapowers` | Start every conversation by finding and invoking the right skill. |
| `initializing-a-research-lab` | Start, join or upgrade a lab in a project. |
| `migrating-from-claude-science` | Continue a Claude Science project in the lab. |
| `running-the-lab` | Address the lab, a role or a gate: the roster, gates, briefs and hand-offs. |
| `holding-lab-meetings` | Open each session with a kickoff, close it with a stand-up, review a gate. |
| `verifying-evidence-by-doi` | Check a source before anyone cites it. |
| `searching-the-literature` | Build the evidence base with a systematic or snowball search. |
| `recording-findings` | Record, verify and quote findings and canonical numbers. |
| `saving-artifacts` | Save, link, search and review the lab's deliverables. |
| `remembering-for-the-lab` | Gate, save, recall, prune and lint the lab memory. |
| `requesting-reference-access` | File a request for a paywalled paper or a Tier-B approval. |
| `planning-paper-figures` | Plan the figure set of a paper before any figure is drawn. |
| `deciding-with-jev` | Use Jev for fast, calibrated triage, never for evidence or gate decisions. |

### Kept engineering skills

| Skill | Use it to |
|---|---|
| `systematic-debugging` | Find the root cause before proposing a fix. |
| `test-driven-development` | Write the test before the implementation. |
| `verification-before-completion` | Run the checks before claiming that work is done. |
| `requesting-code-review` | Ask a non-author to review finished work. |
| `receiving-code-review` | Weigh review feedback with rigour, not blind agreement. |
| `dispatching-parallel-agents` | Run independent tasks in parallel. |
| `writing-skills` | Create and pressure-test a skill. |

### Vendored third-party skills

Each carries a lab overlay, its upstream licence and a `PROVENANCE.md` that records the source, the pinned commit and the vetting. The evidence rule overrides anything a vendored skill says.

| Skill | Upstream | Licence |
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
| `typesafe-ai` | TypeSafe AI documentation skill (docs.typesafe.ai) | MIT |

## Connectors

The catalogue is `skills/initializing-a-research-lab/connectors.json`. Choose connectors when you start a lab (`--connectors science,<id>,...`).

- **The science set**, six http servers, written to `.mcp.json` on request: Firecrawl, PubMed, bioRxiv, ChEMBL, Clinical Trials and Microsoft Learn. Sign in with `/mcp` if a server asks.
- **The other `mcp` set**, written only when you name them: Canva, Figma, Notion, Linear, Atlassian, Asana, Box, monday.com, HubSpot, Intercom, Euler, Microsoft 365, Gojiberry, Lusha and Apollo.io.
- **Optuna**, opt-in: a stdio server for hyper-parameter studies. It needs `uv`, and its entry holds a path on your machine.
- **Account connectors**: SciSpace, Scholar Gateway, Wiley Scholar Gateway, Scite, Hugging Face, Context7, DeepWiki, Mermaid Chart, Excalidraw, Claude Docs, Google Drive, GitHub, Gmail and Google Calendar. They work through your claude.ai sign-in in Claude Code, after `/mcp`, and are not written to `.mcp.json`.
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

The leak gate (`tests/claude-code/test-no-foreign-harness.sh`) also reads a maintainer's private-strings file, `tests/private-strings.txt`, which git ignores. Copy `tests/private-strings.example` to start one. `docs/testing.md` describes every kind of test.

## Licence

The source is published under the licence in `LICENSE`. It is source-available, not open source: you may install the plugin in Claude Code and use it, and the files it writes into your projects are yours. The template and the vendored skills keep their own licences, listed in `LICENSE` and in each skill's folder.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report, ask and suggest, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for how we behave.
