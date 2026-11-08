#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
out=$(CLAUDE_PLUGIN_ROOT="$PWD" bash hooks/session-start)
echo "$out" | jq -e '.hookSpecificOutput.hookEventName == "SessionStart"' >/dev/null || { echo "hook output is not a SessionStart hookSpecificOutput"; exit 1; }
ctx=$(echo "$out" | jq -r '.hookSpecificOutput.additionalContext')
n=${#ctx}
[ "$n" -lt 9000 ] || { echo "context is $n chars, limit 9000"; exit 1; }
case "$ctx" in *"You have science-ultrapowers."*) ;; *) echo "wrapper text missing"; exit 1;; esac
case "$ctx" in *"name: using-science-ultrapowers"*) ;; *) echo "skill body missing"; exit 1;; esac
echo "$out" | jq -e 'has("additional_context") | not' >/dev/null || { echo "hook output also carries additional_context"; exit 1; }
jq -e '.hooks.SessionStart[0].matcher == "startup|clear|compact"' hooks/hooks.json >/dev/null || { echo "hooks.json SessionStart matcher is not startup|clear|compact"; exit 1; }
jq -e '.hooks.SessionStart[0].hooks[0] | has("powershell") | not' hooks/hooks.json >/dev/null || { echo "hooks.json still has the powershell key"; exit 1; }

# The scaffold-version line: three cases, each run from a throwaway folder
# with the hook called by its absolute path (the hook walks up from $PWD).
repo="$PWD"
plugin_version=$(jq -r '.version' .claude-plugin/plugin.json)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
marker="The lab scaffold was written by plugin"
ctx_in() { (cd "$1" && bash "$repo/hooks/session-start") | jq -r '.hookSpecificOutput.additionalContext'; }

mkdir -p "$tmp/nolab"
case "$(ctx_in "$tmp/nolab")" in *"$marker"*) echo "scaffold line printed where no lab exists"; exit 1;; esac

mkdir -p "$tmp/same/research_lab" "$tmp/same/sub/dir"
printf '{\n  "pluginVersion": "%s"\n}\n' "$plugin_version" > "$tmp/same/research_lab/lab.json"
case "$(ctx_in "$tmp/same")" in *"$marker"*) echo "scaffold line printed for a lab of the same version"; exit 1;; esac

mkdir -p "$tmp/old/research_lab" "$tmp/old/sub/dir"
printf '{\n  "pluginVersion": "0.0.1"\n}\n' > "$tmp/old/research_lab/lab.json"
want="$marker 0.0.1; this plugin is $plugin_version: run science-ultrapowers:initializing-a-research-lab to upgrade."
case "$(ctx_in "$tmp/old")" in *"$want"*) ;; *) echo "scaffold line missing for an older lab"; exit 1;; esac
case "$(ctx_in "$tmp/old/sub/dir")" in *"$want"*) ;; *) echo "scaffold line missing when the lab is in a parent folder"; exit 1;; esac
case "$(ctx_in "$tmp/old")" in *"name: using-science-ultrapowers"*) ;; *) echo "bootstrap missing next to the scaffold line"; exit 1;; esac
echo "session-start: ok"
