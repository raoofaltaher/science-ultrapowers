# PLAN-01: Plugin Shell and Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ultrapowers:subagent-driven-development (recommended) or ultrapowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn a clone of `obra/superpowers` v7.0.2 into the `science-ultrapowers` Claude Code plugin skeleton: one harness, new name, manifests, hooks, the `using-science-ultrapowers` bootstrap, a test runner and a gate that keeps every other harness and every project-specific string out.

**Architecture:** Copy the superpowers tree (minus `.git`) into this repository, delete the non-Claude-Code harness files listed in spec Components "Plugin shell", rewrite the two manifests and `.version-bump.json`, reduce `hooks/session-start` to the Claude Code branch reading the new bootstrap skill, and replace the test suite with three shell tests (bootstrap output, no foreign harness, version sync). Skills other than the bootstrap are only moved or deleted here; their rewrites are PLAN-04.

**Tech Stack:** bash (Git for Windows), `hooks/run-hook.cmd` polyglot wrapper, `jq` (used by `scripts/bump-version.sh`, dev-time only), JSON manifests.

**Spec:** `docs/science-ultrapowers/specs/2026-11-07-science-ultrapowers-design.md` — G1, G2, Constraints, D1, D9, Architecture units 1-2, Components "Plugin shell" and "Bootstrap skill", Testing "Plugin shape" and "Bootstrap".

