#!/usr/bin/env bash
# The plugin's own text keeps to the terminology standard: no not-approved term, no
# stage code, no British spelling from the list, and every listed abbreviation
# expanded at its first use in a file. The standard is
# docs/science-ultrapowers/terminology.md; tests/terminology-allow.txt lists the
# paths still to be renamed during phase 0. TERMINOLOGY_STANDARD and
# TERMINOLOGY_ALLOW override the two paths (the test of the test uses them);
# --list prints the scanned files and exits.
set -euo pipefail
cd "$(dirname "$0")/../.."
fail=0
std="${TERMINOLOGY_STANDARD:-docs/science-ultrapowers/terminology.md}"
allow="${TERMINOLOGY_ALLOW:-tests/terminology-allow.txt}"
list_only=0
[ "${1:-}" = "--list" ] && list_only=1
tab=$(printf '\t')

if [ ! -f "$std" ]; then
  echo "terminology: the standard $std is missing"
  exit 1
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
export LC_ALL=C
py=$(command -v python || command -v python3 || true)

# ---- the three lists: the fenced block after each marker comment -------------
# Output: one line per entry, "left<TAB>right" (CR trimmed, blanks ignored).
read_list() {
  awk -v marker="<!-- $1 -->" '
    { sub(/\r$/, "") }
    state == 0 { t = $0; sub(/^[ \t]+/, "", t); sub(/[ \t]+$/, "", t); if (t == marker) state = 1; next }
    state == 1 { if ($0 ~ /^[ \t]*```/) state = 2; next }
    state == 2 {
      if ($0 ~ /^[ \t]*```/) { state = 3; next }
      if ($0 ~ /^[ \t]*$/) next
      i = index($0, "=>")
      if (i > 0) { l = substr($0, 1, i - 1); r = substr($0, i + 2) } else { l = $0; r = "" }
      gsub(/^[ \t]+|[ \t]+$/, "", l); gsub(/^[ \t]+|[ \t]+$/, "", r)
      if (l != "") print l "\t" r
    }
  ' "$2"
}
{
  read_list not-approved "$std" | sed 's/^/N\t/'
  read_list spelling "$std" | sed 's/^/S\t/'
  read_list abbreviations "$std" | sed 's/^/A\t/'
} > "$tmp/lists"
for k in N S A; do
  if ! grep -q "^$k$tab" "$tmp/lists"; then
    case $k in N) n=not-approved;; S) n=spelling;; A) n=abbreviations;; esac
    echo "FAIL: $std has no entries after the marker <!-- $n -->"; fail=1
  fi
done

