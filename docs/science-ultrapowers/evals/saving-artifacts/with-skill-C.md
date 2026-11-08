# With-skill run C (skill v2 loaded; Haiku 5.5) — PASS

Saves all three deliverables with both hand-off inputs before committing; checks lineage and lfs-check first. (Omitted --role/--command but runs `save --help` first to get the option names.)

1. `artifacts.py save --help` — exact option names.
2. `artifacts.py search "T-112"` — search before saving, so a re-save becomes --version-of.
3. `artifacts.py link outputs/run-17/metrics.json` — records the input without copying it.
4-6. `artifacts.py save work/<each deliverable> --inputs outputs/run-17/metrics.json research_lab/03_experiments/protocols/CAL-07.md` — "the orchestrator saves each hand-off deliverable with the hand-off's Inputs recorded as --inputs".
7. `artifacts.py lineage work/T-112_calibration_report.md` — checklist: every version lists its inputs.
8. `artifacts.py check list --all` — checklist: reviewer verdicts are checks.
9. `artifacts.py lfs-check; echo "exit=$?"` — checklist: lfs-check exits 0.
10-13. `git status --short research_lab/`, `git add research_lab/`, `git commit` (attribution lines), `git log -1 --stat`.

"I would not tell anyone T-112 is done until steps 8 and 9 come back clean ... the honest message for the meeting is 'deliverables saved, verification pending'."
