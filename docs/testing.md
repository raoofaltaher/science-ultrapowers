# Testing science-ultrapowers

There are three kinds of tests.

## 1. Shell tests: `tests/<area>/test-*.sh`

- `tests/claude-code/`: plugin shape. Version sync across manifests, bootstrap size, session-start output, the no-foreign-harness gate, the lab-memory hooks (`test-memory-hooks.sh`: nudge and post-compaction, silent without a store, junctions, a closed stdout), the skill content (`test-skill-content.sh`: no old skill names, trigger-only descriptions, the load-bearing sentences in the skill that owns each, bare script and skill names, cross-references that resolve), the vendored skills (`test-vendored-skills.sh`: overlay, cleanliness, provenance hashes), the agent contract (`test-agents.sh`: frontmatter shape, preloaded skills that exist, `Agent` disallowed for the twelve, the `When to invoke` section, the manifest list, and running-the-lab's main-session line), the repository documents (`test-repo-documents.sh`: README sections, the credit line, the licence, the community files, the self-contained banner SVG, the release notes, the manifest licence field, the ignore rules, the CI permissions block), the environment script's dry run (`test-setup-env-dryrun.sh`: `setup_lab_env.ps1 -DryRun` under `pwsh -NonInteractive` writes nothing and asks nothing; skipped when pwsh is absent); also `run-tests.sh`, the runner itself.
- `tests/hooks/`: session-start behaviour, including an empty PATH, a closed stdout and no forks, a plugin root with a space; `run-hook.cmd` on Windows.
- `tests/version-bump/`: `scripts/bump-version.sh`.
- `tests/shell-lint/`: `scripts/lint-shell.sh` (the test stubs shellcheck; the script itself needs it).
- `tests/skill-layout/`: no development files inside skills.
- `tests/skill-size/`: every SKILL.md is under 20,000 bytes.
- `tests/systematic-debugging/`: `find-polluter.sh`.
- `tests/writing-skills/`: `render-graphs.js`; the rendering cases skip without Graphviz.

## 2. Python unittest: `skills/<skill>/scripts/tests/test_*.py`

`skills/saving-artifacts/scripts/tests/` (the artifact store, `artifacts.py`), `skills/verifying-evidence-by-doi/scripts/tests/` (`verify_doi.py`), `skills/deciding-with-jev/scripts/tests/` (`jev_ask.py`, offline), `skills/searching-the-literature/scripts/tests/` (`search_openalex.py`, offline), `skills/initializing-a-research-lab/scripts/tests/` (`init_lab.py`: a fresh folder, an existing project, connectors, permissions; each test runs the script in a temp folder), `skills/migrating-from-claude-science/scripts/tests/` (`migrate_claude_science.py` against a fixture database built from the CREATE TABLE statements recorded in `docs/science-ultrapowers/claude-science-schema.md`; the real database is used only by the dry run recorded in `docs/science-ultrapowers/evals/migration-dry-run.md`). The runner discovers them per directory. `skills/svg-primitives/tests/` is the vendored upstream pytest suite, not run by the lab runner.

## 3. Node tests: `skills/<skill>/scripts/tests/*.test.mjs`

`skills/remembering-for-the-lab/scripts/tests/memory-lint.test.mjs` (the lab-memory lint). Run with `node --test`.

## Behaviour tests for skills

Baseline and with-skill pressure transcripts live under `docs/science-ultrapowers/evals/<skill>/`, one folder per skill with the scenarios, the runs and the grading; `docs/science-ultrapowers/evals/README.md` lists them all.

## How to run

Everything:

```
bash tests/claude-code/run-tests.sh
```

One file:

```
bash tests/claude-code/test-version-sync.sh
```

## Requirements

Git Bash, jq, node 22+, Python 3.11+. shellcheck and Graphviz are optional for the tests (shellcheck is needed to run scripts/lint-shell.sh itself).
