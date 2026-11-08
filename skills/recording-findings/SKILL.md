---
name: recording-findings
description: Use when recording, verifying, reconciling, quoting or looking up any project fact, result, number or experiment, when two documents disagree on a number, or when a role is about to write "verified", "confirmed" or "re-checked"
---

# Recording Findings

## Overview

Every number or fact in a document, report, manuscript or chat answer is quoted from the lab's records, never retyped from memory. If it is not in the ledger, it is not a finding.

**Core principle:** A claim is only as good as the check it names.

## The Iron Law

```
A NUMBER NOT IN THE LEDGER IS NOT A FINDING; A VERIFICATION THAT DOES NOT NAME ITS CHECK IS NOT A VERIFICATION
```

## Findings ledger

`research_lab/02_findings_ledger/FINDINGS.md`: one row per finding, append-only.

| Field | Content |
|---|---|
| `F-id` | `F-0001`, sequential |
| Statement | One precise sentence including the number and its definition (metric, split, seed count, confidence interval) |
| Type | `experimental`, `literature`, `code-audit`, `data-audit` or `doc-audit` |
| Evidence | Experimental: experiment id and metrics file path (and row or epoch). Literature: registry ref-id and evidence card id. Audit: file path and line or cell |
| Status | `tentative`, `verified`, `superseded by F-xxxx` or `refuted by F-xxxx` |
| Recorded / verified | Date and role for each |
| Scope / caveats | e.g. "dev split only", "known leakage in this split", "single seed" |

These four statuses are the only ones. There is no "candidate", "provisional" or "pending" row.

Transitions:

- `tentative` to `verified` requires an independent re-check by the Curator: re-open the file or re-run the query; for literature, re-run `science-ultrapowers:verifying-evidence-by-doi` and re-read the quote. For claims a manuscript or thesis will use, Supervisor approval at G4 as well.
- A verified row is never edited. Write a new row and mark the old one `superseded by F-new` or `refuted by F-new`.
- A single-seed, dev-only or partial-run result stays `tentative` and says so in its caveats.

A number seen only in a console log, a progress bar, a report or another role's hand-off has no row, not even a `tentative` one. Recompute it from the metrics file yourself (see Verification before recording); the recomputed number enters as `tentative`, never `verified`. `tentative` means you recomputed it; it never means "not yet checked".

## Canonical numbers

`research_lab/02_findings_ledger/CANONICAL_NUMBERS.md` lists the numbers documents quote (headline metrics, ratios, dataset counts, parameter counts): `name | value | exact definition | F-id | allowed wording`.

When documents disagree on a number, the Curator traces each variant to its source, records one canonical value with its definition, and opens a doc-fix task for every document that deviates. Open reconciliations stay listed at the bottom of the file until resolved.

## Lab notebook

`research_lab/02_findings_ledger/LAB_NOTEBOOK.md`: dated, append-only entries, one per working session per role. Record what was attempted, the commands or configs used, what happened (failures and dead ends included), links to experiment ids, F-ids and evidence cards, and next steps. Record negative results as carefully as positive ones.

## Experiment register

`research_lab/03_experiments/EXPERIMENT_REGISTER.md`: one row per experiment.

| Field | Content |
|---|---|
| Experiment id | Keep the project's scheme |
| Protocol | Path to the pre-registration in `research_lab/03_experiments/protocols/`, and the G2 approval decision |
| Hypothesis | H-id(s) |
| Code / config | Git commit, config file SHA-256, overrides |
| Seeds / splits | Seed list; splits used (test only for the pre-registered final evaluation) |
| Environment | Lock-file hash, framework and CUDA versions, GPU |
| Status | `planned`, `registered`, `running`, `completed`, `failed` or `aborted` (with the reason) |
| Outputs | Run dir, checkpoints, metrics files, logs, tuning study |
| Deviations | Anything that differed from the protocol |
| Findings | F-ids derived from this run |

## Verification before recording

- **Experimental:** open the metrics file and recompute the number rather than copying it from a log line or a report.
- **Literature:** the finding must point to an evidence card whose DOI is `VERIFIED` and whose quote you re-read in the full text.
- **Audit:** cite the file path and line or cell, and re-open the file at recording time.

## Naming the check

Write "verified", "re-hashed", "confirmed identical", "checked" or similar only together with the mechanism: which files, which method (byte hash, row count, substring presence, visual inspection) and against what. A bare claim of verification counts as unverified.

A source is not a check. "The CSV row" names where a number lives, not what was done to it.

```
Verified: recomputed val_f1 with python -c from the epoch-12 row of <run dir>/metrics.csv (byte hash of the file unchanged since the run) against the number in the F-0042 statement; matches to 4 decimals.
```

## Methodological basis

- Schnell 2015, *Ten simple rules for a computational biologist's laboratory notebook*, PLOS Comput Biol. https://doi.org/10.1371/journal.pcbi.1004385
- Wilkinson et al. 2016, *The FAIR guiding principles for scientific data management and stewardship*, Scientific Data. https://doi.org/10.1038/sdata.2016.18

## Claude Code notes

Change ledger files with the file tools. Recompute with a short `python -c` against the metrics file and paste the command into the notebook entry.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "The log line has the number" | A log line is not the metrics file. Recompute it first. |
| "I'll record it after the run finishes" | Dead ends are forgotten by then. Write the notebook entry now. |
| "I'll add a candidate row until it's checked" | There is no such status. `tentative` after recomputing, nothing before. |
| "I'll add it as `tentative` from the hand-off and let the Curator check it" | `tentative` is a number you recomputed. Open the metrics file and recompute first; until then, no row. |
| "Editing the verified row is quicker" | Never edited. Write the new row; mark the old `superseded by F-new`. |
| "Single seed is fine for now" | Fine as `tentative` with "single seed" in the caveats. Never `verified`. |
| "The report I'm summarising already verified it" | A report is not the file. Re-open the file and recompute. |
| "'Verified' is just a word" | A bare claim counts as unverified. Name files, method and reference. |
| "The CSV row is the check" | That is the source. Name the method and the reference too. |

## Red Flags

- A number in a draft, brief or answer with no F-id behind it
- A row added from a log line, a hand-off or someone's summary, under any status
- A status other than the four above
- "Verified" with no file, method and reference
- An edit to a row that is already `verified`
- Two documents quoting different values for one number

**Any of these: stop, recompute from the file, and record only what the check supports.**

## Verification Checklist

- [ ] Every number I quote has an F-id and matches the ledger
- [ ] Every new row's evidence is a file I re-opened at recording time
- [ ] No `verified` row was edited
- [ ] Single-seed, dev-only and partial-run rows are `tentative` with caveats
- [ ] Every "verified" I wrote names files, method and reference
- [ ] Canonical numbers and the notebook entry are updated
