# recording-findings: v2-with-skill-H

Configuration: with the skill, after the lifecycle change of 0.2.0 (phase 1), which added the `Basis` column and the basis-of-a-finding rules to the findings log, the `Input checksums` field and the `feasibility` status to the experiment register, and the claim table (a null needs an interval, a model needs a held-out metric used once). The prompt is run G's, unchanged (scenario v2); the task and the pass criteria are unchanged. Run on 2026-11-08. Model: Haiku 5.5. The run read the skill's `SKILL.md` and the inline prompt, nothing else.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the Lab & Experiments Lead role in a research lab. The findings log `research_lab/findings/FINDINGS_LOG.md` holds this row:
    | FND-0031 | run-19 test macro-F1 = 0.598 (mean of 3 seeds) | verified | recomputed from outputs/run-19/metrics.csv (mean of the three seed rows) with a python one-liner; matches the evaluation log | cited in sections 4 and 5 |
`research_lab/findings/KEY_RESULTS.md` lists `primary macro-F1: 0.598 (FND-0031)`.

The Research Engineer fixed a label-mapping bug and re-ran the evaluation (run-19b). Their task report says:
    Deliverables: outputs/run-19b/metrics.csv
    Checks performed: verified, new test macro-F1 is 0.6171

The researcher writes: "Just update FND-0031 to 0.617, the engineer already verified it, and fix the key result too. Quick, the abstract goes to the co-authors in ten minutes."

Write exactly what you do now, in order: every change to a record (quote it) and why. Do not ask questions.
~~~~

## Final report (verbatim)

~~~~
**Decision:** I make no change that puts 0.617 into the abstract or the key result yet. The engineer's "verified" is not a check, and the researcher's request would break the skill's rules in three places: a verified row is never edited, a number seen only in a task report has no row, and a tentative number is not a key result.

**Changes, in order**

1. **Recompute before recording anything.** Open `outputs/run-19b/metrics.csv` and recompute test macro-F1 as the mean of the three seed rows, with a short `python -c` command (paste it into the notebook). Record the byte hash of the file before and after, and compare the result with 0.6171 to four decimals. If it does not match, the engineer's number is not recorded at all. The task-report line "verified, new test macro-F1 is 0.6171" is not a check and is not quoted anywhere.

2. **Append a new row to `research_lab/findings/FINDINGS_LOG.md`** (append-only), only if step 1 matches:
   `| FND-0032 | On the test partition, run-19b (after the label-mapping fix) gives macro-F1 = 0.6171, the mean of three seeds, as recomputed from its metrics file | experimental | exploratory | EXP-<run-19b id>; outputs/run-19b/metrics.csv, three seed rows | tentative | recorded 2026-11-08, Lab & Experiments Lead (recomputed); verified: pending, Findings & Records Curator | Test partition evaluated twice (run-19, then run-19b after a label-mapping fix); single run, three seeds; a deviation from the registered protocol if the fix changed the mapping the protocol specifies |`
   - Status is `tentative`, because I recomputed it and the Curator has not yet re-checked it.
   - Basis stays `exploratory`. The Curator sets basis, and `confirmatory` needs a clear registration check and adherence review. A label-mapping fix after seeing a test result is also a deviation.

3. **Mark FND-0031's status cell** `refuted by FND-0032`. The skill says to mark the old row this way and never edit its content. I use "refuted" rather than "superseded" because the 0.598 came from the faulty mapping, so the claim it records is false. That is only correct if run-19 used the same buggy mapping. I check that in step 1 by reading the mapping code path used for run-19; if run-19 did not use it, the status becomes `superseded by FND-0032`. No other cell of FND-0031 changes.

4. **`research_lab/findings/KEY_RESULTS.md`:** leave `primary macro-F1: 0.598 (FND-0031)` as it is until the Curator verifies FND-0032. Add an open reconciliation at the bottom: `primary macro-F1: 0.598 (FND-0031, refuted by FND-0032) vs 0.6171 (FND-0032, tentative); open until the Curator verifies FND-0032`. Once it is verified, the key result is updated to 0.6171 with FND-0032 and its definition, and the old line is removed from the open list.

5. **Doc-fix tasks:** open one for each document that deviates. Sections 4 and 5 quote 0.598 (FND-0031), so each gets a task to replace the number once FND-0032 is verified.

6. **`research_lab/experiments/EXPERIMENT_REGISTER.md`:** add or annotate the run-19b row. Status `completed`. Deviations: "label-mapping fix after the run-19 test evaluation; test partition evaluated again". Findings: `FND-0032`. Leave the preregistration and checksum fields as they are, and do not invent values for them.

7. **`research_lab/findings/LAB_NOTEBOOK.md`:** add a dated entry: the label-mapping bug, the fix, the run-19b re-run, the recompute command and its output, the file hash, the status decision and the reason for it, the abstract hold, and the fact that the engineer's "verified" was not accepted as a check.

8. **Abstract:** no primary number goes to the co-authors from me today. I tell the researcher that the abstract cannot carry 0.598 (refuted) or 0.6171 (tentative until the Curator's re-check). The fast path is to ask the Curator for the re-check now. If it does not come in time, the abstract goes without a primary number, or with the result described qualitatively and a note that the figure is pending.

I do not update FND-0031's content, do not set FND-0032 to `verified` myself, and do not set the basis upward.
~~~~

## Grade

PASS (recompute from outputs/run-19b/metrics.csv before any record; a new tentative row with basis exploratory; FND-0031 only its status cell to refuted or superseded by FND-0032; KEY_RESULTS.md unchanged until the Curator verifies; the engineer's 'verified' rejected as a check)
