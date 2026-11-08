---
name: planning-paper-figures
description: Use when planning the figure set of a paper, chapter or report, deciding what Figure 1 shows, what to cut, or before any figure that will ship is drawn
---

# Planning Paper Figures

## Overview

One message per figure; the figure set tells the paper's story in order. Plan the set before drawing any figure.

**Core principle:** A figure earns its place by carrying a claim the text cannot show as well.

## Planning the set

1. List the claims the paper makes.
2. Give each claim that needs seeing one figure. A claim a sentence or a table carries gets none.
3. Choose Figure 1 first. It is the figure most readers see, so it shows the method itself or the central result. A generic workflow box diagram goes to the supplement or is cut, unless the method is the workflow.
4. Cut every figure that repeats a table.
5. Number the figures by first mention in the text.

## Per figure

| Decide | Rule |
|---|---|
| Message | One sentence. If it takes two, split the figure. |
| Data | Name the data and the FND-id each number comes from. |
| Chart type | Chosen by data shape (comparison, distribution, trend, relationship), never by habit. |
| Axes | Labeled, with units. |
| Color | One meaning per color, the same across the whole set. |
| Labels | Within the theme's minimum and maximum text size. |
| Caption | States the message, not only the content. |

## Next step

- Theme and validation: `science-ultrapowers:figure-bible`.
- Programmatic diagrams: `science-ultrapowers:svg-primitives`.
- Every figure that will ship goes through `science-ultrapowers:figure-qa` first.
- Numbers come only from `science-ultrapowers:recording-findings`; a number with no FND-id does not go in a figure.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Figure 1 is a workflow box diagram because reviewers like them | Show the method itself or the central result. A box diagram that supports none of the paper's claims goes to the supplement or is cut. |
| A figure is drawn before its claim is written | Write the claim first; no claim, no figure. |
| A chart repeats a table | Keep one. Cut the chart. |
| Color changes meaning between figures | Thread one color per meaning through the set. |
| A caption names the content and not the message | Rewrite it to state what the reader should conclude. |
