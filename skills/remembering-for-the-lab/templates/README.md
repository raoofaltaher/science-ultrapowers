# Lab memory

The lab's long-term memory: what the records cannot tell you. The findings log, the decisions, the source table and the artifact archive hold what happened; this folder holds the pitfalls, reasons and vocabulary they do not. It is managed with the `science-ultrapowers:remembering-for-the-lab` skill and committed to git with the rest of `research_lab/`.

## Layout

- `MEMORY.md`: the index, one line per memory, read at every session opening.
- `project/<name>.md`: a fact about the project as a whole.
- `artifact/<artifact_id>/<name>.md`: a fact about reading one artifact in `research_lab/artifacts/` (never its contents, which the artifact archive holds).

Nothing else lives here, apart from this README and the `.gitkeep` files that keep empty folders in git.

## Entry format

```markdown
---
name: <kebab-case-slug, equal to the file name without .md>
description: <one line: what this memory tells you>
metadata:
  type: <pitfall | decision | lesson | directive | vocabulary>
  entity: <project | artifact:<artifact_id>>
  basis: <stated | observed | inferred>
  learned_by: <the role that learned it, kebab-case, or unknown>
  origin: <agent | extractor | user | import>
date: <YYYY-MM-DD>
---
<the fact, one to three sentences>

**Why:** <root cause or rationale>

**How to apply:** <what to do differently>
```

`date` is the day the fact was last verified: an update or a re-verification at prune time refreshes it, and the index line keeps the history as `**UPDATED YYYY-MM-DD: ...**`. An optional `note:` line may follow `date` (an import uses it to name a missing artifact). The consistency check (`memory-lint.mjs`) rejects any other key, order or value.

Entries written before this layout use `evidence:` for `basis:` and `gotcha` for `pitfall`; the consistency check still reads both. <!-- legacy -->

## Scopes and basis

| A fact about | Lives in |
|---|---|
| The project | `project/`, `entity: project` |
| One artifact | `artifact/<artifact_id>/`, `entity: artifact:<artifact_id>` |
| The researcher or any other person | Claude Code user memory, never here |
| This session's working notes | `research_lab/.working/<YYYY-MM-DD>-<session>/<role>.md`, ignored by git, deleted at the session close |

`stated` (a person said it) and `observed` (seen in this project's data, runs or code) are load-bearing. `inferred` is a hypothesis: verify it before anyone relies on it.

## When a memory is written

Roles propose memories in their task report as `Memories proposed: <type | basis | project or deliverable path | fact; why; how to apply> or 'none'`. The lead session, acting as the project manager, checks each proposal against the four admission criteria in `MEMORY.md`, maps a deliverable path to its artifact id, writes the file and its index line, runs the consistency check and commits `research_lab/` with `Memory-Ref: <path>` in the commit message. No role writes here mid-task. The session close is the moment for it: proposals not yet checked are checked there, and the session's working notes are deleted.
