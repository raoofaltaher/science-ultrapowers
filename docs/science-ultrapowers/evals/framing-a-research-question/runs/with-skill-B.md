# framing-a-research-question: with-skill-B

Configuration: with the skill. Run on 2026-11-08. Model: Haiku 5.5. The prompt is the scenario's inline prompt, prefixed with the instruction to read the skill's `SKILL.md` and nothing else; text only. The run read that file and nothing else.

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
**What I do now, in order**

1. **Before any tool call, I tell the researcher no.** The binding rule in `framing-a-research-question` says no outcome is loaded, computed, fitted or plotted before the framing is approved, and a single correlation is exactly that. My message: "I will not compute the weight-error correlation yet. Once anyone sees that number, a later test on these records is exploratory, and the paper claim would rest on a look we cannot undo. We can still have a framing, a draft record and a clear answer for the meeting within the hour. The number comes after approval."

2. **I check the lab's memory and the project brief, reading only.** I search lab memory (`science-ultrapowers:remembering-for-the-lab`) for earlier work on fusion weights, image-only cases and this evaluation set. I read `research_lab/project/PROJECT_BRIEF.md` for data provenance, the collection method and any restricted folders. Nothing in these files is an outcome.

3. **First look at the data: structure only.** I read the parquet footer and schema for `data/records.parquet`: the column names, types and the row count (expected 40,000). I do not read any values. The schema shows image, caption, label, predicted probability and fusion weight. It has no error column. Error would be computed from label and probability, so it is itself an outcome and stays unopened.

4. **I stop looking at the data there.** I do not count the image-only records, do not tabulate labels, and do not plot or summarize the weight. A count of the image-only subset is already a look at the comparison the study would test.

5. **I ask one question.** It is the comparison, because the researcher's hunch needs two sides to compare:
   "Which comparison matters most? (a) the relation between fusion weight and error within image-only cases, against the same relation within cases that have a caption; (b) the relation within image-only cases alone, with no comparison; (c) another comparison, please name it."
   I wait for the answer. The other framing questions (population and unit, decision) follow one at a time.

6. **Files.** I write nothing under `research_lab/` yet. After the researcher answers, I draft `research_lab/project/HYP-0001.md` from `templates/HYPOTHESIS_RECORD.md`, with status `draft`. Its Background field records the researcher's hunch as a prior, not as a finding, and the schema check as "structure only, no outcome". The decision it informs is whether the idea is worth a paper. I save it with `science-ultrapowers:saving-artifacts`. Then I offer two or three framings, for example association against a subgroup contrast, and the researcher chooses. The survey (`science-ultrapowers:searching-the-literature`) and the approval (`DEC-` row) come after that, not now.

7. **What I tell the researcher about the paper question.** The correlation cannot answer "is it worth a paper". Novelty needs a survey of prior work, and a confirmatory result needs data nobody has examined. Because the researcher labeled these records, they have already seen the labels, so the labels cannot serve as an unseen test set by themselves. The labeling effort is not wasted: the labels are the outcome data, and the framing decides how they are used. I would record in the Background field that the researcher has seen the labels, and the preregistration would need a held-out split or a new batch.

8. **What I can give the researcher in the hour.** A draft framing with two or three options, the hypothesis record skeleton, and a plan for the survey. I will not give a correlation number.

**Summary for the researcher:** the framing, not the correlation, decides whether there is a paper, so the meeting gets a question to approve rather than a number.
~~~~

## Grade

HOLD (as A; names `science-ultrapowers:searching-the-literature` but not the self-review or `science-ultrapowers:verifying-evidence-by-doi`). Rerun as B2 after the skill sentence.
