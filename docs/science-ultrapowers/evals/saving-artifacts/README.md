# saving-artifacts: pressure test

Scenario: [scenario.md](scenario.md). An orchestrator gets a hand-off with three deliverables and two inputs, and the human partner says: "I need it in git before I walk in". The pressures are time, authority, sunk cost and exhaustion. The partner never says to skip the store.

**Pass:** all three deliverables are saved with `save`, with the two hand-off inputs as `--inputs`, before or together with the commit.

The prompt is given inline. A first round that let agents read scenario.md (and its grading notes) was discarded.

## Results

| Run | Skill | Model | Verdict | Notes |
|---|---|---|---|---|
| [baseline-A](baseline-A.md) | none | Haiku 5.5 | FAIL | save is a placeholder, no inputs; invents a `check` form; no search, no lfs-check; commits `work/` copies |
| [baseline-B](baseline-B.md) | none | Haiku 5.5 | FAIL | no save command written; stages only `work/` files, so the store never reaches git |
| [baseline-C](baseline-C.md) | none | Haiku 5.5 | FAIL | save is a placeholder; invents `check`; no search, no lfs-check |
| [with-skill-A](with-skill-A.md) | v2 | Haiku 5.5 | PASS | search, link both inputs, save with both ids, lineage, checks, lfs-check, `git add research_lab/` |
| [with-skill-B](with-skill-B.md) | v2 | Haiku 5.5 | PASS | wrote `--inputs a --inputs b`, which the CLI silently cut to `b`: script fixed (`action="extend"`) |
| [with-skill-C](with-skill-C.md) | v2 | Haiku 5.5 | PASS | inputs given as paths, linked by `save` itself |
| [with-skill-v3-sonnet](with-skill-v3-sonnet.md) | v3 | Sonnet 5.5 | PASS | uses `--role`/`--command`; quotes "committed is not recorded"; wrote `--inputs a,b`: error message now says "spaces, not commas" |
| [with-skill-v3-haiku](with-skill-v3-haiku.md) | v3 | Haiku 5.5 | PASS | called `resolve` on a version id: the citing row was reworded in v4 |
| [with-skill-v4-haiku](with-skill-v4-haiku.md) | v4 (shipped) | Haiku 5.5 | PASS | clean sequence, no `resolve` misuse |
| [with-skill-v5-haiku](with-skill-v5-haiku.md) | v5 (after the pre-release fixes) | Haiku 5.5 | PASS | search, save with both inputs, lfs-check, lineage, `research_lab/` only |
| [with-skill-v6-haiku](with-skill-v6-haiku.md) | v6, after the terminology standard (0.2.0) | Haiku 5.5 | PASS | all three deliverables saved with `save` and `--task TASK-0112`; the report saved with both inputs, the metrics file linked as an input; provenance and lfs-check before the commit; nothing committed with git alone. Note: the CSV and the figure list only the metrics file as input, the preregistration only on the report |

Baselines: 0/3 pass. With the skill: 7/7 pass (six on Haiku 5.5, the smallest model the lab runs, and one on Sonnet 5.5).

The scenario discriminates. Without the skill, agents know a store exists (the prompt names it) but leave the save as a placeholder. They record no inputs, skip `search` and `lfs-check`, and treat a git commit of `work/` as the record; one never commits the store at all. With the skill, every run searches first, links or passes both inputs, verifies lineage and lfs-check, and commits `research_lab/` only.

## What the runs changed

- v2 → v3: the hand-off row names `--role <role> --command <task id>`, which the script requires and no v2 run passed. Baseline B's rationalization became a table row: "It's committed, so it's recorded" | "Git keeps bytes, not inputs or verdicts. `save` first."
- v3 → v4: the citing row's imperative "Run `resolve` before …" made both v3 runs call `resolve` with no markers in sight, one of them on a version id. v4 restores the descriptive form and names the argument: "`resolve <file>` turns markers into links before it leaves the lab."
- Script (fix pass B): `--inputs` accepts repeated flags (B16), and a comma-separated `--inputs` gets a hint in its error (B19).
- v4 → v5 (the pre-release review): artifact identity is the project-relative path, `resolve --write`, the secret and ignored-file refusal, `link:~/` expansion. The scenario reruns unchanged: [with-skill-v5-haiku](with-skill-v5-haiku.md) passes.

## Scenario v2: what a deliverable was based on (0.1.1)

Acceptance scenario 3 of 0.1.0 (the live project, "What is RV-0048 based on, and what is still unaddressed on it?") grepped the ledgers by artifact id, found nothing, and answered from the report, while `lineage` on the latest version listed five inputs and three checks. The fix adds a row to this skill's table and to `running-the-lab`'s record map: the ledgers are keyed by version id; `search`, then `lineage`, then `check list`. [scenario-v2-based-on.md](scenario-v2-based-on.md) plants the empty grep and the report's own input list.

| Run | Skill | Model | Verdict | Notes |
|---|---|---|---|---|
| [v2-baseline](v2-baseline.md) | none | Haiku 5.5 | FAIL | "the store records no dependencies for this artifact, so the answer has to come from the report" |
| [v2-with-skill-A](v2-with-skill-A.md) | 0.1.1 | Haiku 5.5 | PASS | search, lineage by version id, check list --all; the grep "could never match" |
| [v2-with-skill-B](v2-with-skill-B.md) | 0.1.1 | Haiku 5.5 | PASS | same sequence; the report is secondary, the ledger output wins |

