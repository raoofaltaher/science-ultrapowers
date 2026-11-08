# Release notes

## 0.1.1 (2026-11-08)

- `running-the-lab` and `saving-artifacts`: a "what is this deliverable based on" question runs `search`, then `lineage` by version id and `check list`; a grep of the ledgers by artifact id proves nothing, because the rows are keyed by version id (found by acceptance scenario 3 of 0.1.0).
- The leak gate follows the design documents to `docs/science-ultrapowers/specs/` and `plans/`.
- The acceptance transcripts of 0.1.0 under `docs/science-ultrapowers/evals/acceptance/`.

## 0.1.0 (2026-11-08)

Initial release, built from obra/superpowers v7.0.2 (MIT) as the template.

- Plugin shell and hooks: the template cut to Claude Code, renamed, with both manifests, the session bootstrap, the cross-platform hook runner and the test runner.
- Artifact store: the `saving-artifacts` skill and `artifacts.py` (save, link, search, path, lineage, graph, check, mark-addressed, resolve, lfs-check) for a versioned, linked artifact store.
- Memory store: the `remembering-for-the-lab` skill, `memory-lint.mjs`, and the nudge and post-compaction hooks.
- Lab skills: `running-the-lab`, `holding-lab-meetings`, `verifying-evidence-by-doi`, `recording-findings`, `requesting-reference-access`, `deciding-with-jev`, `searching-the-literature` and `planning-paper-figures`, each with a pressure test.
- Fourteen agents: the research roles, from the lab project manager and the literature researcher to the paper author and the reviewers, with one G3 definition and the Auditor's gates.
- Init: `initializing-a-research-lab` and `init_lab.py`, the project templates, `connectors.json`, `setup_lab_env.ps1` and the opt-in project permission rules.
- Migrate: `migrating-from-claude-science`, the recorded Claude Science schema and `migrate_claude_science.py`, with `PERMISSIONS.md` and `SKILLS.md` output, fixture tests and a dry run on a database copy.
- Vendored skills with overlays: the kept third-party skills, each with a cleaned overlay and `python -B` in the vendored scripts.
- Tests and gates: `tests/claude-code/run-tests.sh` runs every shell, Python and node test, and the no-foreign-harness gate checks the plugin for project-specific strings, other harness names, executable bits and Git LFS.
- Pre-release review: the review findings are closed, the design documents are sanitised, the leak gates scan them, and a private-strings gate checks for owner-specific strings kept out of the repository.
