# Lab memory

The lab's long-term memory: what the records cannot tell you. The findings ledger, the decisions, the reference registry and the artifact store hold what happened; this folder holds the traps, reasons and vocabulary they do not. It is managed with the `science-ultrapowers:remembering-for-the-lab` skill and committed to git with the rest of `research_lab/`.

## Layout

- `MEMORY.md`: the index, one line per memory, read at every session kickoff.
- `project/<name>.md`: a fact about the project as a whole.
- `artifact/<artifact_id>/<name>.md`: a fact about reading one artifact in `research_lab/artifacts/` (never its contents, which the artifact store holds).

Nothing else lives here, apart from this README and the `.gitkeep` files that keep empty folders in git.

## Entry format

```markdown
---
name: <kebab-case-slug, equal to the file name without .md>
description: <one line: what this memory tells you>
metadata:
  type: <gotcha | decision | lesson | directive | vocabulary>
  entity: <project | artifact:<artifact_id>>
  evidence: <stated | observed | inferred>
  learned_by: <the role that learned it, kebab-case, or unknown>
  origin: <agent | extractor | user | import>
date: <YYYY-MM-DD>
---
<the fact, one to three sentences>

**Why:** <root cause or rationale>

**How to apply:** <what to do differently>
```

`date` is the day the fact was last verified: an update or a re-verification at prune time refreshes it, and the index line keeps the history as `**UPDATED YYYY-MM-DD: ...**`. An optional `note:` line may follow `date` (an import uses it to name a missing artifact). The lint (`memory-lint.mjs`) rejects any other key, order or value.

## Scopes and evidence

| A fact about | Lives in |
|---|---|
| The project | `project/`, `entity: project` |
| One artifact | `artifact/<artifact_id>/`, `entity: artifact:<artifact_id>` |
| Your human partner or any other person | Claude Code user memory, never here |
| This session's working notes | `research_lab/.scratch/<YYYY-MM-DD>-<session>/<role>.md`, git-ignored, deleted at the stand-up |

`stated` (a person said it) and `observed` (seen in this project's data, runs or code) are load-bearing. `inferred` is a hypothesis: verify it before anyone relies on it.

## When a memory is written

Roles propose memories in their hand-off as `Memories proposed: <type | evidence | project or deliverable path | fact; why; how to apply> or 'none'`. The orchestrator gates each proposal against the four criteria in `MEMORY.md`, maps a deliverable path to its artifact id, writes the file and its index line, runs the lint and commits `research_lab/` with `Memory-Ref: <path>` in the commit message. No role writes here mid-task. The stand-up is the gating moment: proposals not yet gated are gated there, and the session scratchpad is deleted.
