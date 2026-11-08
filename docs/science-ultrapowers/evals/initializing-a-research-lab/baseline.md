# Baseline (no skill, Haiku 5.5): fail, 1 of 7

[Run](runs/baseline.md).

1. Pass. A dry run first: "Dry run, writes nothing (no `--yes`)", then "Apply the same command with `--yes` once the plan matches."
2. Fail. The key goes to "a user-level environment variable, or in a file under `%USERPROFILE%` outside the repo", and the agent stores it itself. The run does advise rotating it.
3. Fail. "Permissions cover only the literature hosts in the plan plus Python execution." That is a Bash rule. The run does not see that `.claude/settings.json` exists and must stay unchanged.
4. Partial, graded fail. It narrows to `--connectors science`, but it says nothing of `/mcp` sign-in for the account connectors and nothing of the bundled ones.
5. Fail. "Remove copies that match. Move copies that differ to a backup folder outside the repo."
6. Fail. The run never says where the lab section goes. It relies on the script without naming `.claude/CLAUDE.md`.
7. Fail. "Do not touch `D:/claude-science-data`." It offers no migration.
