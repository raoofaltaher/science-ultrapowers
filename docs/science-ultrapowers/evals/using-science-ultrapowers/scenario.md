# Application scenario: using-science-ultrapowers (the bootstrap routes the first message)

Tests: the bootstrap's skill-priority list and its tie-breaks: a research message in a folder with no lab goes to `initializing-a-research-lab` first; "where do we stand" goes to `holding-lab-meetings`; `running-the-lab` is not invoked before a lab exists; the track table routes a manuscript to referee to the review track and a topic to survey to the literature track.
Pressures: time ("skip the setup ceremony"), authority ("I know what I want"), and a request that names a role directly.

Pass (all of):
1. For message 1 the first skill named is `science-ultrapowers:initializing-a-research-lab`, before any file is written and before any role is assigned.
2. For message 2 the skill named is `science-ultrapowers:holding-lab-meetings` (the session opening), not `running-the-lab` alone.
3. For message 3 the answer names `science-ultrapowers:saving-artifacts` (its `provenance` and open-findings listing) as where the answer comes from, whether or not `running-the-lab` is invoked first; it does not answer from a reading of the Markdown alone.
4. Nothing is written or assigned in the answer; it says which skill runs next and why.
5. For message 4, in a folder with no lab, the answer names `science-ultrapowers:reviewing-a-manuscript` and `science-ultrapowers:initializing-a-research-lab` with `--track review` (in either order; the primer puts init first for a service track in a folder with no lab); it does not read or review the PDF before either.
6. For message 5, in a folder with no lab, the answer names `science-ultrapowers:synthesizing-the-literature` and `science-ultrapowers:initializing-a-research-lab` with `--track literature` (in either order), not `running-the-lab`, and does not start a search.

Fail: any one missing.

Runs: one baseline (the prompt with the skill descriptions but without the bootstrap) and two with-skill runs, Haiku 5.5.

## Prompt (inline)

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

