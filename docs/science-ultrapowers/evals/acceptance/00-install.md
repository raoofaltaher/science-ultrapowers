# Acceptance 00: install from the marketplace into a fresh folder

Date: 2026-11-08. Claude Code 2.1.319. Plugin 0.1.0 from the public marketplace `raoofaltaher/science-ultrapowers`.

## Step 1: no local-path install to remove

`claude plugin list` showed no `science-ultrapowers` entry and no settings file referenced one, so there was nothing to uninstall.

## Step 2: install at project scope

```
claude plugin marketplace add raoofaltaher/science-ultrapowers
# Clone complete, validating marketplace…
# ✔ Successfully added marketplace: science-ultrapowers (declared in user settings)

mkdir <smoke-folder> && cd <smoke-folder>
claude plugin install science-ultrapowers@science-ultrapowers --scope project
# ✔ Successfully installed plugin: science-ultrapowers@science-ultrapowers (scope: project)
```

`<smoke-folder>/.claude/settings.json` afterwards:

```json
{
  "enabledPlugins": {
    "science-ultrapowers@science-ultrapowers": true
  }
}
```

## Step 3: a session sees the bootstrap

A headless session in the folder (`claude -p "What skills do you have? List their names only."`, one turn, no tool use) listed, among the other installed plugins' skills, every `science-ultrapowers:` skill (35 names), `science-ultrapowers:running-the-lab` included. Excerpt:

```
- science-ultrapowers:debugging
- science-ultrapowers:deciding-with-jev
- science-ultrapowers:dispatching-parallel-agents
- science-ultrapowers:figure-bible
- science-ultrapowers:figure-qa
- science-ultrapowers:holding-lab-meetings
- science-ultrapowers:hypothesis-generation
- science-ultrapowers:implementation-planning
- science-ultrapowers:initializing-a-research-lab
- science-ultrapowers:manuscript-formatting
- science-ultrapowers:migrating-from-claude-science
- ...
- science-ultrapowers:running-the-lab
- ...
```

Verdict: PASS. Definition of done 1 holds on this Windows machine: marketplace add, install at project scope, the plugin loads in a new session.
