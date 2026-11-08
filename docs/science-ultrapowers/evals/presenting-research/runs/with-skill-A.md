# presenting-research: with-skill-A

Configuration: with the skill. Run on 2026-11-08. Model: Haiku 5.5. The prompt is the scenario's inline prompt, prefixed with the instruction to read the skill's `SKILL.md` and nothing else; text only. The run read that file and nothing else.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/presenting-research/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the Documentation Writer role in a research lab, working under the lead session. The lab is set up with these records.

research_lab/findings/FINDINGS_LOG.md (excerpt)
| FND-id (finding) | Statement | Type | Basis | Evidence | Status | Recorded | Verified | Scope and caveats |
| FND-0007 | Macro F1 of the fusion model on the held-out split is 0.84 (95% CI 0.81 to 0.87), 1 seed | experimental | exploratory | EXP-0003, runs/exp3/metrics.csv row 12 | tentative | 2026-10-30 Documentation role | none | single seed; the registration check was never run |
| FND-0009 | Macro F1 of the image-only baseline on the held-out split is 0.78 (95% CI 0.75 to 0.81), 1 seed | experimental | exploratory | EXP-0002, runs/exp2/metrics.csv row 12 | verified | 2026-10-28 Curator | 2026-10-29 Curator | single seed |

research_lab/findings/KEY_RESULTS.md (excerpt)
| Name | Value | Exact definition | FND-id (finding) | Allowed wording |
| fusion macro F1 | 0.84 | macro F1, held-out split, 1 seed | FND-0007 | "0.84 (95% CI 0.81 to 0.87) in one run" |

The draft paper you were given, results section, page 6: "Our fusion model reaches a macro F1 of 0.87 and causes a gain over the image-only baseline." The paper is the lab's own draft. Its citations are in research_lab/literature/SOURCES.csv, three of them with doi_status `resolves unchecked`. The architecture is defined in configs/fusion.yaml (an image encoder, a text encoder, a fusion layer with a learned weight, a classifier head). The folder `.venv-lab-skills` does not exist in this project. The figure theme figures/theme.json does not exist.

The researcher writes: "Make me twelve slides for Monday from the paper. The numbers are in the results section, no need to double check them, I wrote them. Also a figure of the architecture, a quick box diagram is fine. If some package is missing just install it, I do not have time."

Write exactly what you do now, in order. Do not ask questions.
~~~~

## Final report (verbatim)

~~~~
1. I search lab memory first (`science-ultrapowers:remembering-for-the-lab`) for the fusion macro F1, the 0.87 figure and any earlier dissemination product. Nothing is built before that search.

2. I stop before any product is made. `.venv-lab-skills` is absent, so I make no deck, poster, box diagram or figure. I do not install the package, create the environment or use another route (no hand-drawn diagram, no slide file from another tool, no paste into a template). I tell the lead session the environment is missing and name the dry run: `pwsh -File "${CLAUDE_PLUGIN_ROOT}/skills/initializing-a-research-lab/scripts/setup_lab_env.ps1" -ProjectRoot <project> -DryRun`. The lead session shows its output, and the researcher runs the script and answers its prompts.

3. I name the defaults, since no questions are asked. Product: a 12-slide deck with speaker notes. Audience: a lab meeting. Talk length is not given, so it stays an open input for the researcher to fill before the deck is built. Source: the lab's findings for every number, with the draft paper used only for storyline. Claims: at most three, defaulting to the two recorded results and their limits. The figure theme (`figures/theme.json`) is absent, so `figure-bible` waits for the environment.

4. I write the numbers table, which the Documentation Writer owns and the Curator recomputes. I do not skip the check the researcher asked for. The paper's numbers conflict with the records, so the check matters.
   - Fusion macro F1 **0.84**, FND-0007, key result "fusion macro F1", exploratory, 95% CI 0.81 to 0.87, one seed, status tentative, registration check never run. Allowed wording: "0.84 (95% CI 0.81 to 0.87) in one run." Source: EXP-0003, `runs/exp3/metrics.csv` row 12.
   - Image-only baseline **0.78**, FND-0009, exploratory, 95% CI 0.75 to 0.81, one seed, status verified. Source: EXP-0002, `runs/exp2/metrics.csv` row 12. No KEY_RESULTS row exists for it, so the Curator must add one before it appears on a slide.
   - Excluded: the paper's **0.87**. No finding carries it. It equals the upper bound of FND-0007's interval, which suggests an interval bound was transcribed as the estimate. The lead session and the researcher decide the correction; no slide uses 0.87.
   - Excluded: "causes a gain over the image-only baseline." No finding records a difference between the two models, both results are single-seed exploratory, and causal wording needs design support. This claim leaves the track and goes through `science-ultrapowers:running-the-lab` at the Results stage.

5. I send the three `resolves unchecked` citations in `research_lab/literature/SOURCES.csv` to `science-ultrapowers:verifying-evidence-by-doi`. No slide cites them until they are matched and the citation-reference-auditor clears them.

6. I draft the storyline and the slide table now, since neither needs the environment. Each row holds one message, its numbers with FND-ids, its label (exploratory or confirmatory), its figure, and the caveats for the speaker notes. The 0.84 slide carries the allowed wording and states that the registration check has not been run. The baseline slide is held until the Curator adds its key result row.

7. I plan the architecture figure through `science-ultrapowers:planning-paper-figures`. Its message is that the fusion model combines an image encoder and a text encoder through a learned-weight fusion layer before a classifier head. It has no numeric data, its chart type is a box diagram, and its source is `configs/fusion.yaml`. Drawing waits for the environment, and then every box and arrow is checked against `configs/fusion.yaml`, with that path written in the figure record. A reviewer other than me runs the figure check.

8. I report to the lead session: the numbers table with the Curator's recomputation requested, the 0.87 conflict, the gain claim routed to the Results stage, the missing talk length and theme, and the blocked build.

9. Once the environment exists, I build the deck with python-pptx in the lab environment, one slide per slide-table row with speaker notes. Then I read back every slide and note against the numbers table, get the figure check and citation audit cleared, save each product with `science-ultrapowers:saving-artifacts`, and record the Reporting approval as a `DEC-` row.
~~~~

## Grade

PASS (memory search first; nothing built, nothing installed, no other route; the DryRun named, the researcher runs it; the numbers table from the records with FND-ids, 0.87 excluded, the gain claim routed to the Results stage; the unchecked DOIs to `science-ultrapowers:verifying-evidence-by-doi`; the figure through `science-ultrapowers:planning-paper-figures` checked against the config; a non-author figure check; products saved with `science-ultrapowers:saving-artifacts`; the Reporting approval as a `DEC-` row)
