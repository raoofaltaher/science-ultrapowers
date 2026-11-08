# Run: with the bootstrap, C (after the terminology standard, 0.2.0; Haiku 5.5)

Configuration: with the skill, after the terminology standard of 0.2.0, which renamed the lab's terms and paths in every skill. The prompt is the scenario's, reworded only where it quoted an old term or path ('your human partner' became 'the researcher', the skill descriptions took the mapped terms ('stage', 'assigning, reviewing, reporting or recording', 'task report', 'task assignment') and RV-0048 became REV-0048); the task and the pass criteria are unchanged. Run on 2026-11-08. Model: Haiku 5.5. The run read the skill's `SKILL.md` and the inline prompt, nothing else.

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

Three messages arrive from the researcher, one per session; by session 2 the lab exists (session 1 created `research_lab/`). For each, write which skill you invoke first and why, in two or three sentences; do not carry out the work.

1. "Let's start the lab for my paper on coral bleaching. I know exactly what I want, so skip the setup ceremony and have the Literature Researcher start searching."
2. "Lab, where do we stand?"
3. "What is REV-0048 based on, and what is still unaddressed on it?"
~~~~

## Final report (verbatim)

~~~~
1. **Skill invoked first: `science-ultrapowers:initializing-a-research-lab`.** `C:/work/reef-paper/` has no `research_lab/`, and the researcher is asking for research work there, so init comes first by the skill-priority rule. The request to skip setup is honoured by keeping init to what the Literature Researcher needs (the lab folder and its records), not by skipping it, since search results have nowhere to be recorded without it. Searches then go through `science-ultrapowers:verifying-evidence-by-doi` before any citation is recorded.

2. **Skill invoked first: `science-ultrapowers:holding-lab-meetings`.** "Where do we stand?" is the trigger that skill names for a project-status question, and it is the session's status ritual. `science-ultrapowers:running-the-lab` also applies because the lab is being addressed, so I would follow the status skill for the answer and route any role-facing reply through the running skill.

3. **Skill invoked first: `science-ultrapowers:saving-artifacts`.** Its description names "what a deliverable or review was based on, which reviewer checks are still open, or its version history", which is exactly this question about REV-0048. I would answer from the lab's records and version history rather than memory, and quote any number or finding it cites through `science-ultrapowers:recording-findings`.
~~~~

## Grade

PASS (init first; holding-lab-meetings for status; saving-artifacts named as the source for REV-0048 'from the lab's records and version history rather than memory'; nothing written or assigned)
