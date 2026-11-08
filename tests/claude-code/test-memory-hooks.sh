#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
root="$PWD"
tmp=$(mktemp -d)
links=()
cleanup() {
  # Junctions and symlinks go first, with commands that never touch the target.
  local l
  for l in "${links[@]+"${links[@]}"}"; do
    if command -v cygpath >/dev/null 2>&1; then
      cmd //c rmdir "$(cygpath -w "$l")" >/dev/null 2>&1 || true
    else
      rm -f "$l" || true
    fi
  done
  rm -rf "$tmp"
}
trap cleanup EXIT
fail() { echo "memory-hooks: $*"; exit 1; }

mkdir -p "$tmp/proj/research_lab/memory" "$tmp/proj/src/deep" "$tmp/empty"
printf '# Lab memory: index\n' > "$tmp/proj/research_lab/memory/MEMORY.md"
before=$(find "$tmp" | sort)

# (a) nudge from a deep directory
out=$(printf '{"cwd":"%s"}' "$tmp/proj/src/deep" | bash hooks/memory-nudge)
echo "$out" | jq -e '.hookSpecificOutput.hookEventName == "UserPromptSubmit"' >/dev/null || fail "nudge is not a UserPromptSubmit hookSpecificOutput"
ctx=$(echo "$out" | jq -r '.hookSpecificOutput.additionalContext')
case "$ctx" in *"science-ultrapowers:remembering-for-the-lab"*) ;; *) fail "nudge does not name the skill";; esac
case "$ctx" in *"../../research_lab/memory/"*) ;; *) fail "nudge does not carry the relative store path";; esac
case "$ctx" in *"gate it and save it"*) ;; *) fail "nudge does not tell the session to gate and save";; esac
echo "$out" | jq -e 'has("additionalContext") or has("additional_context") | not' >/dev/null || fail "nudge carries a top-level context key"

# (b) no store, and a cwd that does not exist: silent
rc=0; out=$(printf '{"cwd":"%s"}' "$tmp/empty" | bash hooks/memory-nudge) || rc=$?
[ "$rc" -eq 0 ] || fail "nudge exit $rc outside a store"
[ -z "$out" ] || fail "nudge printed outside a store"
rc=0; out=$(printf '{"cwd":"%s"}' "$tmp/nope" | bash hooks/memory-nudge) || rc=$?
[ "$rc" -eq 0 ] || fail "nudge exit $rc for a missing cwd"
[ -z "$out" ] || fail "nudge printed for a missing cwd"

# (c) post-compaction hook
for input in "$(printf '{"cwd":"%s","source":"compact"}' "$tmp/proj")" "$(printf '{"cwd":"%s"}' "$tmp/proj")"; do
  out=$(printf '%s' "$input" | bash hooks/memory-postcompact)
  echo "$out" | jq -e '.hookSpecificOutput.hookEventName == "SessionStart"' >/dev/null || fail "postcompact is not a SessionStart hookSpecificOutput"
  ctx=$(echo "$out" | jq -r '.hookSpecificOutput.additionalContext')
  case "$ctx" in *compacted*) ;; *) fail "postcompact context lacks 'compacted'";; esac
  case "$ctx" in *"science-ultrapowers:remembering-for-the-lab"*) ;; *) fail "postcompact does not name the skill";; esac
  case "$ctx" in *"research_lab/memory/"*) ;; *) fail "postcompact does not name the store";; esac
done

# (d) other sources stay silent
for src in startup resume clear; do
  rc=0; out=$(printf '{"cwd":"%s","source":"%s"}' "$tmp/proj" "$src" | bash hooks/memory-postcompact) || rc=$?
  [ "$rc" -eq 0 ] || fail "postcompact exit $rc for source $src"
  [ -z "$out" ] || fail "postcompact printed for source $src"
done

# (e) the off switch governs both hooks
rc=0; out=$(printf '{"cwd":"%s"}' "$tmp/proj" | SCIENCE_ULTRAPOWERS_NO_MEMORY_NUDGE=1 bash hooks/memory-nudge) || rc=$?
[ "$rc" -eq 0 ] && [ -z "$out" ] || fail "nudge ignored the off switch"
rc=0; out=$(printf '{"cwd":"%s","source":"compact"}' "$tmp/proj" | SCIENCE_ULTRAPOWERS_NO_MEMORY_NUDGE=1 bash hooks/memory-postcompact) || rc=$?
[ "$rc" -eq 0 ] && [ -z "$out" ] || fail "postcompact ignored the off switch"
out=$(printf '{"cwd":"%s"}' "$tmp/proj" | SCIENCE_ULTRAPOWERS_NO_MEMORY_NUDGE=0 bash hooks/memory-nudge)
echo "$out" | jq -e '.hookSpecificOutput.hookEventName == "UserPromptSubmit"' >/dev/null || fail "nudge stayed silent with the switch set to 0"
for v in false OFF; do
  out=$(printf '{"cwd":"%s"}' "$tmp/proj" | SCIENCE_ULTRAPOWERS_NO_MEMORY_NUDGE=$v bash hooks/memory-nudge)
  echo "$out" | jq -e '.hookSpecificOutput.hookEventName == "UserPromptSubmit"' >/dev/null || fail "nudge stayed silent with the switch set to $v"
