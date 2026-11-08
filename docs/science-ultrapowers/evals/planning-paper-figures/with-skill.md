# With the skill (Haiku 5.5): 2/2 pass

Both runs read only the skill. In the baseline, the run kept the five-box pipeline as Figure 1. With the skill:

- A: "Figure 1 is not the pipeline boxes. The skill says a generic pipeline box diagram goes to the supplement or is cut, unless the method is the pipeline ... Figure 1 should show the central result instead: the before/after reliability diagram." The per-seed bar chart is cut because it repeats the table. "A number with no F-id does not go in a figure."
- B: "Pipeline diagram ... carries none of C1-C3. It is a generic box diagram, so it is NOT Figure 1. Move it to the supplement (or cut it). Keep it only if the paper's contribution is the pipeline itself". Figure 1 is the reliability diagram. The bar chart is cut. Each number needs an F-id. The hand-off goes to figure-bible, svg-primitives and figure-qa.

# With the skill, scenario v2 (Haiku 5.5): 2/2 pass

Both runs make Figure 1 the reliability diagram before and after. They move the partner's Illustrator pipeline to the supplement as Figure S1 instead of cutting it: "The pipeline is not thrown away ... That keeps the Sunday work and needs no new drawing before 8am" (A). Both cut the per-seed bar chart because it repeats the ECE table. Both refuse the notes' numbers until each has an F-id from the ledger. Both send every shipped figure through `science-ultrapowers:figure-qa` with the `science-ultrapowers:figure-bible` theme. [A](runs/v2-with-skill-A.md), [B](runs/v2-with-skill-B.md).

# After the terminology standard (0.2.0), scenario v2 (Haiku 5.5): 1/1 pass

The skills now use the lab's terminology standard (0.2.0). Run v2-with-skill-C, on the prompt reworded only in the old terms (task and pass criteria unchanged): PASS (pipeline boxes refused as Figure 1 and moved to S1; reliability diagram as Figure 1; per-seed bar chart cut as a repeat of the table; every number traced to an FND-id, "notes from last week are not a source"; figure-bible and figure-qa named as next steps). [Run](runs/v2-with-skill-C.md).
