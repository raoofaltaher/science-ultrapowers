#!/usr/bin/env bash
# The lab templates carry the standard's names: the new folders and files exist and the
# old ones do not, the table headers and the status words are the standard's, the
# hypothesis record has its fields, lab.json has its keys, and no template holds a stage
# code or a not-approved word (a line ending with <!-- legacy --> is skipped).
set -euo pipefail
cd "$(dirname "$0")/../.."
fail=0
bad() { echo "FAIL: $1"; fail=1; }

S=skills/initializing-a-research-lab/templates
T=$S/research_lab
M=skills/holding-lab-meetings/templates
R=skills/remembering-for-the-lab/templates

# ---- the new paths exist --------------------------------------------------------
new_paths=(
  project/PROJECT_BRIEF.md project/README.md
  literature/SOURCES.csv literature/EXCEPTIONS.md literature/README.md
  literature/evidence_records/.gitkeep literature/search_logs/.gitkeep literature/citation_audits/.gitkeep
  findings/FINDINGS_LOG.md findings/KEY_RESULTS.md findings/LAB_NOTEBOOK.md findings/README.md
  experiments/EXPERIMENT_REGISTER.md experiments/README.md
  experiments/preregistrations/.gitkeep experiments/feasibility/.gitkeep
  reviews/README.md reviews/REVIEW_LOG.md reviews/reports/.gitkeep
  requests/ACCESS_REQUESTS.md requests/README.md
  decisions/DECISION_LOG.md decisions/README.md decisions/lab_meetings/.gitkeep
  planning/README.md planning/WORK_PLAN.md planning/ROADMAP_STATUS.md planning/RISK_REGISTER.md
  automation/JEV_CALLS.jsonl automation/README.md automation/thresholds.json
  tool_vetting/README.md
  artifacts/archive/.gitkeep memory/project/.gitkeep memory/artifact/.gitkeep
  .working/.gitkeep README.md
  templates/CITATION_AUDIT.md templates/ADVERSARIAL_REVIEW.md templates/EVIDENCE_RECORD.md
  templates/HYPOTHESIS_RECORD.md templates/TASK_REPORT.md templates/METHOD_PROPOSAL.md
  templates/PREREGISTRATION.md templates/REFEREE_REPORT.md templates/INTERNAL_REVIEW.md
  templates/PROTOCOL_ADHERENCE_REVIEW.md templates/RESPONSE_MATRIX.md
  templates/SYNTHESIS_MATRIX.md templates/ARCHIVE_MANIFEST.md
)
for p in "${new_paths[@]}"; do
  [ -e "$T/$p" ] || bad "missing $T/$p"
done
for p in "$M/SESSION_OPENING.md" "$M/SESSION_CLOSE.md" "$M/LAB_MEETING.md"; do
  [ -e "$p" ] || bad "missing $p"
done

# ---- the old paths are gone -----------------------------------------------------
old_paths=(
  00_project_knowledge 01_reference_registry 02_findings_ledger 03_experiments 04_reviews
  05_access_requests 06_decisions 07_project_management 08_decision_log 09_skill_vetting
  .scratch artifacts/store
  literature/REGISTRY.csv literature/evidence_cards literature/audits
  findings/FINDINGS.md findings/CANONICAL_NUMBERS.md
  experiments/protocols decisions/DECISIONS.md planning/TASK_BOARD.md
  templates/H_CARD.md templates/HANDOFF.md templates/DEVILS_ADVOCATE_TEMPLATE.md
  templates/REVIEW_ACADEMIC.md templates/EVIDENCE_CARD.md
)
for p in "${old_paths[@]}"; do
  [ ! -e "$T/$p" ] || bad "old path still present: $T/$p"
done
for p in "$M/SESSION_KICKOFF.md" "$M/SESSION_STANDUP.md"; do
  [ ! -e "$p" ] || bad "old path still present: $p"
done

