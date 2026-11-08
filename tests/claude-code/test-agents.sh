#!/usr/bin/env bash
# Agent contract test: every agents/*.md has the plugin-agent shape, and plugin.json lists them.
# Usage: test-agents.sh [agents/a.md ...]   (with file arguments the manifest check is skipped)
set -euo pipefail
cd "$(dirname "$0")/../.."
export LC_ALL=C

fail() {
  echo "agents: $1"
  exit 1
}

COMMON=(
  "science-ultrapowers:running-the-lab"
  "science-ultrapowers:verifying-evidence-by-doi"
  "science-ultrapowers:saving-artifacts"
  "science-ultrapowers:remembering-for-the-lab"
)
COLORS=" red blue green yellow purple orange pink cyan "
TOOLKIT_ROLES=" academic-supervisor methods-innovation-researcher data-evaluation-researcher lab-experiments-lead documentation-writer academic-paper-author academic-reviewer scientific-peer-reviewer research-engineer "
NEW_IDS=(research-project-manager academic-supervisor literature-researcher methods-innovation-researcher data-evaluation-researcher lab-experiments-lead findings-records-curator documentation-writer academic-paper-author academic-reviewer scientific-peer-reviewer citation-reference-auditor research-engineer decision-systems-specialist)
OLD_IDS=(lab-project-manager methods-researcher experiments-lead findings-curator paper-author scientific-reviewer citation-auditor)
# Words an agent must not use (the terminology standard, D2 to D10): old names and software metaphors. Stage codes are checked separately.
VOCAB_STEMS=(ledger hand-off handoff kickoff stand-up standup orchestrat dispatch subagent devil "red team" red-team pre-regist freez frozen registry "evidence card" canonical "task board" "task brief" "iron law" lineage "verification record" "your human partner")
VOCAB_CASE=(CRITICAL VERIFIED PASS FAIL)
# The CRediT roles each agent performs (ANSI/NISO Z39.104-2022); the en dash is part of two role names.
credit_roles() {
  case "$1" in
    research-project-manager) echo "Project administration, Resources" ;;
    academic-supervisor) echo "Supervision, Conceptualization, Validation" ;;
    literature-researcher) echo "Investigation, Data curation, Conceptualization" ;;
    methods-innovation-researcher) echo "Methodology, Conceptualization, Formal analysis" ;;
    data-evaluation-researcher) echo "Formal analysis, Methodology, Data curation, Validation" ;;
    lab-experiments-lead) echo "Investigation, Resources, Data curation, Validation" ;;
    findings-records-curator) echo "Data curation, Validation" ;;
    documentation-writer) echo "Writing – original draft, Visualization, Data curation" ;;
    academic-paper-author) echo "Writing – original draft, Writing – review & editing, Visualization" ;;
    academic-reviewer) echo "Writing – review & editing, Validation" ;;
    scientific-peer-reviewer) echo "Validation, Writing – review & editing" ;;
    citation-reference-auditor) echo "Validation, Data curation" ;;
    research-engineer) echo "Software, Methodology" ;;
    decision-systems-specialist) echo "Methodology, Formal analysis, Software, Validation" ;;
    *) echo "" ;;
  esac
}
FORBIDDEN_WORDS=(DistilBERT BERT ViT UPF GFU CIFM ACT TIK Springer Optuna ruff mypy bandit config_validator)
# Owner-specific words come from tests/private-strings.txt (git-ignored; see tests/private-strings.example).
if [ -f tests/private-strings.txt ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    line=${line%$'\r'}
    case "$line" in ''|'#'*) continue ;; esac
    FORBIDDEN_WORDS+=("$line")
  done < tests/private-strings.txt
fi
FORBIDDEN_FIXED=('uv run' '.claude/skills' 'research-lab-workflow' 'doi-verified-evidence' 'findings-ledger' 'reference-access-request' 'jev-decisions' '## Operating rules' 'Running the lab from Claude Code')

