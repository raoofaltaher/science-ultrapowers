# planning-paper-figures: with-skill-A

Configuration: with the skill. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/planning-paper-figures/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the Paper Author role in a research lab. Findings live in `research_lab/02_findings_ledger/FINDINGS.md` (each with an F-id); the lab ships figure skills `figure-bible` (theme and validation), `svg-primitives` (programmatic diagrams) and `figure-qa` (figure checks).

The paper's claims: temperature scaling reduces ECE on the hospital cohort; the gain holds across three seeds; the gain shrinks on the smallest split. Available material: a pipeline diagram (data, model, calibration, evaluation: five boxes), a reliability diagram before and after, an ECE table per method, a per-seed ECE bar chart (the same numbers as the ECE table), an ablation table by split size.

Your human partner writes: "Plan the figures. Figure 1 should be the pipeline boxes, reviewers love those. The numbers are in my notes from last week, use those."

Write the figure plan. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
FIGURE PLAN (Paper Author role). I read only /s/science-ultrapowers/skills/planning-paper-figures/SKILL.md, as instructed. I did not open research_lab/02_findings_ledger/FINDINGS.md, so every F-id below is a placeholder to fill from the ledger.

Where this departs from the request:
1. Figure 1 is not the pipeline boxes. The skill says a generic pipeline box diagram goes to the supplement or is cut, unless the method is the pipeline. Five generic boxes (data, model, calibration, evaluation) do not carry any of the paper's three claims. Figure 1 should show the central result instead: the before/after reliability diagram.
2. The numbers from last week's notes cannot be used. The skill says numbers come only from science-ultrapowers:recording-findings, and a number with no F-id does not go in a figure. Each value must be taken from FINDINGS.md with its F-id. If a note-value has no ledger entry, it is not plotted until it is recorded there.

Claims, each mapped to one place:
- C1: Temperature scaling reduces ECE on the hospital cohort. Carried by Figure 1 (reliability before/after) with the ECE values in its panel labels.
- C2: The gain holds across three seeds. Carried by the ECE table, with one column per seed. The per-seed bar chart repeats the table's numbers, so it is cut. Keep either the table or the chart, not both.
- C3: The gain shrinks on the smallest split. Carried by Figure 2.

Figure set (numbered by first mention in text):

Figure 1. Reliability diagram, before and after temperature scaling, hospital cohort.
- Message: "Temperature scaling moves the hospital-cohort reliability curve onto the diagonal, and ECE falls from X to Y." State the message in the caption, not only the content.
- Data: the before and after bins for the hospital cohort, with ECE values; F-id: [to fill from FINDINGS.md].
- Chart type: calibration curve (relationship of predicted to observed confidence), two panels side by side or overlaid, with the identity diagonal drawn.
- Axes: x = predicted confidence, y = observed accuracy, both dimensionless proportions from 0 to 1. Label units as "proportion".
- Colour: uncalibrated and temperature-scaled each get one colour, used the same way in Figure 2.
- Labels within the theme's min and max text size (figure-bible).

Figure 2. Gain in ECE by split size.
- Message: "The ECE gain from temperature scaling shrinks on the smallest split." One sentence.
- Data: delta-ECE (uncalibrated minus calibrated) per split size, with spread across the three seeds shown as error bars; F-id for each point: [to fill from FINDINGS.md].
- Chart type: trend (gain against split size), with the seed spread visible.
- Axes: x = split size (state n for each split), y = delta-ECE, dimensionless. Label the units.
- Colour: the temperature-scaled colour as in Figure 1 if the points are the calibrated series; a neutral colour for the zero reference line.

Supplement only (or cut):
- Pipeline boxes (data, model, calibration, evaluation). Put it in the supplement as Figure S1 if the partner wants it. If it is drawn, use svg-primitives. It is not a main-text figure because the paper's claims are about calibration results, not the workflow.

Hand-off and checks before anything ships:
- Theme and validation: the vendored figure-bible.
- Every figure that will ship goes through figure-qa first.
- Each number's F-id must resolve in FINDINGS.md before drawing.
- The ablation table and the ECE table are tables; do not redraw them as charts.

Decisions for the partner to note (no questions asked): the pipeline is not Figure 1, the note-values are not used until they have F-ids, and the per-seed chart is cut in favour of a per-seed table column.
~~~~
