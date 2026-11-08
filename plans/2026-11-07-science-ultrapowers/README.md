# science-ultrapowers Implementation Plan Set

> **For agentic workers:** REQUIRED SUB-SKILL: Use ultrapowers:subagent-driven-development (recommended) or ultrapowers:executing-plans to implement these plans task-by-task, in the order below. Steps use checkbox (`- [ ]`) syntax for tracking.

**Spec:** `specs/2026-11-07-science-ultrapowers-design.md` (approved 2026-11-07). Every plan argues from it; read the spec first.

**Why a set:** the spec names seven independently testable units (plugin shell and bootstrap, lab skills, agents, artifact store, memory store, `init`, `migrate`) plus a release gate. Each plan below produces working, tested software on its own; later plans consume the earlier ones' interfaces, named in each plan's Interfaces blocks.

| # | Plan | Produces | Depends on |
|---|---|---|---|
| 01 | [PLAN-01-plugin-shell.md](PLAN-01-plugin-shell.md) | The superpowers clone cut to Claude Code, renamed, with manifests, hooks, the `using-science-ultrapowers` bootstrap, the test runner and the no-foreign-harness gate | nothing |
| 02 | [PLAN-02-artifact-store.md](PLAN-02-artifact-store.md) | `saving-artifacts` skill and `artifacts.py` (save, link, search, path, lineage, graph, check, mark-addressed, resolve, lfs-check) | 01 |
| 03 | [PLAN-03-memory-store.md](PLAN-03-memory-store.md) | `remembering-for-the-lab` skill, `memory-lint.mjs`, the nudge and post-compaction hooks | 01 |
| 04 | [PLAN-04-lab-skills.md](PLAN-04-lab-skills.md) | The rewritten lab skills (`running-the-lab`, `holding-lab-meetings`, `verifying-evidence-by-doi`, `recording-findings`, `requesting-reference-access`, `deciding-with-jev`, `searching-the-literature`, `planning-paper-figures`), the vendored third-party skills with cleaned overlays, the kept superpowers skills, and the pressure tests | 01, 02, 03 |
| 05 | [PLAN-05-agents.md](PLAN-05-agents.md) | The 14 role agents | 04 |
| 06 | [PLAN-06-init.md](PLAN-06-init.md) | `initializing-a-research-lab`, `init_lab.py`, the project templates, `connectors.json`, `setup_lab_env.ps1`, the opt-in project permission rules | 02, 03, 04 |
| 07 | [PLAN-07-migrate.md](PLAN-07-migrate.md) | `migrating-from-claude-science`, the recorded Claude Science schema, `migrate_claude_science.py` (incl. `PERMISSIONS.md` and `SKILLS.md`), fixture tests, the dry run on the source-project database copy | 02, 03, 06 |
| 08 | [PLAN-08-release.md](PLAN-08-release.md) | README, release notes, `claude plugin validate`, the private GitHub repository, the marketplace install test, the three acceptance transcripts | all |

**Conventions shared by every plan**

- Repository root: `<repo>` (git, branch `main`). Commands are written for Git Bash on Windows; `python` is CPython 3.11+ (3.13 is installed), `node` 22+, `git` 2.4x, `git-lfs` 3.8.
- Tests: shell tests under `tests/<area>/test-*.sh`; Python tests are stdlib `unittest` files named `test_*.py` under each `skills/<skill>/scripts/tests/`, run per directory with `python -m unittest discover -s skills/<skill>/scripts/tests -p "test_*.py"` (no `-t`: hyphenated skill folders are not importable packages, so the test modules put their `scripts/` folder on `sys.path` themselves); node tests are `skills/<skill>/scripts/tests/*.test.mjs`, run with `node --test <files>`. `bash tests/claude-code/run-tests.sh` runs all three kinds and is every plan's final gate.
- Windows (learned in PLAN-01): git records new files as 100644 here, so every new script or hook is staged with `git add --chmod=+x` (the gate fails a shebang file or hook without it); `.gitattributes` keeps hooks, scripts and Markdown LF; call `python`, not `python3` (which can be the Windows Store stub); never `find … -delete` near the repository root; edit text containing backslashes with a file editor, not `sed`.
- The gate `tests/claude-code/test-no-foreign-harness.sh` also rejects names of the skills PLAN-01 removed (`subagent-driven…`, `writing-plans`, `executing-plans`, `using-git-worktrees`, `finishing-a-development-branch`, `diagnosing-superpowers`, `using-superpowers`, the brainstorming skill) and the product names `Cursor`, `Muse`, `Devin` as capitalised words.
- Commit messages: imperative subject, body optional, and the trailer lines the session requires (the author line and a `Claude-Session:` link).
- "Spec §X" references point into `specs/2026-11-07-science-ultrapowers-design.md`.
- Nothing in the plugin repository may contain a path of the source project's machine, the source project's name, a Claude Science `host.` call, a decision id (`D-00xx`) outside `RELEASE-NOTES.md`, or a secret. PLAN-01 Task 6 installs the test that enforces this.
