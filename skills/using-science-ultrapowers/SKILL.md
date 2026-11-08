---
name: using-science-ultrapowers
description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
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

- `science-ultrapowers:running-the-lab` once a lab exists, whenever your human partner addresses the lab, a role, a gate, a record or a research task.
- `science-ultrapowers:holding-lab-meetings` when the session starts, ends, or your human partner asks where the project stands.
- `science-ultrapowers:verifying-evidence-by-doi` whenever a source is cited or a literature claim is written.
- `science-ultrapowers:initializing-a-research-lab` when your human partner asks for lab or research work and the project has no `research_lab/` (init first, then the rest).
- `science-ultrapowers:migrating-from-claude-science` when your human partner asks to continue a Claude Science project here, or init found a data directory.

"Fix this bug" → `science-ultrapowers:systematic-debugging` first, then domain skills.

## The lab in one breath

- Facts come only from peer-reviewed, DOI-verified sources, read in full text and recorded on an evidence card.
- Numbers and findings are quoted from the lab records, never retyped.
- Nobody reviews or audits their own work.
- When the project has a `research_lab/` folder, that folder is the lab: its records, artifact store and memory are the source of truth.
- Address the team, one role or a gate in plain words; the main session acts as the Research Project Manager, briefs the role agents and relays their requests to your human partner.

## Red Flags

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

## User Instructions

User instructions (CLAUDE.md, direct requests) take precedence over skills, which in turn override default behavior. Only skip skill workflows or instructions when your human partner has explicitly told you to.
