# tests/claude-code

Plugin-shape tests, run from the repository root with bash.

- `test-version-sync.sh`: both manifests and the top RELEASE-NOTES.md heading agree on the version.
- `test-bootstrap-length.sh`: the using-science-ultrapowers bootstrap stays within its size budget.
- `test-session-start.sh`: the session-start hook injects the bootstrap for Claude Code only.
- `test-no-foreign-harness.sh`: no other harness, template remnant, project-specific string (specs/ and plans/ included, with a positive control), bad skill name, root CLAUDE.md, Git LFS attribute or non-executable script.
- `test-skill-content.sh`: no old skill names, trigger-only descriptions, the load-bearing sentences in the skill that owns each, bare script and skill names, cross-references that resolve.
- `test-vendored-skills.sh`: the vendored skills' overlay, cleanliness and provenance hashes.
- `test-agents.sh`: the agent contract: frontmatter shape, preloaded skills that exist, `Agent` disallowed for the twelve, the `When to invoke` section, the manifest list.
- `test-setup-env-dryrun.sh`: `setup_lab_env.ps1 -DryRun` under `pwsh -NonInteractive` writes nothing and asks nothing; skipped when pwsh is absent.
- `test-memory-hooks.sh`: the lab-memory nudge and post-compaction hooks: their JSON, the store path from a nested or junctioned cwd, silence without a store or for other session sources, the off switch, the wrapper, a closed stdout, and that they never write.
- `run-tests.sh`: the runner. It runs every shell, Python and node test in the repository and exits 0 only when all pass.

Run everything with `bash tests/claude-code/run-tests.sh`. `docs/testing.md` describes every kind of test in the repository.
