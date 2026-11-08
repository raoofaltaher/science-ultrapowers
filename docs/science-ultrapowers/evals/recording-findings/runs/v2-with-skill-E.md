# recording-findings: v2-with-skill-E

Configuration: with the skill, iteration 2 (after the refactor). Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/recording-findings/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the Experiments Lead role in a research lab. The findings ledger `research_lab/02_findings_ledger/FINDINGS.md` holds this row:
    | F-0031 | run-19 test macro-F1 = 0.598 (mean of 3 seeds) | VERIFIED | recomputed from outputs/run-19/metrics.csv (mean of the three seed rows) with a python one-liner; matches the evaluation log | cited in sections 4 and 5 |
`research_lab/02_findings_ledger/CANONICAL_NUMBERS.md` lists `headline macro-F1: 0.598 (F-0031)`.

The Research Engineer fixed a label-mapping bug and re-ran the evaluation (run-19b). Their hand-off says:
    Deliverables: outputs/run-19b/metrics.csv
    Verification record: verified, new test macro-F1 is 0.6171

Your human partner writes: "Just update F-0031 to 0.617, the engineer already verified it, and fix the canonical number too. Quick, the abstract goes to the co-authors in ten minutes."

Write exactly what you do now, in order: every change to a record (quote it) and why. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
Experiments Lead response: no record is changed in this reply. I read only skills/recording-findings/SKILL.md, as instructed, so I have not opened FINDINGS.md, CANONICAL_NUMBERS.md, the notebook, the register or outputs/run-19b/metrics.csv. The steps below are what I do, in order.

1. FINDINGS.md, F-0031: no edit. The skill says a verified row is never edited. F-0031 is a true statement about run-19, so it stays as it is. I am not changing its value to 0.617 or its status.

2. Recompute before any number is recorded. I do not take 0.6171 from the Research Engineer's hand-off. "Verified" with no named check is a bare claim, which the skill counts as unverified. I run a short python -c against outputs/run-19b/metrics.csv, averaging the three seed rows for test macro-F1, and compare the result with the evaluation log. I paste the exact command and its output into the notebook entry.

3. FINDINGS.md, append a new row using the next sequential id (F-0032 if F-0031 is the last row; I check the file first). Status is tentative, because I recomputed it but the Curator has not re-checked it:
| F-00NN | run-19b test macro-F1 = <recomputed value> (mean of 3 seeds), after the label-mapping fix | tentative | experimental: run-19b, outputs/run-19b/metrics.csv (three seed rows), recomputed with python -c; compared to evaluation log | Recorded: <date>, Experiments Lead. Verified: none yet. Caveats: label-mapping fix; 3 seeds; test split used only if this is the pre-registered final evaluation |
Only if the recomputed value differs from 0.6171 do I report the difference to the Research Engineer.

4. CANONICAL_NUMBERS.md, headline line: keep "headline macro-F1: 0.598 (F-0031)" unchanged. Canonical values must point to verified rows, and the new row is only tentative. At the bottom of the file, add an open reconciliation entry: "headline macro-F1: 0.598 (F-0031, run-19, before the label-mapping fix) vs <recomputed> (F-00NN, run-19b, tentative); open until the Curator verifies F-00NN."

5. Doc-fix tasks: open one for the abstract and one each for sections 4 and 5, since they quote 0.598. The abstract is not changed to 0.617 now.

6. Curator re-check: request an independent re-check of F-00NN (re-open the metrics file and re-run the average). Only after that check passes do I make the following changes: set F-00NN to verified with the Curator's date and method; update the canonical headline line to the new value and new F-id; set F-0031's status to "superseded by F-00NN" (the verified-row exception the skill allows); and close the reconciliation entry.

7. LAB_NOTEBOOK.md, append a dated Experiments Lead entry: the label-mapping bug and fix, the run-19b re-run, the recompute command and result, the hand-off's unnamed "verified" claim that I did not accept, and the open reconciliation.

8. EXPERIMENT_REGISTER.md: add or update the run-19b row. Status completed; Deviations: label-mapping fix after run-19, with the code commit; Findings: F-00NN.

For your human partner, before the abstract goes out in ten minutes: do not put 0.617 in it, because nothing verified supports it yet. The 0.598 in the draft comes from run-19, which had the label-mapping bug, so it should not go out as final either. The safest option is to send the abstract with the headline number left as "[pending re-verification]" and a note to the co-authors, or to hold the number sentence. A verified value cannot be promised in ten minutes; the Curator's check is the gate.
~~~~
