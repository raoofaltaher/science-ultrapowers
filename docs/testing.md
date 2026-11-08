# Testing science-ultrapowers

There are three kinds of tests.

## 1. Shell tests: `tests/<area>/test-*.sh`

- `tests/claude-code/`: plugin shape. Version sync across manifests, session primer size, session-start output, the disclosure check (`test-no-foreign-harness.sh`), the terminology test (`test-terminology.sh`, below), the lab templates (`test-lab-templates.sh`), the lab-memory hooks (`test-memory-hooks.sh`: reminder and post-compaction, silent without lab memory, junctions, a closed stdout), the skill content (`test-skill-content.sh`: no old skill names, trigger-only descriptions, the load-bearing sentences in the skill that owns each, bare script and skill names, cross-references that resolve), the adopted skills (`test-vendored-skills.sh`: the lab addendum, cleanliness, provenance hashes), the agent contract (`test-agents.sh`: frontmatter shape, preloaded skills that exist, the fourteen ids and the manifest list, `Agent` disallowed for the twelve, the `When to invoke` section, the `Contributor Roles Taxonomy (CRediT)` section with its exact line for each role, and the lead-session line of `running-the-lab`), the repository documents (`test-repo-documents.sh`: README sections, the credit line, the license, the community files, the terminology standard and the output style file, the self-contained banner SVG, the release notes, the manifest license field, the ignore rules, the workflow permissions block), the environment script's dry run (`test-setup-env-dryrun.sh`: `setup_lab_env.ps1 -DryRun` under `pwsh -NonInteractive` writes nothing and asks nothing; skipped when pwsh is absent); also `run-tests.sh`, the runner itself.
  - `test-terminology.sh` keeps the plugin's own text to `docs/science-ultrapowers/terminology.md`. It scans the thirteen lab skills, the addenda of the adopted skills, the agents, the lab templates, the four documents (`README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `docs/testing.md`), the hooks, the string constants of the lab scripts, and the lifecycle design and plan. It reads three lists from the standard, each in the fenced block after its marker comment: the not-approved terms, the British spellings and the abbreviations. It refuses a not-approved term, a stage code, a British spelling, and an abbreviation that is not expanded at its first use in a file. `tests/terminology-allow.txt` lists the paths still to be renamed; a listed path with no remaining hit fails the test. A line that ends with `<!-- legacy -->`, `# legacy` or `// legacy` is skipped. A positive control feeds the matcher four known violations and fails if it misses one. `--list` prints the scanned files and exits. `TERMINOLOGY_STANDARD` and `TERMINOLOGY_ALLOW` override the two paths, which the test of the test uses.
  - `test-lab-templates.sh` checks the template tree: the new folders and files exist and the old ones do not, the table headers and the status words are the standard's, the hypothesis record has its fields, `lab.json` has its keys, and no template holds a stage code or a not-approved word.
- `tests/hooks/`: session-start behavior, including an empty PATH, a closed stdout and no forks, a plugin root with a space; `run-hook.cmd` on Windows.
- `tests/version-bump/`: `scripts/bump-version.sh`.
- `tests/shell-lint/`: `scripts/lint-shell.sh` (the test stubs shellcheck; the script itself needs it).
- `tests/skill-layout/`: no development files inside skills.
- `tests/skill-size/`: every SKILL.md is under 20,000 bytes.
- `tests/systematic-debugging/`: `find-polluter.sh`.
- `tests/writing-skills/`: `render-graphs.js`; the rendering cases skip without Graphviz.

## 2. Python unittest: `skills/<skill>/scripts/tests/test_*.py`

`skills/saving-artifacts/scripts/tests/` (the artifact archive, `artifacts.py`: `save --task`, `provenance`, `findings add | list | review`, `respond`; `test_terminology_rename.py` checks that each new name works, that the 0.1 verbs stay as hidden aliases, that legacy values are read and reported with the new word, and that a lab in the 0.1 layout exits 2 with the migration message), `skills/verifying-evidence-by-doi/scripts/tests/` (`verify_doi.py`), `skills/deciding-with-jev/scripts/tests/` (`jev_ask.py`, offline), `skills/searching-the-literature/scripts/tests/` (`search_openalex.py`, offline), `skills/initializing-a-research-lab/scripts/tests/` (`init_lab.py`: a fresh folder, an existing project, connectors, permissions, restricted folders; `test_init_migration.py` runs a lab in the 0.1 layout through the shown plan, the renames, the header and status-word rewrites, the archive patterns in `.gitattributes`, the `lab.json` keys and the hand copies of old role ids, and checks that a second run changes nothing; `test_init_output_style.py` checks that the Scholarly Explanatory style is installed, never overwritten and also installed in a migrated lab; each test runs the script in a temp folder), `skills/migrating-from-claude-science/scripts/tests/` (`migrate_claude_science.py` against a fixture database built from the CREATE TABLE statements recorded in `docs/science-ultrapowers/claude-science-schema.md`; the real database is used only by the dry run recorded in `docs/science-ultrapowers/evals/migration-dry-run.md`). The runner discovers them per directory. `skills/svg-primitives/tests/` is the adopted upstream pytest suite, not run by the lab runner.

## 3. Node tests: `skills/<skill>/scripts/tests/*.test.mjs`

`skills/remembering-for-the-lab/scripts/tests/memory-lint.test.mjs` (the lab-memory consistency check). Run with `node --test`.

## Behavior tests for skills

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
