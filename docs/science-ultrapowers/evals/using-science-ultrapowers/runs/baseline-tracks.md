# Run: baseline, tracks scenario (Haiku 5.5)

Configuration: baseline, the tracks scenario after the lifecycle change of 0.2.0 (phase 1): the prompt with the skill descriptions and without the bootstrap. The prompt is the scenario's tracks form: the skill list gained `reviewing-a-manuscript` and `synthesizing-the-literature`, and the three messages became five (messages 4 and 5 arrive in folders that hold only `papers/`, with no `research_lab/`); the pass criteria are the scenario's six. Run on 2026-11-08. Model: Haiku 5.5. The prompt was given inline; the run read no file.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are a Claude Code session with the science-ultrapowers plugin installed. The project folder `C:/work/reef-paper/` holds `src/`, `data/` and a `README.md`; there is no `research_lab/` folder. These skills are available (name: when to use):
- running-the-lab: Use whenever the researcher addresses the lab, a role, a stage, a record or a research task, before assigning, reviewing, reporting or recording anything
- holding-lab-meetings: Use at the start of every work session before any task, at the end of every session, at a milestone, at a stage approval review, or when the researcher asks where the project stands
- initializing-a-research-lab: Use when the researcher wants a research lab started, joined or upgraded in this project, or asks for research work in a folder that has no research_lab/
- migrating-from-claude-science: Use when a Claude Science data directory exists on this machine and a project in it should continue in this lab, when the researcher says to import, migrate or pick up from Claude Science, or after init detected a data directory
- saving-artifacts: Use when a task produces or changes a file the lab must keep, before a task report, when a deliverable needs a version, or when asked what a deliverable or review was based on, which reviewer checks are still open, or its version history
- recording-findings: Use when a number, result or claim is about to enter a record, a task assignment or a manuscript, or when looking up any project fact
- verifying-evidence-by-doi: Use before any citation, quote or literature claim enters a lab record or manuscript
- reviewing-a-manuscript: Use when the researcher has a manuscript to referee, their own draft to check or review, references, citations or facts to audit, or reviewer comments to answer, with or without a lab
- synthesizing-the-literature: Use when the researcher wants a literature review, a survey, a synthesis or gap matrix, a meta-analysis or a PRISMA or CONSORT diagram on a topic, keyword or set of papers, with or without a study

Five messages arrive from the researcher, one per session. Messages 1 to 3 arrive in `C:/work/reef-paper/`; by session 2 the lab exists (session 1 created `research_lab/`). Messages 4 and 5 arrive in other folders that hold only a `papers/` folder, with no `research_lab/`. For each, write which skill you invoke first and why, in two or three sentences; do not carry out the work.

1. "Let's start the lab for my paper on coral bleaching. I know exactly what I want, so skip the setup ceremony and have the Literature Researcher start searching."
2. "Lab, where do we stand?"
3. "What is REV-0048 based on, and what is still unaddressed on it?"
4. "Here is a PDF a journal asked me to referee by Friday."
5. "I have a topic, uncertainty in multimodal fusion, and I want to know what is out there."
~~~~

## Final report (verbatim)

~~~~
1. Message 1 (coral bleaching lab, C:/work/reef-paper/): first invoke initializing-a-research-lab. The folder has no research_lab/ and the researcher asks to start the lab, so the lab must exist before the Literature Researcher can be assigned. The request to skip the setup ceremony can shorten the questions, but it does not skip the initialization.

2. Message 2 ("Lab, where do we stand?", session 2): first invoke holding-lab-meetings. Asking where the project stands is its named trigger, and it is the start of a work session. running-the-lab also applies because the researcher addresses the lab, but the status meeting comes first and routes the answer.

3. Message 3 (REV-0048): first invoke saving-artifacts. Its description names the questions asked here: what a review was based on, which reviewer checks are still open, and version history. If the answer cites a project fact, recording-findings applies afterwards.

4. Message 4 (refereeing a PDF, folder with only papers/): first invoke reviewing-a-manuscript. The researcher has a manuscript to referee, and that skill applies with or without a lab. Initializing a lab in the folder is needed only if the researcher wants the referee report kept as a lab record, so I would offer that rather than assume it.

5. Message 5 (uncertainty in multimodal fusion, folder with only papers/): first invoke synthesizing-the-literature. The researcher asks what is out there on a topic with no study yet, which is that skill's stated trigger. No lab is requested, and verifying-evidence-by-doi applies before any citation enters a record.
~~~~

## Grade

FAIL on messages 4 and 5, largely complies on 1 to 3 (init, meetings, saving-artifacts; message 4 names reviewing-a-manuscript and offers init but not --track review; message 5 names synthesizing-the-literature and no init)
