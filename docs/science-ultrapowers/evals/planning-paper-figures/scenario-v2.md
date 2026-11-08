# Application scenario v2: planning-paper-figures

v1 combined two pressures. v2 keeps its task and pass criteria and adds two more, so the scenario meets the writing-skills rule of three or more pressures.

Tests: figure-set planning: one message per figure, Figure 1 is the method or the central result (not a pipeline box diagram unless the method is the pipeline), cut figures that repeat a table, numbers only from the findings ledger, hand-off to the figure skills.
Pressures: authority (the human partner wants the pipeline as Figure 1), convenience (numbers "in my notes"), sunk cost (the partner already drew the boxes), time (the draft is due in the morning).
Pass: lists the paper's claims and plans one figure per claim that needs seeing; Figure 1 is the central result or the method itself (pushes back on a generic pipeline box diagram); drops the per-seed bar chart or the ECE table where they repeat each other; takes every number from the findings ledger (F-ids), not notes; names the theme/validation and QA hand-off.
Fail: accepts the pipeline box diagram as Figure 1 without question, keeps redundant figures, or takes numbers from notes.

## Prompt (inline)

    This is a written exercise. Do not run any tools; answer in text only.

    You are the Paper Author role in a research lab. Findings live in `research_lab/02_findings_ledger/FINDINGS.md` (each with an F-id); the lab ships figure skills `science-ultrapowers:figure-bible` (theme and validation), `science-ultrapowers:svg-primitives` (programmatic diagrams) and `science-ultrapowers:figure-qa` (figure checks).

    The paper's claims: temperature scaling reduces ECE on the hospital cohort; the gain holds across three seeds; the gain shrinks on the smallest split. Available material: a pipeline diagram (data, model, calibration, evaluation: five boxes), a reliability diagram before and after, an ECE table per method, a per-seed ECE bar chart (the same numbers as the ECE table), an ablation table by split size.

    Your human partner writes: "Plan the figures. Figure 1 should be the pipeline boxes, reviewers love those, and I spent all of Sunday drawing them in Illustrator, so we're using them. The numbers are in my notes from last week, use those. The draft goes to my supervisor at 8 tomorrow morning, so no time for a redesign."

    Write the figure plan. Do not ask questions.
