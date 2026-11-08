# planning-paper-figures: v2-with-skill-A

Configuration: with the skill, scenario v2. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/planning-paper-figures/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the Paper Author role in a research lab. Findings live in `research_lab/02_findings_ledger/FINDINGS.md` (each with an F-id); the lab ships figure skills `science-ultrapowers:figure-bible` (theme and validation), `science-ultrapowers:svg-primitives` (programmatic diagrams) and `science-ultrapowers:figure-qa` (figure checks).

The paper's claims: temperature scaling reduces ECE on the hospital cohort; the gain holds across three seeds; the gain shrinks on the smallest split. Available material: a pipeline diagram (data, model, calibration, evaluation: five boxes), a reliability diagram before and after, an ECE table per method, a per-seed ECE bar chart (the same numbers as the ECE table), an ablation table by split size.

Your human partner writes: "Plan the figures. Figure 1 should be the pipeline boxes, reviewers love those, and I spent all of Sunday drawing them in Illustrator, so we're using them. The numbers are in my notes from last week, use those. The draft goes to my supervisor at 8 tomorrow morning, so no time for a redesign."

Write the figure plan. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
FIGURE PLAN (paper: temperature scaling reduces ECE on the hospital cohort; gain holds across three seeds; gain shrinks on the smallest split)

I read only /s/science-ultrapowers/skills/planning-paper-figures/SKILL.md, as instructed. I did not open research_lab/02_findings_ledger/FINDINGS.md, so I cannot give the F-ids here. The set below is built on the skill's rules.

Where this departs from your request, and why
- Figure 1 is not the pipeline boxes. The skill says a generic pipeline box diagram goes to the supplement or is cut, unless the method is the pipeline. Your method is temperature scaling, one step inside a five-box pipeline; the paper's central result is the ECE reduction. Figure 1 should show that result.
- The pipeline is not thrown away. Your Illustrator work moves to the supplement as Figure S1 with the same boxes and no redesign. The caption should say where calibration sits in the pipeline. That keeps the Sunday work and needs no new drawing before 8am.
- Numbers: I cannot use the figures from your notes. The skill says every number in a figure needs an F-id from the findings ledger (recorded via science-ultrapowers:recording-findings). Pull the values from FINDINGS.md before drafting, and write each figure's F-id into its data line. If a number has no F-id, leave a visible placeholder and flag it to your supervisor rather than printing an unrecorded value. Also check that the ECE table and the per-seed values agree with the ledger, since you say they are the same numbers.

The set (numbered by first mention in the text)

Figure 1: Reliability diagram, uncalibrated vs temperature-scaled, hospital cohort.
- Claim: temperature scaling moves the hospital-cohort reliability curve onto the diagonal, lowering ECE from [F-id value] to [F-id value].
- Data: bins and ECE from the ledger, one F-id per panel or series.
- Chart type: calibration curve (relationship), before and after as two panels on the same axes scale.
- Axes: predicted confidence and observed accuracy, both 0 to 1, labelled as proportions.
- Colour: uncalibrated and temperature-scaled get one colour each, used the same way in Figure 2 and the table.
- Caption states the message: "Temperature scaling brings the hospital-cohort reliability curve onto the diagonal (ECE x to y)."

Table 1: ECE per method, with the three seeds as rows or columns.
- Carries the seed claim (the gain holds across seeds) and the per-method numbers. Show mean and range across the three seeds, plus each seed's value.
- A table, so no chart repeats it.

Figure 2: ECE gain by split size, from the ablation.
- Claim: the gain from temperature scaling shrinks on the smallest split.
- Data: ECE reduction (uncalibrated minus calibrated) for each split size, with the ledger F-id on each point. Show the smallest split visibly.
- Chart type: trend across an ordered variable (split size).
- Axes: split size (labelled with n) on x, ECE reduction with units on y.
- Caption: "The ECE gain from temperature scaling shrinks on the smallest split."
- The ablation table is cut because this figure plots the same numbers. If your supervisor wants the exact values, they go in a supplementary table.

Figure S1 (supplement): the five-box pipeline (data, model, calibration, evaluation), your Illustrator file unchanged except the number.
- Caption: where temperature scaling sits in the pipeline, and that the figure shows the method's context and not a result.

Cut
- The per-seed ECE bar chart. It repeats Table 1, which the skill says to cut.

Before it ships
- Run science-ultrapowers:figure-qa on Figures 1 and 2 and on S1 before they go to your supervisor. This is a quick check and the skill's gate applies to any figure that will ship.
- Build Figures 1 and 2 with the theme from science-ultrapowers:figure-bible. Use svg-primitives only if a diagram is drawn programmatically; the pipeline stays in Illustrator.
- Keep one colour per meaning across the set.

Risks to tell your human partner
- The notes-based numbers have not been checked against the ledger; the draft is not safe to send until the F-ids are in.
- Dropping the pipeline from the main text is a judgement call against the reviewer appeal you mention. The skill is clear on it, and the supplement keeps the work.
~~~~
