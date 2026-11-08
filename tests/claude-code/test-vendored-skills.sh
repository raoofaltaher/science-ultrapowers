#!/usr/bin/env bash
# Two lists of adopted skills with an addendum: NAMES (the fourteen adopted before 0.2.0) and NAMES_0_2 (adopted in 0.2.0):
# shape, lab addendum, cleanliness, provenance hashes.
# The one adopted skill copied verbatim (typesafe-ai, no addendum): shape, cleanliness, provenance hashes.
set -euo pipefail
cd "$(dirname "$0")/../.."

NAMES="peer-review scientific-writing hypothesis-generation scientific-critical-thinking scholar-evaluation pptx-posters debugging implementation-planning pr-review-toolkit paper-review figure-qa svg-primitives figure-bible manuscript-formatting"
NAMES_0_2="investigating-anomalous-results establishing-feasibility-first"
VERBATIM="typesafe-ai"

fail() { echo "vendored-skills: $1: $2" >&2; exit 1; }

# The repository patterns (same as the repository gate plus the repository rules not yet in it).
repo_patterns_ci='superpowers:|obra/|codex|gemini|opencode|hermes|antigravity|kimi|\.pi/|jesse vincent|prime radiant|subagent-driven|writing-plans|executing-plans|using-superpowers|using-git-worktrees|finishing-a-development-branch|diagnosing-superpowers|:brainstorming\b|/brainstorming\b|brainstorming skill|copilot|claude science|\.claude/skills'
repo_patterns_cs='\bCursor\b|\bMuse\b|\bDevin\b|CURSOR_|MUSE_|DEVIN_|Z:[\\]|Z:/|host\.(skills|artifacts|lineage|agents|query|mcp)|(^|[^A-Za-z])D-00[0-9][0-9]|RV-00[0-9]+|doi-verified-evidence|research-lab-workflow|findings-ledger|reference-access-request|jev-decisions|pdf-explore|kernel\.py'
old_names='doi-verified-evidence|findings-ledger|research-lab-workflow|reference-access-request|jev-decisions'
# Owner-specific strings come from tests/private-strings.txt (git-ignored; see tests/private-strings.example).
if [ -f tests/private-strings.txt ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    line=${line%$'\r'}
    case "$line" in ''|'#'*) continue ;; esac
    repo_patterns_cs="$repo_patterns_cs|$line"
  done < tests/private-strings.txt
fi

# repo_scan FILE: print the lines of FILE the repository rules reject.
repo_scan() {
  grep -n -H -i -E "$repo_patterns_ci" "$1" 2>/dev/null || true
  grep -n -H -E "$repo_patterns_cs" "$1" 2>/dev/null || true
}

# check_hash_table NAME DIR: every hash-table row of DIR/PROVENANCE.md whose status is not
# "removed" names an existing file whose SHA-256 (first 12 hex) matches its Vendored column.
# Sets skill_modified=1 when SKILL.md is listed as modified.
# Rows: | `path` | status | `upstream` | `vendored` |
check_hash_table() {
  local name=$1 dir=$2 rows=0 line path status vendored actual
  skill_modified=0
  while IFS= read -r line; do
    path=$(printf '%s\n' "$line" | awk -F'|' '{gsub(/[ `]/,"",$2); print $2}')
    status=$(printf '%s\n' "$line" | awk -F'|' '{gsub(/[ `]/,"",$3); print $3}')
    vendored=$(printf '%s\n' "$line" | awk -F'|' '{gsub(/[ `]/,"",$5); print $5}')
    rows=$((rows + 1))
    if [ "$path" = "SKILL.md" ] && [ "$status" = "modified" ]; then skill_modified=1; fi
    if [ "$status" != "removed" ]; then
      [ -f "$dir/$path" ] || fail "$name" "PROVENANCE.md lists $path but the file is missing"
      actual=$(sha256sum "$dir/$path" | cut -c1-12)
      [ "$actual" = "$vendored" ] || fail "$name" "hash of $path is $actual, PROVENANCE.md says $vendored"
    fi
  done < <(grep -E '^\| `[^`]+` \| [a-z]+ \| ' "$dir/PROVENANCE.md")
  [ "$rows" -gt 0 ] || fail "$name" "PROVENANCE.md hash table has no rows"
}

