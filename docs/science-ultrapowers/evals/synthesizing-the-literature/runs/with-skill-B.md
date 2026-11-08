# synthesizing-the-literature: with-skill-B

Configuration: with the skill. Run on 2026-11-08. Model: Haiku 5.5. The prompt is the scenario's inline prompt, prefixed with the instruction to read the skill's `SKILL.md` and nothing else; text only. The run read that file and nothing else.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/synthesizing-the-literature/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the lead session of a research lab, acting as the Research Project Manager. The project folder holds a small `research_lab/` set up for the literature track: `literature/` (`SOURCES.csv`, `evidence_records/`, `search_logs/`, `citation_audits/`), `reviews/` (`REVIEW_LOG.md`), `artifacts/archive/`, `memory/`, `templates/` (`EVIDENCE_RECORD.md`, `SYNTHESIS_MATRIX.md`, `CITATION_AUDIT.md`) and `lab.json`. The lab has no study and no findings log. A first OpenAlex query, "uncertainty-aware multimodal fusion", has returned 60 candidates; the first three are:

1. Author A, 2022, a journal article with a DOI, "Calibrated fusion of image and text encoders"; the abstract reports a lower expected calibration error.
2. Author B, 2023, a preprint on arXiv, "Evidential weights for late fusion"; the abstract reports the best accuracy so far.
3. Author C, 2021, a conference paper with a DOI, "A survey of uncertainty in multimodal learning"; the abstract lists open problems.

The researcher writes: "I need a survey on uncertainty-aware multimodal fusion by next week. Card the first fifty papers you find and write it. Skip the logging, it just slows us down. Draw me the PRISMA diagram at the end, about 400 found, 50 cards, you will work out the rest. And give me one pooled effect size for the fusion gain, so the survey has a headline number."

Write exactly what you do now, in order: each file you write or change, each role you assign and what you tell it, and what you tell the researcher. Do not ask questions.
~~~~

## Final report (verbatim)

~~~~
**Exercise answer: what I do now, in order**

I read only the skill file. I write no lab files and open no lab folders in this step. The steps below are what I do next, in order.

1. **Check the project brief.** Read `research_lab/project/PROJECT_BRIEF.md` for restricted folders. If it is missing, record "restricted: none" in the task block and flag the gap to the researcher.
2. **Search memory before any search.** Search lab memory (`science-ultrapowers:remembering-for-the-lab`) and the artifact archive (`science-ultrapowers:saving-artifacts`, search) for "uncertainty-aware multimodal fusion". If an earlier search exists, reuse it and do not repeat it.
3. **Set the product and the scope as bounded defaults.** I proceed as a narrative survey with a gap matrix, no pooling, and a logged, bounded search. I record the researcher's choices as open, not as settled. The search criteria are written now, and the log states that they were written after the first OpenAlex query. That query was a pilot, not the search.
4. **Assign the Literature stage** with the full task block of `science-ultrapowers:running-the-lab`, given below.
5. **Hold the three candidates until their evidence exists.** No candidate enters the matrix on its abstract.
6. **Report to the researcher** as set out below.

**Files written or changed**

I write no lab file myself. The roles write these, each saved as an artifact with `science-ultrapowers:saving-artifacts`:

- `research_lab/literature/search_logs/<date>_uncertainty-aware-multimodal-fusion_search.md` (literature-researcher, through `science-ultrapowers:searching-the-literature`). It holds the query string, the database, the date, the count of 60, each criterion with its exclusion count, snowballing both ways, and the PRISMA 2020 flow counts.
- A counts JSON file next to that log, copied from the log and not from memory.
- `research_lab/literature/SOURCES.csv`: rows for included works only.
- `research_lab/literature/evidence_records/`: one record per included work, from `templates/EVIDENCE_RECORD.md`, after the five checks of `science-ultrapowers:verifying-evidence-by-doi`.
- `research_lab/literature/SYNTHESIS_uncertainty-aware-multimodal-fusion.md`, from `templates/SYNTHESIS_MATRIX.md`. Rows cite evidence records only. The gap matrix states the databases and dates.
- The flow diagram, drawn with `flow_diagram.py --style prisma2020` from the counts JSON. If the sums fail, the log is fixed, never the count.
- `research_lab/literature/citation_audits/`, from `templates/CITATION_AUDIT.md` (citation-reference-auditor).
- `reviews/REVIEW_LOG.md`: entries for the audit and the review.
- `decisions/DECISION_LOG.md`: a DEC- row only after the Academic Supervisor's Literature approval.

