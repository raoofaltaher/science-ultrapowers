# Lab memory: index

One line per memory; each file under `project/` or `artifact/<artifact_id>/` holds one fact.
Read at every session kickoff. Hard budget: `memory.indexBudget` lines in `research_lab/lab.json` (default 150), this header included.

Save a memory only when all four hold:
1. Verified: tested or observed in this project, not inferred.
2. Durable: still true next month.
3. Expensive: rediscovering it would cost 15 minutes or more.
4. Not derivable: not in code, docs, specs, git history, or the lab records (findings, decisions, registry, artifact store).

Never store: secrets, tokens, credentials, URLs embedding auth, personal data, facts about people (they go to Claude Code user memory), records, artifact contents, code, fix recipes, task state, tool availability, anything in `CLAUDE.md`, anything derivable from the records or the artifact store.

Index line: `- [<title>](<folder>/<name>.md) — <one-line hook> (<YYYY-MM>)`; an update folds in as `**UPDATED YYYY-MM-DD: ...**`.

## Project

## Artifacts
