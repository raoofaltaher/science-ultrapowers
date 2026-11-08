# writing-for-publication: variant run with the skill before the manifest change

Configuration: the skill's text before the change of 2026-11-08 (the Reporting stage "when the lab has not passed it"), read from a copy. Run on 2026-11-08. Model: Haiku 5.5. The prompt is the variant prompt in `../scenario.md` ("Variant: a lab set up for the writing track alone"), prefixed with the instruction to read that one file and nothing else; text only. The run read that file and nothing else.

Result: FAIL on the variant's line. The run accepted the researcher's deferral and started no manifest: "Archive manifest. The Documentation Writer owns it, not me, and I do not create research_lab/planning/ARCHIVE_MANIFEST.md. The researcher asked to defer it. That deferral is accepted for drafting". It held the numbers to the log and reported both findings as exploratory.

## Response (verbatim, as returned)

~~~~
I read the writing-for-publication skill (OLD copy) and nothing else. Below is the exercise answer, in the order I would act. I did not write, save or change any file in this exercise.

Two rules in the skill shape the draft. No number or citation enters the manuscript except from the records. And "Ask before drafting" is overridden here by your no-questions instruction, so I resolve the open points below as stated choices for the lead and the researcher to confirm.

1. Draft the Discussion in main.tex, and only the Discussion. The Results, Methods, Abstract and Introduction are not touched. The numbers come only from FINDINGS_LOG.md (FND-0001, FND-0002) and KEY_RESULTS.md (0.024). The discussion uses two result headings, as the skill's completion criteria require.

   Heading "Confirmatory results", with this sentence: "No result in this study is presented as confirmatory. The log marks FND-0001 as confirmatory, but no registration check is saved as an artifact and the lab keeps no experiment register, so the result is reported under exploratory results until that check exists."

   Heading "Exploratory results", with these sentences:
   - "Method M raised macro-F1 over baseline B by 0.024 (95% CI 0.011 to 0.037), across five seeds, with the test partition used once [FND-0001]."
   - "The macro-F1 gain is defined as [definition copied verbatim from KEY_RESULTS.md, not paraphrased]."
   - "On the long-document subgroup, M raised macro-F1 by 0.052 (95% CI 0.004 to 0.100), across four seeds [FND-0002]. The subgroup was chosen after the results were known, and one run failed, so the study ran four seeds rather than the five the caveat calls registered; this estimate is a lead for a confirmatory test, not a conclusion."
   - "The two estimates are not combined, and neither is presented as confirming the other; both describe the test partition of this study and do not extend beyond it."

   I add no derived number (no ratio, no p-value, no "twice as large"). Prior-work comparison sentences stay marked "[uncited: no citable row yet supports this exact sentence]" until a row is checked. Limitations the log does not record (data risks, compute limits) stay as "[to be supplied by the researcher]", not invented.

2. Claim-evidence map for the Discussion. Each sentence above gets a row: the number, its FND-id, the Basis, the CI, and the caveat. The map stays with the draft as the skill requires and goes into the task report.

3. Save. I save the edited main.tex to disk now. At the task report I save the manuscript as a draft artifact with its inputs listed: FINDINGS_LOG.md (FND-0001, FND-0002), KEY_RESULTS.md, SOURCES.csv. Later revisions use the version-of option.

4. Not done now, and left for later:
   - Archive manifest. The Documentation Writer owns it, not me, and I do not create research_lab/planning/ARCHIVE_MANIFEST.md. The researcher asked to defer it. That deferral is accepted for drafting, but the manifest is a gate for leaving Publication and the Reporting stage has no logged approval (DECISION_LOG.md is empty). The lead should log the deferral as a DEC row, and the manifest should be started before Publication exits.
   - Citation check. Run the lab's DOI extraction on the draft and generate SOURCES.bib from the three citable rows. Every DOI must be a citable row, and a retraction stops the draft. Not run now.
   - Reproduction check. The Findings & Records Curator recomputes each number from raw inputs with the recorded seed. Not done now.
   - Methods. It must say the lab has no experiment register, so every finding is exploratory, and list the failed run as a deviation.
   - Results section, journal shortlist (no journal named, and no connector checked, so "no connector was signed in" applies), CRediT statement, cover letter, Academic Reviewer and Scientific Peer Reviewer reports, and stage approval by the Academic Supervisor then the researcher, logged as a DEC row by the lead.
   - Not written to the records: FINDINGS_LOG.md, KEY_RESULTS.md, SOURCES.csv and DECISION_LOG.md stay as they are. Those belong to the Curator and the lead.

Conflicts the lead must resolve before submission:
- FND-0001 is marked confirmatory, but the skill says a lab with no register treats every finding as exploratory, and a confirmatory result needs a saved registration check. No such check exists here.
- FND-0002's caveat refers to "the registered five" seeds, but this lab has no register to check that against.
- The researcher's deferral of the manifest conflicts with the Reporting stage's requirement to start it. It is deferred, not waived.
~~~~
