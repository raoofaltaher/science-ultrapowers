# With-skill run, skill v3 (Sonnet 5.5) — PASS

v3 names `--role` and `--command` and adds the rationalization "It's committed, so it's recorded". The run uses both and quotes the rationalization: "'committed' is not 'recorded' (git keeps bytes, not inputs)."

1. `ART search "T-112 calibration"`: check for an earlier version to chain with `--version-of`.
2-3. `ART link` for each hand-off input.
4-6. `ART save work/<each deliverable> --role data-evaluation-researcher --command T-112 --inputs <metrics id>,<CAL-07 id>`.
7. `ART resolve work/T-112_calibration_report.md`, "only if the report contains `{{artifact:...}}` markers".
8. `ART search "T-112"`, then `ART lineage <report version id>`.
9. `ART lfs-check`: "If `save` warned, I run `git lfs install` first".
10-11. `git add research_lab/ && git status --short`, `git commit` (attribution lines).

Finding: `--inputs a,b` (comma-separated). Validate-first refuses it with `unknown input` and writes nothing, so the failure is loud, not data loss. Pass B adds a hint to the error (B19: "separate inputs with spaces, not commas").
