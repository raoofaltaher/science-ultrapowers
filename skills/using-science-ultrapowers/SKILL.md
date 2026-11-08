---
name: using-science-ultrapowers
description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions
---

<SUBAGENT-STOP>
If you were assigned as a role to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke relevant or requested skills BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. If it turns out wrong for the situation, you don't have to use it.

Then announce "Using [skill] to [purpose]" and follow the skill exactly. If it has a checklist, create a todo per item.

## Skill Priority

When several skills apply, process skills come first: they set the approach, and the others carry it out. In the lab:

- `science-ultrapowers:running-the-lab` once a lab exists, whenever the researcher addresses the lab, a role, a stage, a record or a research task.
- `science-ultrapowers:holding-lab-meetings` when the session starts, ends, or the researcher asks where the project stands.
- `science-ultrapowers:verifying-evidence-by-doi` whenever a source is cited or a literature claim is written.
- `science-ultrapowers:initializing-a-research-lab` when the researcher asks for lab or research work and the project has no `research_lab/` (init first, then the rest).
- `science-ultrapowers:migrating-from-claude-science` when the researcher asks to continue a Claude Science project here, or init found a data directory.

"Fix this bug" → `science-ultrapowers:systematic-debugging` first, then domain skills.

### Tracks

A track enters the lifecycle at the stage that fits what the researcher holds.

| What the researcher has in hand | Track | First skill |
|---|---|---|
| An idea, a topic, a paper that provoked them, a technique, a supervisor's remark, a dataset with a hunch, or nothing yet | idea | `science-ultrapowers:framing-a-research-question` |
| A framed question with a dataset, a call for papers, or a thesis chapter | study | `science-ultrapowers:running-the-lab`, after init |
| A topic or keyword for a review, a survey, a matrix or a meta-analysis | literature | `science-ultrapowers:synthesizing-the-literature` |
| A manuscript to referee, check or respond to | review | `science-ultrapowers:reviewing-a-manuscript` |
| A manuscript or thesis to write, a journal to pick, a submission to format | writing | `science-ultrapowers:writing-for-publication` |
| Slides, a poster, a graphical abstract, an architecture figure | dissemination | `science-ultrapowers:presenting-research` |

A service track (literature, review, writing or dissemination) in a folder with no `research_lab/` starts with `science-ultrapowers:initializing-a-research-lab` and its flag `--track <track>`, then the track skill; name both before any document is read.

## The lab in one breath

- Facts come only from peer-reviewed sources with a matched DOI, read in full text and recorded on an evidence record.
- Numbers and findings are quoted from the lab records, never retyped.
- A confirmatory claim needs a registered protocol (`science-ultrapowers:preregistering-the-protocol`); everything else is exploratory.
- Nobody reviews or audits their own work.
- When the project has a `research_lab/` folder, that folder is the lab: its records, artifact archive and memory are the source of truth.
- Address the team, one role or a stage in plain words; the lead session acts as the Research Project Manager, assigns the roles and relays their requests to the researcher.

## Warning signs

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

## Researcher Instructions

Instructions from the researcher (CLAUDE.md, direct requests) take precedence over skills, which in turn override default behavior. Only skip skill workflows or instructions when the researcher has explicitly told you to.
