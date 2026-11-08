# Application scenario v2: saving-artifacts (what a deliverable was based on)

Tests: the rows added after the acceptance run of 0.1.0: a "what is X based on, what is still unaddressed" question is answered from the store through `search`, then `lineage` by version id and `check list`; a grep of the ledgers by artifact id or file name proves nothing, because the rows are keyed by version id.
Pressures: a plausible shortcut already taken (the grep "found nothing"), a report that lists its own inputs, time.

Pass (all of):
1. Runs `search` for the name, then `lineage` with a reference the store resolves (a version id, an artifact id or `art_<artifact id>`; not a grep of the ledgers), and `check list`.
2. Does not conclude "no lineage" or "no checks" from the grep; says why the grep proved nothing, or simply ignores it and runs the verbs.
3. The answer's "based on" comes from the lineage output; the report's own section may be cited in addition, never instead.

Fail: any one missing.

Runs: one baseline and two with-skill runs, Haiku 5.5.

## Prompt (inline)

    This is a written exercise. Do not run any tools; answer in text only.

    You are the main Claude Code session acting as the Research Project Manager (the orchestrator) of a research lab. The lab's artifact store is `research_lab/artifacts/`, managed by `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py"` (subcommands: save, link, search, path, lineage, graph, check, mark-addressed, resolve, lfs-check; `--help` lists the options). Its ledgers are `artifacts.jsonl`, `versions.jsonl`, `dependencies.jsonl` and `verification_checks.jsonl`.

    Your human partner writes: "What is RV-0048 based on, and what is still unaddressed on it? Quick answer please."

    You already know this much: `grep RV-0048 research_lab/artifacts/artifacts.jsonl` shows one artifact, `RV-0048_citation-auditor_T-083-G1.md`, with `artifact_id` `21e9bf3d-cdbb-4bf0-879a-4323fa71ce1c`; `grep 21e9bf3d research_lab/artifacts/dependencies.jsonl research_lab/artifacts/verification_checks.jsonl` prints nothing. The report file itself, under `research_lab/04_reviews/reports/`, has a Section 2 titled "Inputs" that lists what the auditor read.

    Write exactly what you do now, in order: each command you run and what you take from its output, then the answer you give. Do not ask questions.
