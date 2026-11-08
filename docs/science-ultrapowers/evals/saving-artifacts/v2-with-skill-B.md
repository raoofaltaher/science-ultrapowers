# v2 with the skill, B (Haiku 5.5) — PASS

Prompt: [scenario-v2-based-on.md](scenario-v2-based-on.md). The run read the skill file (0.1.1 text) and the prompt, nothing else.

## Final report (verbatim)

I read only the two files named in the brief: S:/science-ultrapowers/skills/saving-artifacts/SKILL.md and the exercise file in the scratchpad prompts folder. I ran no other tools, and this answer is text only, as the exercise requires.

Exercise: "What is RV-0048 based on, and what is still unaddressed on it?"

Commands, in order, and what I take from each. The script is invoked as `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" <command>`, with `--lab <research_lab>` only if run outside the project.

1. `search RV-0048`
   I take the artifact's version ids from the output. The artifact is `RV-0048_citation-auditor_T-083-G1.md`, artifact id `21e9bf3d-cdbb-4bf0-879a-4323fa71ce1c`. I pick the latest version id from the listed versions. The search is by name, so this step gives me the ids to work from. A folder listing or a grep of the file is not a search, so I do not use one.

2. `lineage <latest version id>`
   I take the inputs this version was built from (the `--inputs` recorded at save) and the checks attached to it. The inputs answer "what is it based on". The checks shown here are the first list of verdicts to examine.

3. `check list <latest version id> --all`
   I take every verdict on that version, including closed ones. A verdict is unaddressed if it has no `mark-addressed` note and its status has not been closed by `check review`. These are the open items for "what is still unaddressed".

4. Cross-check against the report at `research_lab/04_reviews/reports/`, Section 2 "Inputs".
   The report lists what the auditor read. I compare it with the lineage inputs from step 2. Any input in the report but missing from lineage is a gap to flag in the answer. The report is a secondary source, so the ledger output wins where they disagree.

What the earlier checks do and do not show. The grep of `21e9bf3d` in `dependencies.jsonl` and `verification_checks.jsonl` printing nothing proves nothing. Those ledgers are keyed by version id, not artifact id, so the empty result is not evidence that the artifact has no inputs or no verdicts. I do not report "no dependencies" or "no open checks" on that basis.

Answer, as it stands now. I cannot yet give the list of inputs or the open verdicts, because the store has not been searched. What I can state is the artifact identity: `RV-0048_citation-auditor_T-083-G1.md`, artifact id `21e9bf3d-cdbb-4bf0-879a-4323fa71ce1c`. Once steps 1 to 3 return, the answer to the partner is:
- Based on: the inputs listed by `lineage <latest version id>`, with any report Section 2 inputs missing from that list flagged as a discrepancy.
- Still unaddressed: the checks from `check list <latest version id> --all` that have no `mark-addressed` note and no closing `check review`, each named by its check id and verdict.
- If `search` returns no version for RV-0048, I say so and do not infer from the report alone.

## Verdict: PASS (3/3)

`search`, `lineage` by version id, `check list --all`; the empty grep "proves nothing" with the reason; the report is secondary and the ledger output wins.
