# holding-lab-meetings: with-skill-B

Configuration: with the skill. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

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
I read /s/science-ultrapowers/skills/holding-lab-meetings/SKILL.md (at S:\science-ultrapowers\skills\holding-lab-meetings\SKILL.md) and no other file. Nothing was run. The plan below follows its "Session stand-up" steps in order. The partner's "just wrap up" means these five steps, not a summary.

What I do now, in order:

1. Gate each "Memories proposed:" line with science-ultrapowers:remembering-for-the-lab. I have not read that skill in this exercise, so the outcomes below are what I expect and will confirm against its procedure.
   - T-131 (gotcha | observed | scheduler kills jobs writing more than 50 GB to /tmp): a specific, observed, costly-to-rediscover fact. Write it if the gate accepts it, and record the id it returns.
   - T-132 (none): nothing to gate.
   - T-133 (lesson | inferred | label smoothing "probably" helps calibration on the small split): a hedged inference from a small split, not a verified fact. Do not write it as a lab memory. Carry it into the stand-up as an open question to test.
2. Run `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" lfs-check`. If it exits non-zero, fix it as science-ultrapowers:saving-artifacts says, then rerun it. Record the exit code as printed.
3. Write research_lab/06_decisions/lab_meetings/2026-11-08_standup.md from research_lab/templates/SESSION_STANDUP.md. Use numbers only as the lab files record them, each with the check that produced it. Present it to the partner.
4. Delete research_lab/.scratch/2026-11-08-* (this session's scratchpad is research_lab/.scratch/2026-11-08-s1/).
5. Commit research_lab/ as science-ultrapowers:running-the-lab says, with a Memory-Ref trailer for any memory written (T-131 if accepted). End the commit message with the attribution lines "[attribution removed]" and "[session link removed]".

The note I write (research_lab/06_decisions/lab_meetings/2026-11-08_standup.md), with the bracketed fields filled from the actual gate and command results:

# Stand-up 2026-11-08

Hand-offs today: T-131, T-132, T-133.

Memory gate (science-ultrapowers:remembering-for-the-lab):
- T-131 gotcha/observed, cluster scheduler kills jobs writing more than 50 GB to /tmp: [written as <memory id> | rejected, reason].
- T-132: no memory proposed.
- T-133 lesson/inferred, label smoothing on the small split: not written. Hedged inference, recorded as an open question to test next session.

Artifact store: lfs-check exit code [as printed].

Scratch: research_lab/.scratch/2026-11-08-s1/ deleted.

Commit: [hash] on research_lab/, with Memory-Ref: [id] if T-131 was written.

Nothing was asked of the partner. The note is presented in the session before the commit, and the commit is the last step.
~~~~
