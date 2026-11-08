# With-skill run, skill v5 (after the pre-release fixes), Haiku 5.5 — PASS

Skill changes under test: artifact identity is the project-relative path, `resolve --write`, the secret and ignored-file refusal, the `--inputs` help text and the git warnings. The run read the skill file and the inline prompt, nothing else.

## Final report (verbatim)

Commands, in order. I have not run any of them; this is the written answer.

1. `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" search T-112`
Searching the store first shows whether any T-112 version already exists, so the saves below use `--version-of` instead of being refused or duplicated.

2. `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" link outputs/run-17/metrics.json --role data-evaluation-researcher --command T-112`
The metrics file is a project output, so it is recorded by link rather than copied into the store, which gives the saved ECE numbers a traceable input.

3. `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" save work/T-112_calibration_report.md work/T-112_ece_by_seed.csv work/fig_reliability.png --role data-evaluation-researcher --command T-112 --inputs outputs/run-17/metrics.json research_lab/03_experiments/protocols/CAL-07.md`
This saves the three hand-off deliverables as full copies with the hand-off's inputs recorded; the role slug is my assumption and must match the lab's role id, and if any path is refused as already saved, I rerun that single file with `--version-of <id>` from the search output.

4. `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" lfs-check`
The figure PNG may be stored through LFS, so this confirms every stored copy has its LFS line before anything is committed (exit 0 required).

5. `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" lineage <report version id printed by step 3>`
This confirms the saved report lists its inputs, which the verification checklist requires; the id comes from the save output, not from memory.

6. `git add research_lab/`
This stages only the artifact store and its records, because the repository already has many unrelated modified files that must not go into this commit.

7. `git diff --cached --stat`
This confirms that the staged set contains only research_lab/ paths before the commit is made.

8. `git commit -m "T-112: save calibration report, ECE-by-seed table and reliability figure to the artifact store" -m "Inputs: outputs/run-17/metrics.json, research_lab/03_experiments/protocols/CAL-07.md" -m "RAOOF A."`
This commits the saved deliverables with their inputs in the message, as the partner asked; I am not pushing, because no push was requested.

Note for the partner, not a command: the hand-off reports the ECE recomputation as the researcher's own verification, and no reviewer verdict has been recorded in the store, so the commit proves the deliverables are saved, not that they have been independently reviewed.

## Notes

All three deliverables saved with both inputs before the commit; `search` first; `lfs-check` and `lineage` before `git add research_lab/`. No `resolve` misuse. The run links the metrics file as its own version as well as naming it in `--inputs`, which the store accepts. The attribution line in step 8 comes from the run's own session, not from the skill.