done
for v in yes 1; do
  rc=0; out=$(printf '{"cwd":"%s"}' "$tmp/proj" | SCIENCE_ULTRAPOWERS_NO_MEMORY_NUDGE=$v bash hooks/memory-nudge) || rc=$?
  [ "$rc" -eq 0 ] && [ -z "$out" ] || fail "nudge ignored the off switch set to $v"
done

# (f) registration
jq -e '.hooks.UserPromptSubmit[0].hooks[0].command | test("memory-nudge")' hooks/hooks.json >/dev/null || fail "hooks.json lacks the memory-nudge UserPromptSubmit hook"
jq -e '.hooks.SessionStart[1].matcher == "compact"' hooks/hooks.json >/dev/null || fail "hooks.json second SessionStart matcher is not compact"
jq -e '.hooks.SessionStart[1].hooks[0].command | test("memory-postcompact")' hooks/hooks.json >/dev/null || fail "hooks.json lacks the memory-postcompact hook"
jq -e '.hooks.SessionStart[0].matcher == "startup|clear|compact"' hooks/hooks.json >/dev/null || fail "hooks.json first SessionStart matcher changed"

# (g) a Windows-form cwd
if command -v cygpath >/dev/null 2>&1; then
  win=$(cygpath -w "$tmp/proj/src/deep")
  esc=${win//\\/\\\\}
  out=$(printf '{"cwd":"%s"}' "$esc" | bash hooks/memory-nudge)
  ctx=$(echo "$out" | jq -r '.hookSpecificOutput.additionalContext')
  case "$ctx" in *"research_lab/memory/"*) ;; *) fail "nudge ignored a Windows-form cwd";; esac
fi

# (h) through the wrapper
out=$(printf '{"cwd":"%s"}' "$tmp/proj" | bash hooks/run-hook.cmd memory-nudge)
echo "$out" | jq -e '.hookSpecificOutput.hookEventName == "UserPromptSubmit"' >/dev/null || fail "wrapper did not run the nudge"

# (i) empty stdin falls back to $PWD
out=$(cd "$tmp/proj" && bash "$root/hooks/memory-nudge" < /dev/null)
echo "$out" | jq -e '.hookSpecificOutput.hookEventName == "UserPromptSubmit"' >/dev/null || fail "nudge ignored \$PWD on empty stdin"

# (j) the hooks never write
after=$(find "$tmp" | sort)
[ "$before" = "$after" ] || fail "a hook wrote under the temp tree"

# (m) a closed stdout: exit 0 and nothing on stderr
# (n) a reader that exits early: the hook's own status is 0
for hook in memory-nudge memory-postcompact; do
  rc=0
  err=$( { printf '{"cwd":"%s","source":"compact"}' "$tmp/proj" | bash "hooks/$hook" >&-; } 2>&1 ) || rc=$?
  [ "$rc" -eq 0 ] || fail "$hook exit $rc with stdout closed"
  [ -z "$err" ] || fail "$hook wrote to stderr with stdout closed: $err"
  printf '{"cwd":"%s","source":"compact"}' "$tmp/proj" | bash "hooks/$hook" | true
  [ "${PIPESTATUS[1]}" -eq 0 ] || fail "$hook exit ${PIPESTATUS[1]} into an early-exit reader"
done

# (k, l) a cwd reached through a junction or symlink. A relative store path is
# only right when it counts ../ against the path the text is read from.
mkdir -p "$tmp/links"
make_link() { # make_link <link> <target>: 0 on success, 1 when no link can be made
  local link="$1" target="$2"
  if command -v cygpath >/dev/null 2>&1; then
    MSYS2_ARG_CONV_EXCL="*" cmd /c mklink /J "$(cygpath -w "$link")" "$(cygpath -w "$target")" >/dev/null 2>&1 || return 1
  else
    ln -s "$target" "$link" 2>/dev/null || return 1
  fi
  [ -d "$link" ] || return 1
  links+=("$link")
}
if make_link "$tmp/links/deep" "$tmp/proj/src/deep" && make_link "$tmp/links/projlink" "$tmp/proj"; then
  if command -v cygpath >/dev/null 2>&1; then
    # Through the physical path: the hook prints the long-name form, while
    # cygpath on the mktemp path can print the 8.3 short form of the same dir.
    abs="$(cygpath -m "$(cd "$tmp/proj" && pwd -P)")/research_lab/memory/"
  else
    abs="$(cd "$tmp/proj" && pwd -P)/research_lab/memory/"
  fi
  # (k) the junction points below the project: only the physical path finds it
  out=$(printf '{"cwd":"%s"}' "$tmp/links/deep" | bash hooks/memory-nudge)
  ctx=$(echo "$out" | jq -r '.hookSpecificOutput.additionalContext')
  case "$ctx" in *"$abs"*) ;; *) fail "nudge through a junction lacks the absolute store path $abs (got: $ctx)";; esac
  case "$ctx" in *"../../research_lab/memory/"*) fail "nudge through a junction counted ../ against the physical path";; esac
  # (l) the junction points at the project: the logical walk finds it
  out=$(printf '{"cwd":"%s"}' "$tmp/links/projlink/src/deep" | bash hooks/memory-nudge)
  ctx=$(echo "$out" | jq -r '.hookSpecificOutput.additionalContext')
  case "$ctx" in *"../../research_lab/memory/"*) ;; *) fail "nudge through a project junction lacks the relative store path (got: $ctx)";; esac
  case "$ctx" in *"$abs"*) fail "nudge through a project junction used an absolute path";; esac
else
  echo "memory-hooks: junction cases skipped"
fi

echo "memory-hooks: ok"
