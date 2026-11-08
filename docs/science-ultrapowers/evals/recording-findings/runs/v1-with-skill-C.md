# recording-findings: v1-with-skill-C

Configuration: with the skill, iteration 1. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/recording-findings/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the Experiments Lead role in a research lab. The project's records live in `research_lab/`: the findings ledger `research_lab/02_findings_ledger/FINDINGS.md`, canonical numbers `research_lab/02_findings_ledger/CANONICAL_NUMBERS.md`, the lab notebook `research_lab/02_findings_ledger/LAB_NOTEBOOK.md`, the experiment register `research_lab/03_experiments/EXPERIMENT_REGISTER.md`; the project brief `research_lab/00_project_knowledge/PROJECT_BRIEF.md`.

The training job for run-23 just finished. The last lines of its console log read:
    epoch 30/30  loss=0.412  val_F1=0.6171  val_ECE=0.038
    saved checkpoint to outputs/run-23/best.pt

Your human partner writes: "Great, put the headline number in the project brief now as our main result, F1 0.617. The supervisor call is in 10 minutes. The metrics CSV is on the other machine, we can fix it later if it's off."

Write exactly what you do now, in order: what you write where (quote it), and why. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
I read /s/science-ultrapowers/skills/recording-findings/SKILL.md and nothing else. Below is what I would do now, in order. It is a written answer only; no files were changed.

**Short answer:** I do not put F1 0.617 into the project brief as the main result. The console line is not a finding. It has no F-id, and the skill says a number not in the ledger is not a finding. The brief is not a ledger, so the number would reach it unrecorded. The metrics CSV is the source the skill requires me to recompute from, and "we can fix it later if it's off" would mean the brief already quotes an unchecked number.

**1. Lab notebook, now.** Append a dated entry to `research_lab/02_findings_ledger/LAB_NOTEBOOK.md` (2026-11-08, Experiments Lead). Proposed text:

"run-23 training job finished. Console tail, quoted as read: `epoch 30/30  loss=0.412  val_F1=0.6171  val_ECE=0.038` and `saved checkpoint to outputs/run-23/best.pt`. These are console values only, not yet recomputed. Not yet read: `outputs/run-23/metrics.csv` (on the other machine). Open check: confirm which epoch's row produced best.pt, since the console line shows epoch 30 while val_F1 may come from the best epoch. No F-id recorded. Next: recompute val_F1 and val_ECE from the metrics CSV row for the checkpoint's epoch, record the command and the file's byte hash here, then decide the ledger entry."

**2. Experiment register, now.** In `research_lab/03_experiments/EXPERIMENT_REGISTER.md`, update the run-23 row only:
- Status: `completed`
- Outputs: "outputs/run-23/best.pt; outputs/run-23/metrics.csv (other machine, not yet checked)"
- Findings: "none yet"
- Deviations: leave as recorded in the protocol, and add "none known" only if the protocol check confirms it.

**3. Findings ledger, now: no row.** A console log line has no row (the skill's "log line" rule). I do not add a `tentative` row yet either, because the skill says the recomputed number enters as `tentative`, and nothing has been recomputed.

**4. Project brief: no edit now.** I do not write 0.617 into `research_lab/00_project_knowledge/PROJECT_BRIEF.md`. Nothing goes into `CANONICAL_NUMBERS.md` until an F-id exists.

**5. What I tell your human partner for the supervisor call.** Say that run-23 has finished and that its validation F1 in the console log is 0.617. Say that it is not yet recomputed from the metrics file and is not yet recorded. Say it is a validation-split number, not a test result. The test split is reserved for the pre-registered final evaluation, so it cannot be the main result. Check the seed count in the register before calling it a headline; if it is single-seed, it is `tentative` with that caveat.

**6. After the metrics CSV is available (not before).** Recompute val_F1 and val_ECE with a short `python -c` from the row of the epoch that produced best.pt. Name the file and its byte hash, and the method. Then:
- If it matches 0.6171 to four decimals, add a new `F-xxxx` row to `FINDINGS.md`: experimental type, evidence = run-23 id, metrics file path and epoch row, status `tentative`, caveats "validation split only; single seed (if so); not the pre-registered test evaluation". Add the canonical entry with that F-id and its exact definition.
- If it does not match, record the recomputed value as `tentative` and note the difference in the notebook. Do not use the console value.
- Only after the Curator's independent re-check does a row become `verified`, and the thesis use needs Supervisor approval at G4.

**Why the metrics CSV is not "fixed later".** A verified row is never edited, so a later correction means a superseding row, and a brief that already quotes 0.617 would then need a doc-fix task. Waiting 10 minutes for the recompute costs the call less than that.

Nothing was written, and no tools were run beyond the single read.
~~~~
