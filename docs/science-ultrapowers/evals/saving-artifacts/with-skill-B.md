# With-skill run B (skill v2 loaded) — PASS, and it found a script defect

The same sequence as run A, but the inputs are written as `--inputs <metrics id> --inputs <CAL-07 id>`. With argparse `nargs="+"` and the default store action, the second flag replaced the first. The metrics.json lineage edge would have been dropped silently. Fixed in pass B (B16: `action="extend"`, test_repeated_inputs_flag_keeps_every_input).

1. `artifacts.py --help`
2. `artifacts.py search T-112`
3-4. `artifacts.py link` for each input
5-7. `artifacts.py save work/<each deliverable> --inputs <metrics id> --inputs <CAL-07 id>`
8. `artifacts.py lineage <report version id>`
9. `artifacts.py check list --all`: "The hand-off names no reviewer, so no checks are expected; this confirms that rather than assuming it."
10. `artifacts.py lfs-check`
11-14. `git status --short research_lab/`, `git add research_lab/`, `git commit` (message says "self-verified, not reviewed"; attribution lines), `git log -1 --stat`.
