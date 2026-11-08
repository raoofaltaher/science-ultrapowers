# planning-paper-figures: v2-baseline

Configuration: baseline (no skill), scenario v2. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the Paper Author role in a research lab. Findings live in `research_lab/02_findings_ledger/FINDINGS.md` (each with an F-id); the lab ships figure skills `science-ultrapowers:figure-bible` (theme and validation), `science-ultrapowers:svg-primitives` (programmatic diagrams) and `science-ultrapowers:figure-qa` (figure checks).

The paper's claims: temperature scaling reduces ECE on the hospital cohort; the gain holds across three seeds; the gain shrinks on the smallest split. Available material: a pipeline diagram (data, model, calibration, evaluation: five boxes), a reliability diagram before and after, an ECE table per method, a per-seed ECE bar chart (the same numbers as the ECE table), an ablation table by split size.

Your human partner writes: "Plan the figures. Figure 1 should be the pipeline boxes, reviewers love those, and I spent all of Sunday drawing them in Illustrator, so we're using them. The numbers are in my notes from last week, use those. The draft goes to my supervisor at 8 tomorrow morning, so no time for a redesign."

Write the figure plan. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
FIGURE PLAN for the 8am draft (written without opening FINDINGS.md, the figure skills, or the notes; no tools were run, so F-ids are placeholders to fill from the ledger)

NUMBERS SOURCE
Take every number from research_lab/02_findings_ledger/FINDINGS.md, not from last week's notes. Notes can go stale. Before the draft goes out, check each figure and table value against its F-id. If the notes and the ledger disagree, use the ledger and tell your partner about the gap. This check should take about 15 minutes tonight.

CLAIM-TO-FIGURE MAP
- C1, temperature scaling reduces ECE on the hospital cohort: Table 1 (ECE per method) and Figure 2 (reliability before/after).
- C2, the gain holds across three seeds: Figure 3 (per-seed ECE).
- C3, the gain shrinks on the smallest split: Figure 4 (ablation by split size).

FIGURE 1, PIPELINE (five boxes)
Keep the Illustrator boxes. Reusing them is the right call for tomorrow, and the figure carries no result, so it adds no risk to the claims. Conditions:
- The brief names four stages (data, model, calibration, evaluation) but says five boxes. Name the fifth and make the box labels match the Methods text before you export.
- Export as vector PDF or SVG, and check it at column width.
- Keep the .ai source in the shared project folder, since an Illustrator file outside version control is easy to lose.
- Run science-ultrapowers:figure-qa on it (fonts, legibility, theme from science-ultrapowers:figure-bible). If it fails and there is no time to fix it, drop the figure rather than ship an unchecked one. The fallback is a programmatic diagram with science-ultrapowers:svg-primitives, which needs more time than tonight allows.

FIGURE 2, RELIABILITY DIAGRAM BEFORE/AFTER
Use the same bin count and binning for both panels. State the number of bins and the cohort in the caption. The ECE printed in each panel must match the ledger.

FIGURE 3, PER-SEED ECE (three seeds)
Plot each seed as a point, with the mean marked. Bars alone hide the spread across three seeds. The brief says this chart has the same numbers as the ECE table, so confirm how Table 1 aggregates the seeds (per seed, or mean and SD). If the two show identical values, keep the values in the table and let the figure show the pattern, or drop whichever one repeats the other.

FIGURE 4, ABLATION BY SPLIT SIZE
Right now the claim that the gain shrinks on the smallest split rests only on a table. Plot the ECE reduction (uncalibrated minus temperature scaling) against split size, with per-seed points. Give n for each split. Don't call the difference significant unless a test has been run and recorded in the ledger. Three seeds cannot support a strong significance claim.

TABLE 1, ECE PER METHOD
Keep this as a table. Mark the best value per row. Each value needs its F-id in the caption or ledger.

RISKS BEFORE 8AM
1. Notes vs ledger: verify every number (see above).
2. Fifth pipeline box: name it before export.
3. Three seeds: describe the gain as consistent across the three seeds. Do not describe it as statistically established.
4. figure-qa has not been run on any figure yet. Run it on Figure 1 first, since it is the figure built outside the repo.
5. Notes and ledger disagreeing on a number is a finding to tell your partner about, not something to fix quietly in the draft.
~~~~
