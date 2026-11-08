---
name: holding-lab-meetings
description: Use at the start of every work session before any task, at the end of every session, at a milestone, at a gate review, or when your human partner asks where the project stands
---

# Holding Lab Meetings

## Overview

The lab opens each session with a kickoff, closes it with a stand-up, and meets at milestones. Notes live in `research_lab/06_decisions/lab_meetings/`, from the templates in `research_lab/templates/`.

**Core principle:** A session starts from the records and ends in the records; nothing is carried in anyone's head.

## Session kickoff

Before any task, including a short session:

1. Read `research_lab/00_project_knowledge/PROJECT_BRIEF.md`, `research_lab/07_project_management/TASK_BOARD.md`, the last note in `research_lab/06_decisions/lab_meetings/`, the open rows of `research_lab/05_access_requests/ACCESS_REQUESTS.md` and `research_lab/memory/MEMORY.md`; and `research_lab/migration/WHERE_WE_LEFT_OFF.md` when it exists and no lab-meeting note is newer than the import.
2. Write `research_lab/06_decisions/lab_meetings/YYYY-MM-DD_kickoff.md` from `SESSION_KICKOFF.md`; a second session the same day is `YYYY-MM-DD_kickoff-2.md`, and likewise `_standup-2.md`. Its first paragraph is a short lab status: open tasks by gate, blocked items, open access requests, and the recommended next action.
3. Present it. No task starts before it is presented.

## Session stand-up

At the end of every session, in this order; none is optional:

1. Gate every `Memories proposed:` line not already gated after its hand-off, with `science-ultrapowers:remembering-for-the-lab`.
2. Run `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" lfs-check`. A non-zero exit is fixed as `science-ultrapowers:saving-artifacts` says.
3. Write `research_lab/06_decisions/lab_meetings/YYYY-MM-DD_standup.md` from `SESSION_STANDUP.md`. Numbers only as recorded in the lab files, each with the check that produced it. Present it.
4. Delete `research_lab/.scratch/<today>-*`.
5. Commit `research_lab/` as `science-ultrapowers:running-the-lab` says, with the `Memory-Ref` trailer for any memory written.

Every session in a git repository ends with a commit, asked for or not; in a folder that is not a git repository, say the commit was skipped.

## Lab meeting

At each milestone, or weekly: write `research_lab/06_decisions/lab_meetings/YYYY-MM-DD.md` from `LAB_MEETING.md`. Findings appear as F-ids only.

## Gate review

1. The gate's owner submits.
2. The gate's independent checks run in parallel.
3. The approver decides.
4. Log the decision in `research_lab/06_decisions/DECISIONS.md`: id, context, options, decision, rationale, evidence ids, approver.

The gates, owners and checks are in `science-ultrapowers:running-the-lab`.

## Committee-report cycle

For each progress report to a monitoring committee that the project brief names, the Documentation Writer drafts from the ledger, the Academic Reviewer reviews, the Academic Supervisor approves, then your human partner.

## Red Flags

| Thought | Reality |
|---|---|
| "The session is short, skip the kickoff" | Short sessions drift fastest. Kick off. |
| "The stand-up can wait until tomorrow" | Tomorrow starts from the record. Stand up now. |
| "I'll summarise from memory instead of the records" | A summary from memory is a claim without a check. Read the records. |
| "Just wrap up means a summary" | Wrapping up means the five steps, in order. |
| "Your human partner didn't ask for a commit" | In a git repository, closing the stand-up includes the commit. Commit. |
| "The scratchpad is git-ignored anyway" | Ignored is not deleted. Delete it. |
| "The artifact store hasn't changed" | Unchecked is unknown. Run `lfs-check`. |
