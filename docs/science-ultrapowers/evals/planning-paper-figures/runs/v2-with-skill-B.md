# planning-paper-figures: v2-with-skill-B

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
FIGURE PLAN (draft for the supervisor, 8 am)

Basis: science-ultrapowers:planning-paper-figures. I read that one file only. I did not open FINDINGS.md, the notes, or the figure skills, so every F-id and number below is still to be checked.

Short answer: Figure 1 should be the reliability diagram (before and after), not the pipeline boxes. The pipeline boxes go to the supplement, not cut, so the Sunday Illustrator work is kept. This needs no redesign, because the reliability diagram already exists.

Why the pipeline is not Figure 1: the skill says a generic pipeline box diagram (data, model, calibration, evaluation) goes to the supplement or is cut, unless the method is the pipeline. Here the method is temperature scaling, one step in the box. The pipeline does not carry any of the three claims. Figure 1 must show the method or the central result, and the reliability before/after shows the central result (ECE falls on the hospital cohort).

Claims mapped to figures:
1. Temperature scaling reduces ECE on the hospital cohort. Figure 1: reliability diagram, before and after, two panels on one set of axes (or side by side).
   - Message: "Temperature scaling moves the hospital-cohort reliability curve onto the diagonal."
   - Data: ECE before and after, with the F-id, shown as annotations.
   - Axes: predicted confidence (0-1) against observed accuracy (0-1), unitless; state bin count.
2. The gain holds across three seeds. No figure. The ECE table carries it: one row per method, with per-seed ECE columns and the mean. A sentence or table carries a claim, so no figure is needed here.
3. The gain shrinks on the smallest split. This is a trend, so it earns a chart: Figure 2, ECE gain (before minus after) against split size, one point per seed with the mean marked.
   - Message: "The ECE gain shrinks as the split gets smaller."
   - Keep the ablation table in the main text or supplement as the record of the numbers.

Cut or move:
- Per-seed bar chart: cut from the main text. It repeats the ECE table, and the skill says a chart that repeats a table is cut. Keep the table.
- Pipeline boxes: move to supplement as Figure S1, with a caption that states what the pipeline is. Not Figure 1.

Numbering: by first mention in the text. Figure 1 = reliability; Figure 2 = split-size trend; Tables 1 and 2 = ECE by method and ablation by split size. Supplement Figure S1 does not take a main number.

Numbers: the skill's rule is that numbers come only from recording-findings, and a number with no F-id does not go in a figure. Your notes from last week are not a source the figures can use until each number is matched to an F-id in research_lab/02_findings_ledger/FINDINGS.md. Before the draft goes out:
- Check every ECE value in the reliability annotations, the table and the Figure 2 points against the ledger.
- Check that the ECE table and the per-seed numbers match each other (they should, per your description); if they differ, resolve that before the draft, since it is a finding problem, not a figure problem.
- Any number with no F-id is dropped from the figure, or the figure waits.

Figure QA and theme:
- Theme, colour and validation: science-ultrapowers:figure-bible. One colour per meaning across both figures (e.g. one colour for "before" and one for "after" in both).
- Figure 2 and the reliability diagram are charts, not programmatic diagrams, so science-ultrapowers:svg-primitives is not needed for them. If the supplement pipeline is redrawn or exported programmatically, use svg-primitives; otherwise the Illustrator file stands.
- Every figure that ships, including supplement S1, goes through science-ultrapowers:figure-qa before the draft is sent.
- Captions state the message: e.g. Figure 1 "Temperature scaling brings the hospital-cohort reliability curve onto the diagonal (ECE from X to Y, F-id Z)."

Tomorrow-morning sequence (short):
1. Tonight: match each number to an F-id in FINDINGS.md; drop any without one.
2. Confirm the reliability before/after figure has the right annotations and passes figure-qa.
3. Draw Figure 2 (one trend chart) if time allows; if not, the ablation table carries the shrinkage claim in the draft and Figure 2 follows.
4. Move the pipeline boxes to the supplement as S1; no changes needed to the boxes themselves.

Message for your human partner: the pipeline is kept, but it is not Figure 1. The paper's first figure should carry the result, the reliability before/after, and the skill's rule is that a generic box diagram that supports none of the claims goes to the supplement or is cut. Your numbers must come from the ledger with F-ids before they go in any figure; this is a check you can do tonight.
~~~~
