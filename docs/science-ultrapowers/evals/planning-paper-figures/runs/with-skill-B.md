# planning-paper-figures: with-skill-B

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
FIGURE PLAN (planning-paper-figures applied)

Claims to carry:
- C1: temperature scaling reduces ECE on the hospital cohort.
- C2: the gain holds across three seeds.
- C3: the gain shrinks on the smallest split.

Assignment of the available material:
- Pipeline diagram (data, model, calibration, evaluation): carries none of C1-C3. It is a generic box diagram, so it is NOT Figure 1. Move it to the supplement (or cut it). Keep it only if the paper's contribution is the pipeline itself, which I am assuming it is not. If that assumption is wrong, this plan changes.
- Reliability diagram before/after: carries C1 visually. This is the central result.
- ECE table per method: carries C1 numerically and C2 through per-seed values. Keep it as a table in the main text.
- Per-seed ECE bar chart: same numbers as the ECE table, so it repeats a table. CUT.
- Ablation table by split size: carries C3 as a trend. A trend is best shown as a chart, so the table moves to the supplement and its numbers feed Figure 2.

Figure set (numbered by first mention in the text; the text must mention Figure 1 before Figure 2):

Figure 1. Reliability diagram, hospital cohort, uncalibrated vs temperature-scaled.
- Message: after temperature scaling, the hospital cohort's reliability curve sits closer to the diagonal. (C1)
- Data: observed frequency vs predicted probability per bin; ECE before and after shown in the panel. Each ECE value needs its F-id.
- Chart type: reliability curve (relationship: predicted vs observed). Both curves on one set of axes, 0 to 1, with the diagonal drawn.
- Axes: "Predicted probability" and "Observed frequency", unitless proportions, labelled.
- Caption states the message: "Temperature scaling moves the hospital cohort's calibration curve onto the diagonal (ECE x to y)."

Figure 2. ECE reduction by split size.
- Message: the gain is smallest on the smallest split. (C3)
- Data: delta-ECE (uncalibrated minus scaled) per split size, with the spread across the three seeds shown as error bars. Each value needs its F-id.
- Chart type: dot or line plot against split size (trend).
- Axes: "Split size (n)" and "ECE reduction (absolute)", with units.
- Caption states the message: "The ECE reduction from temperature scaling shrinks on the smallest split."

Tables (not figures):
- Main text: ECE per method, with per-seed columns. This carries C1 and C2 numerically. The text states "the gain holds across three seeds" only after the per-seed values have been checked.
- Supplement: ablation table by split size (raw numbers behind Figure 2), pipeline diagram (as S1 if kept).

Cut: per-seed ECE bar chart (repeats the ECE table).

Numbers and sources:
- Your notes from last week are not a source. The skill says a number with no F-id does not go in a figure, and numbers come only from science-ultrapowers:recording-findings. Each ECE value, each delta-ECE, and each split size result must be recorded in research_lab/02_findings_ledger/FINDINGS.md with an F-id before it is plotted. Once recorded, the values from your notes can be used as they are, provided they match the ledger.
- I did not open FINDINGS.md (I was asked to read only the skill file), so I have not confirmed which F-ids exist. Check this before drafting.
- Check that the per-seed values in the ECE table match the bar chart you mentioned before one is cut, and that the three seeds actually show the same sign of gain. C2 depends on this.

Style and validation:
- Colour: one meaning per colour across the set. Uncalibrated and temperature-scaled get fixed colours, used in Figure 1 and in any later figure. Theme and minimum/maximum label sizes come from figure-bible.
- Diagrams (if the supplement pipeline is drawn): svg-primitives.
- Every figure that ships goes through figure-qa before it is used.

Summary for your partner: Figure 1 is the reliability diagram rather than the pipeline, because the pipeline carries none of the paper's three claims and the skill puts generic box diagrams in the supplement or cuts them. The pipeline is still in the paper, as a supplement item.
~~~~
