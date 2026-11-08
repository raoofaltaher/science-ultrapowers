#!/usr/bin/env bash
# The repository documents, the logo assets, the release notes and the
# license field are in place and agree with each other.
set -euo pipefail
cd "$(dirname "$0")/../.."
fail=0
bad() { echo "FAIL: $1"; fail=1; }

for f in README.md LICENSE CONTRIBUTING.md CODE_OF_CONDUCT.md RELEASE-NOTES.md \
  assets/science-ultrapowers-small.svg \
  .github/ISSUE_TEMPLATE/bug_report.md .github/ISSUE_TEMPLATE/feature_request.md \
  .github/ISSUE_TEMPLATE/config.yml .github/PULL_REQUEST_TEMPLATE.md \
  .github/CODEOWNERS .github/workflows/ci.yml; do
  [ -f "$f" ] || bad "missing file: $f"
done

if [ -f README.md ]; then
  for h in "Install" "Start a lab" "Continue from Claude Science" "The team" \
    "How a session runs" "Tracks" "The records and the archive" "Scholarly output style" "Skills" "Connectors" "Testing" "License"; do
    grep -qx "## $h" README.md || bad "README.md lacks the heading: ## $h"
  done
  grep -qF 'terminology.md' README.md || bad "README.md does not name terminology.md"
  grep -qF 'Scholarly Explanatory' README.md || bad "README.md does not name Scholarly Explanatory"
  grep -qE '^Built from obra/superpowers v7\.0\.2 \(MIT\) as the template' README.md \
    || bad "README.md lacks the template credit line"
  grep -qF 'assets/science-ultrapowers-small.svg' README.md \
    || bad "README.md does not reference assets/science-ultrapowers-small.svg"
  for l in 'discussions/new?category=q-a' 'discussions/new?category=ideas' \
    'discussions/new?category=show-and-tell' 'issues/new/choose' 'discussions'; do
    grep -qF "$l" README.md || bad "README.md lacks the link: $l"
  done
fi

if [ -f LICENSE ]; then
  [ "$(head -n1 LICENSE | tr -d '\r')" = "science-ultrapowers Proprietary Use License" ] \
    || bad "LICENSE first line is not 'science-ultrapowers Proprietary Use License'"
  grep -qF '7.0.2' LICENSE || bad "LICENSE does not name 7.0.2"
  grep -qF 'MIT' LICENSE || bad "LICENSE does not name MIT"
  grep -qF 'science-superpowers' LICENSE || bad "LICENSE does not name science-superpowers"
fi

if [ -f RELEASE-NOTES.md ]; then
  grep -qE '^## 0\.1\.0( |$)' RELEASE-NOTES.md || bad "RELEASE-NOTES.md has no '## 0.1.0' heading"
  grep -qE '^## 0\.2\.0' RELEASE-NOTES.md || bad "RELEASE-NOTES.md has no '## 0.2.0' heading"
  ! grep -qi 'unreleased' RELEASE-NOTES.md || bad "RELEASE-NOTES.md still says unreleased"
fi

svg=assets/science-ultrapowers-small.svg
if [ -f "$svg" ]; then
  python -c "import xml.dom.minidom,sys; xml.dom.minidom.parse(sys.argv[1])" "$svg" 2>/dev/null \
    || bad "$svg is not well-formed XML"
  grep -qF 'viewBox="0 0 420 80"' "$svg" || bad "$svg does not declare viewBox=\"0 0 420 80\""
  ! grep -q '<image' "$svg" || bad "$svg contains <image"
  ! sed 's#xmlns="http://www.w3.org/2000/svg"##g' "$svg" | grep -q 'http' \
    || bad "$svg has an http reference other than the xmlns"
  ! grep -q '@import' "$svg" || bad "$svg contains @import"
  ! grep -q 'font-face' "$svg" || bad "$svg contains font-face"
fi

[ "$(python -c "import json,sys; print(json.load(open(sys.argv[1], encoding='utf-8')).get('license', ''))" .claude-plugin/plugin.json)" != "MIT" ] \
  || bad "plugin.json license is still MIT"

for f in docs/science-ultrapowers/terminology.md output-styles/scholarly-explanatory.md; do
  [ -f "$f" ] || bad "missing file: $f"
done

for e in '.claude/' '__pycache__/' '*.pyc' 'node_modules/' '.DS_Store' '/.ultrapowers/'; do
  grep -qxF "$e" .gitignore || bad ".gitignore lacks: $e"
done

# The install block holds shell commands only; the slash forms stay in prose.
if [ -f README.md ]; then
  ! awk '/^## Install/{f=1} /^## Start a lab/{f=0} f && /^```/{c=!c; next} f && c' README.md | grep -q '^/plugin' \
    || bad "README.md install block holds a /plugin session command"
  grep -q 'claude plugin marketplace add raoofaltaher/science-ultrapowers' README.md \
    || bad "README.md install block lacks the marketplace add command"
  grep -qi 'pwsh\|PowerShell 7' README.md || bad "README.md requirements do not name PowerShell 7"
fi
grep -q 'test-repo-documents.sh' docs/testing.md || bad "docs/testing.md does not list test-repo-documents.sh"
grep -q 'test_preregister.py' docs/testing.md || bad "docs/testing.md does not name test_preregister.py"
grep -q '^permissions:' .github/workflows/ci.yml || bad "ci.yml has no permissions block"
grep -q 'validate-0.1.0.txt' docs/science-ultrapowers/evals/README.md || bad "evals/README.md does not index validate-0.1.0.txt"

[ "$fail" = 0 ] || exit 1
echo "repo-documents: ok"
