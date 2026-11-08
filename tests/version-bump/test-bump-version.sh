#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPT_SOURCE="$REPO_ROOT/scripts/bump-version.sh"
TEST_ROOT="$(mktemp -d)"

cleanup() {
  rm -rf "$TEST_ROOT"
}
trap cleanup EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

make_fixture() {
  local repo="$1"

  mkdir -p "$repo/scripts" "$repo/.claude-plugin"
  cp "$SCRIPT_SOURCE" "$repo/scripts/bump-version.sh"
  cat >"$repo/.version-bump.json" <<'JSON'
{
  "files": [
    { "path": ".claude-plugin/plugin.json", "field": "version" },
    { "path": ".claude-plugin/marketplace.json", "field": "plugins.0.version" }
  ],
  "audit": { "exclude": [] }
}
JSON
  cat >"$repo/.claude-plugin/plugin.json" <<'JSON'
{
  "name": "fixture",
  "description": "fixture plugin",
  "version": "1.0.0"
}
JSON
  cat >"$repo/.claude-plugin/marketplace.json" <<'JSON'
{
  "name": "fixture",
  "plugins": [
    { "name": "fixture", "version": "1.0.0", "source": "./" }
  ]
}
JSON
}

# a) bump rewrites both files and leaves every other key alone
repo="$TEST_ROOT/bump"
make_fixture "$repo"
jq -S 'del(.version)' "$repo/.claude-plugin/plugin.json" >"$TEST_ROOT/plugin.rest.before"
jq -S 'del(.plugins[0].version)' "$repo/.claude-plugin/marketplace.json" >"$TEST_ROOT/market.rest.before"
/bin/bash "$repo/scripts/bump-version.sh" 2.3.4 >"$TEST_ROOT/bump.out" 2>&1 \
  || fail "bump to 2.3.4 exited non-zero"
[[ "$(jq -r '.version' "$repo/.claude-plugin/plugin.json")" == "2.3.4" ]] \
  || fail "plugin.json was not bumped to 2.3.4"
[[ "$(jq -r '.plugins[0].version' "$repo/.claude-plugin/marketplace.json")" == "2.3.4" ]] \
  || fail "marketplace.json was not bumped to 2.3.4"
jq -S 'del(.version)' "$repo/.claude-plugin/plugin.json" >"$TEST_ROOT/plugin.rest.after"
jq -S 'del(.plugins[0].version)' "$repo/.claude-plugin/marketplace.json" >"$TEST_ROOT/market.rest.after"
cmp -s "$TEST_ROOT/plugin.rest.before" "$TEST_ROOT/plugin.rest.after" \
  || fail "bump changed keys other than version in plugin.json"
cmp -s "$TEST_ROOT/market.rest.before" "$TEST_ROOT/market.rest.after" \
  || fail "bump changed keys other than the plugin version in marketplace.json"

# b) check passes when in sync
/bin/bash "$repo/scripts/bump-version.sh" --check >"$TEST_ROOT/check.out" 2>&1 \
  || fail "--check failed on files that are in sync"

# c) check reports drift
jq '.plugins[0].version = "9.9.9"' "$repo/.claude-plugin/marketplace.json" >"$TEST_ROOT/market.drift"
cp "$TEST_ROOT/market.drift" "$repo/.claude-plugin/marketplace.json"
if /bin/bash "$repo/scripts/bump-version.sh" --check >"$TEST_ROOT/drift.out" 2>&1; then
  fail "--check exited 0 despite version drift"
fi
grep -q '2.3.4' "$TEST_ROOT/drift.out" || fail "drift output does not show the plugin.json version 2.3.4"
grep -q '9.9.9' "$TEST_ROOT/drift.out" || fail "drift output does not show the drifted version 9.9.9"

# d) invalid JSON: fail, leave the file untouched, leave no temp file behind
repo="$TEST_ROOT/invalid"
make_fixture "$repo"
printf '{ "version": "1.0.0",\n' >"$repo/.claude-plugin/plugin.json"
cp "$repo/.claude-plugin/plugin.json" "$TEST_ROOT/plugin.invalid.before"
if /bin/bash "$repo/scripts/bump-version.sh" 3.0.0 >"$TEST_ROOT/invalid.out" 2>&1; then
  fail "bump accepted an invalid JSON manifest"
fi
cmp -s "$TEST_ROOT/plugin.invalid.before" "$repo/.claude-plugin/plugin.json" \
  || fail "invalid JSON manifest was modified"
leftover="$(find "$repo" -name '*.tmp')"
[[ -z "$leftover" ]] || fail "temp file left behind: $leftover"

# e) unsupported manifest format
repo="$TEST_ROOT/unsupported"
make_fixture "$repo"
cat >"$repo/.version-bump.json" <<'JSON'
{
  "files": [
    { "path": ".claude-plugin/plugin.json", "field": "version" },
    { "path": ".claude-plugin/marketplace.json", "field": "plugins.0.version" },
    { "path": ".claude-plugin/extra.yaml", "field": "version" }
  ],
  "audit": { "exclude": [] }
}
JSON
printf 'version: 1.0.0\n' >"$repo/.claude-plugin/extra.yaml"
if /bin/bash "$repo/scripts/bump-version.sh" --check >"$TEST_ROOT/unsupported.out" 2>&1; then
  fail "--check accepted a .yaml manifest"
fi
grep -q 'unsupported manifest format' "$TEST_ROOT/unsupported.out" \
  || fail "output does not say 'unsupported manifest format' for a .yaml manifest"

# f) the real repository declares exactly the two Claude Code manifests
jq -e '.files | map(.path) == [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"]' \
  "$REPO_ROOT/.version-bump.json" >/dev/null \
  || fail "repository .version-bump.json must declare exactly the two Claude Code manifests"

echo "bump-version: ok"
