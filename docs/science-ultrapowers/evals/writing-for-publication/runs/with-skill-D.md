# writing-for-publication: with-skill-D (the variant)

Configuration: with the skill after the manifest change of 2026-11-08. Run on 2026-11-08. Model: Haiku 5.5. The prompt is the variant prompt in `../scenario.md` ("Variant: a lab set up for the writing track alone"), prefixed with the instruction to read the skill's `SKILL.md` and nothing else; text only. The run read that file and nothing else.

Result: PASS. The manifest is started before the draft and the run quotes the new row of the rationalization table: "The skill's warning sign applies: 'The manifest is for the end ... Start it in the first session.'" Both findings are reported as exploratory, with their FND-ids and intervals.

## Response (verbatim, as returned)

~~~~
I read only S:/science-ultrapowers/skills/writing-for-publication/SKILL.md, as instructed. Nothing else was read or run. This is the written plan, with the sentences that carry numbers.

The skill overrides the request in two places: the archive manifest is started now, not at submission, and the two findings cannot both sit under "confirmatory".

Order of work

1. Reporting stage first. The skill says a lab set up for the writing track alone logs no Reporting approval, so the stage runs before drafting. I create research_lab/planning/ARCHIVE_MANIFEST.md from research_lab/templates/ARCHIVE_MANIFEST.md. Every line I cannot fill yet is marked "missing", with what the researcher must supply. The lines I can fill are FND-0001 and FND-0002, KEY_RESULTS.md, and the three citable SOURCES.csv rows. I save it as an artifact. This takes little effort and does not hold up the draft. The skill's warning sign applies: "The manifest is for the end ... Start it in the first session." I update the documents from the findings log and the source table, and check that KEY_RESULTS.md still matches FND-0001.

2. Decide the headings. The skill's rule is that a result is confirmatory only with a saved registration check, and that a lab with no register treats every finding as exploratory. No registration check is saved and there is no experiment register. So FND-0001 is not placed under a confirmatory heading, even though its log Basis says confirmatory. Both findings go under "Exploratory results", and the Methods states that no register exists. The manuscript's two-heading completion criterion is met by a confirmatory heading that holds a sentence saying none is claimed, or by the Methods statement. The choice goes to the Academic Reviewer.

3. Draft the Discussion in manuscript/main.tex, with a claim-evidence map for every section. Planned sentences with numbers:
   - "Method M raised macro-F1 over baseline B by 0.024 (95% confidence interval 0.011 to 0.037) on the test partition, which was used once (FND-0001)." Wording is copied from KEY_RESULTS.md, with its definition quoted in the sentence. Phrased as a lead, not a conclusion.
   - "In an exploratory subgroup of long documents, Method M raised macro-F1 by 0.052 (95% confidence interval 0.004 to 0.100) over four seeds, not the five registered, after one run failed (FND-0002). This is a lead for a confirmatory test, not a conclusion."
   - Limitations: four seeds, the subgroup chosen after the results, the one failed run, and the sample's limits. Nothing is claimed beyond the sample, and no causal wording is used. Known data risks and compute limits are placeholders for the researcher.
   - Citations: no citation is typed into the Discussion for prior work. Each such sentence is marked "citation pending: needs a citable row whose evidence record supports this exact sentence". The bibliography is generated, never typed.

4. Checks, with the lab's script. Run verify_doi.py --extract-from manuscript/main.tex, then verify_doi.py --sources-bib research_lab/literature/SOURCES.csv --out research_lab/literature/SOURCES.bib. Every extracted DOI must be a citable row, and a retracted source stops the draft.

5. Save the manuscript as an artifact with saving-artifacts, with the claim-evidence map. If an earlier version exists, it is saved with --version-of.

6. Hand off by role. I am the author, so the reviewer is not me: the Academic Reviewer reviews the draft. The Findings & Records Curator confirms the numbers against the metrics and names the mechanism. The Data & Evaluation Researcher checks the recomputation.

Left for later, with reasons

- Methods statement of deviations and of no register. It is required, but there is no Methods section yet. This is the first item the Discussion depends on.
- Results section. The request covered only the Discussion. The Results must carry the same numbers.
- Citation audit and retraction check (Citation & Reference Auditor), and the Academic Reviewer and Scientific Peer Reviewer reports saved in research_lab/reviews/reports/.
- Journal shortlist. None is named from memory. The connectors (scispace, scholar-gateway, wiley-scholar-gateway, scite) are tried only if signed in, and otherwise the file records that no journal was checked. The target journal is the researcher's choice.
- Manuscript formatting, after the journal is chosen.
- CRediT statement, which uses the researcher's own roles, and the cover letter.
- Stage approvals: Academic Supervisor, then the researcher. The lead session logs the DEC- row.
- Questions the skill would ask before drafting, which the researcher answers later: which journal, the registration check (if one exists), the known data risks, the compute limits, and the real names for Method M and baseline B.

Nothing in the list above was saved or changed by this read-only run. The plan is the report.
~~~~
