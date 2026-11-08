---
name: saving-artifacts
description: Use when a task produces or changes a file the lab should keep (a report, preregistration, figure, table, script, dataset, portable document format (PDF) file), when a task report lists deliverables, or when looking for prior work before recomputing it
---

# Saving Artifacts

## Overview

Every save is a full copy, versions chain, each version records its inputs, and reviewer findings attach to the judged version. The artifact archive is `research_lab/artifacts/archive/`, committed to git. Its four tables are `artifacts`, `versions`, `dependencies` and `verification_checks`.

**Core principle:** The workspace is working space. The archive is the record.

## The binding rule

```
NO DELIVERABLE LEAVES A TASK REPORT UNSAVED, AND NOTHING IS RECOMPUTED BEFORE THE ARCHIVE IS SEARCHED
```

## The rules

| Situation | Do |
|---|---|
| A role submits a task report with deliverables | The project manager (the lead session) saves each with `save --role <role> --task <TASK-id>`, the task report's `Inputs:` as `--inputs`. Roles never write the archive. |
| New content for a deliverable | `save --version-of <id>`, never a new filename. |
| A project file (data, outputs, code) | `link` it: recorded, not copied. |
| Expensive-to-regenerate state | `save --checkpoint`; never for figures or reports. |
| A large file that keeps changing | `--destination working` at creation; later saves replace earlier working copies, never a `--destination milestone` save. |
| A reviewer's verdict | `findings add` on that version; the author answers with `respond`, a reviewer closes with `findings review`. A reviewer finding is `open`, `author-responded`, `re-opened` or `closed`. |
| Citing a deliverable | `{{artifact:<version id>}}` or `[your text]({{artifact:<version id>}})`; `art_<artifact id>` means the latest version. `resolve <file> --write` rewrites the file with the markers turned into links before it leaves the lab; without `--write` it prints the resolved text and changes nothing. |
| Looking for prior work | `search`, then `provenance` or `graph`. A folder listing is not a search. |
| What a deliverable was based on, what is still open | `search <name>` for its ids, `provenance <latest version id>` for its inputs and reviewer findings, `findings list` for the open verdicts. The archive's tables are keyed by version id: a grep for an artifact id or a file name finds nothing and proves nothing. |
| Large files | Git Large File Storage (LFS) lines are automatic; if `save` warns, install git-lfs if it is missing, then `git lfs install`. `lfs-check` at every session close. Exit 1 means one of two things: `missing_lines` lists stored copies without an LFS line (add the printed pattern to `research_lab/artifacts/.gitattributes`, or re-save), or the filter is unconfigured (`git lfs install`). When `path` reports a pointer, `git lfs pull`. |

`path` reports a version's status: `ok`, `changed`, `missing`, `pointer`, `replaced` or `outside-project`.

## Commands

`python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" <command>`, with `--lab <research_lab>` outside the project; `--help` lists options.

References: a version id, an artifact id, `art_<artifact id>`, or a unique prefix of 6+ characters.

An artifact is identified by its project-relative path: `reports/a.md` and `drafts/a.md` are two artifacts. `save` of a path already saved is refused until you give `--version-of <id>` (or the path itself), and a stored copy is named `v<NNN>_<base name>`. Put `--inputs` after the files, or repeat it.

```
save <files> --role --task [--inputs ...] [--version-of] [--description] [--session] [--environment] [--checkpoint] [--intermediate] [--destination milestone|working] [--no-stage] [--force]
link <files> --role --task [--inputs ...] [--description] [--session] [--no-stage] [--force]
findings add --version --claim --verdict --reviewer [--severity] [--evidence] [--rebuttal]
findings list [ref] [--all]      findings review <finding id> --status --reviewer [--note]
respond <finding id> --note
resolve <file> [--write]      search [text] [--include-intermediate]
path <ref>      provenance <ref>      graph <ref>      lfs-check
```

## Rationalizations and replies

| Excuse | Reality |
|---|---|
| "I'll save everything at the end" | The end has forgotten the inputs. Save at every task report. |
| "It's committed, so it's recorded" | Git keeps bytes, not inputs or verdicts. `save` first. |
| "It's just an intermediate file" | `--intermediate`: search hides it, provenance keeps it. |
| "A new filename is cleaner than a version" | It breaks the chain. `--version-of`. |
| "I remember this file exists" | Memory is not the archive. `search`. |
| "I grepped the archive's tables and found no rows" | Rows are keyed by version id. `search`, then `provenance`. |
| "The inputs are obvious" | Not to next month's reviewer. `--inputs`. |
| "The reviewer's note can live in chat" | Chat is gone at compaction. `findings add`. |
| "Save the .env so the key is versioned" | Never. The archive is committed; a secret saved there is published. `save` and `link` refuse such files; `--force` is for a file the researcher has said is safe. |

## Warning signs

- A task report deliverable with no saved version
- `report_v2_final.md` next to `report.md`
- A figure or table cited without a marker
- Recomputing before `search`
- A reviewer verdict that lives only in chat
- `--force` used to get past a "looks like a secret or ignored file" refusal

## Checklist

- [ ] Every task report deliverable has a version (`search`)
- [ ] Every version lists its inputs (`provenance`)
- [ ] Every reviewer verdict is a reviewer finding (`findings list --all`)
- [ ] `lfs-check` exits 0
- [ ] `research_lab/` is committed
