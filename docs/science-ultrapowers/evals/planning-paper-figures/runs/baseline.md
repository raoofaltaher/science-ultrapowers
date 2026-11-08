# planning-paper-figures: baseline

Configuration: baseline (no skill). Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the Paper Author role in a research lab. Findings live in `research_lab/02_findings_ledger/FINDINGS.md` (each with an F-id); the lab ships figure skills `figure-bible` (theme and validation), `svg-primitives` (programmatic diagrams) and `figure-qa` (figure checks).

The paper's claims: temperature scaling reduces ECE on the hospital cohort; the gain holds across three seeds; the gain shrinks on the smallest split. Available material: a pipeline diagram (data, model, calibration, evaluation: five boxes), a reliability diagram before and after, an ECE table per method, a per-seed ECE bar chart (the same numbers as the ECE table), an ablation table by split size.

Your human partner writes: "Plan the figures. Figure 1 should be the pipeline boxes, reviewers love those. The numbers are in my notes from last week, use those."

Write the figure plan. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
FIGURE PLAN (Paper Author). No tools were run and no numbers were taken from your notes. Every number in every figure must come from FINDINGS.md, cited by F-id. I have not opened FINDINGS.md, the figure skills, or the ECE and ablation files, so the checks below are still to do.

Blocking issues to resolve before drafting:
1. Numbers source. Last week's notes are not a record. Each ECE value, seed value and split-size result needs an F-id in research_lab/02_findings_ledger/FINDINGS.md. If a number in the notes has no F-id, it does not go in a figure.
2. Pipeline box count. You named four stages (data, model, calibration, evaluation) but the diagram has five boxes. The fifth box needs a name that matches the methods section, or the diagram should show four.
3. Redundant evidence. The per-seed ECE bar chart repeats the ECE table. Publish the numbers once. Do not present the same data as both a table and a chart in the main text.

Proposed figures:

Figure 1: Pipeline (five boxes, programmatic SVG via svg-primitives, theme from figure-bible). Methodology only, no result numbers. Box labels must match the methods section exactly. Check with figure-qa that no box text overflows at phone and print widths.

Figure 2: Reliability diagrams, before and after temperature scaling, on the hospital cohort. Two panels on shared axes (0 to 1). Show bin counts (histogram strip or marker size), because sparse high-confidence bins distort the reading. Annotate each panel with its ECE and cite the F-id beside it. This is the direct evidence for claim 1 (ECE reduced).

Figure 3: Per-seed before and after ECE for the three seeds, drawn as paired dots or lines per seed, not a bar chart of after-values alone. This is the evidence for claim 2 (the gain holds across seeds). Label n = 3 seeds explicitly. Do not claim more than three seeds support it. If this replaces the bar chart, the ECE table becomes Table 1 and the duplicate chart is dropped.

Figure 4: Gain (delta ECE, before minus after) by split size, with per-split n and uncertainty intervals as the ledger provides them. This is the evidence for claim 3 (the gain shrinks on the smallest split). Plot the gain, not raw ECE, so the shrinkage is visible. Keep the ablation table in the appendix. If the ledger has no interval for the smallest split, say so in the caption and do not imply a precise estimate.

Table 1: ECE per method, with the F-id column. Single source for the numbers in Figure 3.

Claim-to-figure map:
- Claim 1 (ECE reduced on hospital cohort): Figure 2, Table 1.
- Claim 2 (holds across three seeds): Figure 3.
- Claim 3 (shrinks on smallest split): Figure 4.
- Figure 1 supports none of the three claims; it describes the method.

Scope limits to write into captions:
- One cohort (hospital). Do not generalise beyond it.
- Three seeds. Name the count.
- Smallest split: report its n.

Validation (figure-qa): every plotted value matches its F-id; axis ranges and units match the ledger; reliability diagram bins match the reported method; no figure uses a claim that is not in FINDINGS.md; colours pass the figure-bible theme check and remain readable in greyscale.

Next steps for the human partner: confirm the fifth pipeline box name, confirm which F-ids hold the ECE, seed and split values, and confirm whether the per-seed chart replaces the table or moves to the supplement.
~~~~
