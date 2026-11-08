---
name: recording-findings
description: Use when recording, verifying, reconciling, quoting or looking up any project fact, result, number or experiment, when two documents disagree on a number, or when a role is about to write "verified", "confirmed" or "re-checked"
---

# Recording Findings

## Overview

Every number or fact in a document, report, manuscript or chat answer is quoted from the lab's records, never retyped from memory. If it is not in the findings log, it is not a finding.

**Core principle:** A claim is only as good as the check it names.

## The binding rule

```
A NUMBER NOT IN THE FINDINGS LOG IS NOT A FINDING; A CHECK THAT DOES NOT NAME ITS MECHANISM IS NOT A CHECK
```

## Findings log

`research_lab/findings/FINDINGS_LOG.md`: one row per finding, append-only. The header is `| FND-id (finding) | Statement | Type | Basis | Evidence | Status | Recorded | Verified | Scope and caveats |`.

| Field | Content |
|---|---|
| `FND-id` | `FND-0001`, sequential, one counter per lab. Rows written under the 0.1 layout keep their old ids (`F-0001`), which stay valid |
| Statement | One precise sentence including the number and its definition (metric, partition, seed count, confidence interval (CI)) |
| Type | `experimental`, `literature`, `code inspection`, `data inspection` or `document inspection` |
| Basis | `confirmatory` or `exploratory`; see Basis of a finding below. A row written before the column existed reads as `exploratory` |
| Evidence | Experimental: experiment id (EXP-id) and metrics file path (and row or epoch). Literature: source id and evidence record id (EVR-id). Inspection: file path and line or cell |
| Status | `tentative`, `verified`, `superseded by FND-xxxx` or `refuted by FND-xxxx` |
| Recorded and verified | Date and role for each |
| Scope and caveats | e.g. "dev partition only", "known leakage in this partition", "single seed" |

These four statuses are the only ones. There is no "candidate", "provisional" or "pending" row.

Transitions:

- `tentative` to `verified` requires an independent re-check by the Findings & Records Curator (the Curator): re-open the file or re-run the query; for literature, re-run `science-ultrapowers:verifying-evidence-by-doi` and re-read the quote. For claims a manuscript or thesis will use, Academic Supervisor approval at the Results stage as well.
- A verified row is never edited. Write a new row and mark the old one `superseded by FND-new` or `refuted by FND-new`.
- A single-seed, dev-only or partial-run result stays `tentative` and says so in its caveats.

A number seen only in a console log, a progress bar, a report or another role's task report has no row, not even a `tentative` one. Recompute it from the metrics file yourself (see Checks before recording); the recomputed number enters as `tentative`, never `verified`. `tentative` means you recomputed it; it never means "not yet checked".

## Basis of a finding

A finding is confirmatory only with a registered protocol whose registration check is clear and a run that matched it. Everything else is exploratory.

The Findings & Records Curator sets the basis. For `confirmatory` it needs two files, both clear: the registration check saved as an artifact (`science-ultrapowers:preregistering-the-protocol`) and the protocol-adherence review of the run. A missing file, an `unprovable` item or an adherence issue makes the row `exploratory`. A deviation from the registered protocol makes the affected finding exploratory; the row says so in its caveats. A basis is never relabeled upward after the fact.

| Claim | Requires | Not sufficient |
|---|---|---|
| A null result | An effect size and an interval, read against the smallest effect size of interest in the protocol | "Not significant", or a p-value alone |
| Model quality | A held-out metric on the registered held-out test set, used once | A validation score, or a test score after tuning |
| "Reproduces" | A re-run from the raw inputs with the recorded seed that matches the recorded number | Loading a saved output, or a cached intermediate |
| Confirmatory | A registered protocol, a clear registration check and a clear adherence review | A prediction that was "obvious", or a plan not registered before the runs |

A null result needs an effect size and an interval. A row that states a null without both stays `tentative` and says what is missing.

## Key results table

`research_lab/findings/KEY_RESULTS.md` lists the numbers documents quote (primary metrics, ratios, dataset counts, parameter counts): `name | value | exact definition | FND-id | allowed wording`.

When documents disagree on a number, the Curator traces each variant to its source, records one key result with its definition, and opens a doc-fix task for every document that deviates. Open reconciliations stay listed at the bottom of the file until resolved.

## Lab notebook

`research_lab/findings/LAB_NOTEBOOK.md`: dated, append-only entries, one per working session per role. Record what was attempted, the commands or configs used, what happened (failures and negative results included), links to experiment ids, FND-ids and evidence records, and next steps. Record negative results as carefully as positive ones.

## Experiment register

`research_lab/experiments/EXPERIMENT_REGISTER.md`: one row per experiment. The header is `| EXP-id (experiment) | Preregistration | Hypothesis | Code and config | Seeds and partitions | Environment | Input checksums | Status | Outputs | Deviations | Findings |`.

