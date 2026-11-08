---
name: remembering-for-the-lab
description: Use when the researcher or a role learns a checked, durable, expensive-to-rediscover fact about the project that no lab record holds, when deciding whether the lab already hit a problem, before assigning a role a topic the lab may have met before, or when asked to prune the lab memory or run its consistency check
---

# Remembering for the Lab

## Overview

`research_lab/memory/` holds one fact per file, indexed by `MEMORY.md`, committed to git.

**Core principle:** Records hold what happened; memory holds what the records cannot tell you.

A hook prints a line that begins "Lab memory reminder" when a session may have learned such a fact. The reminder asks; the admission criteria below decide. `SCIENCE_ULTRAPOWERS_NO_MEMORY_REMINDER` turns it off.

## The binding rule

```
SEARCH MEMORY BEFORE ASSIGNING; ADMIT BEFORE WRITING; NEVER STORE WHAT A RECORD ALREADY SAYS
```

## Scopes and tags

| A fact about | Goes to |
|---|---|
| The project | `project/<name>.md`, `entity: project` |
| Reading one artifact | `artifact/<artifact_id>/<name>.md`, `entity: artifact:<artifact_id>` |
| The researcher or any person | Claude Code user memory, never the lab |
| This session's working notes | `research_lab/.working/<YYYY-MM-DD>-<session>/<role>.md`, deleted at the session close |

`basis:` `stated` (a person said it) and `observed` (seen in this project's data or runs) are load-bearing; `inferred` is a hypothesis. `type`: pitfall, decision (a reason no decision record holds), lesson, directive, vocabulary.

Entries written under the 0.1 layout may carry `evidence:` for `basis:` and the old type for `pitfall`; the consistency check reads them without a finding. <!-- legacy -->

## remember

Roles propose in the task report (`Memories proposed: <type | basis | project or deliverable path | fact; why; how to apply> or 'none'`); only the project manager (the lead session) writes, never mid-task, and maps a deliverable path to its artifact id after saving.

1. Admission criteria: checked, durable, expensive to rediscover, not derivable from code, docs, git history or the lab records. All four, or save nothing and say which failed.
2. Never store secrets, credentials, personal data, facts about people, records, artifact contents, code, fix recipes, task state, tool availability, or anything in `CLAUDE.md`.
3. Check the index; for a known topic, update that entry, refresh `date` and fold `**UPDATED YYYY-MM-DD: ...**` into its line.
4. Distill to one fact, three sentences at most.
5. Write it in `research_lab/memory/README.md`'s entry format; `learned_by` names the role that learned it.
6. Add its index line under `## Project` or `## Artifacts`.
7. Over `memory.indexBudget` lines? Stop and prune first.
8. Run the consistency check; the project manager commits `research_lab/` with `Memory-Ref: <path>` in the commit message.

## recall

Before assigning a role or recomputing: `MEMORY.md`, then search `research_lab/memory/`, then the records (`DECISION_LOG.md`, `FINDINGS_LOG.md`, `LAB_NOTEBOOK.md`, `REVIEW_LOG.md`), then `git log --grep`. Write back what only the last two rungs found.

## prune and the consistency check

Prune at milestones: re-check entries older than six months and every `inferred` one, merge near-duplicates. Consistency check (it prints one line per finding; exit 0 is clean):

```
node "${CLAUDE_PLUGIN_ROOT}/skills/remembering-for-the-lab/scripts/memory-lint.mjs" research_lab/memory  # legacy
```

| Code | Fix |
|---|---|
| `BUDGET` | Prune; add nothing. |
| `DANGLING`, `ORPHAN`, `STRAY` | One file per index line, in `project/` or `artifact/<id>/`. |
| `FM_*` | Fix the frontmatter. |
| `RECORD_ONLY`, `NO_FACT` | Already a record, or no fact: delete. |
| `WIKILINK`, `NEAR_DUP` | Fix the name, or merge. |

## Warning signs

| Thought | Reality |
|---|---|
| "Useful context for the next session" | Task state: working notes or task record. |
| "It's in a decision, but a note saves time" | Derivable. `RECORD_ONLY`. |
| "The Academic Supervisor said they prefer…" | A person. User memory, not here. |
| "Fairly sure" | That is `inferred`. Check it first. |
| "The index is only a little over" | A hard stop. Prune first. |
| "I'll assign the role now and check memory later" | Search first; the lab may know. |