# ---- the matcher: one awk over a numbered file ("N<TAB>text" per line) -------
cat > "$tmp/match.awk" <<'AWK'
function isw(c) { return c ~ /^[A-Za-z0-9_]$/ }
# A slash always joins a word (a path is not a hit). A hyphen joins a word only when the
# whitespace-delimited token that holds the match also holds ".", "/", ":", "<", ">" or a
# backtick (a file name, a path, a placeholder, a code span); a hyphenated compound in
# prose ("gate-keeping") is a hit. Trailing sentence punctuation does not count.
function tokjoin(s, p, n,   l, r, tok) {
  l = p; while (l > 1 && substr(s, l - 1, 1) !~ /[ \t]/) l--
  r = p + n - 1; while (r < length(s) && substr(s, r + 1, 1) !~ /[ \t]/) r++
  tok = substr(s, l, r - l + 1)
  sub(/[.,;:!?]+$/, "", tok)
  return tok ~ /[.\/:<>`]/
}
function joins(c, s, p, n) {
  if (c == "/") return 1
  if (c == "-") return tokjoin(s, p, n)
  return isw(c)
}
function hasword(s, t,   p, i, n, b, a) {
  n = length(t); i = 1
  if (n == 0) return 0
  while ((p = index(substr(s, i), t)) > 0) {
    p = p + i - 1
    b = (p == 1) ? "" : substr(s, p - 1, 1)
    a = substr(s, p + n, 1)
    if (!joins(b, s, p, n) && !joins(a, s, p, n)) return 1
    i = p + 1
  }
  return 0
}
BEGIN {
  FS = "\t"
  while ((getline l < lists) > 0) {
    split(l, f, "\t")
    if (f[1] == "N") { nn++; nt[nn] = f[2]; nl[nn] = tolower(f[2]); ncs[nn] = (f[2] ~ /^[A-Z_]+$/) }
    else if (f[1] == "S") { ns++; st[ns] = f[2]; sl[ns] = tolower(f[2]) }
    else if (f[1] == "A") { na++; at[na] = f[2]; ae[na] = tolower(f[3]) }
  }
}
{
  ln = $1
  text = substr($0, length($1) + 2)
  low = tolower(text)
  for (i = 1; i <= nn; i++)
    if (ncs[i] ? hasword(text, nt[i]) : hasword(low, nl[i])) print label ":" ln ": not-approved term '" nt[i] "'"
  rest = text
  while (match(rest, /(^|[^A-Za-z0-9_])G[0-6]([^A-Za-z0-9_]|$)/)) {
    code = substr(rest, RSTART, RLENGTH)
    sub(/^[^G]*/, "", code); code = substr(code, 1, 2)
    if (!((ln SUBSEP code) in sc)) { sc[ln SUBSEP code] = 1; print label ":" ln ": stage code '" code "'" }
    rest = substr(rest, RSTART + RLENGTH - 1)
  }
  for (i = 1; i <= ns; i++)
    if (hasword(low, sl[i])) print label ":" ln ": British spelling '" st[i] "'"
  for (j = 1; j <= na; j++)
    if (!(j in seen) && hasword(text, at[j])) {
      seen[j] = 1
      if (index(low, ae[j]) == 0) print label ":" ln ": abbreviation '" at[j] "' not expanded at first use"
    }
}
AWK
match_numbered() { # label numbered-file
  awk -v label="$1" -v lists="$tmp/lists" -f "$tmp/match.awk" "$2"
}

# ---- numbered forms of a file (legacy-marked lines blanked, CR trimmed) ------
legacy_re='(<!-- legacy -->|# legacy|// legacy)[ \t]*$'
prep_plain() { # file -> "N<TAB>text"
  awk -v re="$legacy_re" '{ sub(/\r$/, ""); t = $0; if (t ~ re) t = ""; print NR "\t" t }' "$1"
}
prep_blockquote() { # SKILL.md -> the leading blockquote after the frontmatter
  awk -v re="$legacy_re" '
    { sub(/\r$/, "") }
    NR == 1 { if ($0 ~ /^---[ \t]*$/) { fm = 1; next } else exit }
    fm == 1 { if ($0 ~ /^---[ \t]*$/) fm = 2; next }
    fm == 2 { if ($0 ~ /^>( |$)/) { t = $0; if (t ~ re) t = ""; print NR "\t" t } else exit }
  ' "$1"
}
prep_py() { # the string constants, "line<TAB>text"
  [ -n "$py" ] || { echo "FAIL: no python or python3 on PATH" >&2; return 1; }
  "$py" -c '
import ast, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
path = sys.argv[1]
NL, CR, TAB = chr(10), chr(13), chr(9)
src = open(path, encoding="utf-8-sig", errors="replace").read()
lines = src.replace(CR + NL, NL).replace(CR, NL).split(NL)
mark = re.compile(r"(<!-- legacy -->|# legacy|// legacy)[ \t]*$")
try:
    tree = ast.parse(src)
except SyntaxError as e:
    sys.stderr.write("cannot parse " + path + ": " + str(e) + NL)
    sys.exit(3)
out = []
for n, node in enumerate(ast.walk(tree)):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        end = getattr(node, "end_lineno", node.lineno)
        if end > node.lineno:
            # A constant over several lines (a triple-quoted string or adjacent
            # literals): the source text of each physical line keeps line numbers exact.
            pieces = []
            for k in range(node.lineno, end + 1):
                raw = lines[k - 1].encode("utf-8", "replace") if k <= len(lines) else b""
                a = node.col_offset if k == node.lineno else 0
                b = node.end_col_offset if k == end else len(raw)
                pieces.append((k, raw[a:b].decode("utf-8", "replace")))
        else:
            pieces = [(node.lineno, node.value.replace(NL, " "))]
        for i, (ln, piece) in enumerate(pieces):
            piece = piece.replace(TAB, " ").replace(CR, "")
            phys = lines[ln - 1] if 0 < ln <= len(lines) else ""
            if mark.search(phys) or mark.search(piece):
                continue
            out.append((ln, n, i, piece))
out.sort()
for ln, _, _, piece in out:
    print(str(ln) + TAB + piece)
' "$1"
}
cat > "$tmp/ticks.awk" <<'AWK'
# The backtick (template) literals of a JavaScript file, "line<TAB>text", one record per
# physical line of a literal, each labeled with its own line number. The ${...} parts are
# code and are skipped. Quoted strings, regular expressions and comments outside a literal
# are skipped so that a backtick inside them never opens a literal.
BEGIN { tick = 0; depth = 0; cmt = 0; OFS = "\t" }
{
  line = $0; n = length(line); out = ""; i = 1; prev = ""
  while (i <= n) {
    c = substr(line, i, 1); d = substr(line, i + 1, 1)
    if (cmt) {
      if (c == "*" && d == "/") { cmt = 0; i += 2 } else i++
      continue
    }
    if (tick) {
      if (depth > 0) {
        if (c == "{") depth++
        else if (c == "}") depth--
        i++
      } else if (c == "\\") { out = out ((d == "n" || d == "t" || d == "r") ? " " : d); i += 2 }
      else if (c == "$" && d == "{") { depth = 1; i += 2 }
      else if (c == "`") { print NR, out; out = ""; tick = 0; prev = "`"; i++ }
      else { out = out c; i++ }
      continue
    }
    if (c == "'" || c == "\"") {
      j = i + 1
      while (j <= n) { e = substr(line, j, 1); if (e == "\\") { j += 2; continue } if (e == c) break; j++ }
      i = j + 1; prev = c; continue
    }
    if (c == "`") { tick = 1; out = ""; i++; continue }
    if (c == "/" && d == "/") break
    if (c == "/" && d == "*") { cmt = 1; i += 2; continue }
    if (c == "/" && (prev == "" || index("(,=:[!&|?{};+-*%<>~^", prev) > 0)) {
      j = i + 1; cls = 0
      while (j <= n) {
        e = substr(line, j, 1)
        if (e == "\\") { j += 2; continue }
        if (e == "[") cls = 1
        else if (e == "]") cls = 0
        else if (e == "/" && !cls) break
        j++
      }
      i = j + 1; prev = "/"; continue
    }
    if (c != " " && c != "\t") prev = c
    i++
  }
  if (tick) print NR, out
}
AWK
prep_literals() { # .mjs and .ps1: the quoted literals; .mjs also the backtick literals, "line<TAB>text"
  awk -v re="$legacy_re" '{ sub(/\r$/, ""); t = $0; if (t ~ re) t = ""; print t }' "$1" > "$tmp/lit.src"
  {
    grep -n -o -E "\"[^\"]*\"|'[^']*'" "$tmp/lit.src" | sed 's/^\([0-9][0-9]*\):/\1\t/' || true
    case "$1" in *.mjs) awk -f "$tmp/ticks.awk" "$tmp/lit.src" | tr -d '\r' ;; esac
  } | sort -n -s -t "$tab" -k1,1
}

