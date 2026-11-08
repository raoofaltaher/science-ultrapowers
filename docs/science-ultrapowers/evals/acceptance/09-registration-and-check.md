# Acceptance 09: the migration of a 0.1 lab, and the registration cycle

Date: 2026-11-08. Claude Code 2.1.319. The acceptance folder of 0.1.0 (`<acceptance-folder>`, the coral-bleaching lab of acceptance 01, plugin 0.1.1 from the marketplace, a git repository with `core.autocrlf` set to `true`). The 0.2.0 build was installed before the release from the repository path: `claude plugin marketplace add <repository> --scope local` in the folder (the override lives in the folder's `.claude/settings.local.json`; the user-level marketplace entry and the researcher's live project stay on 0.1.1), then `claude plugin update science-ultrapowers@science-ultrapowers` (0.1.1 to 0.2.0). After each fix below the plugin was uninstalled and installed again at project scope, because the version number does not change between commits. That path proved unreliable on this machine (a marketplace refresh re-cloned the GitHub source, 0.1.1, and the cached copy did not follow the repository's later commits), so the track sessions of transcripts 04 to 08 load the plugin from the repository for the session with `claude --plugin-dir <repository>` instead; the marketplace install of the release is exercised by Task 27's update of the two installs.

## Step 1: the migration

`init_lab.py --name ... --short-name ... --description ...` without `--yes` printed the plan: 6 files to create (the two new folders' `.gitkeep` files and the four new templates), 3 appends, 12 skips, 1 warning and 65 migration lines:

- 28 `rename` lines: the ten numbered folders, `artifacts/store` to `artifacts/archive`, `.scratch` to `.working`, the records (`REGISTRY.csv` to `SOURCES.csv`, `evidence_cards` to `evidence_records`, `audits` to `search_logs`, `FINDINGS.md` to `FINDINGS_LOG.md`, `CANONICAL_NUMBERS.md` to `KEY_RESULTS.md`, `protocols` to `preregistrations`, `DECISIONS.md` to `DECISION_LOG.md`, `TASK_BOARD.md` to `WORK_PLAN.md`), the seven templates and the meeting note `2026-11-08_kickoff.md` to `2026-11-08_opening.md`.
- 25 `header` lines, among them `F-id -> FND-id (finding)`, `(none) -> Basis` on the findings log, the five source-table columns, `(none) -> Input checksums` on the experiment register, `Gate -> Stage` on the review log and the work plan, `D-id -> DEC-id (decision)`.
- `rewrite` lines: the work plan's stage tokens (`G0 -> Question`, 3 rows; `G1 -> Literature`, 1 row), `lab.json` (`jev.blockedPaths -> scope.restrictedFolders`, the seven role ids, `idPrefixes` added) and the archive's `.gitattributes` (`store/ -> archive/`, 1 line).
- The output style: `.claude/output-styles/scholarly-explanatory.md: create`, with the settings line `"outputStyle": "Scholarly Explanatory"`.
- The warning: `CLAUDE.md imports research_lab/00_project_knowledge/PROJECT_BRIEF.md; change the import to research_lab/project/PROJECT_BRIEF.md by hand`.

With `--yes`: `git status` showed 40 renames staged by `git mv` (no delete-plus-add), the headers and tokens rewritten, the output style written. A second run planned no migration line and nothing to create. The import line was changed by hand as the warning said, and `research_lab/`, `.gitignore` and `CLAUDE.md` were committed.

Observation, as designed: the migration rewrites headers, status tokens and keys only. The prose of the migrated record files (for example the findings log's introduction, which still says "Findings ledger" and "F-id") is the 0.1 template's free text and stays as written; the templates of a fresh 0.2.0 lab carry the new words.

Verdict for the migration: PASS.

## Step 2: the registration cycle

A fixture input `data/raw/fixture.csv` was committed, the protocol `research_lab/experiments/preregistrations/EXP-0001.md` was copied from the lab's `templates/PREREGISTRATION.md`, and:

```
python "<plugin-root>/skills/preregistering-the-protocol/scripts/preregister.py" register research_lab/experiments/preregistrations/EXP-0001.md --input data/raw/fixture.csv --task TASK-0001
```

Exit 0; the JSON named the registration commit and the time-stamp commit and the one input with its blob hash. `git log` showed `TASK-0001 research-project-manager: register protocol EXP-0001` with the trailer `Preregistration: EXP-0001`, then `... time-stamp protocol EXP-0001` with `Preregistration-Timestamp: <registration hash>`; the file's line 2 read `Registered at commit: <registration hash>`.

An output `results/EXP-0001/metrics.csv` was committed, then:

```
python "<plugin-root>/skills/preregistering-the-protocol/scripts/preregister.py" check research_lab/experiments/preregistrations/EXP-0001.md --outputs results
```

### First run of the check: two defects

1. `registered` was `not clear` with "the first commit of the protocol also holds: .gitignore, .mcp.json, CLAUDE.md, research_lab/..." and the four other items `unprovable` ("registration commit unknown"). Cause: the script found the registration commit as the first commit touching the path with `git log --follow`, and git's copy detection traced the protocol, copied from the tracked template, back to the lab's initial commit. Fix: the registration commit is the oldest commit touching the path whose `Preregistration:` trailer names the protocol id, with the first-commit search as the fallback; test `test_check_registered_when_protocol_copied_from_a_tracked_template` added (RED, then GREEN).
2. After the reinstall, `registered`, `timestamp`, `chronology` and `inputs` were clear, and `unaltered` was `not clear` with "the protocol has uncommitted edits" on a clean tree. Cause: Review Focus item 1. The checkout has `core.autocrlf` set to `true`, so the working copy carries CRLF while the registered blob carries LF, and the byte comparison read the line endings as an edit. Fix: the working-copy comparison runs through git (`git diff --quiet HEAD -- <protocol>`), which applies the line-ending filters; the comparison of the branch head with the registered version stays byte for byte on the blobs; test `test_check_unaltered_is_clear_on_an_autocrlf_checkout` added (RED, then GREEN).

### After the fixes

Clean tree: exit 0, `ok: true`:

```
registered  clear  commit <registration hash> holds the protocol alone
timestamp   clear  time-stamped by commit <time-stamp hash>
unaltered   clear  the protocol equals the registered version
chronology  clear  1 output commit(s), all after the registration
inputs      clear  1 input checksum(s) match
```

After a line was appended to the protocol and committed: exit 1, `ok: false`, `unaltered not clear` with "the protocol at the branch head differs from the registered version", the four other items clear. The edit commit was then removed from the acceptance folder.

Verdict for the registration cycle: PASS after the two fixes, on a Windows checkout with `core.autocrlf` set to `true` (Review Focus items 1 and 2 exercised; item 2's linked worktree was not built).
