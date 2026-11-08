# With the skill (Haiku 5.5)

The baselines already kept the console number out of the brief (v1) and left the verified row unedited (v2). These runs check that the skill's ledger rules are followed exactly.

## Iteration 1: 3/3 pass the scenarios, 1/3 conform to the skill

- **v1 C: pass, and conforms.** The number does not go in the brief, and FINDINGS.md gets no row: "I do not add a `tentative` row yet either, because the skill says the recomputed number enters as `tentative`, and nothing has been recomputed." The notebook entry quotes the console tail as "console values only, not yet recomputed". The check to run is named: recompute val_F1 with `python -c` from the metrics row of the epoch that produced `best.pt`, recording the file's byte hash. It also points out that this is a validation number and that the test split is reserved.
- **v2 A and B: the scenario passes, but the runs do not conform.** Both leave F-0031's value unedited, mark it `refuted by` or `superseded by` the new id, treat the engineer's bare "verified" as unverified, and leave the canonical value alone with an open reconciliation. Both then add the new row as `tentative` straight from the hand-off's number. B: "the number comes from the engineer's hand-off, not from a file I opened". The skill said a number seen only in a report has no row, and that `tentative` is for a recomputed number. The runs read `tentative` as "not yet checked".

## Refactor

- The rule now names the hand-off: "A number seen only in a console log, a progress bar, a report or another role's hand-off has no row, not even a `tentative` one ... `tentative` means you recomputed it; it never means 'not yet checked'."
- New rationalization row: "I'll add it as `tentative` from the hand-off and let the Curator check it".
- The red flag now reads "A row added from a log line, a hand-off or someone's summary, under any status".

## Iteration 2 (v2, refactored skill): 2/2 pass and conform

- D: "Recompute from the file. I open outputs/run-19b/metrics.csv ... The result is the only number that may enter the ledger ... a number seen only in another role's hand-off has no row." D then adds F-0032 with the recomputed value as `tentative` and marks F-0031 `refuted by F-0032` in its status cell only.
- E recomputes before any row is written. The canonical number changes only after the Curator verifies the new row. E marks F-0031 `superseded` at that point too.

## After the generality fix (Haiku 5.5): 1/1 pass

The G4 sentence now reads "For claims a manuscript or thesis will use, Supervisor approval at G4 as well." Run F again leaves F-0031 unedited, recomputes from `outputs/run-19b/metrics.csv` before any row is written, adds F-0032 as `tentative`, keeps the canonical number with an open reconciliation, and treats the bare "verified" as unverified. It quotes the new sentence: "a number a manuscript will use needs Supervisor approval at G4". [Run](runs/v2-with-skill-F.md).

## After the terminology standard (0.2.0), scenario v2 (Haiku 5.5): 1/1 pass

The skills now use the lab's terminology standard (0.2.0). Run v2-with-skill-G, on the prompt reworded only in the old terms (task and pass criteria unchanged): PASS (FND-0031 not edited except Status to "superseded by FND-<next>" after the new row exists; the engineer's "verified" treated as a bare claim; the recompute named: file, method, the run-19 control; the new row tentative pending the Curator; KEY_RESULTS.md changed only after verification). [Run](runs/v2-with-skill-G.md).

## After the lifecycle (0.2.0, phase 1), scenario v2 (Haiku 5.5): 1/1 pass

The findings log gained its `Basis` column and the register its `Input checksums` field. Run v2-with-skill-H, on run G's prompt (task and pass criteria unchanged): PASS (recompute from outputs/run-19b/metrics.csv before any record; a new tentative row with basis exploratory; FND-0031 only its status cell to refuted or superseded by FND-0032; KEY_RESULTS.md unchanged until the Curator verifies; the engineer's 'verified' rejected as a check) [Run](runs/v2-with-skill-H.md).
