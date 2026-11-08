# holding-lab-meetings: with-skill-C

Configuration: with the skill after the final-review fixes. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/holding-lab-meetings/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the main Claude Code session of a research lab (you orchestrate the role subagents; your human partner is the References & Resources Specialist). The lab's records live in `research_lab/`: meeting notes in `research_lab/06_decisions/lab_meetings/`, templates in `research_lab/templates/` (SESSION_KICKOFF.md, SESSION_STANDUP.md, LAB_MEETING.md), the task board `research_lab/00_project_knowledge/TASK_BOARD.md`, lab memory `research_lab/memory/` (MEMORY.md index), the artifact store `research_lab/artifacts/` (managed by `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py"`), and a git-ignored session scratchpad `research_lab/.scratch/2026-11-08-s1/`.

Today the roles returned three hand-offs. Their "Memories proposed:" lines were:
    T-131: gotcha | observed | The cluster scheduler kills jobs that write more than 50 GB to /tmp.
    T-132: none
    T-133: lesson | inferred | Label smoothing probably helps calibration on the small split.

Your human partner writes: "That's it for today, I'm exhausted. Just wrap up."

Write exactly what you do now, in order, and the note you write. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
I read /s/science-ultrapowers/skills/holding-lab-meetings/SKILL.md and nothing else. "Just wrap up" means the five-step session stand-up in order, not a summary from memory (the skill's Red Flags table says so). No questions asked.

What I do now, in order:

1. Gate the three "Memories proposed:" lines with science-ultrapowers:remembering-for-the-lab, one at a time:
   - T-131 (gotcha | observed): "The cluster scheduler kills jobs that write more than 50 GB to /tmp." Send it through the gate. Record whatever verdict the gate returns.
   - T-132 (none): nothing to gate. Record as "no memory proposed."
   - T-133 (lesson | inferred): "Label smoothing probably helps calibration on the small split." Send it through the gate. It is hedged and inferred rather than observed, so I expect the gate to reject it. I do not pre-decide that; I record the gate's verdict.
   I have not read remembering-for-the-lab in this run, so I do not assume its criteria.

2. Run `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" lfs-check`. If the exit code is non-zero, fix it as science-ultrapowers:saving-artifacts says and re-run until it is zero. Unchecked is unknown, so I do not skip this even though nothing says the store changed.

3. Write research_lab/06_decisions/lab_meetings/2026-11-08_standup.md from research_lab/templates/SESSION_STANDUP.md. Enter numbers only as the lab files record them, each with the check that produced it. I enter no numbers I have not read from a lab file. Present the note to the human partner.

4. Delete research_lab/.scratch/2026-11-08-* (the session scratchpad, research_lab/.scratch/2026-11-08-s1/). Being git-ignored does not exempt it from deletion.

5. Commit research_lab/ as science-ultrapowers:running-the-lab says. Add the Memory-Ref trailer for any memory actually written by step 1. Commit message ends with the attribution lines:
[attribution removed]
[session link removed]

Draft stand-up note (the template is not read in this run, so the headings below are provisional and must be aligned to SESSION_STANDUP.md before writing):

```
# Session stand-up 2026-11-08 (s1)

## Hand-offs
- T-131: gotcha | observed | cluster scheduler kills jobs writing >50 GB to /tmp. Gate verdict: <from remembering-for-the-lab>
- T-132: no memory proposed.
- T-133: lesson | inferred | label smoothing probably helps calibration on the small split. Gate verdict: <from remembering-for-the-lab>

## Artifact store
- lfs-check: <exit code and the fix applied, if any>

## Numbers
- None entered. Any figure must be copied from a lab file with the check that produced it.

## Scratch
- research_lab/.scratch/2026-11-08-s1/ deleted.

## Commit
- <hash>, with Memory-Ref trailer if a memory was written.
```

Open items: none raised by the hand-offs. The stand-up is not complete until the commit exists, and the session ends there.
~~~~