shopt -s nullglob
if [ "$#" -gt 0 ]; then
  files=("$@")
  with_manifest=0
else
  files=(agents/*.md)
  with_manifest=1
  [ "${#files[@]}" -gt 0 ] || fail "no agents/*.md files"
fi

check_file() {
  local f=$1 base name line
  base=$(basename "$f" .md)
  [ -f "$f" ] || { echo "agents: $f: file not found"; exit 1; }
  err() { echo "agents: $f: $1"; exit 1; }

  # 1. frontmatter delimiters
  [ "$(head -n 1 "$f" | tr -d '\r')" = "---" ] || err "first line is not ---"
  local close
  close=$(awk 'NR>1 && /^---\r?$/{print NR; exit}' "$f")
  [ -n "$close" ] || err "no closing --- for the frontmatter"
  local fm body
  fm=$(sed -n "2,$((close - 1))p" "$f" | tr -d '\r')
  body=$(sed -n "$((close + 1)),\$p" "$f" | tr -d '\r')

  # 2. top-level keys
  local keys
  keys=$(printf '%s\n' "$fm" | { grep -E '^[A-Za-z][A-Za-z]*:' || true; } | sed 's/:.*//' | tr '\n' ' ')
  keys=${keys% }
  [ "$keys" = "name description model skills disallowedTools color" ] \
    || err "frontmatter keys are $keys, expected name description model skills disallowedTools color"

  # 3. name
  name=$(printf '%s\n' "$fm" | sed -n 's/^name:[ ]*//p')
  [ "$name" = "$base" ] || err "name is '$name', expected '$base'"
  printf '%s\n' "$name" | grep -qE '^[a-z0-9-]+$' || err "name '$name' is not lowercase letters, digits and hyphens"

  # 4. description
  local desc inner
  desc=$(printf '%s\n' "$fm" | sed -n 's/^description:[ ]*//p')
  case "$desc" in
    \"*\") ;;
    *) err "description is not wrapped in double quotes" ;;
  esac
  [ "${#desc}" -ge 2 ] || err "description is not wrapped in double quotes"
  inner=${desc#\"}
  inner=${inner%\"}
  case "$inner" in
    *\"*) err "description contains a double quote inside" ;;
  esac
  case "$inner" in
    Use*) ;;
    *) err "description must start with 'Use'" ;;
  esac
  [ "${#inner}" -lt 1024 ] || err "description is ${#inner} characters, limit is under 1024"
  case "$inner" in
    *" then "*)
      [ "${#inner}" -le 300 ] || err "description reads like a workflow (a 'then' chain over 300 characters)"
      ;;
  esac

  # 5. model
  [ "$(printf '%s\n' "$fm" | sed -n 's/^model:[ ]*//p')" = "inherit" ] || err "model must be exactly inherit"

  # 6. skills
  local block entries=() entry seen=" " n i
  block=$(printf '%s\n' "$fm" | awk '/^skills:/{on=1; next} on && /^[A-Za-z][A-Za-z]*:/{exit} on{print}')
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    case "$line" in
      "  - "?*) entries+=("${line#  - }") ;;
      *) err "skills entry is not '  - <entry>': $line" ;;
    esac
  done <<< "$block"
  n=${#entries[@]}
  { [ "$n" -ge 1 ] && [ "$n" -le 32 ]; } || err "skills has $n entries, expected 1 to 32"
  for entry in "${entries[@]}"; do
    printf '%s\n' "$entry" | grep -qE '^science-ultrapowers:[a-z0-9-]+$' || err "skill entry '$entry' is not science-ultrapowers:<name>"
    [ -f "skills/${entry#science-ultrapowers:}/SKILL.md" ] || err "skill $entry does not exist"
    case "$seen" in *" $entry "*) err "skill $entry is listed twice" ;; esac
    seen="$seen$entry "
  done
  for i in 0 1 2 3; do
    [ "${entries[$i]:-}" = "${COMMON[$i]}" ] || err "skills entry $((i + 1)) is '${entries[$i]:-}', expected ${COMMON[$i]}"
  done

  # 7. disallowedTools
  local dt want
  dt=$(printf '%s\n' "$fm" | sed -n 's/^disallowedTools:[ ]*//p')
  case "$base" in
    research-project-manager|scientific-peer-reviewer) want='[]' ;;
    *) want='[Agent]' ;;
  esac
  [ "$dt" = "$want" ] || err "disallowedTools is '$dt', expected $want"

  # 8. color
  local color
  color=$(printf '%s\n' "$fm" | sed -n 's/^color:[ ]*//p')
  case "$COLORS" in *" $color "*) [ -n "$color" ] || err "color is empty" ;; *) err "color '$color' is not one of red blue green yellow purple orange pink cyan" ;; esac

  # 9. forbidden words anywhere in the file
  local w hit
  for w in "${FORBIDDEN_WORDS[@]}"; do
    hit=$({ tr -d '\r' < "$f" | grep -n -w -E -m1 -- "$w" || true; } | head -n 1)
    [ -z "$hit" ] || err "forbidden word '$w' at line ${hit%%:*}"
  done
  for w in "${FORBIDDEN_FIXED[@]}"; do
    hit=$({ tr -d '\r' < "$f" | grep -n -F -m1 -- "$w" || true; } | head -n 1)
    [ -z "$hit" ] || err "forbidden text '$w' at line ${hit%%:*}"
  done
  hit=$({ tr -d '\r' < "$f" | grep -n -E -m1 'D-00[0-9]' || true; } | head -n 1)
  [ -z "$hit" ] || err "forbidden pattern 'D-00[0-9]' at line ${hit%%:*}"

  # 10. Role toolkit iff the role has one
  local has_toolkit=0
  if printf '%s\n' "$body" | grep -qF '## Role toolkit'; then has_toolkit=1; fi
  case "$TOOLKIT_ROLES" in
    *" $base "*) [ "$has_toolkit" = 1 ] || err "body lacks '## Role toolkit', which $base needs" ;;
    *) [ "$has_toolkit" = 0 ] || err "body has '## Role toolkit', which $base must not have" ;;
  esac

  # 11. every science-ultrapowers:<x> in the body names a skill
  local ref x
  for ref in $(printf '%s\n' "$body" | { grep -oE 'science-ultrapowers:[a-z0-9-]+' || true; } | sort -u); do
    x=${ref#science-ultrapowers:}
    [ -f "skills/$x/SKILL.md" ] || err "body names science-ultrapowers:$x, which does not exist"
  done

  # 12. no bare skill name in backticks
  local d
  for d in skills/*/; do
    d=${d%/}; d=${d##*/}
    if printf '%s\n' "$body" | grep -qF -- "\`$d\`"; then
      err "body names the skill as \`$d\`, write science-ultrapowers:$d"
    fi
  done

  # 13. body length
  local len
  len=$(printf '%s\n' "$body" | wc -c | tr -d ' ')
  { [ "$len" -ge 200 ] && [ "$len" -le 10000 ]; } || err "body is $len characters, expected 200 to 10000"

  # 14. one '## When to invoke' (before the toolkit), 3 to 5 bullets, the last one 'Not this role'
  local wcount wline tline bullets=() b nb
  wcount=$(printf '%s\n' "$body" | { grep -c -x -- '## When to invoke' || true; })
  [ "$wcount" = 1 ] || err "body has $wcount '## When to invoke' headings, expected 1"
  wline=$(printf '%s\n' "$body" | grep -n -x -m1 -- '## When to invoke' | cut -d: -f1)
  tline=$(printf '%s\n' "$body" | { grep -n -m1 -- '^## Role toolkit' || true; } | cut -d: -f1)
  if [ -n "$tline" ] && [ "$wline" -gt "$tline" ]; then
    err "'## When to invoke' must come before '## Role toolkit'"
  fi
  while IFS= read -r line; do
    bullets+=("$line")
  done < <(printf '%s\n' "$body" | awk -v s="$wline" 'NR > s { if ($0 ~ /^## /) exit; if ($0 ~ /^- /) print }')
  nb=${#bullets[@]}
  { [ "$nb" -ge 3 ] && [ "$nb" -le 5 ]; } || err "'## When to invoke' has $nb bullets, expected 3 to 5"
  for ((i = 0; i < nb; i++)); do
    b=${bullets[$i]}
    printf '%s\n' "$b" | grep -qE '^- \*\*[^*]+\.\*\* [^ ]' || err "bullet is not '- **<Name>.** <text>': $b"
    case "$b" in
      "- **Not this role.** "*)
        [ "$i" -eq $((nb - 1)) ] || err "the last bullet must be '- **Not this role.** ...'"
        ;;
    esac
  done
  case "${bullets[$((nb - 1))]}" in
    "- **Not this role.** "*) ;;
    *) err "the last bullet must be '- **Not this role.** ...'" ;;
  esac

  # 15. the description points at 'When to invoke'
  case "$inner" in
    *"See 'When to invoke' in the agent body.") ;;
    *) err "description does not end with the pointer to 'When to invoke'" ;;
  esac

  # 16. generality: nothing tied to one research project or one person
  for w in 'PhD' 'the candidate' 'human user' 'doctoral-standard' 'doctoral standards' 'thesis committee'; do
    hit=$({ tr -d '\r' < "$f" | grep -n -i -F -m1 -- "$w" || true; } | head -n 1)
    [ -z "$hit" ] || err "forbidden generality text '$w' at line ${hit%%:*}"
  done
  hit=$({ tr -d '\r' < "$f" | grep -n -i -w -m1 -- 'the user' || true; } | head -n 1)
  [ -z "$hit" ] || err "forbidden generality text 'the user' at line ${hit%%:*}"

  # 17. every Role toolkit points at the vendored skills' PROVENANCE.md records
  case "$TOOLKIT_ROLES" in
    *" $base "*)
      printf '%s\n' "$body" | grep -qF 'its PROVENANCE.md records the source, version, license and the vetting summary' \
        || err "the Role toolkit does not point at the skills' PROVENANCE.md"
      ;;
  esac

  # 18. the vocabulary: no old name, no stage code, no software metaphor
  local stem
  hit=$({ tr -d '\r' < "$f" | grep -n -E -m1 '\bG[0-6]\b' || true; } | head -n 1)
  [ -z "$hit" ] || err "stage code at line ${hit%%:*}; write the stage name"
  for stem in "${VOCAB_STEMS[@]}"; do
    hit=$({ tr -d '\r' < "$f" | grep -n -i -F -m1 -- "$stem" || true; } | head -n 1)
    [ -z "$hit" ] || err "not-approved term '$stem' at line ${hit%%:*}"
  done
  for stem in "${VOCAB_CASE[@]}"; do
    hit=$({ tr -d '\r' < "$f" | grep -n -w -m1 -- "$stem" || true; } | head -n 1)
    [ -z "$hit" ] || err "not-approved term '$stem' at line ${hit%%:*}"
  done
  hit=$({ tr -d '\r' < "$f" | grep -n -i -w -E -m1 'gates?|gated' || true; } | head -n 1)
  [ -z "$hit" ] || err "not-approved term 'gate' at line ${hit%%:*}; write stage approval"

  # 19. one '## Contributor Roles Taxonomy (CRediT)' section, after 'When to invoke' and before the toolkit, with the exact line
  local ccount cline roles want_line
  ccount=$(printf '%s\n' "$body" | { grep -c -x -- '## Contributor Roles Taxonomy (CRediT)' || true; })
  [ "$ccount" = 1 ] || err "body has $ccount '## Contributor Roles Taxonomy (CRediT)' headings, expected 1"
  cline=$(printf '%s\n' "$body" | grep -n -x -m1 -- '## Contributor Roles Taxonomy (CRediT)' | cut -d: -f1)
  [ "$cline" -gt "$wline" ] || err "'## Contributor Roles Taxonomy (CRediT)' must come after '## When to invoke'"
  if [ -n "$tline" ] && [ "$cline" -gt "$tline" ]; then
    err "'## Contributor Roles Taxonomy (CRediT)' must come before '## Role toolkit'"
  fi
  roles=$(credit_roles "$base")
  [ -n "$roles" ] || err "no CRediT roles are pinned for $base"
  want_line="CRediT (ANSI/NISO Z39.104-2022) roles this role performs: $roles. AI roles are not authors; the researcher's contribution statement lists the researcher's own CRediT roles and discloses AI assistance."
  printf '%s\n' "$body" | grep -qxF -- "$want_line" || err "the CRediT section lacks the exact line for $base"
}

