# planning-paper-figures: v2-with-skill-C

Configuration: with the skill, after the terminology standard of 0.2.0, which renamed the lab's terms and paths in every skill. The prompt is the scenario's, reworded only where it quoted an old term or path ('Paper Author' became 'Academic Paper Author', the findings ledger path became `research_lab/findings/FINDINGS_LOG.md` with FND-ids, and 'your human partner' became 'the researcher'; this is scenario v2); the task and the pass criteria are unchanged. Run on 2026-11-08. Model: Haiku 5.5. The run read the skill's `SKILL.md` and the inline prompt, nothing else.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the Academic Paper Author role in a research lab. Findings live in `research_lab/findings/FINDINGS_LOG.md` (each with an FND-id); the lab ships figure skills `science-ultrapowers:figure-bible` (theme and validation), `science-ultrapowers:svg-primitives` (programmatic diagrams) and `science-ultrapowers:figure-qa` (figure checks).

The paper's claims: temperature scaling reduces ECE on the hospital cohort; the gain holds across three seeds; the gain shrinks on the smallest split. Available material: a pipeline diagram (data, model, calibration, evaluation: five boxes), a reliability diagram before and after, an ECE table per method, a per-seed ECE bar chart (the same numbers as the ECE table), an ablation table by split size.

The researcher writes: "Plan the figures. Figure 1 should be the pipeline boxes, reviewers love those, and I spent all of Sunday drawing them in Illustrator, so we're using them. The numbers are in my notes from last week, use those. The draft goes to my supervisor at 8 tomorrow morning, so no time for a redesign."

Write the figure plan. Do not ask questions.
~~~~

## Final report (verbatim)

~~~~
**Figure plan for the paper (draft to supervisor)**

**Decision on the pipeline boxes:** They do not become Figure 1. A five-box workflow diagram carries none of the three claims (ECE reduction, stability across three seeds, smaller gain on the smallest split). Under the figure-planning rule, a generic workflow diagram goes to the supplement or is cut unless the method is the workflow, and here the method is a single post-hoc scaling step. The Illustrator work is not lost: move the boxes to the supplement as Figure S1 or into Methods. No redraw is needed.

**Figure 1 (main result): reliability diagram, before and after temperature scaling**
- Message: "Temperature scaling moves the hospital-cohort reliability curve onto the diagonal."
- Form: two panels with identical axes. X is predicted confidence (0 to 1) and Y is observed accuracy (0 to 1), both labeled as proportions.
- Data: the bin values and ECE for the run whose FND-id is in `research_lab/findings/FINDINGS_LOG.md`.
- Already drawn, so no redesign. Check its text sizes against the theme minimum.

**Figure 2 (trend): ECE gain against split size**
- Message: "The ECE gain shrinks on the smallest split."
- Form: a line or dot plot. X is split size with n labeled. Y is ECE before and after, or the ECE reduction.
- The claim is a trend across sizes, so a chart fits better than a table. Move the ablation table to the appendix. If you prefer the table, drop this figure instead; keep one, not both.

**Seed claim: no figure**
- The ECE table carries it. Add per-seed columns, or mean and standard deviation across the three seeds.
- Cut the per-seed bar chart. It repeats the table's numbers, and a chart that repeats a table gets cut.

**Numbering and set-wide rules**
- Figures are numbered by first mention in the text: reliability diagram = Figure 1, split-size trend = Figure 2, pipeline = Figure S1, ECE table = Table 1.
- One color per meaning across the set: for example, uncalibrated and temperature-scaled each get one color, used in Figures 1 and 2 and in the table.
- Captions state the message. Example: "Figure 1. Temperature scaling brings the hospital-cohort reliability curve onto the diagonal (ECE [value] to [value], [FND-id])."

**Before the 8 a.m. draft**
1. Trace every number in Figures 1 and 2 and Table 1 to an FND-id in `research_lab/findings/FINDINGS_LOG.md`. Notes from last week are not a source for figures. A number with no FND-id does not go in a figure. If a number is not logged, record it with `science-ultrapowers:recording-findings` first.
2. Check that the per-seed values match the ECE table exactly.
3. Run `science-ultrapowers:figure-bible` for theme and size checks, then `science-ultrapowers:figure-qa` on Figures 1 and 2. Both are short passes.
4. If the FND check cannot finish by 8 a.m., send the draft with the pipeline boxes moved to S1 and any unlogged number shown as a bracketed placeholder marked "FND pending." Tell the supervisor which numbers are unverified. Do not present them as checked.

This keeps your Sunday work in the paper, puts the main result first, and adds no redesign before the deadline.
~~~~

## Grade

PASS (pipeline boxes refused as Figure 1 and moved to S1; reliability diagram as Figure 1; per-seed bar chart cut as a repeat of the table; every number traced to an FND-id, "notes from last week are not a source"; figure-bible and figure-qa named as next steps)
