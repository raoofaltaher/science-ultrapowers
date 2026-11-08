---
name: initializing-a-research-lab
description: Use when a project has no research_lab/, when your human partner asks to start, set up, join or upgrade a lab for a paper or project, or when the lab scaffold is older than the plugin
---

# Initializing a Research Lab

## Overview

The setup script adds what the project lacks: record folders and ledgers, templates, the artifact and memory stores, the lab section of the root `CLAUDE.md`, or of `.claude/CLAUDE.md` when that is the only one; on request, connectors and permission rules. It never overwrites a file. A re-run after a plugin update adds what is new.

**Core principle:** Show the plan, then write. "Do all of it" is a yes to the lab, never to what the lab does not do.

## Ask first

Ask once; after "no questions", take and name the defaults.

1. Name, short name, one-paragraph description.
2. **Claude Science:** if `%USERPROFILE%\.claude-science\config.toml` exists, read the `data_dir` it names and offer `science-ultrapowers:migrating-from-claude-science`. Never copy that folder by hand.
3. **Connectors:** the `science` set ticked, the other `mcp` entries unticked. `account` connectors are reachable after `/mcp` sign-in; `bundled` ones work only in Claude Science. Neither goes into `.mcp.json`.
4. LFS threshold (default 10 MB).
5. Whether to set up the figure and poster skills' environment.
6. **Permission rules** (default no): `--permissions` carries the lab's own `WebFetch` rules for the literature sites, plus any `--allow-domain` (offer those a migration's `PERMISSIONS.md` approved). It writes `.claude/settings.json` only when absent; otherwise it prints the rules to merge by hand.

## Show, then write

1. Run the script without `--yes` and show its plan word for word.
2. Run it with `--yes` after a yes. A go-ahead given before the plan covers it when the plan holds only what was asked for; refusing part of a request never blocks the rest.
3. In a folder that is not a git repository, offer `--git-init`.
4. Show the environment script's `-DryRun` output; your human partner runs it for real, since it asks before each change.

## After writing

Tell your human partner to:
- fill in `research_lab/00_project_knowledge/PROJECT_BRIEF.md`;
- approve `.mcp.json` when Claude Code asks, then run `/mcp` for sign-ins;
- remove the listed `.claude/agents` and `.claude/skills` duplicates by hand, once checked for local changes;
- install `git lfs` if the report says so;
- merge any printed permission rules by hand.

## Never, even when asked

| Request | What you do |
|---|---|
| "Put the key in a config file" | No secret in a file or on a command line. The Jev key lives in the `TYPESAFE_API_KEY` environment variable, set by your human partner or by the environment script's hidden input. A key pasted into chat should be rotated. |
| "Clean out the old copies" | You move and delete nothing under `.claude/agents` or `.claude/skills`. List them. |
| "Allow running python" | No permission rule for commands. |
| "Every connector" | The `mcp` entries at most. |

Never edit `~/.claude`, an existing `.claude/settings.json`, or any file the plan marks `skip`.

## Command

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/initializing-a-research-lab/scripts/init_lab.py" [--project-root <dir>] --name "<name>" --short-name <short> --description "<paragraph>" [--connectors science,<id>,...] [--lfs-threshold-mb 10] [--git-init] [--permissions [--allow-domain <host> ...]] [--yes] [--json]
pwsh -File "${CLAUDE_PLUGIN_ROOT}/skills/initializing-a-research-lab/scripts/setup_lab_env.ps1" -ProjectRoot <project> -DryRun
```
