#!/usr/bin/env bash
# Runs every test in the repository: shell tests under tests/<area>/test-*.sh,
# Python unittest files under skills/*/scripts/tests/, node tests named
# skills/*/scripts/tests/*.test.mjs. Exit 0 only when all of them pass.
set -uo pipefail
cd "$(dirname "$0")/../.."
status=0
for t in tests/*/test-*.sh; do
  echo "== $t"
  bash "$t" || { echo "FAILED: $t"; status=1; }
done
py=$(command -v python || command -v python3 || true)
for d in skills/*/scripts/tests; do
  [ -d "$d" ] || continue
  ls "$d"/test_*.py >/dev/null 2>&1 || continue
  [ -n "$py" ] || { echo "FAILED: $d (no python or python3 on PATH)"; status=1; continue; }
  echo "== python: $d"
  "$py" -m unittest discover -s "$d" -p "test_*.py" || { echo "FAILED: $d (python)"; status=1; }
done
if ls skills/*/scripts/tests/*.test.mjs >/dev/null 2>&1; then
  echo "== node: skills/*/scripts/tests/*.test.mjs"
  node --test skills/*/scripts/tests/*.test.mjs || { echo "FAILED: node tests"; status=1; }
fi
[ "$status" = 0 ] && echo "ALL TESTS PASSED" || echo "SOME TESTS FAILED"
exit $status