# ---- the scanned set: "kind<TAB>path" ----------------------------------------
kept=" systematic-debugging test-driven-development verification-before-completion requesting-code-review receiving-code-review dispatching-parallel-agents writing-skills "
# Adopted skills whose whole body was reworded into the standard at the researcher's request: scanned in full.
reworded=" investigating-anomalous-results establishing-feasibility-first "
{
  for d in skills/*/; do
    n=$(basename "$d")
    [ -f "skills/$n/SKILL.md" ] || continue
    if [ -f "skills/$n/PROVENANCE.md" ] && case "$reworded" in *" $n "*) true;; *) false;; esac; then
      printf 'plain\t%s\n' "skills/$n/SKILL.md"
    elif [ -f "skills/$n/PROVENANCE.md" ]; then
      printf 'blockquote\t%s\n' "skills/$n/SKILL.md"
    else
      case "$kept" in *" $n "*) ;; *) printf 'plain\t%s\n' "skills/$n/SKILL.md";; esac
    fi
  done
  for f in agents/*.md; do if [ -f "$f" ]; then printf 'plain\t%s\n' "$f"; fi; done
  if [ -d skills/initializing-a-research-lab/templates ]; then
    find skills/initializing-a-research-lab/templates -type f | sort | sed 's/^/plain\t/'
  fi
  for f in README.md CONTRIBUTING.md AGENTS.md docs/testing.md RELEASE-NOTES.md \
    .claude-plugin/plugin.json .claude-plugin/marketplace.json \
    hooks/session-start hooks/memory-nudge hooks/memory-postcompact; do
    if [ -f "$f" ]; then printf 'plain\t%s\n' "$f"; fi
  done
  if [ -d hooks/lib ]; then find hooks/lib -maxdepth 1 -type f | sort | sed 's/^/plain\t/'; fi
  # The Python files under skills/*/scripts/ at any depth, except a tests/ folder and the adopted skills.
  find skills -mindepth 3 -type f -name '*.py' -path 'skills/*/scripts/*' ! -path '*/tests/*' | LC_ALL=C sort | while IFS= read -r f; do
    if [ ! -f "${f%%/scripts/*}/PROVENANCE.md" ]; then printf 'py\t%s\n' "$f"; fi
  done
  for f in skills/*/scripts/*.mjs skills/*/scripts/*.ps1; do
    if [ -f "$f" ]; then printf 'literals\t%s\n' "$f"; fi
  done
  for f in docs/science-ultrapowers/specs/2026-11-08-research-lifecycle-design.md \
    docs/science-ultrapowers/plans/2026-11-08-research-lifecycle.md; do
    if [ -f "$f" ]; then printf 'plain\t%s\n' "$f"; fi
  done
} > "$tmp/scanset"

if [ "$list_only" = 1 ]; then cat "$tmp/scanset"; exit 0; fi

# ---- the allow-list ----------------------------------------------------------
: > "$tmp/allowed"
if [ -f "$allow" ]; then
  tr -d '\r' < "$allow" | sed -e 's/^[ \t]*//' -e 's/[ \t]*$//' | grep -v -E '^(#|$)' > "$tmp/allowed" || true
fi
is_allowed() { grep -qxF -- "$1" "$tmp/allowed"; }
: > "$tmp/allowed_hits"   # one path per line, per hit

# ---- the scan ----------------------------------------------------------------
while IFS="$tab" read -r kind path; do
  [ -n "$path" ] || continue
  case $kind in
    plain) prep_plain "$path" > "$tmp/num" ;;
    blockquote) prep_blockquote "$path" > "$tmp/num" ;;
    py) prep_py "$path" > "$tmp/num" || { echo "FAIL: cannot extract the string constants of $path"; fail=1; continue; } ;;
    literals) prep_literals "$path" > "$tmp/num" ;;
  esac
  match_numbered "$path" "$tmp/num" | awk '!seen[$0]++' > "$tmp/hits"
  if is_allowed "$path"; then
    while IFS= read -r _; do echo "$path" >> "$tmp/allowed_hits"; done < "$tmp/hits"
  elif [ -s "$tmp/hits" ]; then
    cat "$tmp/hits"; fail=1
  fi
