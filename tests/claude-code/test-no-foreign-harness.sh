#!/usr/bin/env bash
# The plugin carries no other harness, no template remnant, no removed skill,
# no project-specific or Claude-Science-specific string (the design documents
# under docs/science-ultrapowers/specs/ and plans/ are scanned too), valid skill names, no root CLAUDE.md, no Git LFS attribute, and
# an executable bit on every script and hook.
set -euo pipefail
cd "$(dirname "$0")/../.."
fail=0
# The private-string scan covers the design documents and the reading records. The
# harness and removed-skill scans leave them out: the design documents name the other harnesses and the
# removed skills on purpose, as non-goals and as history.
exempt='^(RELEASE-NOTES\.md|LICENSE|skills/[^/]+/LICENSE$|tests/|docs/science-ultrapowers/evals/|docs/science-ultrapowers/claude-science-schema\.md)'
exempt_design='^(RELEASE-NOTES\.md|LICENSE|skills/[^/]+/LICENSE$|docs/science-ultrapowers/specs/|docs/science-ultrapowers/plans/|docs/science-ultrapowers/research/|tests/|docs/science-ultrapowers/evals/|docs/science-ultrapowers/claude-science-schema\.md)'
ex="$exempt_design"
# scan FLAGS PATTERN: matching lines of every non-exempt tracked file (NUL-safe).
scan() {
  git ls-files -z | grep -z -v -E "$ex" | xargs -0 grep -n -H $1 -E "$2" -- || true
}
report() { [ -z "$2" ] || { echo "$1:"; echo "$2"; fail=1; }; }
# The one allowed mention of the template: the README credit line.
credit='^README\.md:[0-9]+:Built from obra/superpowers v7\.0\.2 \(MIT\) as the template'
# Other harnesses and template remnants (unambiguous tokens, any case).
report "other harness or template remnant" "$(scan -i 'superpowers:|obra/|codex|gemini|opencode|hermes|antigravity|kimi|\.pi/|jesse vincent|prime radiant|primeradiant' | grep -v -E "$credit" || true)"
# Product names that are also English words: match the product spelling only.
report "other harness product name" "$(scan '' '\bCursor\b|\bMuse\b|\bDevin\b|\.cursor-plugin|\.muse-plugin|\.devin-plugin|CURSOR_|MUSE_|DEVIN_')"
# Skills this plugin removed.
report "removed skill named" "$(scan -i 'subagent-driven|writing-plans|executing-plans|using-superpowers|using-git-worktrees|finishing-a-development-branch|diagnosing-superpowers|:brainstorming\b|/brainstorming\b|brainstorming skill')"
# Generic private patterns: a path on any drive but C: (C: system paths such as
# Program Files, Windows and a user profile are legitimate; a profile name is an
# owner-specific string for the private file), host-object calls, decision ids.
private='(^|[^A-Za-z0-9_<>])[A-BD-Zabd-z]:[\\/]|host\.(skills|artifacts|lineage|agents|query|mcp)|(^|[^A-Za-z])D-00[0-9][0-9]'
planted_private=('S:\x' 'D:/x' 'host.skills.read' 'D-0011')
# Owner-specific strings (project, dataset, funder, ids, profile paths) live in
# tests/private-strings.txt, git-ignored, one extended-regex alternative per line
# (tests/private-strings.example shows the form). Without the file the gate scans
# the generic patterns only and says so.
private_file="tests/private-strings.txt"
if [ -f "$private_file" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    line=${line%$'\r'}
    case "$line" in ''|'#'*) continue ;; esac
    private="$private|$line"
    planted_private+=("$line")
  done < "$private_file"
else
  echo "no-foreign-harness: tests/private-strings.txt absent; scanning the generic private patterns only"
fi
# Positive control: a planted line for every alternative must match the pattern,
# or the scan below proves nothing.
for planted in "${planted_private[@]}"; do
  sample=$(printf '%s' "$planted" | sed -E 's/\[([^]])[^]]*\]/\1/g')
  printf '%s\n' "planted $sample line" | grep -q -E "$private" || { echo "positive control: the private-string pattern does not match '$planted'"; fail=1; }
done
ex="$exempt"
report "project- or Claude-Science-specific string" "$(scan '' "$private")"
# The plugin repository uses no Git LFS.
lfs_hits=$(git ls-files -z -- '.gitattributes' '**/.gitattributes' | xargs -0 -r grep -n -H 'filter=lfs' -- || true)
report "Git LFS attribute (this repository uses no LFS)" "$lfs_hits"
# Skill names: a SKILL.md exists, its name is kebab-case and equals the folder.
for d in skills/*/; do
  n=$(basename "$d")
  [ -f "$d/SKILL.md" ] || { echo "missing $d/SKILL.md"; fail=1; continue; }
  nm=$(grep -m1 '^name:' "$d/SKILL.md" | sed 's/^name: *//' || true)
  [ "$nm" = "$n" ] || { echo "skill name mismatch: $d has name '$nm'"; fail=1; }
  echo "$n" | grep -qE '^[a-z0-9-]+$' || { echo "bad skill name: $n"; fail=1; }
done
[ ! -f CLAUDE.md ] || { echo "plugin root CLAUDE.md is not loaded by Claude Code; move instructions into a skill"; fail=1; }
# Executable bits in the index (core.filemode=false on Windows records new
# files as 100644): every shebang file, and every hook file except JSON
# (hooks/run-hook.cmd starts with ': <<' and has no shebang).
while read -r mode _ _ path; do
  [ "$mode" = 100755 ] && continue
  case "$path" in hooks/*.json) ;; hooks/*) echo "hook not executable in the index: $path"; fail=1; continue ;; esac
  [ "$(head -c2 "$path" 2>/dev/null)" = '#!' ] && { echo "not executable in the index: $path"; fail=1; }
done < <(git ls-files -s)
[ "$fail" = 0 ] && echo "no-foreign-harness: ok"
exit $fail
