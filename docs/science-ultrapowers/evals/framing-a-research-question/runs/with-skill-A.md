# framing-a-research-question: with-skill-A

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
What I do now, in order.

1. I search lab memory for earlier work on fusion weights, image-only cases and this classifier. I list the titles in research_lab/literature/ and read no full texts yet. No file is written.

2. I read research_lab/project/PROJECT_BRIEF.md and research_lab/decisions/DECISION_LOG.md to learn the project's question, its restricted folders and any earlier decisions about this data.

3. I open data/records.parquet for structure and provenance only: the column names, the data types, the row count and the file's key-value metadata (collection method, label source, model version, any split information). I do not read row values. I also do not read row-group statistics (min, max, null counts) for the weight, error or probability columns, because those are outcome distributions. I write nothing to research_lab/ during this step.

4. I ask the researcher one question, as a multiple-choice question:
"Which comparison should the study test? (a) the weight-error relation in image-only cases against the same relation in cases that have both an image and a caption; (b) the weight-error relation in image-only cases alone, with no comparison; (c) another comparison, please name it."

I wait for the answer before asking anything else.

5. I tell the researcher the following. I will not load the outcome columns or compute the correlation now. The correlation is the outcome, and a look before the question and the prediction are fixed cannot test them, so a result from it could not support a confirmatory paper. A correlation today also cannot tell us whether the effect is worth a paper, because we have not yet fixed the smallest effect that would matter. The labeling is not lost: the labels are the data the framing will use, and the framing decides what they must support. If you have already looked at weight-error patterns, tell me, and I will write that look into the Background field of the hypothesis record as exploratory.

6. For the meeting in an hour, I can give you the structure of the file, two or three candidate framings (each with what it can conclude, what it cannot, the data it needs and its contribution relative to prior work), and a draft hypothesis record. The go or no-go on the paper follows the framing approval and the prior-work survey, not a correlation today.

7. After you choose a framing and review the sections, I write research_lab/project/HYP-0001.md from the template as a draft. The survey then goes to the Literature Researcher, and the record is reviewed by the Academic Reviewer. No outcome is touched before the Question approval.
~~~~

## Grade

HOLD (no outcome loaded or computed, structure only, one multiple-choice question; the framings, the record and the survey deferred without naming the skills). The skill gets a sentence that names what follows the one question; run A2 is the rerun.
