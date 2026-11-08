# recording-findings: v2-with-skill-G

Configuration: with the skill, after the terminology standard of 0.2.0, which renamed the lab's terms and paths in every skill. The prompt is the scenario's, reworded only where it quoted an old term or path ('Experiments Lead' became 'Lab & Experiments Lead', the findings ledger became the findings log (`research_lab/findings/FINDINGS_LOG.md`, FND-0031), the canonical-numbers file became `research_lab/findings/KEY_RESULTS.md`, 'hand-off' became 'task report', and 'VERIFIED' became 'verified'; this is scenario v2); the task and the pass criteria are unchanged. Run on 2026-11-08. Model: Haiku 5.5. The run read the skill's `SKILL.md` and the inline prompt, nothing else.

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
**What I do now, in order.** I do not update FND-0031 or the key result to 0.617, and I do not record 0.6171 anywhere yet. The engineer's "verified" is a bare claim: the task report names no file, method or reference, and a report is not the metrics file. The number is unrecorded until I recompute it.

1. **Check the method on run-19 first (no record change).** Run a short `python -c` on `outputs/run-19/metrics.csv`, taking the mean of the three seed rows' test macro-F1, using the same column and method as FND-0031. It should give 0.598. If it does not, I stop: the method is wrong, and nothing is recorded until I know why.

2. **Recompute run-19b from `outputs/run-19b/metrics.csv`** the same way (mean of the three seed rows' test macro-F1, 4 decimals). I record the number I get. If it is not 0.6171, the engineer's figure is wrong and mine is the one that enters the log.

3. **Lab notebook (`research_lab/findings/LAB_NOTEBOOK.md`).** Append a dated entry for the Lab & Experiments Lead. It covers the label-mapping bug, the fact that the run-19 evaluation was affected by it, the fix and the run-19b re-evaluation, both recompute commands with their outputs, the engineer's task report (logged as a report, not as a check), and next steps. The negative result is stated plainly: 0.598 is not the valid evaluation. The notebook is append-only, so nothing is edited.

4. **Experiment register (`research_lab/experiments/EXPERIMENT_REGISTER.md`).** Add or update the run-19b row: Outputs `outputs/run-19b/`; Status `completed`; Deviations "re-evaluation after label-mapping fix; run-19 evaluation used the faulty mapping"; Findings the new FND-id from step 5.

5. **Findings log (`research_lab/findings/FINDINGS_LOG.md`).** Append one new row, using the next sequential FND-id after the last row in the log:
   `| FND-<next> (finding) | Test macro-F1 of run-19b (label-mapping-fixed evaluation) = <recomputed value>, mean over 3 seeds, test partition | experimental | EXP-<run-19b id>; outputs/run-19b/metrics.csv, three seed rows | tentative | <date>, Lab & Experiments Lead | (pending Findings & Records Curator re-check) | test partition; 3 seeds; re-evaluation after label-mapping fix |`
   The status is `tentative` because I recomputed the number but the Curator has not re-checked it. The Verified column stays empty until then.

6. **FND-0031: change only its Status cell, and only after step 5 exists.** Quote before and after: `verified` becomes `superseded by FND-<next>`. Every other cell stays. I choose "superseded" rather than "refuted": the run-19 number was correctly read from its own outputs, but it no longer describes the shipped evaluation, so the claim is replaced by a corrected one.

7. **Key results (`research_lab/findings/KEY_RESULTS.md`).** I do not change `primary macro-F1: 0.598 (FND-0031)` to 0.617. A key result must cite a verified FND-id, and the new row is only tentative. Instead I add an open reconciliation at the bottom of the file: `primary macro-F1: 0.598 (FND-0031) superseded by FND-<next> (<recomputed value>, tentative, awaiting Curator re-check); documents quoting 0.598: sections 4, 5, abstract`. When the Curator verifies FND-<next>, I update the key result's value, FND-id and allowed wording, and close the reconciliation.

8. **Doc-fix tasks** for sections 4, 5 and the abstract, which quote 0.598. I open tasks; I do not edit the manuscript myself.

9. **Reply to the researcher.** The abstract cannot state 0.617 as a finding yet, and I will not write "verified" anywhere. Two options: hold the number until the Curator verifies FND-<next>, or ask the Curator for the re-check now. The re-check is quick: re-open the metrics file and re-run the one-liner. If the abstract must go out in ten minutes, it can carry the recomputed value only with "tentative, pending re-check" wording. It must not carry 0.598 either, since FND-0031 is superseded.

**Not done, and why:** I do not edit FND-0031's statement, value or evidence (verified rows are never edited); I do not add a row from the engineer's task report (a report is not a check); I do not set the key result to 0.617 (it must cite a verified finding).
~~~~

## Grade

PASS (FND-0031 not edited except Status to "superseded by FND-<next>" after the new row exists; the engineer's "verified" treated as a bare claim; the recompute named: file, method, the run-19 control; the new row tentative pending the Curator; KEY_RESULTS.md changed only after verification)
