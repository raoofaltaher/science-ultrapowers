#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
f=skills/using-science-ultrapowers/SKILL.md
[ -f "$f" ] || { echo "missing $f"; exit 1; }
n=$(wc -c < "$f")
[ "$n" -lt 8500 ] || { echo "bootstrap is $n bytes, limit 8500"; exit 1; }
grep -q '^name: using-science-ultrapowers$' "$f" || { echo "name is not using-science-ultrapowers"; exit 1; }
grep -q '^description: Use when starting any conversation' "$f" || { echo "description does not start with 'Use when starting any conversation'"; exit 1; }
grep -q 'science-ultrapowers:running-the-lab' "$f" || { echo "bootstrap does not cite science-ultrapowers:running-the-lab"; exit 1; }
grep -q 'science-ultrapowers:holding-lab-meetings' "$f" || { echo "bootstrap does not cite science-ultrapowers:holding-lab-meetings"; exit 1; }
grep -q 'science-ultrapowers:verifying-evidence-by-doi' "$f" || { echo "bootstrap does not cite science-ultrapowers:verifying-evidence-by-doi"; exit 1; }
! grep -qi 'superpowers:' "$f" || { echo "bootstrap still names a superpowers: skill"; exit 1; }
grep -q 'that folder is the lab' "$f" || { echo "bootstrap does not say research_lab/ is the lab"; exit 1; }
grep -q 'acts as the Research Project Manager' "$f" || { echo "bootstrap does not say how the team is addressed"; exit 1; }
grep -q 'science-ultrapowers:framing-a-research-question' "$f" || { echo "the session primer lacks the track table"; exit 1; }
grep -q 'science-ultrapowers:synthesizing-the-literature' "$f" || { echo "the session primer lacks the track table"; exit 1; }
grep -q 'science-ultrapowers:reviewing-a-manuscript' "$f" || { echo "the session primer lacks the track table"; exit 1; }
grep -q 'science-ultrapowers:writing-for-publication' "$f" || { echo "the session primer lacks the track table"; exit 1; }
grep -q 'science-ultrapowers:presenting-research' "$f" || { echo "the session primer lacks the track table"; exit 1; }
grep -q 'science-ultrapowers:preregistering-the-protocol' "$f" || { echo "the session primer lacks the track table"; exit 1; }
echo "bootstrap-length: ok"
