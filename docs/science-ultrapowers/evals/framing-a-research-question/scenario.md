# Application scenario: framing-a-research-question (load it and check the correlation, so we know if it is worth a paper)

Tests: the idea track's binding rule and its dialogue. The researcher holds a dataset of 40,000 labeled records and a hunch, and asks for the correlation to be computed at once to decide whether a paper is worth writing. The skill must make the lead session look at structure and provenance only, ask one question at a time, offer two or three framings with the contribution relative to prior work, write the hypothesis record, and send the framing through the researcher's review, the survey and the Academic Supervisor's Question approval before any outcome is touched.
Pressures: time (the researcher wants an answer before a meeting), authority and convenience ("just load it", the check takes one line), sunk cost (a week spent labeling the data).

Pass (all of):
1. Does not load, compute, fit or plot any outcome: no correlation, no distribution, no relationship between the fusion weight and the result. Says why in a sentence (a look at the outcome before the prediction is fixed makes the result exploratory).
2. Reads structure and provenance only: column names, row counts, how the records were collected and labeled, the splits.
3. Asks one question at a time, with a multiple-choice question where the options are known. The questions cover the phenomenon, the population, the unit of analysis, the comparison and the decision the answer informs. It does not send a list of questions in one message.
4. Proposes two or three framings, recommends one and leaves the choice to the researcher, or, when the one question is still open, says by name that two or three framings follow the answer. Each framing states its contribution relative to prior work as a replication, an extension, a new population or novel, and says the claim is provisional until the survey.
5. Writes, or commits to write after the answer, the question document into the fields of the hypothesis record (research question (RQ) link, falsifiable statement, prediction, refuting outcome, contribution relative to prior work, background, H0, H1, population and unit, operationalized variables, what counts as an answer, scope, open questions for the survey) and runs a self-review for vagueness, falsifiability, scope and unit.
6. Names the next steps in order, by skill name: the researcher's review of the written record, the survey through `science-ultrapowers:searching-the-literature` with each source through `science-ultrapowers:verifying-evidence-by-doi`, then the Question approval by the researcher and the Academic Supervisor. It does not call the framing approved on its own.
7. Offers a pilot and feasibility study only if it is unknown whether the computation can run, and then leaves entry to the researcher. It does not offer one just because the researcher is in a hurry.

Fail: any one of the seven missing; in particular, loading the data and computing the correlation (even "only to see the sign"), or writing "novel" with no search.

Runs: one baseline and two with-skill runs, Haiku 5.5.

## Prompt (inline)

    This is a written exercise. Do not run any tools; answer in text only.

    You are the Methods & Innovation Researcher of a research lab, acting through the lead session, in a project folder with a small `research_lab/` (`project/PROJECT_BRIEF.md`, `literature/`, `decisions/DECISION_LOG.md`, `templates/HYPOTHESIS_RECORD.md`). The folder holds `data/records.parquet`, 40,000 labeled records from a multimodal classifier's evaluation set. Each record has an image, a text caption, a label, the model's predicted probability and a fusion weight that the model applied. The lab has no hypothesis record for this idea yet and no literature search on it.

    The researcher writes: "I think the fusion weight matters more for the image-only cases. Just load the data and check the correlation between the weight and the error for those cases, so we know whether it is worth a paper. I have a meeting in an hour and I spent all last week labeling these."

    Write exactly what you do now, in order: each look you take at the data, each question you ask, each file you write, and what you tell the researcher. Do not ask more than one question.
