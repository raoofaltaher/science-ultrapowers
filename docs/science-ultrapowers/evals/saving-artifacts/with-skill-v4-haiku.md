# With-skill run, skill v4, the shipped text (Haiku 5.5) — PASS

1. `artifacts.py search T-112`: chain with `--version-of` instead of making a new filename.
2. `artifacts.py save --help`: confirm the flag syntax for `--role`, `--command` and `--inputs`.
3-5. `artifacts.py save work/<each deliverable> --role data-evaluation-researcher --command T-112 --inputs outputs/run-17/metrics.json research_lab/03_experiments/protocols/CAL-07.md`: "the workspace is scratch, the store is the record".
6. `artifacts.py lineage <report version id>`
7. `artifacts.py check list --all`: "none were filed, so the stand-up must not say 'reviewed'".
8. `artifacts.py lfs-check`: must exit 0 before the commit.
9-11. `git add research_lab/`, `git diff --cached --stat`, `git commit` (inputs and "no reviewer check yet" in the body; attribution lines).

No `resolve` call: v4's descriptive citing row (`resolve <file>` turns markers into links …) does not trigger it when the hand-off has no markers.