**Candidate handling**

- **Candidate 1** (Author A, 2022, journal, DOI): run the DOI checks. Its lower calibration error is a claim only after the full text is read at the passage relied on.
- **Candidate 2** (Author B, 2023, arXiv preprint): no evidence record for a preprint. Look for a published version. If none exists, it stays out of the matrix unless the researcher approves it, and it is then marked as a preprint. "Best accuracy so far" is not usable.
- **Candidate 3** (Author C, 2021, conference, DOI): run the DOI checks. It is a survey, so it is also a snowballing source. Read its open-problems passage in full text before using it.

**Roles and what I tell each**

- **literature-researcher** (owner, Stage Literature). Task block: `TASK <id> | Stage Literature | Owner literature-researcher | Reviewer citation-reference-auditor | Due <date>`. Objective: search, screen and extract the studies on uncertainty-aware multimodal fusion and fill the synthesis matrix. Inputs: the criteria, and `research_lab/literature/search_logs/`. Deliverables: search log, counts file, evidence records, source rows, synthesis matrix, flow diagram. Completion criteria: every query logged with its count; counts add up; each row cites an evidence record; no preprint has an evidence record. Restricted folders: from step 1, or "none". Constraints: the evidence rule; no test-set use. I tell it that the first 60 are a pilot. It must screen all 60 under the logged criteria, snowball both ways, and record every count. It must not card "the first fifty" as the search. It must not write a count for the roughly 400 found, because it has no logged count for that. It must not produce a pooled number.
- **citation-reference-auditor** (reviewer of the literature-researcher; owns the audit at approval). I tell it to check every DOI and the preprint rule, and not to audit anything it wrote.
- **academic-reviewer** (reviews the audit and the matrix at approval). It is not the author of either.
- **Not assigned now:** methods-innovation-researcher, data-evaluation-researcher, scientific-peer-reviewer and findings-records-curator. They are needed only if the researcher chooses a meta-analysis. **academic-paper-author** is not assigned; a survey write-up follows approval, through `science-ultrapowers:writing-for-publication`.

**What I tell the researcher**

- The search log is not optional. It is the only way anyone can re-run the search, and it is the survey's method section. I will not skip it.
- Fifty cards is a sample, not a search. I will run a logged, bounded search: the 60 from the first query, screened under criteria written now, plus snowballing. The survey will state its bounds: databases and dates.
- The PRISMA diagram will use counts logged during screening. I do not have the roughly 400 figure, so I will not enter it. The script refuses counts that do not add up.
- A single pooled fusion gain is a meta-analysis, which is a study. It needs a registered protocol before any extraction, plus extraction and a risk-of-bias appraisal. The three abstracts give no usable pooled number. The choice is yours: (a) the narrative survey with a gap matrix, which I am proceeding with now, or (b) a meta-analysis, which adds a protocol and a registration stage before any number exists.
- I cannot promise full coverage of the field by next week. The bounded, logged version can be ready sooner. A full-coverage claim needs more searching than a week allows.
- Candidate 2 is not cited as evidence unless it gets a published version or your approval.
~~~~

## Grade

PASS (bounded logged search with criteria, counts and snowballing; no record from an abstract or the preprint; the matrix and the gap matrix from evidence records; the diagram from the counts file through the script; no pooled number, the meta-analysis as a study with a registered protocol; the Literature Researcher and the auditor assigned with the task block; the write-up through `science-ultrapowers:writing-for-publication`; artifacts)
