# Baseline run C (no skill) — FAIL

The save is a placeholder ("with the flags from step 7"), so no inputs are named. It invents `check` and runs no search and no lfs-check. Stages `work/` deliverables.

1-6. `git status`, `ls -l`, `wc -l` on the CSV, two `python -c` reads of metrics.json, `grep ece` on the report: re-verify before committing.
7. `artifacts.py save --help`
8. `artifacts.py save <deliverables with the flags from step 7>`: "Registers the three deliverables with their inputs". The inputs are not written.
9. `artifacts.py check`: "Validates the store". No such form exists.
10. `git add work/T-112_* work/fig_reliability.png research_lab/artifacts/`
11-13. `git diff --cached --stat`, `git commit` (attribution lines), `git log -1 --stat`.
