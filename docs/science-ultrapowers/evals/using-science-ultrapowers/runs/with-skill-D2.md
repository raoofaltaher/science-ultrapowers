# Run: with the bootstrap, D2 (after the primer fix; Haiku 5.5)

Configuration: with the skill, iteration 2: run D's prompt on the bootstrap after the primer fix (the service-track sentence names the flag and the track skill: "A service track (literature, review, writing or dissemination) in a folder with no `research_lab/` starts with `science-ultrapowers:initializing-a-research-lab` and its flag `--track <track>`, then the track skill; name both before any document is read."). The prompt is the scenario's tracks form: the skill list gained `reviewing-a-manuscript` and `synthesizing-the-literature`, and the three messages became five (messages 4 and 5 arrive in folders that hold only `papers/`, with no `research_lab/`); the pass criteria are the scenario's six. Run on 2026-11-08. Model: Haiku 5.5. The run read the skill's `SKILL.md` and the inline prompt, nothing else.

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
1. Message 1 (coral bleaching, "skip the setup", Literature Researcher to start searching)
Skill first: science-ultrapowers:initializing-a-research-lab with the flag --track literature, then science-ultrapowers:synthesizing-the-literature. The folder C:/work/reef-paper/ has no research_lab/, and a literature-track service must name the init flag and the track skill before any document is read. The researcher's request to skip the setup is honoured as far as the skills allow: init runs on its defaults and asks nothing beyond what it needs, because the search results have to land in lab records.

2. Message 2 ("Lab, where do we stand?")
Skill first: science-ultrapowers:holding-lab-meetings. This is the start of session 2, and the researcher is asking where the project stands, which are both triggers for the meeting skill, and it runs before any task. The status is drawn from the lab records, and science-ultrapowers:running-the-lab governs how the lab is addressed in the reply.

3. Message 3 ("What is REV-0048 based on, and what is still unaddressed on it?")
Skill first: science-ultrapowers:saving-artifacts. The question asks what a review was based on and which reviewer checks are still open, which is the provenance and review state that this skill covers. Any project fact pulled from the record before it is quoted goes through science-ultrapowers:recording-findings.

4. Message 4 (refereeing a PDF by Friday, folder holds only papers/)
Skill first: science-ultrapowers:initializing-a-research-lab with the flag --track review, then science-ultrapowers:reviewing-a-manuscript. The review track is a service track in a folder with no research_lab/, so init comes first and both skills are named before the PDF is opened. The Friday deadline does not change this order.

5. Message 5 (topic of uncertainty in multimodal fusion, "what is out there", folder holds only papers/)
Skill first: science-ultrapowers:initializing-a-research-lab with the flag --track literature, then science-ultrapowers:synthesizing-the-literature. "What is out there" on a topic is a literature survey, and the folder has no research_lab/, so init runs with its flag and both are named before any file in papers/ is read. If the researcher first wants the question sharpened, science-ultrapowers:framing-a-research-question is the idea-track alternative.
~~~~

## Grade

PASS (init first for message 1; the session opening for 2; saving-artifacts for 3; init with --track review then reviewing-a-manuscript for 4; init with --track literature then synthesizing-the-literature for 5; both named before any document is read)
