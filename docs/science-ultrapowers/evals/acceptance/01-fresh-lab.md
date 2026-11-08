# Acceptance 01: a fresh lab

Date: 2026-11-08. In `<smoke-folder>` (only `.claude/settings.json` from acceptance 00), a headless session: `claude -p "Let's start the lab for my paper on coral bleaching and symbiont shuffling."` (20 turns).

## What the session did, in order

1. Invoked `science-ultrapowers:initializing-a-research-lab` as its first tool use, before any other action ("Using science-ultrapowers:initializing-a-research-lab to set up the lab...").
2. Listed the folder, checked for an existing `research_lab/` and for a Claude Science config home.
3. Ran `init_lab.py` without `--yes` (the plan) with a name, a short name and a description derived from the request, the six science connectors and the defaults.
4. Looked into the Claude Science data directory for a matching project (read-only listing and grep), found none, and did not migrate anything.
5. Ran `init_lab.py` with `--yes`: `research_lab/`, `CLAUDE.md` with the lab section, `.mcp.json`, `.gitignore`, `references/`; `--git-init` since the folder had no repository.
6. Ran `setup_lab_env.ps1 -DryRun` and showed its output; did not run it for real.
7. Invoked `science-ultrapowers:holding-lab-meetings` for a kickoff, wrote the kickoff note under `research_lab/06_decisions/lab_meetings/`, seeded the task board, pre-drafted brief sections 1, 7 and 8, left an H-card stub, and committed `research_lab/` (two commits).
8. Closed with what it needs from its human partner: the research question and the H-card, the remaining brief sections, approval of `.mcp.json` and `/mcp` sign-in, the environment script to run by hand.

`research_lab/lab.json` afterwards named the lab, its short name, the description, `pluginVersion` 0.1.0 and the fourteen roles.

## Verdict

PASS on the order of events: the init skill ran first, the plan was printed before any write, nothing was written before the plan, the environment script stayed a dry run, and the session asked for what only its human partner can supply.

Gap, recorded: a headless `-p` session has no channel for the skill's questions (name, description, connectors, out-of-scope folders), so the session chose defaults and took the request as the go-ahead under the skill's rule that a plan holding only what was asked for is covered by the request. The spec's "after showing the file list and getting a yes" is therefore shown by the eight interactive-style pressure runs under `../initializing-a-research-lab/` and by this transcript's plan-then-write order, not by a typed yes. An interactive session is the place to see the question step.

Observation: the kickoff went beyond a status note (task board rows, a brief pre-draft, an H-card stub). Nothing of it was wrong, and the note says what the owner must fill in.
