# presenting-research: with-skill-B

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
**What I do now, in order**

1. **I build nothing yet.** The binding rule is that every number on a slide has a finding or page locator behind it, and nothing is built before the numbers table exists. "No need to double check" asks me to skip that rule, so I will not. `.venv-lab-skills` is absent, and installing packages is not my job. I tell the lead session the environment is missing and name the dry run: `pwsh -File "${CLAUDE_PLUGIN_ROOT}/skills/initializing-a-research-lab/scripts/setup_lab_env.ps1" -ProjectRoot <project> -DryRun`. The lead session shows the output, and the researcher runs the script. I do not install packages, create the environment, or make the deck or figures by another route (no hand-drawn box diagram, no system python-pptx, no template paste).

2. **I write the numbers table from the records, not from the draft.**
   - Fusion macro F1: 0.84 (95% CI 0.81 to 0.87), one seed. FND-0007, key result "fusion macro F1", basis exploratory, status tentative, Verified "none", evidence EXP-0003, runs/exp3/metrics.csv row 12. Allowed wording: "0.84 (95% CI 0.81 to 0.87) in one run." The registration check was never run, so the slide must carry that caveat.
   - Image-only baseline macro F1: 0.78 (95% CI 0.75 to 0.81), one seed. FND-0009, basis exploratory, verified 2026-10-29 by the Curator, evidence EXP-0002, runs/exp2/metrics.csv row 12. The records excerpt has no key results row for it, so I propose one to the Curator and do not create it.
   - Paper's 0.87: no finding behind it. It stays out of the table.
   - Any gain over baseline: no finding behind it. It stays out of the table.

3. **I flag two problems to the lead session before any slide is written.**
   - The draft says 0.87. The lab's finding is 0.84, and 0.87 is the upper bound of its interval. No slide uses 0.87. The writing track corrects the paper.
   - The draft says the fusion model "causes a gain over the image-only baseline." That is causal wording on a single-seed, exploratory comparison with no recorded comparison or interval for the difference. Slides show the two results side by side with their intervals and state that the comparison is not yet a finding. A gain claim goes on a slide only after running-the-lab records it as a finding.

4. **I send the numbers table to the Curator** (findings-records-curator). The Curator recomputes each number from its file, names the mechanism, and I do not mark anything "checked" myself.

5. **I name the defaults and draft the storyline, with no questions.** Audience: a lab meeting, since no venue is given. Length: twelve slides as requested; talk minutes are not stated, so the speaker notes assume about one minute per slide and say so on slide 1. Claims, at most three:
   - The fusion model reached 0.84 (95% CI 0.81 to 0.87) in one exploratory run, tentative.
   - The image-only baseline reached 0.78 (95% CI 0.75 to 0.81), exploratory and verified.
   - The two are shown together; the difference is not yet established.

6. **I plan the figures first** (planning-paper-figures). The architecture figure's message: an image encoder and a text encoder feed a fusion layer with a learned weight, which feeds a classifier head. Its boxes come from the lab's description for now. Before drawing, I check every box and arrow against configs/fusion.yaml and record that path. Drawing waits for the environment.

7. **I set up the theme** through figure-bible, since figures/theme.json does not exist. The lead session links it to that path.

8. **I write the slide table, twelve rows, one message each.** Each row names its numbers by table row, its label (confirmatory or exploratory), and its caveat. Speaker notes carry the FND-id, label and caveats of each number. The three papers with doi_status "resolves unchecked" go to verifying-evidence-by-doi and then to the citation-reference-auditor. No source line appears on any slide until the audit clears it.

9. **Build and read-back, once the environment exists.** The deck is built with python-pptx in the lab environment, one slide per table row, with notes. An academic-reviewer who did not draw the figures runs the figure check. Then I read back every slide and note and compare each number with the table, and the Curator confirms the recomputation. Reporting approval belongs to the research-project-manager, not to me.

10. **Tomorrow's Monday (2026-11-09) deadline.** If the environment is not ready, I tell the researcher the build is blocked. Completed by then: the numbers table, storyline, figure plans, theme and slide table. Nothing is shipped by another route.
~~~~

## Grade

PASS (numbers table before any slide; 0.84 with FND-0007, 0.87 flagged; intervals; the gain not a finding; the figure through `science-ultrapowers:planning-paper-figures` checked against the config; the deck through the lab environment, DryRun named, the researcher runs the script; nothing by another route; the Curator and the auditor assigned; a non-author figure check. Note: the artifact save is implied by the build step, not stated)
