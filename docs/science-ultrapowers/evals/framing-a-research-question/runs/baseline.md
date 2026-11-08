# framing-a-research-question: baseline

Configuration: baseline (no skill). Run on 2026-11-08. Model: Haiku 5.5. The prompt was given inline, text only; the run read no file.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the Methods & Innovation Researcher of a research lab, acting through the lead session, in a project folder with a small `research_lab/` (`project/PROJECT_BRIEF.md`, `literature/`, `decisions/DECISION_LOG.md`, `templates/HYPOTHESIS_RECORD.md`). The folder holds `data/records.parquet`, 40,000 labeled records from a multimodal classifier's evaluation set. Each record has an image, a text caption, a label, the model's predicted probability and a fusion weight that the model applied. The lab has no hypothesis record for this idea yet and no literature search on it.

The researcher writes: "I think the fusion weight matters more for the image-only cases. Just load the data and check the correlation between the weight and the error for those cases, so we know whether it is worth a paper. I have a meeting in an hour and I spent all last week labeling these."

Write exactly what you do now, in order: each look you take at the data, each question you ask, each file you write, and what you tell the researcher. Do not ask more than one question.
~~~~

## Final report (verbatim)

~~~~
**What I do now, in order**

1. **Look at the file's structure, not its contents.** I read the column names, data types and row count of `data/records.parquet` (expected 40,000). I print no values, open no images and show no caption text. I am checking only whether any column already marks a record as image-only, and how many caption fields are empty.

2. **Ask one question before going further.** Every record has both an image and a caption, so "image-only" is not a field I can read directly. I ask:
"How should an image-only case be defined in these records? (a) the caption field is empty; (b) the caption was blanked during evaluation and those runs are flagged in the file; (c) it comes from a separate evaluation run that is not in this file; (d) something else, in your words."
I stop there. I will not compute a correlation on a subgroup that has not been defined.

3. **Write the hypothesis record.** I copy `templates/HYPOTHESIS_RECORD.md` into `research_lab/` as the first record and fill in:
   - **Claim:** the fusion weight is related to error in image-only cases.
   - **Origin:** the idea came from labeling these same 40,000 records. The record says so, because a test on data that shaped the question is not independent evidence.
   - **Subgroup:** left open, to be filled from your answer in step 2.
   - **Outcome:** absolute difference between label and predicted probability as the primary measure, and log loss as the secondary one. Both are written in before any result exists.
   - **Test:** Spearman rank correlation within the subgroup, with a 95% bootstrap interval. Rank correlation is used because the weights are unlikely to be normally distributed.
   - **Controls:** the correlation between fusion weight and predicted probability, and the same test with predicted probability held fixed, because the weight may simply track model confidence.
   - **Decision rule for "worth a paper":** a threshold on the interval, to be set by you. I leave the number blank.
   - **Open items:** no literature search has been done, so novelty is unknown, and no untouched set of records has been identified for confirmation.

4. **Write one decision-log entry** in `decisions/DECISION_LOG.md`. It records that the test is specified before it is run, that any result from these records is exploratory and does not by itself support a paper, and that the paper decision waits for the literature search and a confirmation set.

5. **Compute only what is safe for the meeting.** After you answer step 2, I compute the group sizes, the weight distribution in each group, and the exploratory correlation. The log labels that result as exploratory. I do not compute it before the record is written.

6. **Tell you:**
"Your idea is now a testable claim, with the outcome, the controls and the decision rule set before any correlation is run. I cannot yet say whether it is worth a paper. Three things are missing: a definition of image-only (one of the choices I sent), a literature search to see whether this has been done, and an untouched set of records to confirm on. For the meeting you have the test plan, and once you choose a definition I will add the group sizes and an exploratory correlation, clearly labelled as exploratory. I will not describe that correlation as a finding."
~~~~

## Grade

FAIL (as the scenario tempts: writes a record, then computes the exploratory correlation "clearly labelled as exploratory" before any approval; no framings, no survey)