done < "$tmp/scanset"

while IFS= read -r p; do
  [ -n "$p" ] || continue
  if [ ! -e "$p" ]; then
    echo "allow-list entry does not exist: $p"; fail=1
  elif ! grep -qxF -- "$p" "$tmp/allowed_hits"; then
    echo "allow-list entry has no remaining hit: $p"; fail=1
  fi
done < "$tmp/allowed"

# ---- the positive control ----------------------------------------------------
ctl_ok=1
cut -f1,2 "$tmp/lists" | grep -qix -E "N${tab}ledger" || { echo "FAIL: the control needs 'ledger' on the not-approved list"; ctl_ok=0; }
cut -f1,2 "$tmp/lists" | grep -qix -E "S${tab}analyse" || { echo "FAIL: the control needs 'analyse' on the spelling list"; ctl_ok=0; }
cut -f1,2 "$tmp/lists" | grep -qx -E "A${tab}RQ" || { echo "FAIL: the control needs 'RQ' on the abbreviations list"; ctl_ok=0; }
if [ "$ctl_ok" = 1 ]; then
  printf '%s\n' 'at G3 now' 'the ledger row' 'we analyse it' 'the RQ' > "$tmp/control.txt"
  prep_plain "$tmp/control.txt" > "$tmp/control.num"
  match_numbered control "$tmp/control.num" > "$tmp/control.hits"
  n=$(wc -l < "$tmp/control.hits" | tr -d ' ')
  if [ "$n" != 4 ] \
    || ! grep -q "stage code 'G3'" "$tmp/control.hits" \
    || ! grep -qi "not-approved term 'ledger'" "$tmp/control.hits" \
    || ! grep -qi "British spelling 'analyse'" "$tmp/control.hits" \
    || ! grep -q "abbreviation 'RQ' not expanded" "$tmp/control.hits"; then
    echo "FAIL: the positive control expected four hits (stage code, term, spelling, abbreviation) and found $n:"
    sed 's/^/  /' "$tmp/control.hits"
    ctl_ok=0
  fi
fi
# The second control: a hyphen joins a word only inside a file name or a path.
if cut -f1,2 "$tmp/lists" | grep -qix -E "N${tab}gate"; then
  printf '%s\n' 'the gate-keeping step' 'see `ledger-based.md`' > "$tmp/control2.txt"
  prep_plain "$tmp/control2.txt" > "$tmp/control2.num"
  match_numbered control2 "$tmp/control2.num" > "$tmp/control2.hits"
  n=$(wc -l < "$tmp/control2.hits" | tr -d ' ')
  if [ "$n" != 1 ] || ! grep -q "^control2:1: not-approved term 'gate'" "$tmp/control2.hits"; then
    echo "FAIL: the hyphen control expected one hit ('gate' on line 1, none on line 2) and found $n:"
    sed 's/^/  /' "$tmp/control2.hits"
    ctl_ok=0
  fi
else
  echo "FAIL: the hyphen control needs 'gate' on the not-approved list"; ctl_ok=0
fi
[ "$ctl_ok" = 1 ] || fail=1

[ "$fail" = 0 ] && echo "terminology: ok"
exit $fail
