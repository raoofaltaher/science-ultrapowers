#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
out=$(CLAUDE_PLUGIN_ROOT="$PWD" bash hooks/session-start)
echo "$out" | jq -e '.hookSpecificOutput.hookEventName == "SessionStart"' >/dev/null || { echo "hook output is not a SessionStart hookSpecificOutput"; exit 1; }
ctx=$(echo "$out" | jq -r '.hookSpecificOutput.additionalContext')
n=${#ctx}
[ "$n" -lt 9000 ] || { echo "context is $n chars, limit 9000"; exit 1; }
case "$ctx" in *"You have science-ultrapowers."*) ;; *) echo "wrapper text missing"; exit 1;; esac
case "$ctx" in *"session primer"*) ;; *) echo "wrapper text does not call the skill the session primer"; exit 1;; esac
case "$ctx" in *bootstrap*|*Bootstrap*) echo "wrapper text still says bootstrap"; exit 1;; esac
case "$ctx" in *"name: using-science-ultrapowers"*) ;; *) echo "skill body missing"; exit 1;; esac
echo "$out" | jq -e 'has("additional_context") | not' >/dev/null || { echo "hook output also carries additional_context"; exit 1; }
jq -e '.hooks.SessionStart[0].matcher == "startup|clear|compact"' hooks/hooks.json >/dev/null || { echo "hooks.json SessionStart matcher is not startup|clear|compact"; exit 1; }
jq -e '.hooks.SessionStart[0].hooks[0] | has("powershell") | not' hooks/hooks.json >/dev/null || { echo "hooks.json still has the powershell key"; exit 1; }

# The lab set-up version line and the old-layout line: each case runs from a
# throwaway folder with the hook called by its absolute path (the hook walks up
# from $PWD).
repo="$PWD"
plugin_version=$(jq -r '.version' .claude-plugin/plugin.json)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
marker="The lab set-up was written by plugin"
oldlayout="this lab uses the 0.1 layout; run science-ultrapowers:initializing-a-research-lab to migrate it"
ctx_in() { (cd "$1" && bash "$repo/hooks/session-start") | jq -r '.hookSpecificOutput.additionalContext'; }

mkdir -p "$tmp/nolab"
case "$(ctx_in "$tmp/nolab")" in *"$marker"*) echo "set-up line printed where no lab exists"; exit 1;; esac
case "$(ctx_in "$tmp/nolab")" in *"$oldlayout"*) echo "old-layout line printed where no lab exists"; exit 1;; esac

mkdir -p "$tmp/same/research_lab" "$tmp/same/sub/dir"
printf '{\n  "pluginVersion": "%s"\n}\n' "$plugin_version" > "$tmp/same/research_lab/lab.json"
case "$(ctx_in "$tmp/same")" in *"$marker"*) echo "set-up line printed for a lab of the same version"; exit 1;; esac
case "$(ctx_in "$tmp/same")" in *"$oldlayout"*) echo "old-layout line printed for a lab with the new layout"; exit 1;; esac

mkdir -p "$tmp/old/research_lab" "$tmp/old/sub/dir"
printf '{\n  "pluginVersion": "0.0.1"\n}\n' > "$tmp/old/research_lab/lab.json"
want="$marker 0.0.1; this plugin is $plugin_version: run science-ultrapowers:initializing-a-research-lab to upgrade."
case "$(ctx_in "$tmp/old")" in *"$want"*) ;; *) echo "set-up line missing for an older lab"; exit 1;; esac
case "$(ctx_in "$tmp/old/sub/dir")" in *"$want"*) ;; *) echo "set-up line missing when the lab is in a parent folder"; exit 1;; esac
case "$(ctx_in "$tmp/old")" in *"name: using-science-ultrapowers"*) ;; *) echo "session primer missing next to the set-up line"; exit 1;; esac
case "$(ctx_in "$tmp/old")" in *scaffold*) echo "set-up line still says scaffold"; exit 1;; esac

# A lab with a numbered folder under research_lab/ is the 0.1 layout: the old-layout
# line prints, whether or not the version differs, and from a folder below it.
mkdir -p "$tmp/legacy/research_lab/02_findings_ledger" "$tmp/legacy/sub/dir"
printf '{\n  "pluginVersion": "%s"\n}\n' "$plugin_version" > "$tmp/legacy/research_lab/lab.json"
case "$(ctx_in "$tmp/legacy")" in *"$oldlayout"*) ;; *) echo "old-layout line missing for a numbered folder"; exit 1;; esac
case "$(ctx_in "$tmp/legacy/sub/dir")" in *"$oldlayout"*) ;; *) echo "old-layout line missing when the lab is in a parent folder"; exit 1;; esac
case "$(ctx_in "$tmp/legacy")" in *"$marker"*) echo "set-up line printed for a lab of the same version"; exit 1;; esac
mkdir -p "$tmp/legacyold/research_lab/00_project_knowledge"
printf '{\n  "pluginVersion": "0.0.1"\n}\n' > "$tmp/legacyold/research_lab/lab.json"
both=$(ctx_in "$tmp/legacyold")
case "$both" in *"$oldlayout"*"$marker 0.0.1"*|*"$marker 0.0.1"*"$oldlayout"*) ;; *) echo "both lines expected for an old version in the old layout"; exit 1;; esac
# A numbered folder beside the new folders is still reported (a half-migrated lab).
mkdir -p "$tmp/half/research_lab/findings" "$tmp/half/research_lab/03_experiments"
printf '{\n  "pluginVersion": "%s"\n}\n' "$plugin_version" > "$tmp/half/research_lab/lab.json"
case "$(ctx_in "$tmp/half")" in *"$oldlayout"*) ;; *) echo "old-layout line missing for a half-migrated lab"; exit 1;; esac
# A folder with a number in its name that is not a numbered folder does not count.
mkdir -p "$tmp/other/research_lab/data_2026"
printf '{\n  "pluginVersion": "%s"\n}\n' "$plugin_version" > "$tmp/other/research_lab/lab.json"
case "$(ctx_in "$tmp/other")" in *"$oldlayout"*) echo "old-layout line printed for an unrelated folder"; exit 1;; esac
# A researcher's own numbered folder is not one of the ten 0.1 folders: the notice stays silent.
mkdir -p "$tmp/rawdata/research_lab/10_raw_data" "$tmp/rawdata/research_lab/findings"
printf '{\n  "pluginVersion": "%s"\n}\n' "$plugin_version" > "$tmp/rawdata/research_lab/lab.json"
case "$(ctx_in "$tmp/rawdata")" in *"$oldlayout"*) echo "old-layout line printed for a researcher's 10_raw_data folder"; exit 1;; esac
# A lab with only 04_reviews/ left (half migrated) is still the 0.1 layout.
mkdir -p "$tmp/onlyreviews/research_lab/04_reviews" "$tmp/onlyreviews/research_lab/findings"
printf '{\n  "pluginVersion": "%s"\n}\n' "$plugin_version" > "$tmp/onlyreviews/research_lab/lab.json"
case "$(ctx_in "$tmp/onlyreviews")" in *"$oldlayout"*) ;; *) echo "old-layout line missing for a lab with only 04_reviews/ left"; exit 1;; esac
echo "session-start: ok"
