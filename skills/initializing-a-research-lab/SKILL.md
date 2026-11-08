---
name: initializing-a-research-lab
description: Use when the researcher wants a research lab started, joined or upgraded in this project, or asks for research work in a folder that has no research_lab/
---

# Initializing a Research Lab

## Overview

The setup script adds what the project lacks: folders, templates and the artifact archive, the lab section of `CLAUDE.md` (`.claude/CLAUDE.md` if it is the only one) and, on request, connectors and permission rules. It never overwrites a file; a re-run adds what is new and updates `lab.json`.

The lab set-up has these folders under `research_lab/`: `project/`, `literature/`, `findings/`, `experiments/`, `reviews/`, `requests/`, `decisions/`, `planning/`, `automation/`, `tool_vetting/`, `templates/`, `artifacts/`, `memory/` and `.working/`. `lab.json` holds the lab's name, `roles` (the fourteen role ids, such as `research-project-manager`), `idPrefixes`, `connectors`, `scope.restrictedFolders` and `permissions`.

**Core principle:** Show the plan, then write. "Do all of it" is a yes to the lab, never to what the lab does not do.

## Ask first

Ask once; after "no questions", take and name the defaults.

1. Name, short name, description (one or two sentences), Git Large File Storage (LFS) threshold (default 10 MB).
2. **Claude Science:** if `%USERPROFILE%\.claude-science\config.toml` exists, offer `science-ultrapowers:migrating-from-claude-science`. Never copy that folder by hand.
3. **Connectors:** tick the six http `science` entries, not the other `mcp` ones; offer `optuna` when the project brief names hyper-parameter studies. `account` connectors work after `/mcp` sign-in, `bundled` ones only in Claude Science; neither goes into `.mcp.json`.
4. Restricted folders, which no role may open (`--out-of-scope`, repeatable; the script writes them to `scope.restrictedFolders` in `lab.json`).
5. Whether to set up the figure and poster environment.
6. **Permission rules** (default no): `--permissions` writes the lab's literature-site `WebFetch` rules and any `--allow-domain` (offer those a migration's `PERMISSIONS.md` approved) to `.claude/settings.json` only when absent; else it prints a JSON snippet to merge by hand.

## Show, then write

1. Run the script without `--yes` and show its plan word for word.
2. Run it with `--yes` after a yes; an earlier go-ahead covers a plan of only what was asked for, and refusing part never blocks the rest.
3. In a folder that is not a git repository, offer `--git-init`.
4. Show the environment script's `-DryRun` output; the researcher runs it (it asks before each change).

### A lab in the 0.1 layout

Init migrates a lab in the 0.1 layout (a numbered folder such as `02_findings_ledger/` under `research_lab/`). <!-- legacy -->
The plan lists each change as a `rename`, `header` or `rewrite` line, and init applies it only after the researcher confirms with `--yes`. The migration renames folders and files with `git mv` when the lab is tracked. It rewrites table headers, status tokens, the memory keys `basis` and `type`, and `lab.json`. It never edits a free-text cell or an existing identifier. It stops for a folder when the old and the new name both exist, and reports `unexpected layout`. Until the migration runs, every lab script exits with the message `this lab uses the 0.1 layout; run science-ultrapowers:initializing-a-research-lab to migrate it`.

### The scholarly output style

Init installs the scholarly output style at `.claude/output-styles/scholarly-explanatory.md` when the file is absent. It prints the line `"outputStyle": "Scholarly Explanatory"` for the researcher to add to `.claude/settings.json`. It writes nothing when the file exists, and says so.

## After writing

Tell the researcher to:
- fill in `research_lab/project/PROJECT_BRIEF.md`;
- commit `research_lab/`, the new root files and each file the report says to review (in an existing repository init commits nothing);
- approve `.mcp.json` when asked, then sign in via `/mcp`;
- remove the listed `.claude` duplicates by hand after checking them for local changes;
- install `git lfs` if the report says so;
- add the printed `"outputStyle"` line to `.claude/settings.json` to write in the scholarly style.

## Never, even when asked

| Request | What you do |
|---|---|
| "Put the key in a config file" | No secret in a file or on a command line. The Jev key lives in the `TYPESAFE_API_KEY` environment variable, set by the researcher or the environment script's hidden input. Rotate a key pasted into chat. |
| "Clean out the old copies" | You move and delete nothing under `.claude/agents` or `.claude/skills`. List them. |
| "Allow running python" | No permission rule for commands. |
| "Every connector" | The `mcp` entries at most. |

Never edit `~/.claude`, an existing `.claude/settings.json`, or any file the plan marks `skip`.

## Command

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/initializing-a-research-lab/scripts/init_lab.py" [--project-root <dir>] --name "<name>" --short-name <short> --description "<one or two sentences>" [--connectors science,<id>,...] [--out-of-scope <folder> ...] [--lfs-threshold-mb 10] [--git-init] [--permissions [--allow-domain <host> ...]] [--yes] [--json]
pwsh -File "${CLAUDE_PLUGIN_ROOT}/skills/initializing-a-research-lab/scripts/setup_lab_env.ps1" -ProjectRoot <project> -DryRun
```