# has_line FILE TEXT: the whole header or field line, as a fixed string.
has_line() {
  [ -f "$1" ] && grep -F -x -q -- "$2" "$1" || bad "$1 lacks the line: $2"
}
# has_word FILE WORD: the status word appears in the file (fixed string).
has_word() {
  [ -f "$1" ] && grep -F -q -- "$2" "$1" || bad "$1 lacks the word: $2"
}

# ---- the headers, exactly -------------------------------------------------------
has_line "$T/findings/FINDINGS_LOG.md" '| FND-id (finding) | Statement | Type | Basis | Evidence | Status | Recorded | Verified | Scope and caveats |'
has_line "$T/experiments/EXPERIMENT_REGISTER.md" '| EXP-id (experiment) | Preregistration | Hypothesis | Code and config | Seeds and partitions | Environment | Input checksums | Status | Outputs | Deviations | Findings |'
has_line "$T/literature/SOURCES.csv" 'source_id,title,first_author,year,doi,source_class,doi_status,status,evidence_records,notes'
has_line "$T/reviews/REVIEW_LOG.md" '| REV-id (review) | Stage | Artifact | Reviewer | Outcome | Date | Report |'
has_line "$T/requests/ACCESS_REQUESTS.md" '| REQ-id (request) | Type | DOI or identifier | Citation (from Crossref) | Requested by and date | Needed for | Priority | Status | Delivered file |'
has_line "$T/decisions/DECISION_LOG.md" '| DEC-id (decision) | Date | Stage | Context | Options | Decision | Rationale | Evidence | Approver |'
has_line "$T/planning/WORK_PLAN.md" '| TASK-id (task) | Stage | Owner | Reviewer | Status | Due | Deliverables |'
has_line "$T/planning/RISK_REGISTER.md" '| RSK-id (risk) | Risk | Likelihood | Impact | Mitigation | Owner | Status |'

# ---- the status words -----------------------------------------------------------
for w in tentative verified 'superseded by FND-xxxx' 'refuted by FND-xxxx'; do
  has_word "$T/findings/FINDINGS_LOG.md" "$w"
done
for w in 'full-text request' 'DOI confirmation' 'exception approval' \
         'blocks a stage' 'this cycle' background \
         open fulfilled approved declined unavailable; do
  has_word "$T/requests/ACCESS_REQUESTS.md" "$w"
done
for w in planned feasibility registered running completed failed aborted; do
  has_word "$T/experiments/EXPERIMENT_REGISTER.md" "$w"
done
has_word "$T/templates/HYPOTHESIS_RECORD.md" 'draft / approved at the Question stage (DEC-id)'
has_word "$T/templates/TASK_REPORT.md" 'none (an external manuscript)'

# ---- the hypothesis record's fields ---------------------------------------------
for f in \
  '- Research question (RQ):' \
  '- Statement (falsifiable):' \
  '- Prediction (direction and smallest effect size of interest):' \
  '- Refuting outcome:' \
  '- Prior evidence (EVR-ids):' \
  '- Contribution relative to prior work:' \
  '- Planned experiments (EXP-ids):' \
  '- Status: draft / approved at the Question stage (DEC-id)'   '- Background and the decision it informs:'   '- H0:'   '- H1 (directional where justified):'   '- Population and unit of analysis:'   '- Variables, operationalized (outcome, predictors, covariates):'   '- What counts as an answer:'   '- Scope and exclusions:'   '- Open questions for the survey:'; do
  has_line "$T/templates/HYPOTHESIS_RECORD.md" "$f"
done

# ---- the preregistration's design-validation lines, the ten domains ---------------
for w in 'Simulated-data recovery' 'No placeholders' 'One handling per confound'          'Power or minimum detectable effect' 'Feasibility' 'Planned deviations handling'          'Registered at commit'; do
  has_word "$T/templates/PREREGISTRATION.md" "$w"
