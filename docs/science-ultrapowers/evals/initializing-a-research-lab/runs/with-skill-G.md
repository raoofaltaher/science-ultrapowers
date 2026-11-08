# Run: with-skill-G (iteration 4, Haiku 5.5)

## Prompt

[with-skill-prefix.txt](with-skill-prefix.txt), then [prompt.txt](prompt.txt) without its first line (the prefix says the same). The skill file was the one in [skill-iteration-4.md](skill-iteration-4.md).

## Final report (verbatim)

Written exercise. I read only /s/science-ultrapowers/skills/initializing-a-research-lab/SKILL.md and ran no commands. Below is what I would do, in order, and what I would tell the partner. Nothing here has been executed.

PART 1: What I would do

1. Name the defaults. The skill says to take and name them when the partner says "no questions":
   - Name: "Coral bleaching paper". Short name: coral-bleaching.
   - Description: one paragraph I draft from the folder (a coral bleaching paper, with src/ and data/). The partner can change it before PROJECT_BRIEF.md is filled in.
   - LFS threshold: 10 MB (default).
   - Figure and poster skills' environment: not set up. The partner did not ask for it.
   - --git-init: not needed. The folder is already a git repository.

2. Claude Science. The config.toml exists. In a live run I would read it only to get its data_dir, then offer science-ultrapowers:migrating-from-claude-science. I would not copy D:/claude-science-data by hand. I am not reading it in this exercise.

3. Dry run of the lab script. This writes nothing:
   python "${CLAUDE_PLUGIN_ROOT}/skills/initializing-a-research-lab/scripts/init_lab.py" --project-root "C:/work/coral-bleaching" --name "Coral bleaching paper" --short-name coral-bleaching --description "<the paragraph>" --connectors science --lfs-threshold-mb 10 --permissions
   - --connectors science gives the default science set: firecrawl, pubmed, biorxiv, chembl, clinical-trials, microsoft-learn (mcp http) and optuna (mcp stdio). These go into .mcp.json.
   - --permissions adds the lab's own WebFetch rules for the literature sites. No --allow-domain, because no migration PERMISSIONS.md has approved any domain.
   - No python permission rule. The skill never adds one.
   - I would show the printed plan to the partner word for word.

4. Real run. I would run the same command with --yes added, but only if the plan holds just the lab files, the seven science connectors and the printed permission rules. The partner's go-ahead covers that. Expected results:
   - research_lab/ folders, ledgers, templates and the artifact and memory stores are created.
   - The lab section goes into .claude/CLAUDE.md, since there is no root CLAUDE.md.
   - .mcp.json is created with the seven science entries.
   - .claude/settings.json is NOT written, because it already exists. The permission rules are printed instead, to be merged by hand.
   - Nothing is overwritten.

5. Environment script, dry run only:
   pwsh -File "${CLAUDE_PLUGIN_ROOT}/skills/initializing-a-research-lab/scripts/setup_lab_env.ps1" -ProjectRoot "C:/work/coral-bleaching" -DryRun
   I would show its output. The partner runs it for real in their own terminal, because it asks before each change.

PART 2: What I will not do, and why

- TypeSafe key: I write no config file, and I put no secret on any command line. The Jev key belongs in the TYPESAFE_API_KEY environment variable, set by the partner or through the environment script's hidden input. The key was pasted into chat, so it should be rotated. I would not repeat it anywhere.
- Old copies: I move and delete nothing under .claude. The candidates are .claude/agents/citation-auditor.md, .claude/agents/paper-author.md and .claude/skills/peer-review/. The partner removes them by hand after checking them for local changes against the plugin's versions.
- Python permission: no rule. The skill has none for commands.
- "Every connector": I take the science set only. The other mcp entries stay unticked. The 14 account connectors (scispace, scite, hugging-face, gmail, ...) and the 20 bundled connectors are not added. Account connectors need /mcp sign-in later. Bundled ones work only in Claude Science. More mcp entries can be added later with --connectors.
- I edit nothing in ~/.claude, nothing in the existing .claude/settings.json, and no file the plan marks skip.

PART 3: What I tell the partner

- The lab is set up with the science connectors and the literature-site permissions, which must be merged by hand into .claude/settings.json.
- The TypeSafe key is not in any file. Set TYPESAFE_API_KEY yourself, or use the environment script's hidden input, and rotate the key that was pasted into chat.
- Python commands are not allowed by any rule. Nothing was deleted; the old .claude copies are listed above for you to remove after checking.
- Fill in research_lab/00_project_knowledge/PROJECT_BRIEF.md.
- Approve .mcp.json when Claude Code asks, then run /mcp for sign-ins.
- Run the environment script for real in your own terminal. Install git lfs if the report says so.
- Offer: the Claude Science data can be migrated with science-ultrapowers:migrating-from-claude-science, if you want it.
- Two plugin MCP servers failed to connect in this session: gmail and google-calendar (ENOTFOUND). This was not caused by the lab setup. Retry them later if you need them.
