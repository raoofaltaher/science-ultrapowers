# Acceptance 02: init and migrate in the source project, then the kickoff

Date: 2026-11-08. The owner's live research project (`<host-project>`, a git repository on its main branch, clean), which already held a Claude Science era `research_lab/` (records, no `lab.json`), hand copies of the fourteen agents and the old skills under `.claude/`, a `.claude/CLAUDE.md` and a `.claude/settings.json`.

## Install at project scope

`claude plugin install science-ultrapowers@science-ultrapowers --scope project` added the plugin to `.claude/settings.json` beside the one plugin already enabled there. Nothing else under `.claude/` changed.

## init

The plan (no `--yes`) listed 23 creates (the missing READMEs, `.gitkeep` files, `lab.json`, the memory store, the artifact store's `.gitattributes`), two appends (`.claude/CLAUDE.md`, `.gitignore`), 33 skips (every existing record and template) and one warning naming the 14 agent copies and 20 skill folders under `.claude/` that share names with the plugin's, left in place for the owner to check and remove by hand. `--yes` applied exactly that: `written: 23 files`. `git status` afterwards showed the new `research_lab/` files and the three edits outside it (`.claude/CLAUDE.md`, `.claude/settings.json`, `.gitignore`), which were left uncommitted for the owner.

## migrate

Run on a copy of the Claude Science data directory (`--data-dir`), never on the live one.

Dry run, the counts against PLAN-07's pinned values:

| step | source | imported | skipped | left out |
|---|---|---|---|---|
| memories | 79 | 76 | 0 | 3 superseded |
| profiles | 15 | 15 | 0 | 0 |
| artifacts | 418 | 418 | 0 | 0 |
| versions | 555 | 555 | 0 | 0 |
| dependencies | 940 | 940 | 0 | 0 |
| verification checks | 1527 | 1527 | 0 | 0 |
| transcripts | 42936 | 0 | 0 | off (no `--transcripts`) |

Warnings: 116 (per-row list in `migration/WARNINGS.md`). The counts match the pinned values, so the real run followed with the same arguments and the same counts. `git add research_lab/ && git commit` committed the lab and the import only; nothing outside `research_lab/` was staged.

## Session: "Lab, where do we stand?"

A headless session (35 turns) invoked `science-ultrapowers:running-the-lab`, then `science-ultrapowers:holding-lab-meetings`, and read, in this order: the lab-meeting notes (the last one a stand-up dated 2026-11-02), `migration/WHERE_WE_LEFT_OFF.md`, the task board, the open access requests (five `OPEN` rows), the decisions log, the migration report and warnings, the memory index `memory/MEMORY.md`, the recent git log, the pre-registrations, the findings ledger rows they name, and the run folders. It then wrote `research_lab/06_decisions/lab_meetings/2026-11-08_kickoff.md` and committed it.

The kickoff it gave: which phase is closed and what has run since; the two pre-registrations waiting on review and the exact review legs each needs; the one hard blocker (an environment re-sync the owner must run); the record gaps it found (task-board rows missing for four task ids, no notes for two recent sessions, five open full-text requests, the three uncommitted init edits outside `research_lab/`, and that the new `.gitignore` line for `references/` contradicts a standing decision of this project that keeps references tracked); and a recommended next action with the dispatches it would make.

Verdict: PASS. The kickoff cites the last stand-up note, the open tasks, the open access requests, the memory index and the imported where-we-left-off digest, and it ends with a recommended next action. The `references/` ignore line is a real conflict for a project that tracks its references; it is the owner's call and the line stays uncommitted.