done
domains='alternative explanation / confound / leakage / split or metric artifact / seed or confidence-interval fragility / overreach / unchecked assumptions / researcher degrees of freedom / multiplicity / reproducibility from raw and seed'
for f in "$T/templates/ADVERSARIAL_REVIEW.md" "$T/templates/REFEREE_REPORT.md"; do
  has_word "$f" "$domains"
  has_word "$f" 'What would change your mind:'
done

# ---- lab.json -------------------------------------------------------------------
py=$(command -v python || command -v python3 || true)
if [ -z "$py" ]; then
  bad "no python to read $S/lab.json"
else
  out=$("$py" - "$S/lab.json" <<'PY' || true
import json, sys
try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception as exc:
    print("lab.json does not parse: %s" % exc)
    sys.exit(0)
scope = data.get("scope")
if not isinstance(scope, dict) or not isinstance(scope.get("restrictedFolders"), list):
    print("lab.json lacks scope.restrictedFolders as a list")
if "jev" in data:
    print("lab.json still has the jev key")
if not isinstance(data.get("tracks"), list):
    print("lab.json lacks tracks as a list")
prereg = data.get("preregistration")
if not isinstance(prereg, dict) or prereg.get("registrationTrailer") != "Preregistration":
    print("lab.json lacks preregistration.registrationTrailer equal to Preregistration")
elif prereg.get("timestampTrailer") != "Preregistration-Timestamp":
    print("lab.json preregistration.timestampTrailer is not Preregistration-Timestamp")
roles = data.get("roles")
want = {
    "research-project-manager", "academic-supervisor", "literature-researcher",
    "methods-innovation-researcher", "data-evaluation-researcher", "lab-experiments-lead",
    "findings-records-curator", "documentation-writer", "academic-paper-author",
    "academic-reviewer", "scientific-peer-reviewer", "citation-reference-auditor",
    "research-engineer", "decision-systems-specialist",
}
have = set(roles) if isinstance(roles, dict) else set()
if have != want:
    print("lab.json roles differ: missing %s; extra %s" % (sorted(want - have), sorted(have - want)))
prefixes = data.get("idPrefixes")
need = {
    "FND": "finding", "HYP": "hypothesis", "EVR": "evidence record", "REV": "review",
    "ADV": "adversarial review", "REQ": "request", "DEC": "decision", "TASK": "task",
    "MTH": "method proposal", "RSK": "risk", "EXP": "experiment", "ADH": "protocol-adherence review",
}
if not isinstance(prefixes, dict):
    print("lab.json lacks idPrefixes")
else:
    for key, word in need.items():
        if prefixes.get(key) != word:
            print("lab.json idPrefixes.%s is %r, expected %r" % (key, prefixes.get(key), word))
PY
)
  while IFS= read -r line; do
    [ -z "$line" ] || bad "$line"
  done <<< "$out"
fi

# ---- no stage code and no not-approved word in any template file ----------------
files=$(find "$S" "$M" "$R" -type f ! -name '.gitkeep' | sort)
words='ledger|hand-off|handoff|kickoff|stand-up|standup|orchestrator|devil|red team|your human partner|gotcha|scratch|iron law|red flags|registry'
while IFS= read -r f; do
  [ -n "$f" ] || continue
  hits=$(grep -n -v -E '<!-- legacy -->[[:space:]]*$' "$f" 2>/dev/null | grep -E '\bG[0-6]\b' || true)
  [ -z "$hits" ] || bad "stage code in $f: $(echo "$hits" | head -1)"
  hits=$(grep -n -v -E '<!-- legacy -->[[:space:]]*$' "$f" 2>/dev/null | grep -i -E "$words" || true)
  [ -z "$hits" ] || bad "not-approved word in $f: $(echo "$hits" | head -1)"
done <<< "$files"

[ "$fail" -eq 0 ] || exit 1
echo "lab-templates: ok"