**Sources:** Claude Code plugin manifest reference (https://code.claude.com/docs/en/plugins/manifest-reference.md, read 2026-11-07: `name` only required field, reserved-name rules, standard layout, `${CLAUDE_PLUGIN_ROOT}`); marketplace reference (https://code.claude.com/docs/en/plugins/marketplace-reference.md: `"source": "./"`, `version` drives updates); hooks reference (https://code.claude.com/docs/en/hooks.md: SessionStart matchers `startup|resume|clear|compact`, `hookSpecificOutput.additionalContext`, 10,000-character cap, Windows `shell` field); plugin components reference (https://code.claude.com/docs/en/plugins/components.md: `hooks/hooks.json` top-level `hooks` key); superpowers v7.0.2 tree read in this session (`hooks/session-start`, `hooks/run-hook.cmd`, `.version-bump.json`, `scripts/bump-version.sh`, `skills/using-superpowers/SKILL.md`). Not checked: none for this plan.

## Global Constraints

- Plugin, marketplace and repository name `science-ultrapowers`; version `0.1.0` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (`plugins[0].source` = `"./"`), kept in sync by `.version-bump.json` and `scripts/bump-version.sh`.
- Licence MIT: keep `LICENSE` with `Copyright (c) 2025 Jesse Vincent`, add the line `Copyright (c) 2026 RAOOF A.` above it.
- Zero runtime dependencies beyond bash, node and Python 3.11+ stdlib; `jq` is accepted for the dev-time `bump-version.sh` only.
- The bootstrap body plus the hook wrapper stays under 9,000 characters.
- No `CLAUDE.md` with instructions at the plugin root. Nothing is written under `${CLAUDE_PLUGIN_ROOT}`.
- No Git LFS in this repository.
- No file contains `superpowers:`, `obra/`, `Jesse Vincent` (except `LICENSE` and the README attribution line), a harness name from the list in Task 6, a drive-letter path of the source machine, the source project's name, `host.`, or `D-00` (except `RELEASE-NOTES.md`; the test scripts, the recorded Claude Science schema and the eval transcripts are exempt because they quote the patterns on purpose; `specs/` and `plans/` are exempt only from the harness-name and removed-skill patterns and are scanned for the project-specific strings).
- Windows first: hooks run through `hooks/run-hook.cmd`; scripts use forward slashes.

## Review Focus

1. The SessionStart hook fires on `clear` and `compact` as well as `startup`; a bootstrap over 10,000 characters is silently truncated to a 2,000-character preview — Task 4's length test pins the cap at 9,000 including the wrapper.
2. `run-hook.cmd` on a machine without Git Bash exits 0 silently; a session then has no bootstrap. Task 5's test asserts the Claude Code JSON shape so a wrong field name is caught where bash exists; README (PLAN-08) states the Git Bash requirement.
3. A manifest `version` left at `7.0.2` in any file makes auto-update skip releases. Task 3's `bump-version.sh --check` test pins all versions to `0.1.0`.
4. A leftover `.codex-plugin` or `gemini-extension.json` makes another harness load half a plugin. Task 6's grep gate fails on any of those names.
5. A skill named with `:` or a non-kebab name fails to load without an error the user sees. Task 6 also asserts every `skills/*/SKILL.md` `name:` matches `^[a-z0-9-]+$` and equals its folder name.

---

### Task 1: Import the superpowers tree

**Files:**
- Create: everything from the superpowers v7.0.2 clone except `.git/`, copied to the repository root
- Modify: none

**Interfaces:**
- Consumes: nothing
- Produces: the superpowers file tree at the repository root (later tasks delete and rewrite parts of it)

- [ ] **Step 1: Clone superpowers at tag v7.0.2 into the scratchpad**

Run: `git clone --depth 1 --branch v7.0.2 https://github.com/obra/superpowers "$SCRATCH/superpowers-v7.0.2"` where `$SCRATCH` is the session scratchpad directory.
Expected: the clone exists and `jq -r .version "$SCRATCH/superpowers-v7.0.2/.claude-plugin/plugin.json"` prints `7.0.2`.

- [ ] **Step 2: Copy the tree without `.git`**

Run, from the repository root: `rsync -a --exclude .git "$SCRATCH/superpowers-v7.0.2/" ./` (or `robocopy` with `/E /XD .git` when rsync is absent).
Expected: `ls` shows `skills/ hooks/ scripts/ docs/ tests/ assets/ .claude-plugin/ LICENSE README.md` beside the existing `specs/` and `plans/`.

- [ ] **Step 3: Record the import**

Run: `git add -A && git commit -m "chore: import obra/superpowers v7.0.2 tree as the template (MIT)"`
Expected: one commit; `git show --stat HEAD | tail -1` shows several hundred files.

### Task 2: Remove every non-Claude-Code harness

**Files:**
- Delete: `.antigravity-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.devin-plugin/`, `.hermes-plugin/`, `.kimi-plugin/`, `.muse-plugin/`, `.opencode/`, `.pi/`, `.agents/`, `gemini-extension.json`, `GEMINI.md`, `index.js`, `package.json`, `hooks/hooks-cursor.json`, `scripts/package-codex-plugin.sh`, `scripts/sync-to-codex-plugin.sh`, `scripts/render-antigravity-logo.sh`, `assets/antigravity-logo.png`, `docs/README.kimi.md`, `docs/README.opencode.md`, `docs/porting-to-a-new-harness.md`, `docs/windows/`, `docs/plans/`, `docs/superpowers/`, `tests/antigravity/`, `tests/brainstorm-server/`, `tests/claude-code/test-sdd-workspace.sh`, `tests/claude-code/test-subagent-driven-development.sh`, `tests/claude-code/test-subagent-driven-development-integration.sh`, `tests/claude-code/test-worktree-native-preference.sh`, `tests/claude-code/test-worktree-path-policy.sh`, `tests/claude-code/test-executing-plans-scripts.sh`, `tests/claude-code/analyze-token-usage.py`, `tests/claude-code/run-skill-tests.sh`
- Delete (skills removed by spec D9): `skills/brainstorming/`, `skills/writing-plans/`, `skills/executing-plans/`, `skills/subagent-driven-development/`, `skills/finishing-a-development-branch/`, `skills/using-git-worktrees/`, `skills/diagnosing-superpowers/`, `skills/using-superpowers/`
- Keep: `skills/writing-skills/`, `skills/test-driven-development/`, `skills/systematic-debugging/`, `skills/verification-before-completion/`, `skills/requesting-code-review/`, `skills/receiving-code-review/`, `skills/dispatching-parallel-agents/` (their text is adapted in PLAN-04)

**Interfaces:**
- Consumes: Task 1 tree
- Produces: a tree whose only harness files are `.claude-plugin/`, `hooks/hooks.json`, `hooks/run-hook.cmd`, `hooks/session-start`

- [ ] **Step 1: Delete the listed paths**

Run: `git rm -r -q <each path above>` for every path that exists.
Expected: `git status --short | grep -c '^D '` is above 150; `ls -a` shows no `.codex-plugin`, `.cursor-plugin`, `.pi`, `.opencode`, `.agents`.

- [ ] **Step 2: Confirm the remaining skills**

Run: `ls skills`
Expected: exactly `dispatching-parallel-agents receiving-code-review requesting-code-review systematic-debugging test-driven-development verification-before-completion writing-skills`.

- [ ] **Step 3: Commit**

Run: `git commit -m "chore: remove every harness except Claude Code and the skills the lab replaces"`

### Task 3: Manifests, version tooling and licence

**Files:**
- Modify: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.version-bump.json`, `LICENSE`, `RELEASE-NOTES.md`, `CODE_OF_CONDUCT.md` (keep), `.pre-commit-config.yaml` (keep)
- Create: `tests/claude-code/test-version-sync.sh`
- Delete: `assets/superpowers-small.svg`, `assets/app-icon.png`

**Interfaces:**
- Produces: `scripts/bump-version.sh --check` as the version gate; `tests/claude-code/test-version-sync.sh` exit 0 on success

- [ ] **Step 1: Write the failing test**

`tests/claude-code/test-version-sync.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
v=$(jq -r .version .claude-plugin/plugin.json)
[ "$v" = "0.1.0" ] || { echo "plugin.json version is $v"; exit 1; }
m=$(jq -r '.plugins[0].version' .claude-plugin/marketplace.json)
[ "$m" = "0.1.0" ] || { echo "marketplace.json version is $m"; exit 1; }
[ "$(jq -r .name .claude-plugin/plugin.json)" = "science-ultrapowers" ] || exit 1
[ "$(jq -r .name .claude-plugin/marketplace.json)" = "science-ultrapowers" ] || exit 1
[ "$(jq -r '.plugins[0].source' .claude-plugin/marketplace.json)" = "./" ] || exit 1
[ "$(jq -r '.files | length' .version-bump.json)" = "2" ] || exit 1
scripts/bump-version.sh --check >/dev/null
echo "version-sync: ok"
```

- [ ] **Step 2: Run it to see it fail**

Run: `bash tests/claude-code/test-version-sync.sh`
Expected: `plugin.json version is 7.0.2`, exit 1.

- [ ] **Step 3: Rewrite the manifests**

`.claude-plugin/plugin.json`:
```json
{
  "name": "science-ultrapowers",
  "description": "A research-lab methodology for Claude Code: fourteen research roles, stage gates G0-G6, a DOI-verified evidence rule, a versioned artifact store and lab memory, with migration from Claude Science",
  "version": "0.1.0",
  "author": { "name": "RAOOF A." },
  "homepage": "https://github.com/raoofaltaher/science-ultrapowers",
  "repository": "https://github.com/raoofaltaher/science-ultrapowers",
  "license": "MIT",
  "keywords": ["research", "science", "skills", "evidence", "pre-registration", "reproducibility", "research-lab", "workflows"]
}
```
`.claude-plugin/marketplace.json`: `name` `science-ultrapowers`, `description` `Marketplace for the science-ultrapowers research-lab plugin`, `owner` `{ "name": "raoofaltaher", "url": "https://github.com/raoofaltaher" }`, one plugin entry with the same `name`, `description`, `version` `0.1.0`, `source` `"./"`, `author` `{ "name": "RAOOF A." }`. Do not add an `agents` key yet (PLAN-05 adds it).

- [ ] **Step 4: Reduce `.version-bump.json`**

`files` holds exactly `{ "path": ".claude-plugin/plugin.json", "field": "version" }` and `{ "path": ".claude-plugin/marketplace.json", "field": "plugins.0.version" }`; `audit.exclude` keeps `RELEASE-NOTES.md`, `.git`, `.version-bump.json`, `scripts/bump-version.sh` and adds `specs`, `plans`, `docs`.

- [ ] **Step 5: Licence, release notes, assets**

`LICENSE`: insert `Copyright (c) 2026 RAOOF A.` on the line above `Copyright (c) 2025 Jesse Vincent`. `RELEASE-NOTES.md`: replace the content with a `# Release notes` heading and a `## 0.1.0 (unreleased)` section containing one line: `Initial release, built from obra/superpowers v7.0.2 (MIT) as the template.` Delete the two superpowers assets (PLAN-08 adds new ones).

- [ ] **Step 6: Run the test**

Run: `bash tests/claude-code/test-version-sync.sh`
Expected: `version-sync: ok`.

- [ ] **Step 7: Commit**

Run: `git add -A && git commit -m "chore: rename to science-ultrapowers 0.1.0, reduce version tooling to the two Claude Code manifests"`

### Task 4: The `using-science-ultrapowers` bootstrap skill

**Files:**
- Create: `skills/using-science-ultrapowers/SKILL.md`
- Test: `tests/claude-code/test-bootstrap-length.sh`

**Interfaces:**
- Produces: the skill the hook injects; the names it cites (`science-ultrapowers:running-the-lab`, `science-ultrapowers:holding-lab-meetings`, `science-ultrapowers:verifying-evidence-by-doi`, `science-ultrapowers:saving-artifacts`, `science-ultrapowers:remembering-for-the-lab`, `science-ultrapowers:initializing-a-research-lab`, `science-ultrapowers:migrating-from-claude-science`) are the skill names PLAN-02 to PLAN-07 must use

- [ ] **Step 1: Write the failing test**

`tests/claude-code/test-bootstrap-length.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
f=skills/using-science-ultrapowers/SKILL.md
[ -f "$f" ] || { echo "missing $f"; exit 1; }
n=$(wc -c < "$f")
[ "$n" -lt 8500 ] || { echo "bootstrap is $n bytes, limit 8500"; exit 1; }
grep -q '^name: using-science-ultrapowers$' "$f" || exit 1
grep -q '^description: Use when starting any conversation' "$f" || exit 1
grep -q 'science-ultrapowers:running-the-lab' "$f" || exit 1
grep -q 'science-ultrapowers:holding-lab-meetings' "$f" || exit 1
grep -q 'science-ultrapowers:verifying-evidence-by-doi' "$f" || exit 1
! grep -qi 'superpowers:' "$f" || exit 1
echo "bootstrap-length: ok"
```

- [ ] **Step 2: Run it to see it fail**

Run: `bash tests/claude-code/test-bootstrap-length.sh`
Expected: `missing skills/using-science-ultrapowers/SKILL.md`, exit 1.

- [ ] **Step 3: Write the skill**

Start from the deleted `skills/using-superpowers/SKILL.md` (recover with `git show HEAD~2:skills/using-superpowers/SKILL.md`). Keep, with `superpowers` → `science-ultrapowers`: the `<SUBAGENT-STOP>` block, the `<EXTREMELY-IMPORTANT>` block, "The Rule", "Red Flags" table, "User Instructions". Replace "Skill Priority" with this lab order, each item one line: `science-ultrapowers:running-the-lab` whenever the user addresses the lab, a role, a gate, a record or a research task; `science-ultrapowers:holding-lab-meetings` at the start and end of a work session; `science-ultrapowers:verifying-evidence-by-doi` whenever a source is cited or a claim is written; `science-ultrapowers:initializing-a-research-lab` when the project has no `research_lab/`; `science-ultrapowers:migrating-from-claude-science` when a Claude Science data directory exists and the lab has not imported it. Remove "Platform Adaptation" and the "Before entering plan mode" line. Add one section "## The lab in one breath" with three lines: facts come only from peer-reviewed, DOI-verified, full-text-read sources on an evidence card; numbers and findings are quoted from the lab records, never retyped; nobody reviews or audits their own work. Frontmatter: `name: using-science-ultrapowers`, `description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions`. Keep "your human partner".

- [ ] **Step 4: Run the test**

Run: `bash tests/claude-code/test-bootstrap-length.sh`
Expected: `bootstrap-length: ok`.

- [ ] **Step 5: Commit**

Run: `git add skills/using-science-ultrapowers tests/claude-code/test-bootstrap-length.sh && git commit -m "feat: add the using-science-ultrapowers bootstrap skill"`

### Task 5: Hooks: session-start for Claude Code only

**Files:**
- Modify: `hooks/session-start`, `hooks/hooks.json`
- Keep: `hooks/run-hook.cmd` unchanged
- Test: `tests/claude-code/test-session-start.sh`

**Interfaces:**
- Produces: `hooks/session-start` printing `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"<EXTREMELY_IMPORTANT>…"}}`; `hooks/hooks.json` with the SessionStart entry (PLAN-03 adds the two memory entries)

- [ ] **Step 1: Write the failing test**

`tests/claude-code/test-session-start.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
out=$(CLAUDE_PLUGIN_ROOT="$PWD" bash hooks/session-start)
echo "$out" | jq -e '.hookSpecificOutput.hookEventName == "SessionStart"' >/dev/null
ctx=$(echo "$out" | jq -r '.hookSpecificOutput.additionalContext')
n=${#ctx}
[ "$n" -lt 9000 ] || { echo "context is $n chars, limit 9000"; exit 1; }
case "$ctx" in *"You have science-ultrapowers."*) ;; *) echo "wrapper text missing"; exit 1;; esac
case "$ctx" in *"name: using-science-ultrapowers"*) ;; *) echo "skill body missing"; exit 1;; esac
echo "$out" | jq -e 'has("additional_context") | not' >/dev/null
jq -e '.hooks.SessionStart[0].matcher == "startup|clear|compact"' hooks/hooks.json >/dev/null
echo "session-start: ok"
```

- [ ] **Step 2: Run it to see it fail**

Run: `bash tests/claude-code/test-session-start.sh`
Expected: fails at `wrapper text missing` (the script still says "You have superpowers.").

- [ ] **Step 3: Edit `hooks/session-start`**

Change `skill_md` to `"${PLUGIN_ROOT}/skills/using-science-ultrapowers/SKILL.md"`, the error string to `Error reading using-science-ultrapowers skill`, and `session_context` to begin `<EXTREMELY_IMPORTANT>\nYou have science-ultrapowers.\n\n**Below is the full content of your 'science-ultrapowers:using-science-ultrapowers' skill - your introduction to using skills. For all other skills, use the 'Skill' tool:**\n\n`. Replace the four-branch `if` at the end with the single Claude Code `emit_json` call (the `hookSpecificOutput` shape). Keep every comment that explains the PATH-independence and EPIPE handling; delete the comments about Cursor, Copilot and Muse.

- [ ] **Step 4: Edit `hooks/hooks.json`**

Keep the single `SessionStart` entry: matcher `startup|clear|compact`, one hook `{"type":"command","command":"\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start","shell":"bash","async":false}`; remove the `powershell` key.

- [ ] **Step 5: Run the test**

Run: `bash tests/claude-code/test-session-start.sh`
Expected: `session-start: ok`.

- [ ] **Step 6: Commit**

Run: `git add hooks tests/claude-code/test-session-start.sh && git commit -m "feat: session-start hook injects the science-ultrapowers bootstrap for Claude Code only"`

### Task 6: The no-foreign-harness and name gate, and the test runner

**Files:**
- Create: `tests/claude-code/test-no-foreign-harness.sh`, `tests/claude-code/run-tests.sh`
- Modify: `tests/claude-code/README.md` (describe the runner), `tests/claude-code/test-helpers.sh` (keep only helpers the new tests use, or delete it if none)
- Modify: `AGENTS.md` (contributor rules), `docs/testing.md`

**Interfaces:**
- Produces: `bash tests/claude-code/run-tests.sh` exits 0 when every `tests/claude-code/test-*.sh` passes and runs `python -m unittest discover -s skills -p "test_*.py" -t .` and `node --test skills` when those exist

- [ ] **Step 1: Write the failing gate test**

`tests/claude-code/test-no-foreign-harness.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
fail=0
# Harness names and template remnants, case-insensitive, outside RELEASE-NOTES.md, LICENSE and the README attribution line.
pat='superpowers:|obra/|codex|cursor|gemini|opencode|hermes|antigravity|devin|kimi|muse|\.pi/'
files=$(git ls-files | grep -v -E '^(RELEASE-NOTES\.md|LICENSE|specs/|plans/|tests/|docs/science-ultrapowers/evals/|docs/science-ultrapowers/claude-science-schema\.md)')
hits=$(echo "$files" | xargs grep -n -i -E "$pat" 2>/dev/null | grep -v 'README.md:.*template' || true)
[ -z "$hits" ] || { echo "$hits"; fail=1; }
# Project-specific and Claude-Science-specific strings.
pat2='<drive-letter paths|the source project names|org and project ids|installer profile paths|host-object calls|decision ids|the funder and dataset names, as the shipped test lists them>'
files2=$(git ls-files | grep -v -E '^(RELEASE-NOTES\.md|LICENSE|tests/|docs/science-ultrapowers/evals/|docs/science-ultrapowers/claude-science-schema\.md)')
hits2=$(echo "$files2" | xargs grep -n -E "$pat2" 2>/dev/null || true)
[ -z "$hits2" ] || { echo "$hits2"; fail=1; }
# Skill names: kebab-case and equal to the folder.
for d in skills/*/; do
  n=$(basename "$d"); nm=$(grep -m1 '^name:' "$d/SKILL.md" | sed 's/^name: *//')
  [ "$nm" = "$n" ] || { echo "skill name mismatch: $d has name '$nm'"; fail=1; }
  echo "$n" | grep -qE '^[a-z0-9-]+$' || { echo "bad skill name: $n"; fail=1; }
done
[ ! -f CLAUDE.md ] || { echo "plugin root CLAUDE.md is not loaded by Claude Code; move instructions into a skill"; fail=1; }
[ "$fail" = 0 ] && echo "no-foreign-harness: ok"
exit $fail
```

- [ ] **Step 2: Run it to see it fail**

Run: `bash tests/claude-code/test-no-foreign-harness.sh`
Expected: hits in `README.md`, `AGENTS.md`, `docs/testing.md`, the kept skills (`superpowers:` cross-references), exit 1.

- [ ] **Step 3: Rewrite `AGENTS.md`, `docs/testing.md`, and stub `README.md`**

`AGENTS.md`: a contributor guide of under 60 lines: what the project is (one paragraph), the rules copied from superpowers that still apply (skills are behaviour-shaping code; no skill edit without a pressure test; one problem per change; "your human partner" is deliberate; zero dependencies; Claude Code is the only harness), how to run the tests (`bash tests/claude-code/run-tests.sh`), and the version-bump rule. `docs/testing.md`: how the three test kinds run. `README.md`: replace the content with a stub `# science-ultrapowers` and one line: `Built from obra/superpowers v7.0.2 (MIT) as the template; see LICENSE.` (PLAN-08 writes the full README; the gate exempts a README line containing "template").

- [ ] **Step 4: Point the kept skills' cross-references at the new namespace**

In the seven kept skills replace every `superpowers:` with `science-ultrapowers:`, and remove the "Personal skills live in …codex-tools.md / gemini-tools.md" sentence in `writing-skills/SKILL.md` (replace with: `Personal skills live in ~/.claude/skills/; plugin skills live in this repository's skills/.`). Content changes beyond that are PLAN-04.

- [ ] **Step 5: Write the runner**

`tests/claude-code/run-tests.sh`:
```bash
#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/../.."
status=0
for t in tests/claude-code/test-*.sh; do bash "$t" || status=1; done
if ls skills/*/scripts/tests/test_*.py >/dev/null 2>&1; then python -m unittest discover -s skills -p "test_*.py" -t . || status=1; fi
if ls skills/*/scripts/tests/*.test.mjs >/dev/null 2>&1; then node --test skills/*/scripts/tests/ || status=1; fi
exit $status
```

- [ ] **Step 6: Run the gate and the runner**

Run: `bash tests/claude-code/test-no-foreign-harness.sh && bash tests/claude-code/run-tests.sh`
Expected: `no-foreign-harness: ok`, then each test's `ok` line, exit 0.

- [ ] **Step 7: Commit**

Run: `git add -A && git commit -m "test: add the no-foreign-harness gate and the test runner; rewrite contributor docs"`

---

## Execution record (2026-11-07)

Executed inline by an Opus 5.5 orchestrator with Haiku/Sonnet implementers per task; final whole-branch review by a fresh Fable 5.1 reviewer (0 Critical, 4 Important, 13 Minor; all fixed, none deferred). Branch `plan-01-plugin-shell`, commits `e3db194..` on top of `e35d41f`. Deviations from the tasks above, each ruled with the spec as authority:

- R1 Work on a branch in this checkout, not a worktree. R2 Copy with `git -c core.autocrlf=false archive | tar -x` (rsync absent; system git has `core.autocrlf=true`).
- R3 Also removed `.github/`, `CODE_OF_CONDUCT.md`, `.pre-commit-config.yaml` and the tests of every removed harness and skill (spec amended, ledger row 20). R4 Kept the upstream tests that guard kept code (`tests/hooks`, `version-bump`, `systematic-debugging`, `writing-skills`, `skill-layout`, `skill-size`, `shell-lint`); the runner globs `tests/*/test-*.sh`. R5 Adapted `tests/hooks/test-session-start.sh` to Claude Code only instead of deleting it.
- R6 `.gitattributes`: `hooks/** text eol=lf`, `*.py text eol=lf`, `.gitattributes text eol=lf`. R7 `.gitignore` tidied in Task 3. R8/R10 The gate also rejects the upstream author and organisation names and any shebang file or hook not 100755 in the index.
- R9 The import lost every executable bit (`core.filemode=false`); restored and guarded. R12 An implementer's `find -depth … -delete` removed empty `.git` directories; restored, `fsck` clean.
- R11 `bump-version.sh` became JSON-only and its test was rewritten. R13 `test-version-sync.sh` takes the expected version from the top `## X.Y.Z` heading of `RELEASE-NOTES.md`. R14 The README stub carries the install commands.
- R15 `test-render-graphs.sh` skips its rendering cases when Graphviz is absent. R16 `test-run-hook-cmd-windows.sh` passes `LOCALAPPDATA` in long form (`cygpath -w -l`): `where.exe` returns long paths, and an 8.3 temp dir made the WindowsApps case fail. R17 The hooks.json `powershell` key and its test were removed (a VS Code Copilot workaround).
- R19 Python tests run per directory without `-t`; node tests by file list (later plans updated). R20 `tests/claude-code/test-helpers.sh` deleted; `test-lint-shell.sh` made executable.
- Final review additions: hook exec-bit check, removed-skill names and case-sensitive product names in the gate, NUL-safe scan, two bootstrap lines (research_lab/ is the lab; how the team is addressed), a Windows test for a plugin root with a space, python3 fallback in the runner, `.claude-plugin/icon.png` (512×512).
