# With-skill run A (skill v2 loaded) — PASS

Links both inputs and saves each deliverable with both ids as `--inputs`. Searches first; checks lineage, checks and lfs-check; commits `research_lab/` only. It leaves out the required `--role`/`--command`, which v3 of the skill now names.

1. `artifacts.py --help`: confirm option spellings.
2. `artifacts.py search T-112 calibration`: "The Iron Law says search before recomputing".
3-4. `artifacts.py link outputs/run-17/metrics.json` and `link research_lab/03_experiments/protocols/CAL-07.md`: "recorded rather than copied ... the printed id is passed to `--inputs`".
5-7. `artifacts.py save work/<each deliverable> --inputs <metrics-id> <CAL-07-id>`: "The orchestrator saves hand-off deliverables; roles never write the store."
8. `artifacts.py search T-112`: "a folder listing does not count".
9. `artifacts.py lineage <report-id>`
10. `artifacts.py check list --all`
11. `artifacts.py lfs-check; echo "exit=$?"`
12-16. `git status --short research_lab/`, `git add research_lab/`, `git diff --cached --stat`, `git commit -F - <<'EOF'` (attribution lines), `git log -1 --stat`.

"The store checks should not be skipped to save time; they take seconds."
