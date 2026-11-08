#!/usr/bin/env bash
# setup_lab_env.ps1 -DryRun prints its plan, changes nothing and asks nothing.
set -euo pipefail
cd "$(dirname "$0")/../.."
fail() { echo "setup-env-dryrun: $1"; exit 1; }

if ! command -v pwsh >/dev/null 2>&1; then
  echo "setup-env-dryrun: ok (pwsh absent)"
  exit 0
fi

script="skills/initializing-a-research-lab/scripts/setup_lab_env.ps1"
[ -f "$script" ] || fail "$script does not exist"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
win() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi; }

root=$(win "$tmp")
rc=0
out=$(pwsh -NoProfile -NonInteractive -File "$script" -ProjectRoot "$root" -DryRun 2>&1) || rc=$?
[ "$rc" -eq 0 ] || fail "dry run exited $rc: $out"

grep -q -F '.venv-lab-skills' <<<"$out" || fail "output does not name .venv-lab-skills"
grep -q -i 'python-pptx' <<<"$out" || fail "output does not name python-pptx"
grep -q -i 'pillow' <<<"$out" || fail "output does not name pillow"
grep -q -E 'TESSDATA_PREFIX.*separate yes' <<<"$out" || fail "no TESSDATA_PREFIX line with 'separate yes'"
grep -q -E 'TYPESAFE_API_KEY.*separate yes' <<<"$out" || fail "no TYPESAFE_API_KEY line with 'separate yes'"
grep -q -F 'Preview: nothing was changed.' <<<"$out" || fail "the preview does not end with 'Preview: nothing was changed.'"
grep -q -F 'lab set-up' <<<"$out" || fail "the preview does not name the lab set-up"
! grep -q -i 'dry run:' <<<"$out" || fail "the preview still says 'Dry run:'"
! grep -q -i 'vendored' <<<"$out" || fail "the preview still says 'vendored'"
[ -z "$(ls -A "$tmp")" ] || fail "dry run wrote into the project directory: $(ls -A "$tmp")"

missing="$tmp/does-not-exist"
rc=0
pwsh -NoProfile -NonInteractive -File "$script" -ProjectRoot "$(win "$missing")" -DryRun >/dev/null 2>&1 || rc=$?
[ "$rc" -ne 0 ] || fail "a missing -ProjectRoot did not fail"

echo "setup-env-dryrun: ok"
