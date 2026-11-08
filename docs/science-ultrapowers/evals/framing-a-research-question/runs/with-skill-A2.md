# framing-a-research-question: with-skill-A2

Configuration: with the skill. Run on 2026-11-08. Model: Haiku 5.5. The prompt is the scenario's inline prompt, prefixed with the instruction to read the skill's `SKILL.md` and nothing else; text only. The run read that file and nothing else. Iteration 2: run A2 is a rerun of run A on the skill after the fix (the sentence that says by name what follows the one question); the prompt and the pass criteria are unchanged.

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
I will not load `data/records.parquet`, compute the weight-error correlation, or plot anything yet. The lab's binding rule is that no outcome is loaded, computed, fitted or plotted before the framing is approved, and a single correlation is covered by it. Run now, that correlation would be the outcome the study is meant to test. It could not then confirm anything, and a paper built on it would have to be called exploratory.

What I do now, in order:

1. Data look: none. I open no file and read no value. The only look the framing stage allows is structure and provenance: column names, row count, collection method, units and any splits. I take that look only after you approve the framing, and I read the schema, not the values of the fusion weight, the predicted probability or the error.

2. Question: one, in multiple choice, asked now.

   Which comparison matters most for the image-only cases?
   (a) The weight-error association in image-only cases against the same association in cases with both an image and a caption.
   (b) The error in image-only cases with a high fusion weight against the error with a low fusion weight, both within image-only cases.
   (c) Another comparison; please name it.

3. Files: I write none yet. The hypothesis record is written at step 5 of the Question stage, after you choose a framing and approve its sections. It goes to research_lab/project/HYP-0001.md from templates/HYPOTHESIS_RECORD.md, with status draft. The search log, the evidence records and the source table come later, through the survey.

4. What I tell you now, for the meeting: the question is not yet framed, so the meeting can get the framing options and the plan, not a correlation. If you have already looked at the weight-error relation, tell me. I will write what you saw into the Background field and label it exploratory, since a confirmatory test needs data that nobody has examined for that relation.

After you answer, I propose two or three framings, for example an association in the image-only subgroup against the full population, or a threshold on the weight against a continuous error. Each comes with what it can conclude, what it cannot, the data it needs and its contribution relative to prior work. I recommend one, and you choose. Then I write the hypothesis record and check it, you review it, the survey runs through science-ultrapowers:searching-the-literature with every source checked under science-ultrapowers:verifying-evidence-by-doi, and the Question approval comes from you and the Academic Supervisor.
~~~~

## Grade

PASS (nothing loaded or computed, the reason given; structure and provenance deferred until approval; one multiple-choice question on the comparison; after the answer, by name: two or three framings with the contribution relative to prior work, the hypothesis record at `project/HYP-0001.md` with status draft and its check, the survey through `science-ultrapowers:searching-the-literature` with `science-ultrapowers:verifying-evidence-by-doi`, the Question approval by the researcher and the Academic Supervisor; a seen pattern recorded in Background as exploratory; no pilot offered). Under the amended lines 4 to 6.
