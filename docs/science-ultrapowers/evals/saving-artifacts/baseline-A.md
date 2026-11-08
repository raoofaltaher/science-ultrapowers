# Baseline run A (no skill) — FAIL

No `--inputs`: the save is a placeholder to be filled from `--help`. It invents a `check` subcommand form that does not exist, and runs no search and no lfs-check. Stages `work/` deliverables into git.

1. `git status --short`: separate T-112 files from unrelated changes.
2. `ls -l <deliverables and inputs>`: confirm that each file exists.
3. `cat work/T-112_ece_by_seed.csv`: check that the three seed rows are present.
4-5. A scratch script recomputes ECE from metrics.json and is run with `python -I`, to reproduce the researcher's claim.
6. `grep -n -i "ece" work/T-112_calibration_report.md`: check that the report's numbers match the CSV.
7. Read the figure: confirm that it renders.
8. `artifacts.py save --help`: get the flags rather than guess them.
9. `artifacts.py save <the three T-112 deliverables, with input and protocol links as the help text specifies>`. Lineage is intended but not written.
10. `artifacts.py check`: "confirms the artifact store is consistent". No such form exists; `check` takes add|list|review.
11. `git add -- work/T-112_*.md work/T-112_*.csv work/fig_reliability.png research_lab/artifacts`: commits the scratch copies alongside the store.
12-14. `git diff --cached --stat`, `git commit` (attribution lines), `git log -1 --stat`.
