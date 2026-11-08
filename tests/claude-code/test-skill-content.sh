#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

fail() {
  echo "skill-content: $1"
  exit 1
}

# (a) no old Claude Science skill names outside PROVENANCE.md files
offenders=$(grep -rlE --include='*.md' '\.claude/skills/|doi-verified-evidence|research-lab-workflow|findings-ledger|reference-access-request|jev-decisions' skills | grep -v '/PROVENANCE\.md$' || true)
if [ -n "$offenders" ]; then
  fail "old names found in: $(echo "$offenders" | tr '\n' ' ')"
fi

# (b) the plugin's own skills (no PROVENANCE.md) have trigger-only descriptions
for f in skills/*/SKILL.md; do
  dir=$(dirname "$f")
  if [ -f "$dir/PROVENANCE.md" ]; then
    continue
  fi
  desc=$(awk 'NR==1 && $0!="---"{exit} /^---$/{n++; if(n==2) exit; next} n==1 && /^description:/{sub(/^description:[ \t]*/,""); print; exit}' "$f")
  desc=${desc%$'\r'}
  desc=${desc#\"}; desc=${desc%\"}
  desc=${desc#\'}; desc=${desc%\'}
  case "$desc" in
    "Use when"*|"Use whenever"*|"Use for"*|"Use at"*) ;;
    *) fail "$f: description must start with 'Use when', 'Use whenever', 'Use for' or 'Use at'" ;;
  esac
  if [ "${#desc}" -ge 1024 ]; then
    fail "$f: description is ${#desc} characters, limit is under 1024"
  fi
done

# (c) the lab's twelve load-bearing sentences, each in the skill that owns it
sentences=(
  'running-the-lab|Nobody reviews or audits their own work'
  'running-the-lab|A not-cleared citation audit blocks the stage approval'
  'running-the-lab|The test set is touched only by a preregistered final evaluation'
  'running-the-lab|A bare claim of checking counts as unchecked'
  'verifying-evidence-by-doi|Only a matched DOI passes'
  'verifying-evidence-by-doi|Preprints'
  'verifying-evidence-by-doi|never as evidence'
  'verifying-evidence-by-doi|A label of "matched" written by another role is never accepted without re-running the check'
  'verifying-evidence-by-doi|Bibliographies are generated, never typed'
  'recording-findings|A verified row is never edited'
  'recording-findings|A bare claim of checking counts as unchecked'
  'requesting-reference-access|Use shadow libraries or pirate sites'
  'deciding-with-jev|A Jev output is never evidence'
  'preregistering-the-protocol|NO CONFIRMATORY CLAIM WITHOUT A REGISTERED PREDICTION FIRST'
  'preregistering-the-protocol|It is never relabeled'
  'preregistering-the-protocol|A deviation from the registered protocol makes the affected finding exploratory'
  'running-the-lab|No outcome is loaded, computed, fitted or plotted before the framing is approved'
  'running-the-lab|NO ADJUSTMENT WITHOUT ROOT CAUSE FIRST'
  'running-the-lab|Nothing is feasible until it has run'
  'running-the-lab|A deviation from the registered protocol makes the affected finding exploratory'
  'running-the-lab|the protocol-adherence review runs before the rigor review'
  'running-the-lab|Never assign many specifications and report the survivor'
  'running-the-lab|Raw inputs are read-only'
  'recording-findings|A finding is confirmatory only with a registered protocol whose registration check is clear'
  'recording-findings|A null result needs an effect size and an interval'
  'recording-findings|Input checksums'
)
for entry in "${sentences[@]}"; do
  skill=${entry%%|*}
  s=${entry#*|}
  grep -qF -- "$s" "skills/$skill/SKILL.md" || fail "skills/$skill/SKILL.md lacks the sentence: $s"
done
n=$(wc -c < skills/running-the-lab/SKILL.md); [ "$n" -lt 18000 ] || fail "running-the-lab is $n bytes, limit under 18000"

# The plugin's own skills: folders without PROVENANCE.md.
own=()
for d in skills/*/; do
  [ -f "$d/PROVENANCE.md" ] || own+=("${d%/}")
done

# (e) an own SKILL.md names a bundled script only through its ${CLAUDE_PLUGIN_ROOT} path:
#     a bare `verify_doi.py ...` does not run from a plugin install
scripts=$(for d in "${own[@]}"; do
  if [ -d "$d/scripts" ]; then
    find "$d/scripts" -type f \( -name '*.py' -o -name '*.mjs' -o -name '*.sh' \) -not -path '*/tests/*' -not -name '_*' -exec basename {} \;
  fi
done | sort -u)
for name in $scripts; do
  hits=$(for d in "${own[@]}"; do grep -nF -- "\`$name" "$d/SKILL.md" | sed "s#^#$d/SKILL.md:#" || true; done)
  [ -z "$hits" ] || fail "bare script name, use python \"\${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/$name\": $hits"
done

# (f) own skills cross-reference other skills as `science-ultrapowers:<skill>`, never as a bare `<skill>`
for skill_dir in skills/*/; do
  name=$(basename "$skill_dir")
  hits=$(grep -rnF --include='*.md' -- "\`$name\`" "${own[@]}" || true)
  [ -z "$hits" ] || fail "bare skill name \`$name\`, write \`science-ultrapowers:$name\`: $hits"
done

# (g) every science-ultrapowers:<skill> reference resolves to a skill folder. PENDING lists the
#     skills later plans create; remove each name when its folder lands. The CLAUDE.md section
#     markers (<!-- science-ultrapowers:begin --> and :end) are not references.
PENDING="framing-a-research-question synthesizing-the-literature reviewing-a-manuscript writing-for-publication presenting-research"
for ref in $(grep -rhoE --include='*.md' '(<!-- )?science-ultrapowers:[a-z0-9-]+' skills | grep -v '^<!-- ' | sort -u); do
  name=${ref#science-ultrapowers:}
  if [ -f "skills/$name/SKILL.md" ]; then
    case " $PENDING " in *" $name "*) fail "skills/$name exists: remove it from PENDING" ;; esac
    continue
  fi
  case " $PENDING " in *" $name "*) continue ;; esac
  fail "dangling cross-reference $ref: $(grep -rlF --include='*.md' -- "$ref" skills | tr '\n' ' ')"
done

# (d) verification-before-completion carries the lab's sixth gate line and failure row
vbc=skills/verification-before-completion/SKILL.md
grep -q '^6\. NAME the check' "$vbc" || fail "$vbc lacks the line beginning '6. NAME the check'"
grep -q '^| "Verified" written alone' "$vbc" || fail "$vbc lacks the table row beginning '| \"Verified\" written alone'"

echo "skill-content: ok"
