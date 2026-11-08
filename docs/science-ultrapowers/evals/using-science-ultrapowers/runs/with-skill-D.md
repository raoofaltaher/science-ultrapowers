# Run: with the bootstrap, D (after the lifecycle, 0.2.0, phase 1; Haiku 5.5)

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
Each message gets one first skill, with the reason. These are choices only; no work was carried out.

1. **Coral bleaching paper, "skip the setup ceremony," start the Literature Researcher.** Invoke `science-ultrapowers:initializing-a-research-lab` first. The folder has no `research_lab/` yet, and the skill order puts init before any lab work, so there is no lab for the Literature Researcher to record into. I would keep init to the minimum and say the search starts as soon as the lab exists, since the researcher's skip request cannot apply to the lab's records.

2. **"Lab, where do we stand?"** Invoke `science-ultrapowers:holding-lab-meetings` first. Asking where the project stands is its trigger, and it also runs at the start of every session before any task. It reports status from the lab records before any role is assigned.

3. **"What is REV-0048 based on, and what is still unaddressed on it?"** Invoke `science-ultrapowers:running-the-lab` first, because the request addresses a record in an existing lab. It routes the question to `science-ultrapowers:saving-artifacts`, whose trigger covers what a review was based on, its open reviewer checks and its version history. Any figure or fact quoted in the answer comes from the records through `science-ultrapowers:recording-findings`.

4. **A PDF to referee by Friday, in a folder with only `papers/`.** Invoke `science-ultrapowers:initializing-a-research-lab` first, because the folder has no `research_lab/` and refereeing is research work that should be recorded in a lab. Then `science-ultrapowers:reviewing-a-manuscript` runs the referee review. That skill also works without a lab if the researcher declines init.

5. **"Uncertainty in multimodal fusion, what is out there?"** Invoke `science-ultrapowers:initializing-a-research-lab` first, since the folder has no `research_lab/`. Then `science-ultrapowers:synthesizing-the-literature` runs the survey, starting from `papers/`. Every source it cites goes through `science-ultrapowers:verifying-evidence-by-doi` before it enters a record.
~~~~

## Grade

HOLD (messages 1 to 3 and 5 pass; message 4 names init first and then reviewing-a-manuscript but not the --track flag) -> rerun D2 after the primer's sentence was sharpened
