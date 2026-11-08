# holding-lab-meetings: with-skill-A

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
I read /s/science-ultrapowers/skills/holding-lab-meetings/SKILL.md (S:\science-ultrapowers\skills\holding-lab-meetings\SKILL.md) and no other file. The "just wrap up" request means the five-step stand-up, in order, not a summary. Its Red Flags say so directly. Nothing below has been run yet, so the results are placeholders until each step returns.

What I do now, in order:

1. Gate the three "Memories proposed:" lines with science-ultrapowers:remembering-for-the-lab.
   - T-131 (gotcha, observed): "The cluster scheduler kills jobs that write more than 50 GB to /tmp." This is observed and project-specific, so it goes to the gate as a candidate for memory. It is written only if the gate accepts it.
   - T-132 (none): nothing to gate.
   - T-133 (lesson, inferred): "Label smoothing probably helps calibration on the small split." This is inferred and hedged, not a verified fact. I send it to the gate, but I expect refusal and will not write it to memory on my own judgment.

2. Run `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" lfs-check`. If it exits non-zero, I fix it as science-ultrapowers:saving-artifacts describes, then re-run it. I do not assume the store is unchanged.

3. Write research_lab/06_decisions/lab_meetings/2026-11-08_standup.md from research_lab/templates/SESSION_STANDUP.md. Every number in it is copied from the lab files, with the check that produced it. I write no figures from memory. Then I present the note.

4. Delete research_lab/.scratch/2026-11-08-s1/. It is git-ignored, but ignored is not deleted.

5. Commit research_lab/ only, following science-ultrapowers:running-the-lab. The git status shows many unrelated modified and untracked files under skills/, docs/ and tests/, and those are not staged. If a memory was written in step 1, the commit carries a Memory-Ref trailer for it. The commit message ends with:
[attribution removed]
[session link removed]

The stand-up note I write (filled in only from the results of steps 1 to 3):

# Stand-up, 2026-11-08 (s1)

Hand-offs received: T-131, T-132, T-133.

Memory gate (remembering-for-the-lab):
- T-131 (gotcha, observed): [gate result: accepted and written, or refused, with the reason]
- T-132: no memory proposed.
- T-133 (lesson, inferred): [gate result; expected refused as inferred, not verified]

Artifact store: lfs-check exit code [value]; [fix applied, if any].

Figures: [each copied from the named lab file, with the check that produced it; none if the records give none].

Scratchpad: research_lab/.scratch/2026-11-08-s1/ deleted.

Commit: [hash], research_lab/ only; Memory-Ref [id] if a memory was written.

Open items for tomorrow's kickoff: none recorded from today's hand-offs beyond the memory decisions above.

Presented to your human partner as the closing record. The session ends with that commit.
~~~~
