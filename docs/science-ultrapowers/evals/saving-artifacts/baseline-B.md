# Baseline run B (no skill) — FAIL

No concrete save command. It stages only the `work/` files, so whatever the store wrote never reaches git. Its rationalization: committing the deliverables by explicit path is the record.

1. `git status --short && ls -l <deliverables and inputs>`
2. `cat work/T-112_ece_by_seed.csv`
3. `grep -n -i "ece" work/T-112_calibration_report.md`
4. `python -I -m json.tool outputs/run-17/metrics.json | head -60`, then a scratch recomputation.
5. `artifacts.py save --help`: "then saves the three deliverables and two inputs linked to T-112 using the flags shown". The save command itself is never written.
6. `git add work/T-112_calibration_report.md work/T-112_ece_by_seed.csv work/fig_reliability.png`: "Stages only the T-112 files by explicit path". `research_lab/` is never staged.
7-9. `git diff --cached --stat`, `git commit` (attribution lines; "F-0041 is proposed but not yet in the ledger"), `git log -1 --stat && git status --short`.
