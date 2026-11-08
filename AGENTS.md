# science-ultrapowers — contributor guide

science-ultrapowers is a research-lab methodology for Claude Code: fourteen research roles, stage gates G0-G6, a DOI-verified evidence rule, a versioned artifact store and lab memory, with migration from Claude Science. Claude Code is the only supported harness.

## Skills are code

- Skills shape agent behaviour. Iron Laws, rationalization tables and red-flag lists are deliberate devices, not decoration.
- A skill's `description` says only when to use it ("Use when..."), never its workflow.
- No new or changed skill without a pressure test, as `science-ultrapowers:writing-skills` describes.
- Keep "your human partner": it is deliberate terminology.
- Cross-reference skills as `science-ultrapowers:<skill>`, never with `@` links.
- Skills name actions, not tool names.

## What the plugin may contain

- Runtime dependencies are bash (Git for Windows on Windows), node 22+ and the Python 3.11+ standard library only. No pip packages.
- Nothing project-specific (no research-project paths, no decision ids) and nothing Claude-Science-specific.
- No `CLAUDE.md` at the repository root. Claude Code does not load it from a plugin; instructions live in skills.
- Nothing is ever written under `${CLAUDE_PLUGIN_ROOT}`.
- No Git LFS in this repository.
- `tests/claude-code/test-no-foreign-harness.sh` enforces these rules: no project-specific or Claude-Science-specific string (the design documents under `docs/science-ultrapowers/specs/` and `plans/` included), no other harness name or template remnant, no root `CLAUDE.md`, an executable bit on every script and hook in the index, and no Git LFS attribute. The runtime-dependency rule and the rule against writing under `${CLAUDE_PLUGIN_ROOT}` are reviewed by hand.

## Windows

- Git records new files as 100644 here, so stage every script with `git add --chmod=+x`.
- `.gitattributes` keeps hooks and scripts LF.
- Hooks run through `hooks/run-hook.cmd`.

## Testing

`bash tests/claude-code/run-tests.sh` runs every test. See docs/testing.md.

## Releasing

- `scripts/bump-version.sh <version>` updates both manifests.
- Add a `## <version>` heading at the top of RELEASE-NOTES.md; `tests/claude-code/test-version-sync.sh` checks the manifests against it.
- `scripts/bump-version.sh --check` reports drift.

## Changes

One problem per change.
