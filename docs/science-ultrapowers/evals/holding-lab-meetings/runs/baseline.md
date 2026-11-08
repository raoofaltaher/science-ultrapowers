# holding-lab-meetings: baseline

Configuration: baseline (no skill). Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

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
Wrap-up plan for session 2026-11-08-s1 (text only, no tools run; nothing written, moved or committed).

Steps, in order:
1. Triage memory proposals against the verified/durable/non-derivable rule.
   - T-131 (gotcha, observed): accept. Write one entry in research_lab/memory/ in the project entry format: the cluster scheduler kills jobs that write more than 50 GB to /tmp, source T-131. Add its line to research_lab/memory/MEMORY.md.
   - T-132 (none): nothing to write.
   - T-133 (lesson, inferred): do NOT store as a lesson (unverified). Record as an open hypothesis on research_lab/00_project_knowledge/TASK_BOARD.md: label smoothing may improve calibration on the small split; test before any memory entry.
2. Update TASK_BOARD.md: set T-131, T-132, T-133 to the statuses their hand-offs reported (hand-off bodies not seen; statuses taken from the results only); add the T-133 hypothesis line.
3. Write the session wrap-up note from research_lab/templates/SESSION_STANDUP.md, filed under research_lab/06_decisions/lab_meetings/ dated 2026-11-08.
4. research_lab/.scratch/2026-11-08-s1/ is git-ignored and not a record. Register any durable output there via python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" and reference it from the task record; otherwise leave it.
5. No commit or push (not requested). List changed files for review.
6. Short closing message to the partner; no questions.

Note to file:
"Session 2026-11-08-s1 wrap-up. Three hand-offs returned.
- T-131 (gotcha, observed): cluster scheduler kills jobs writing more than 50 GB to /tmp. Stored in lab memory.
- T-132: no memory proposed.
- T-133 (lesson, inferred): label smoothing probably helps calibration on the small split. Not stored as a lesson (unverified). Kept as an open hypothesis on the task board, to test on the small split with a calibration metric before any memory entry.
Nothing committed. Changed files listed for review."

Caveat: paths and entry/index formats are taken from the lab conventions as given and were not checked against the files.
~~~~
