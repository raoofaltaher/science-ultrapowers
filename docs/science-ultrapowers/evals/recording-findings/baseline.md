# Baselines v1 (no skill, Haiku 5.5): the core refusal already happens

All three keep F1 0.617 out of the brief's main result and point out that it is a validation number from the last epoch's console line, while `best.pt` may come from another epoch. Where they diverge from the ledger's rules:

- B and C add the number to FINDINGS.md as a "CANDIDATE (not verified)" or "provisional" finding row from the log line.
- C would add "Headline (provisional, unverified): run-23 val F1 0.617" to the brief if the partner insists. A says the same.
- The check is named loosely ("CSV row for best checkpoint"). A comes closest: "the CSV row for best.pt's epoch shows val_F1 0.6171 ... the split is named".

Verdict: v1 barely discriminates. As in PLAN-03, a harder v2 targets the two rules a baseline is most likely to break: a verified row is never edited, and a bare claim of verification counts as unverified. See scenario-v2.md.

# Baselines v2 (no skill, Haiku 5.5): 3/3 already comply

All three leave F-0031 unedited, propose a new finding that supersedes it ("Mark F-0031 as superseded by F-00XX ... Do not delete it", B), treat the engineer's "verified" as a hand-off claim ("not the recomputation the ledger requires", A), and change CANONICAL_NUMBERS.md only after a recompute. Differences are in form: A adds the new row immediately as `UNVERIFIED`; B and C add it only after the recompute.

Verdict: the control already exhibits the core discipline in both scenarios, so for this skill there is no failure for it to fix (writing-skills: "if the control doesn't exhibit the failure, there is nothing to fix"). The skill still ships, because the spec makes it the home of the ledger schema (fields, statuses, transitions) and of the name-the-check rule. Its with-skill runs check conformance to that schema and that nothing regresses.
