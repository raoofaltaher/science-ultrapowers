# tests/claude-code

Plugin-shape tests, run from the repository root with bash.

- `test-version-sync.sh`: both manifests and the top RELEASE-NOTES.md heading agree on the version.
- `test-bootstrap-length.sh`: the using-science-ultrapowers session primer stays within its size budget.
- `test-session-start.sh`: the session-start hook injects the session primer for Claude Code only.
- `test-no-foreign-harness.sh`: the disclosure check. No other harness, template remnant, project-specific string (the design documents under docs/science-ultrapowers/ included, with a positive control), bad skill name, root CLAUDE.md, Git Large File Storage (LFS) attribute or non-executable script.
- `test-terminology.sh`: the plugin's own text keeps to `docs/science-ultrapowers/terminology.md`. It scans the thirteen lab skills, the addenda of the adopted skills, the agents, the lab templates, the four documents, the hooks, the string constants of the lab scripts, and the lifecycle design and plan. It reads three lists from the standard (the not-approved terms, the British spellings, the abbreviations) and refuses a not-approved term, a stage code, a British spelling and an abbreviation not expanded at its first use in a file. `tests/terminology-allow.txt` lists the paths still to be renamed. A line that ends with `<!-- legacy -->`, `# legacy` or `// legacy` is skipped. A positive control proves the matcher. `--list` prints the scanned files. `TERMINOLOGY_STANDARD` and `TERMINOLOGY_ALLOW` override the two paths.
- `test-lab-templates.sh`: the template tree (the new folders and files exist, the old ones do not), the table headers, the status words, the hypothesis record's fields and the `lab.json` keys, with no stage code or not-approved word in any template.
- `test-skill-content.sh`: no old skill names, trigger-only descriptions, the load-bearing sentences in the skill that owns each, bare script and skill names, cross-references that resolve.
- `test-vendored-skills.sh`: the adopted skills' lab addendum, cleanliness and provenance hashes.
- `test-agents.sh`: the agent contract: frontmatter shape, preloaded skills that exist, the fourteen ids, `Agent` disallowed for the twelve, the `When to invoke` section, the `Contributor Roles Taxonomy (CRediT)` section with its exact line for each role, the manifest list, and the lead-session line of `running-the-lab`.
- `test-repo-documents.sh`: the README sections, the credit line, the license, the community files, the terminology standard and the output style file, the banner SVG, the release notes and the ignore rules.
- `test-setup-env-dryrun.sh`: `setup_lab_env.ps1 -DryRun` under `pwsh -NonInteractive` writes nothing and asks nothing; skipped when pwsh is absent.
- `test-memory-hooks.sh`: the lab-memory reminder and post-compaction hooks: their JSON, the lab memory path from a nested or junctioned cwd, silence without lab memory or for other session sources, the off switch, the wrapper, a closed stdout, and that they never write.
- `run-tests.sh`: the runner. It runs every shell, Python and node test in the repository and exits 0 only when all pass.

Run everything with `bash tests/claude-code/run-tests.sh`. `docs/testing.md` describes every kind of test in the repository.