for name in $NAMES $NAMES_0_2 $VERBATIM; do
  dir="skills/$name"
  overlaid=1; case " $VERBATIM " in *" $name "*) overlaid=0 ;; esac
  [ -d "$dir" ] || fail "$name" "missing folder $dir"
  for f in SKILL.md LICENSE PROVENANCE.md; do
    [ -f "$dir/$f" ] || fail "$name" "missing $f"
  done
  if [ -n "$(find "$dir" -name __pycache__ -type d -print -quit)" ]; then fail "$name" "contains a __pycache__ folder"; fi
  if [ -n "$(find "$dir" -name '*.pyc' -print -quit)" ]; then fail "$name" "contains a .pyc file"; fi

  skill="$dir/SKILL.md"
  if [ "$overlaid" = 1 ]; then
    grep -qF 'LAB ADDENDUM (binding)' "$skill" || fail "$name" "SKILL.md lacks 'LAB ADDENDUM (binding)'"
    ! grep -qF 'LAB OVERLAY' "$skill" || fail "$name" "SKILL.md still says LAB OVERLAY"
    grep -qF "Where anything below conflicts with the lab's rules, the lab's rules win." "$skill" \
      || fail "$name" "SKILL.md lacks the conflict line"
  fi

  if grep -n -E 'host\.|\brepl\b|pdf-explore|Claude Science|kernel\.py|analysis kernel|\.claude/skills/|doi-verified-evidence|findings-ledger|research-lab-workflow|AFN-UPF|(^|[^A-Za-z])D-00[0-9][0-9]' "$skill"; then
    fail "$name" "SKILL.md still carries Claude-Science or project strings (lines above)"
  fi

  # No stage code (G0 to G6) anywhere in an adopted SKILL.md; the stages have names.
  if grep -n -E '\bG[0-6]\b' "$skill"; then
    fail "$name" "SKILL.md names a stage code (lines above)"
  fi

  prov="$dir/PROVENANCE.md"
  if [ "$overlaid" = 1 ]; then
    grep -qF '**Tools in Claude Code:**' "$skill" || fail "$name" "SKILL.md lacks the Tools in Claude Code item"
    grep -qF "\${CLAUDE_PLUGIN_ROOT}/skills/$name/" "$skill" \
      || fail "$name" "SKILL.md lacks \${CLAUDE_PLUGIN_ROOT}/skills/$name/"
    case " $NAMES_0_2 " in
      *" $name "*) ;;
      *) grep -E '^- 2026-11-07 science-ultrapowers:.*Claude-Science-only overlay items removed' "$prov" >/dev/null \
           || fail "$name" "PROVENANCE.md lacks the 2026-11-07 overlay-removal line" ;;
    esac
    grep -E '^- 2026-11-08 science-ultrapowers:.*LAB ADDENDUM' "$prov" >/dev/null \
      || fail "$name" "PROVENANCE.md lacks the 2026-11-08 addendum line"
  fi

  check_hash_table "$name" "$dir"
  [ "$skill_modified" -eq 1 ] || fail "$name" "PROVENANCE.md does not list SKILL.md as modified"

  # Repository patterns over every text file (LICENSE and binaries excepted).
  while IFS= read -r f; do
    if [ "$(basename "$f")" = "PROVENANCE.md" ]; then
      # a hit line is allowed only if every pattern match on it is a historical old skill name
      hits=$(repo_scan "$f" | while IFS= read -r l; do
        stripped=$(printf '%s\n' "$l" | sed -E "s/($old_names)//g")
        if printf '%s\n' "$stripped" | cut -d: -f3- | grep -q -i -E "$repo_patterns_ci" \
          || printf '%s\n' "$stripped" | cut -d: -f3- | grep -q -E "$repo_patterns_cs"; then
          printf '%s\n' "$l"
        fi
      done)
    else
      hits=$(repo_scan "$f")
    fi
    if [ -n "$hits" ]; then
      printf '%s\n' "$hits" >&2
      fail "$name" "repository patterns match in $f (lines above)"
    fi
  done < <(find "$dir" -type f ! -name LICENSE ! -name '*.png' ! -name '*.jpg' ! -name '*.jpeg' ! -name '*.gif' ! -name '*.pdf' ! -name '*.ttf' ! -name '*.otf' ! -name '*.woff*' ! -name '*.pptx' ! -name '*.docx' ! -name '*.xlsx')
done

# Skills copied verbatim, with no lab addendum: their files and provenance hashes only.
VERBATIM="typesafe-ai"
for name in $VERBATIM; do
  dir="skills/$name"
  for f in SKILL.md LICENSE PROVENANCE.md; do
    [ -f "$dir/$f" ] || fail "$name" "missing $f"
  done
  check_hash_table "$name" "$dir"
done

echo "vendored-skills: ok"
