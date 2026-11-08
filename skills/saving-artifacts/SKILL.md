---
name: saving-artifacts
description: Use when a task produces or changes a file the lab should keep (a report, protocol, figure, table, script, dataset, PDF), when a hand-off lists deliverables, or when looking for prior work before recomputing it
---

# Saving Artifacts

## Overview

Every save is a full copy, versions chain, each version records its inputs, and reviewer verdicts attach to the judged version. The store is `research_lab/artifacts/`, committed to git.

**Core principle:** The workspace is scratch. The store is the record.

## The Iron Law

```
NO DELIVERABLE LEAVES A HAND-OFF UNSAVED, AND NOTHING IS RECOMPUTED BEFORE THE STORE IS SEARCHED
```

## The rules

| Situation | Do |
|---|---|
| A role hands off deliverables | The orchestrator saves each with `save --role <role> --command <task id>`, the hand-off's `Inputs:` as `--inputs`. Roles never write the store. |
| New content for a deliverable | `save --version-of <id>`, never a new filename. |
| A project file (data, outputs, code) | `link` it: recorded, not copied. |
| Expensive-to-regenerate state | `save --checkpoint`; never for figures or reports. |
| A large file that keeps changing | `--destination working_data` at creation; later saves replace earlier working copies, never a `--destination snapshot` milestone. |
| A reviewer's verdict | `check add` on that version; the author answers with `mark-addressed`, a reviewer closes with `check review`. |
| Citing a deliverable | `{{artifact:<version id>}}` or `[your text]({{artifact:<version id>}})`; `art_<artifact id>` means the latest version. `resolve <file> --write` rewrites the file with the markers turned into links before it leaves the lab; without `--write` it prints the resolved text and changes nothing. |
| Looking for prior work | `search`, then `lineage` or `graph`. A folder listing is not a search. |
| What a deliverable was based on, what is still open | `search <name>` for its ids, `lineage <latest version id>` for its inputs and checks, `check list` for the open verdicts. The ledgers are keyed by version id: a grep for an artifact id or a file name finds nothing and proves nothing. |
| Large files | LFS lines are automatic; if `save` warns, install git-lfs if it is missing, then `git lfs install`. `lfs-check` at every stand-up. Exit 1 means one of two things: `missing_lines` lists stored copies without an LFS line (add the printed pattern to `research_lab/artifacts/.gitattributes`, or re-save), or the filter is unconfigured (`git lfs install`). When `path` reports a pointer, `git lfs pull`. |

## Commands

`python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" <command>`, with `--lab <research_lab>` outside the project; `--help` lists options.

References: a version id, an artifact id, `art_<artifact id>`, or a unique prefix of 6+ characters.

An artifact is identified by its project-relative path: `reports/a.md` and `drafts/a.md` are two artifacts. `save` of a path already saved is refused until you pass `--version-of <id>` (or the path itself), and a stored copy is named `v<NNN>_<base name>`. Put `--inputs` after the files, or repeat it.

```
save <files> --role --command [--inputs ...] [--version-of] [--description] [--session] [--environment] [--checkpoint] [--intermediate] [--destination] [--no-stage] [--force]
link <files> --role --command [--inputs ...] [--description] [--session] [--no-stage] [--force]
check add --version --claim --verdict --reviewer [--severity] [--evidence] [--rebuttal]
check list [ref] [--all]      check review <check id> --status --reviewer [--note]
mark-addressed <check id> --note
resolve <file> [--write]      search [text] [--include-intermediate]
path <ref>      lineage <ref>      graph <ref>      lfs-check
```

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "I'll save everything at the end" | The end has forgotten the inputs. Save at every hand-off. |
| "It's committed, so it's recorded" | Git keeps bytes, not inputs or verdicts. `save` first. |
| "It's just an intermediate file" | `--intermediate`: search hides it, lineage keeps it. |
| "A new filename is cleaner than a version" | It breaks the chain. `--version-of`. |
| "I remember this file exists" | Memory is not the store. `search`. |
| "I grepped the ledgers and found no rows" | Rows are keyed by version id. `search`, then `lineage`. |
| "The inputs are obvious" | Not to next month's reviewer. `--inputs`. |
| "The reviewer's note can live in chat" | Chat is gone at compaction. `check add`. |
| "Save the .env so the key is versioned" | Never. The store is committed; a secret saved there is published. `save` and `link` refuse such files; `--force` is for a file your human partner has said is safe. |

## Red Flags

- A hand-off deliverable with no saved version
- `report_v2_final.md` next to `report.md`
- A figure or table cited without a marker
- Recomputing before `search`
- A reviewer verdict that lives only in chat
- `--force` used to get past a "looks like a secret or ignored file" refusal

## Verification Checklist

- [ ] Every hand-off deliverable has a version (`search`)
- [ ] Every version lists its inputs (`lineage`)
- [ ] Every reviewer verdict is a check (`check list --all`)
- [ ] `lfs-check` exits 0
- [ ] `research_lab/` is committed
