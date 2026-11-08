# v2 baseline (no skill, Haiku 5.5) — FAIL

Prompt: [scenario-v2-based-on.md](scenario-v2-based-on.md), given inline and alone.

## Final report (verbatim)

This is a written exercise, so I ran no commands. The commands below are the ones I would run, with what I would take from each output. Nothing in this report is a result from running them.

Commands, in order:

1. `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" --help`
   Take: the exact option syntax for `lineage` and `check`, so the later calls use the right arguments.

2. Locate the report by name (a glob for `RV-0048*` under `research_lab/04_reviews/reports/`), then read it.
   Take: the Section 2 "Inputs" list, which names what the citation auditor read. This is the only source I have for what RV-0048 is based on. I would also read the findings in the report, since the ledgers do not record them.

3. `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" lineage 21e9bf3d-cdbb-4bf0-879a-4323fa71ce1c`
   Take: the upstream inputs and versions the store records for the artifact. If it returns nothing, the store has no recorded lineage for it.

4. `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" check 21e9bf3d-cdbb-4bf0-879a-4323fa71ce1c`
   Take: the verification status and any open or unaddressed items the store holds for this artifact. This is the call I would rely on for "unaddressed", in place of the raw ledger grep.

5. Only if the `check` output does not settle it: `grep 21e9bf3d research_lab/artifacts/verification_checks.jsonl` and the same grep on `dependencies.jsonl`, to confirm the id is stored under the same key. I already know these two greps print nothing, so the empty result needs a second look, not a conclusion.

What I already know, without running anything:
- RV-0048 maps to one artifact, `RV-0048_citation-auditor_T-083-G1.md`, with artifact_id `21e9bf3d-cdbb-4bf0-879a-4323fa71ce1c`.
- Neither `dependencies.jsonl` nor `verification_checks.jsonl` has a row for that id.

Answer (provisional, based only on the facts above and the plan):
- What it is based on: the store records no dependencies for this artifact, so the answer has to come from the report's Section 2 "Inputs" list, which I have not read yet.
- What is unaddressed: the ledgers have no verification-check row for this artifact, so nothing is recorded as addressed. That does not show that the findings are open. Whether anything is unaddressed depends on the report's findings and on the output of the `check` command. I cannot give that answer from what I have.
- Caveat: the empty greps could mean the artifact is not recorded under this id, so run steps 3 and 4 before relying on either answer.

## Verdict: FAIL (criteria 2 and 3)

It plans `lineage` and `check` with the artifact id (criterion 1 holds), but it reads the report first as "the only source", and its answer states "the store records no dependencies for this artifact, so the answer has to come from the report" on the strength of the grep. That is the conclusion the live acceptance session reached.
