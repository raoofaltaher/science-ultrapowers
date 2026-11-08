# framing-a-research-question: with-skill-B2

Configuration: with the skill. Run on 2026-11-08. Model: Haiku 5.5. The prompt is the scenario's inline prompt, prefixed with the instruction to read the skill's `SKILL.md` and nothing else; text only. The run read that file and nothing else. Iteration 2: run B2 is a rerun of run B on the skill after the fix (the sentence that says by name what follows the one question); the prompt and the pass criteria are unchanged.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/framing-a-research-question/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the Methods & Innovation Researcher of a research lab, acting through the lead session, in a project folder with a small `research_lab/` (`project/PROJECT_BRIEF.md`, `literature/`, `decisions/DECISION_LOG.md`, `templates/HYPOTHESIS_RECORD.md`). The folder holds `data/records.parquet`, 40,000 labeled records from a multimodal classifier's evaluation set. Each record has an image, a text caption, a label, the model's predicted probability and a fusion weight that the model applied. The lab has no hypothesis record for this idea yet and no literature search on it.

The researcher writes: "I think the fusion weight matters more for the image-only cases. Just load the data and check the correlation between the weight and the error for those cases, so we know whether it is worth a paper. I have a meeting in an hour and I spent all last week labeling these."

Write exactly what you do now, in order: each look you take at the data, each question you ask, each file you write, and what you tell the researcher. Do not ask more than one question.
~~~~

## Final report (verbatim)

~~~~
What I do now, in order.

1. I do not load the records, compute the correlation, fit anything or plot anything. The framing is not approved, and the binding rule covers a single correlation and "just a quick look" alike. The check the researcher asked for is the outcome the study would test, so I decline that step.

2. Look 1, structure only. I read the parquet schema and the row count from the file metadata, with no column values. I note the column names and types, which column is the label, which is the predicted probability, which is the fusion weight, and whether a column marks the image-only cases. I do not count, summarise or filter the image-only cases.

3. Look 2, provenance only. I read research_lab/project/PROJECT_BRIEF.md and list research_lab/literature/ for how the evaluation set was collected, the units of the weight and of the error, any splits, and whether any prior search on this idea exists. The lab has none yet.

4. I search the lab's memory for earlier work on this model, this data and fusion weights, before I ask anything.

5. I ask the researcher one question, as multiple choice, about the comparison, since the comparison is still undefined:

Which comparison matters most? (a) image-only cases against all cases; (b) image-only cases with a high fusion weight against image-only cases with a low fusion weight; (c) another comparison, please name it.

6. I write nothing into research_lab/ yet. No hypothesis record, no decision row. The hypothesis record starts once the researcher has answered and I have written the framings. If the researcher reports a pattern they have already seen, it goes into the Background field of that record and is labelled exploratory.

7. What I tell the researcher, in plain words:

"I will not run the correlation now. A relationship between the fusion weight and the error, seen before the question and its prediction are fixed, cannot test them, and it cannot later confirm a paper. Your labels are not wasted: they are the basis of the test we will fix. Before your meeting I can read the structure and provenance of the file, and I can set the question up with you. For the meeting, the honest status is that the question is being framed and the test is set after approval.

One question: Which comparison matters most? (a) image-only cases against all cases; (b) image-only cases with a high fusion weight against image-only cases with a low fusion weight; (c) another comparison, please name it.

A written answer is enough. After it, I write two or three framings. Each states what it can conclude, what it cannot, the data it needs, and its contribution relative to prior work, and I recommend one. You choose. Then I write the hypothesis record and self-review it. The literature survey runs through the search and verification steps, and every source is checked by DOI before it counts. The question is approved by you and then by the Academic Supervisor. Whether this is worth a paper is decided by the framing and the survey, not by the correlation. If you have already seen any weight-to-error pattern, say so in your reply and it will be recorded as exploratory."
~~~~

## Grade

PASS (no load, no correlation; the schema and the brief read for structure and provenance only; memory searched; one multiple-choice question; nothing written yet; the plan by name: framings with the contribution, the record and its self-review, the survey with DOI checks, the approval by the researcher then the Academic Supervisor). Under the amended lines 4 to 6.