# 20. running-the-lab's lead-session line names the roles that keep the Agent tool, and only those
check_lead_session_line() {
  local skill=skills/running-the-lab/SKILL.md af role dt msl
  local all=(agents/*.md)
  serr() { echo "agents: $skill: $1"; exit 1; }
  msl=
  if [ -f "$skill" ]; then
    msl=$({ tr -d '\r' < "$skill" | grep -F -m1 -- 'run as the lead session' || true; } | head -n 1)
  fi
  [ -n "$msl" ] || serr "running-the-lab has no lead-session line"
  for af in "${all[@]}"; do
    role=$(basename "$af" .md)
    dt=$(tr -d '\r' < "$af" | awk 'NR == 1 { next } /^---$/ { exit } /^disallowedTools:/ { sub(/^disallowedTools:[ ]*/, ""); print; exit }')
    case "$dt" in
      '[]')
        printf '%s\n' "$msl" | grep -qF -- "\`$role\`" \
          || serr "running-the-lab's lead-session line does not name $role, which keeps the Agent tool"
        ;;
      '[Agent]')
        if printf '%s\n' "$msl" | grep -qF -- "\`$role\`"; then
          serr "running-the-lab's lead-session line names $role, which cannot assign"
        fi
        ;;
    esac
  done
}

if [ "$with_manifest" = 1 ]; then
  for id in "${NEW_IDS[@]}"; do
    [ -f "agents/$id.md" ] || fail "agents/$id.md does not exist"
    jq -e --arg p "./agents/$id.md" '.agents | index($p) != null' .claude-plugin/plugin.json >/dev/null 2>&1 \
      || fail "plugin.json agents does not list ./agents/$id.md"
  done
  for id in "${OLD_IDS[@]}"; do
    [ ! -e "agents/$id.md" ] || fail "agents/$id.md still exists; the id is now one of the fourteen new ids"
  done
  [ "${#files[@]}" -eq 14 ] || fail "${#files[@]} agent files, expected 14"
fi

for f in "${files[@]}"; do
  check_file "$f"
done

check_lead_session_line

if [ "$with_manifest" = 1 ]; then
  manifest=.claude-plugin/plugin.json
  jq -e 'has("agents")' "$manifest" >/dev/null 2>&1 || fail "plugin.json has no agents key"
  listed=$(jq -r '.agents[]' "$manifest" | tr -d '\r')
  listed_sorted=$(printf '%s\n' "$listed" | sort)
  on_disk=$(printf '%s\n' "${files[@]}" | sed 's#^#./#' | sort)
  if [ "$listed_sorted" != "$on_disk" ]; then
    echo "agents: plugin.json agents list differs from agents/*.md"
    diff <(printf '%s\n' "$listed_sorted") <(printf '%s\n' "$on_disk") || true
    exit 1
  fi
  [ "$listed" = "$listed_sorted" ] || fail "plugin.json agents list is not alphabetical"
fi

echo "agents: ok"
