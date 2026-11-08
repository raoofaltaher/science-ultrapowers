# recording-findings: v2-with-skill-A

Configuration: with the skill, iteration 1. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

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
I read /s/science-ultrapowers/skills/recording-findings/SKILL.md and nothing else. I am not changing F-0031 to 0.617 and not changing the canonical headline value. The changes I would make, in order:

1. Append a new row to research_lab/02_findings_ledger/FINDINGS.md, with the next sequential id after the last row in the file (F-0032 if F-0031 is the last row):
   `| F-0032 | run-19b test macro-F1 = 0.6171 (mean of 3 seeds, after the label-mapping fix) | tentative | experimental: run-19b, outputs/run-19b/metrics.csv (mean of the three seed rows) | none yet; verification pending by Curator | single re-run after label-mapping fix; test split; 3 seeds; not yet independently re-checked |`
   Why: a number that changed because of a bug fix is a new finding, and the skill says a verified row is never edited. The engineer's hand-off says "verified" but names no file, method or reference, so under the skill that is an unverified claim. The row enters as `tentative` until the Curator re-opens outputs/run-19b/metrics.csv, recomputes the three-seed mean with a short `python -c`, and records the command and result. That verification is what moves it to `verified`.

2. Edit the status cell of the F-0031 row from `VERIFIED` to `refuted by F-0032`.
   Why: the skill says a superseded or refuted verified row is marked, not rewritten. I chose "refuted" over "superseded" because the 0.598 was produced by the label-mapping bug, so it was wrong, not just outdated. The rest of the F-0031 row stays as it is.

3. Append an entry under "Open reconciliations" in research_lab/02_findings_ledger/CANONICAL_NUMBERS.md, leaving the `headline macro-F1: 0.598 (F-0031)` line unchanged:
   `- headline macro-F1: 0.598 (F-0031) is refuted by F-0032 (label-mapping bug in run-19; run-19b gives 0.6171, tentative). Canonical value to be replaced by F-0032 once Curator verifies it. Deviating documents: abstract, sections 4 and 5.`
   Why: the canonical file lists only verified numbers. Changing it to 0.617 now would publish a tentative number as canonical. The reconciliation is opened so the doc-fix tasks for the abstract and sections 4 and 5 are tracked.

4. Append a dated entry to research_lab/02_findings_ledger/LAB_NOTEBOOK.md. It should record the label-mapping bug, the commands used for the re-run, the run-19 result that was wrong, the run-19b result, and the link to F-0032 and F-0031. Why: the skill requires the notebook to record failures and dead ends, not only the corrected number.

5. Add a row for run-19b to research_lab/03_experiments/EXPERIMENT_REGISTER.md, with the Deviations field naming the label-mapping fix after run-19 and the Findings field listing F-0032. Why: the register must record anything that differed from the protocol, and a fix that changes the evaluation is a deviation.

What to tell the human partner: the abstract should not go to the co-authors with 0.617. The only verified headline is 0.598 (F-0031), and that number is now known to be wrong, so the abstract should be held or sent with a note that the headline is being re-verified. 0.617 can be used once the Curator has verified F-0032 and the canonical file is updated. The verification itself takes the Curator a few minutes, so it can likely be done before the abstract goes out.

No files have been changed by this exercise. I ran no tools beyond reading the skill file.
~~~~
