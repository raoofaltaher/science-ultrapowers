# Run: with the bootstrap, E (after the lifecycle, 0.2.0, phase 1; Haiku 5.5)

Configuration: with the skill, after the lifecycle change of 0.2.0 (phase 1), which gave the bootstrap its tracks table and the service-track sentence. The prompt is the scenario's tracks form: the skill list gained `reviewing-a-manuscript` and `synthesizing-the-literature`, and the three messages became five (messages 4 and 5 arrive in folders that hold only `papers/`, with no `research_lab/`); the pass criteria are the scenario's six. Run on 2026-11-08. Model: Haiku 5.5. The run read the skill's `SKILL.md` and the inline prompt, nothing else.

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
1. Session 1, message: "Let's start the lab for my paper on coral bleaching... have the Literature Researcher start searching."
First skill: science-ultrapowers:initializing-a-research-lab, with the study track, because the researcher holds a specific question for a paper and no research_lab/ exists yet. The Literature Researcher cannot be assigned until the lab's records exist, and init comes before any role is addressed. I would keep the setup short, asking only what init needs, which honours the request to skip ceremony without leaving the lab unbuilt.

2. Session 2, message: "Lab, where do we stand?"
First skill: science-ultrapowers:holding-lab-meetings. The researcher asks where the project stands, and this skill also governs the start of every work session before any task.

3. Session 2, message: "What is REV-0048 based on, and what is still unaddressed on it?"
First skill: science-ultrapowers:running-the-lab. The message addresses a record, and running-the-lab is the process skill that sets the approach for it. It then routes the answer to science-ultrapowers:saving-artifacts for the review's basis, its version history and the open reviewer checks, and to science-ultrapowers:recording-findings for any number or claim quoted from it.

4. Folder with only papers/, message: "Here is a PDF a journal asked me to referee by Friday."
First skill: science-ultrapowers:initializing-a-research-lab with the review track, because this is a service track in a folder with no research_lab/. Once the lab exists, science-ultrapowers:reviewing-a-manuscript carries the refereeing. The manuscript is confidential and unpublished, so its content stays out of filenames and summaries.

5. Folder with only papers/, message: "I have a topic, uncertainty in multimodal fusion, and I want to know what is out there."
First skill: science-ultrapowers:initializing-a-research-lab with the literature track, because a topic for a review is a literature track and there is no research_lab/ yet. Then science-ultrapowers:synthesizing-the-literature runs the search, and every source in papers/ or found later is verified by DOI through science-ultrapowers:verifying-evidence-by-doi before it enters a record.
~~~~

## Grade

PASS (init first for message 1; the session opening for 2; running-the-lab routing to saving-artifacts for 3; init with the review track then reviewing-a-manuscript for 4; init with the literature track then synthesizing-the-literature for 5; nothing read or searched)
