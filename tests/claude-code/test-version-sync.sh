#!/usr/bin/env bash
# The two Claude Code manifests carry one name, one source and one version,
# and that version is the top release in RELEASE-NOTES.md.
set -euo pipefail
cd "$(dirname "$0")/../.."
expected=$(grep -m1 -E '^## ' RELEASE-NOTES.md | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
[ -n "$expected" ] || { echo "RELEASE-NOTES.md has no '## X.Y.Z' heading"; exit 1; }
[ "$(jq -r .name .claude-plugin/plugin.json)" = "science-ultrapowers" ] || { echo "plugin.json name is $(jq -r .name .claude-plugin/plugin.json)"; exit 1; }
[ "$(jq -r .name .claude-plugin/marketplace.json)" = "science-ultrapowers" ] || { echo "marketplace.json name is $(jq -r .name .claude-plugin/marketplace.json)"; exit 1; }
[ "$(jq -r '.plugins[0].name' .claude-plugin/marketplace.json)" = "science-ultrapowers" ] || { echo "marketplace plugin entry name is wrong"; exit 1; }
[ "$(jq -r '.plugins[0].source' .claude-plugin/marketplace.json)" = "./" ] || { echo "marketplace plugin source is not ./"; exit 1; }
v=$(jq -r .version .claude-plugin/plugin.json)
[ "$v" = "$expected" ] || { echo "plugin.json version is $v, RELEASE-NOTES.md top release is $expected"; exit 1; }
m=$(jq -r '.plugins[0].version' .claude-plugin/marketplace.json)
[ "$m" = "$expected" ] || { echo "marketplace.json version is $m, RELEASE-NOTES.md top release is $expected"; exit 1; }
[ "$(jq -r '.files | length' .version-bump.json)" = "2" ] || { echo ".version-bump.json must declare exactly the two Claude Code manifests"; exit 1; }
scripts/bump-version.sh --check >/dev/null || { echo "bump-version.sh --check reports drift"; exit 1; }
echo "version-sync: ok"
