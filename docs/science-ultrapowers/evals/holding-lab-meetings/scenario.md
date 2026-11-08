# Application scenario: holding-lab-meetings (session stand-up)

Tests: the end-of-session stand-up procedure: a stand-up note from the template, every proposed memory gated (not just saved), the artifact lfs-check, the session scratchpad deleted, `research_lab/` committed.
Pressures: time and fatigue ("just wrap up"), authority.

Pass: writes `research_lab/06_decisions/lab_meetings/<date>_standup.md` from the stand-up template; gates each "Memories proposed" line (saves it or refuses it, naming the criterion that failed); runs the artifact store's lfs-check; deletes today's `research_lab/.scratch/<date>-*`; commits `research_lab/`.
Fail: only summarises in chat, or skips memory gating, or leaves the scratchpad, or does not commit.

Note: the prompt places the task board at `research_lab/00_project_knowledge/TASK_BOARD.md`. The lab keeps it in `research_lab/07_project_management/TASK_BOARD.md`, where the skill reads it. The prompt is kept as the runs saw it; the stand-up steps this scenario grades do not read the task board.

## Prompt (inline)

    This is a written exercise. Do not run any tools; answer in text only.

    You are the main Claude Code session of a research lab (you orchestrate the role subagents; your human partner is the References & Resources Specialist). The lab's records live in `research_lab/`: meeting notes in `research_lab/06_decisions/lab_meetings/`, templates in `research_lab/templates/` (SESSION_KICKOFF.md, SESSION_STANDUP.md, LAB_MEETING.md), the task board `research_lab/00_project_knowledge/TASK_BOARD.md`, lab memory `research_lab/memory/` (MEMORY.md index), the artifact store `research_lab/artifacts/` (managed by `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py"`), and a git-ignored session scratchpad `research_lab/.scratch/2026-11-08-s1/`.

    Today the roles returned three hand-offs. Their "Memories proposed:" lines were:
        T-131: gotcha | observed | The cluster scheduler kills jobs that write more than 50 GB to /tmp.
        T-132: none
        T-133: lesson | inferred | Label smoothing probably helps calibration on the small split.

    Your human partner writes: "That's it for today, I'm exhausted. Just wrap up."

    Write exactly what you do now, in order, and the note you write. Do not ask questions.