| Field | Content |
|---|---|
| EXP-id | Keep the project's scheme |
| Preregistration | Path to the preregistration in `research_lab/experiments/preregistrations/`, and the Preregistration stage approval decision |
| Hypothesis | HYP-id(s) |
| Code and config | Git commit, Secure Hash Algorithm 256 (SHA-256) hash of the config file, overrides |
| Seeds and partitions | Seed list; partitions used (test only for the preregistered final evaluation) |
| Environment | Lock-file hash, framework and CUDA (Compute Unified Device Architecture) versions, graphics processing unit (GPU) |
| Input checksums | A Secure Hash Algorithm 256 (SHA-256) checksum for every raw input file, recorded before the run; the registration check's `inputs` item compares against it. Rows written before the field existed stay empty |
| Status | `planned`, `feasibility`, `registered`, `running`, `completed`, `failed` or `aborted` (with the reason); `feasibility` marks a pilot run, which never supports a confirmatory finding |
| Outputs | Run directory, checkpoints, metrics files, logs, tuning study |
| Deviations | Anything that differed from the preregistration |
| Findings | FND-ids derived from this run |

## Checks before recording

- **Experimental:** open the metrics file and recompute the number rather than copying it from a log line or a report.
- **Literature:** the finding must point to an evidence record whose DOI status is `matched` and whose quote you re-read in the full text.
- **Confirmatory:** open the registration check's artifact and the adherence review, and read both verdicts at recording time; a verdict quoted from a task report is not a check.
- **Check of a file:** cite the file path and line or cell, and re-open the file at recording time.

## Naming the check

Write "verified", "re-hashed", "confirmed identical", "checked" or similar only together with the mechanism: which files, which method (byte hash, row count, substring presence, visual inspection) and against what. A bare claim of checking counts as unchecked.

A source is not a check. "The metrics file row" names where a number lives, not what was done to it.

```
Verified: recomputed val_f1 with python -c from the epoch-12 row of <run dir>/metrics.csv (byte hash of the file unchanged since the run) against the number in the FND-0042 statement; matches to 4 decimals.
```

## Methodological basis

- Schnell 2015, *Ten simple rules for a computational biologist's laboratory notebook*, PLOS Comput Biol. https://doi.org/10.1371/journal.pcbi.1004385
- Wilkinson et al. 2016, *The FAIR guiding principles for scientific data management and stewardship*, Scientific Data. https://doi.org/10.1038/sdata.2016.18

## Claude Code notes

Change findings log files with the file tools. Recompute with a short `python -c` against the metrics file and paste the command into the notebook entry.

## Rationalizations and replies

| Excuse | Reality |
|---|---|
| "The log line has the number" | A log line is not the metrics file. Recompute it first. |
| "I'll record it after the run finishes" | Negative results are forgotten by then. Write the notebook entry now. |
| "I'll add a candidate row until it's checked" | There is no such status. `tentative` after recomputing, nothing before. |
| "I'll add it as `tentative` from the task report and let the Curator check it" | `tentative` is a number you recomputed. Open the metrics file and recompute first; until then, no row. |
| "It would have been my prediction anyway" | Then it cost nothing to register. It was not registered, so it is exploratory. |
| "Editing the verified row is quicker" | Never edited. Write the new row; mark the old `superseded by FND-new`. |
| "Single seed is fine for now" | Fine as `tentative` with "single seed" in the caveats. Never `verified`. |
| "The report I'm summarizing already verified it" | A report is not the file. Re-open the file and recompute. |
| "'Verified' is just a word" | A bare claim counts as unchecked. Name files, method and reference. |
| "The metrics file row is the check" | That is the source. Name the method and the reference too. |

## Warning signs

- A number in a draft, task assignment or answer with no FND-id behind it
- A row added from a log line, a task report or someone's summary, under any status
- A status other than the four above
- "Verified" with no file, method and reference
- An edit to a row that is already `verified`
- Two documents quoting different values for one number
- A `confirmatory` row with no registration check artifact or no adherence review behind it
- A null result stated without an effect size and an interval

**Any of these: stop, recompute from the file, and record only what the check supports.**

## Checklist

- [ ] Every number I quote has an FND-id and matches the findings log
- [ ] Every new row's evidence is a file I re-opened at recording time
- [ ] No `verified` row was edited
- [ ] Single-seed, dev-only and partial-run rows are `tentative` with caveats
- [ ] Every "verified" I wrote names files, method and reference
- [ ] Every row has a basis; `confirmatory` only with the two clear files
- [ ] The key results table and the notebook entry are updated

Credit: the basis rule and the claim rows are reworded from the verifying-results-before-claiming and preregistering-analysis skills of K-Dense-AI/science-superpowers (MIT, Copyright (c) 2026 K-Dense, Inc.).
