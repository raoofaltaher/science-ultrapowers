---
name: holding-lab-meetings
description: Use at the start of every work session before any task, at the end of every session, at a milestone, at a stage approval review, or when the researcher asks where the project stands
---

# Holding Lab Meetings

## Overview

The lab opens each session with a session opening, closes it with a session close, and meets at milestones. Notes live in `research_lab/decisions/lab_meetings/`, from the templates in `research_lab/templates/`.

**Core principle:** A session starts from the records and ends in the records; nothing is carried in anyone's head.

## Session opening

Before any task, including a short session:

1. Read `research_lab/project/PROJECT_BRIEF.md`, `research_lab/planning/WORK_PLAN.md`, the last note in `research_lab/decisions/lab_meetings/`, the open rows of `research_lab/requests/ACCESS_REQUESTS.md` and `research_lab/memory/MEMORY.md`; and `research_lab/migration/HANDOVER_SUMMARY.md` when it exists and no lab-meeting note is newer than the import.
2. Write `research_lab/decisions/lab_meetings/YYYY-MM-DD_opening.md` from `SESSION_OPENING.md`; a second session the same day is `YYYY-MM-DD_opening-2.md`, and likewise `_close-2.md`. Its first paragraph is a short lab status: open tasks by stage, blocked items, open requests, and the recommended next action.
3. Present it. No task starts before it is presented.

## Session close

At the end of every session, in this order; none is optional:

1. Apply the admission criteria to every `Memories proposed:` line not already checked after its task report, with `science-ultrapowers:remembering-for-the-lab`.
2. Run `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" lfs-check`, the Git Large File Storage (LFS) check. A non-zero exit is fixed as `science-ultrapowers:saving-artifacts` says.
3. Write `research_lab/decisions/lab_meetings/YYYY-MM-DD_close.md` from `SESSION_CLOSE.md`. Numbers only as recorded in the lab files, each with the check that produced it. Present it.
4. Delete `research_lab/.working/<today>-*`.
5. Commit `research_lab/` as `science-ultrapowers:running-the-lab` says, with the `Memory-Ref` trailer for any memory written.

Every session in a git repository ends with a commit, asked for or not; in a folder that is not a git repository, say the commit was skipped.

## Lab meeting

At each milestone, or weekly: write `research_lab/decisions/lab_meetings/YYYY-MM-DD.md` from `LAB_MEETING.md`. Findings appear as FND-ids only.

## Stage approval review

1. The stage's owner submits.
2. The stage's independent checks run in parallel.
3. The approver decides.
4. Log the decision in `research_lab/decisions/DECISION_LOG.md`: id, context, options, decision, rationale, evidence ids, approver.

The stages, owners and checks are in `science-ultrapowers:running-the-lab`.

## Committee-report cycle

For each progress report to a monitoring committee that the project brief names, the Documentation Writer drafts from the findings log, the Academic Reviewer reviews, the Academic Supervisor approves, then the researcher.

## Warning signs

| Thought | Reality |
|---|---|
| "The session is short, skip the opening" | Short sessions drift fastest. Open the session. |
| "The close can wait until tomorrow" | Tomorrow starts from the record. Close now. |
| "I'll summarize from memory instead of the records" | A summary from memory is a claim without a check. Read the records. |
| "Just wrap up means a summary" | Wrapping up means the five steps, in order. |
| "The researcher didn't ask for a commit" | In a git repository, the session close includes the commit. Commit. |
| "The working-notes folder is git-ignored anyway" | Ignored is not deleted. Delete it. |
| "The artifact archive hasn't changed" | Unchecked is unknown. Run `lfs-check`. |
