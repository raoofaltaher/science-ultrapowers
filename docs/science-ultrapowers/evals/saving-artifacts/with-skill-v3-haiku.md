# With-skill run, skill v3 (Haiku 5.5) — PASS, with one misuse that changed the skill

1. `artifacts.py --help`: confirm flags.
2. `artifacts.py search T-112`: search before saving.
3. `artifacts.py link outputs/run-17/metrics.json`
4-6. `artifacts.py save work/<each deliverable> --role data-evaluation-researcher --command T-112 --inputs outputs/run-17/metrics.json research_lab/03_experiments/protocols/CAL-07.md`
7. `artifacts.py resolve <report version id>`: a misuse, since `resolve` takes a file. It fails loudly with "not a file".
8-10. `search T-112`, `lineage <report version id>`, `check list --all`, `lfs-check`.
11-12. `git status --short research_lab/`, `git add research_lab/ && git commit` (attribution lines).

Both v3 runs called `resolve` although the hand-off mentions no markers. v3 had shortened the citing row to the imperative "Run `resolve` before the document leaves the lab"; v2's descriptive "`resolve` turns markers into links before the document leaves the lab" never triggered it in three runs. v4 restores the descriptive form and names the argument: "`resolve <file>` turns markers into links before it leaves the lab."
