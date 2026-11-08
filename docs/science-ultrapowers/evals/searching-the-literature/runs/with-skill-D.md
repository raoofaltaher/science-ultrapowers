# searching-the-literature: with-skill-D

Configuration: with the skill, after the pre-release review fixes (`--cited-by` and `--references` for snowballing, the data-rule line, the search error that exits 1). Model: Haiku 5.5. The run read the skill file and the inline prompt, nothing else.

## Prompt (verbatim)

The prompt of [with-skill-C.md](with-skill-C.md), unchanged.

## Final report (verbatim)

**What I do now, in order, and why**

1. **Log the search before anything else.** I write `research_lab/01_reference_registry/audits/2026-11-08_temperature-scaling-calibration-medical-imaging_search.md` with:
   - the query verbatim: "temperature scaling calibration medical imaging", database OpenAlex;
   - the date (2026-11-08), and the year filter and result limit as they were actually run. If the run did not record them, I write "not recorded" rather than guess;
   - the result count (5);
   - the inclusion and exclusion criteria. If they were not written before the query, I record the date they were written, so the log is honest about the order;
   - the PRISMA-2020 counts so far.

   Why: the protocol requires each query to be logged at once. A reviewer cannot re-run a search that was never written down.

2. **I make no evidence cards yet, and I do not accept "all peer-reviewed."** Why: a search result is a candidate, never a source, and OpenAlex's `type` and `venue` are leads, not peer-review proof. The list itself contradicts the claim. Entry 2 has the DOI prefix 10.48550/ (arXiv), and entry 4 is a bioRxiv preprint (10.1101/). Both are Tier C. A preprint never gets an evidence card, whatever label it carries.

3. **Screen titles and abstracts for all five, and log each exclusion with its reason.**
   - **Entry 2** (10.48550/arXiv.2012.04567): excluded as a preprint. It has the same title as entry 1, so it is probably a preprint of the same work. I search for its published version. Entry 1 (10.1016/j.media.2021.102112, Medical Image Analysis, 2021) is a likely candidate, but that is a hypothesis to confirm, not a fact. I confirm it with the Crossref match and the PDF's first page. If confirmed, the published DOI is what gets screened, and the arXiv record is logged as a duplicate, not counted as a second included paper.
   - **Entry 4** (10.1101/2023.05.11.540123): excluded as a preprint. I search for a published version of "Temperature scaling in histopathology". If none exists, it may be cited for attribution only, under `science-ultrapowers:verifying-evidence-by-doi`, with no card.
   - **Entries 1, 3 and 5** go on to full-text screening.

   Why: the protocol requires title and abstract screening first, with every exclusion logged with its reason.

4. **Run the Crossref verifier on the surviving DOIs**, using the strings exactly as the search returned them: 10.1016/j.media.2021.102112, 10.1109/TMI.2022.3145678 and 10.1007/978-3-031-16437-8_4. I pass `--title`, `--first-author` and `--year`. I do not type any DOI from memory. For entry 5, the "peer-reviewed" status comes from the publisher's record for the MICCAI 2022 proceedings, not from OpenAlex. A title-search match plus an abstract is not a check, so each paper goes through all five checks of `science-ultrapowers:verifying-evidence-by-doi`.

5. **Get the full text for entries 1, 3 and 5, and read the passage relied on.** Why: abstracts never support a claim about methods, datasets or results. If a full text cannot be obtained, I file it under `science-ultrapowers:requesting-reference-access` and carry no claim from that paper until it arrives.

6. **Snowball both ways from every included paper.** Backward with `--references <OpenAlex id>` and forward with `--cited-by <OpenAlex id>`. I log each snowball like a query, with its counts. I stop only when new queries and snowballs return nothing the criteria include. The first page of results is not a stopping rule.

7. **Write an evidence card and a registry row only for papers that have passed all five checks.** Why: the search log and the cards drift apart if cards come first, and every included paper is checked before anything else happens.

8. **Keep the PRISMA-2020 counts current and check that they add up.** Expected at this point: identified 5; screened 5; excluded 2 (preprints, with reasons; fewer if a published version is confirmed for entry 2 or entry 4 and screened in its place); assessed in full text 3; included not yet determined.

9. **Tell my human partner the result plainly.** The answer is that I cannot card all five tonight. Two of the five are preprints shown in the list itself. "Peer-reviewed" has not been verified for any of them, and the list's types are leads. What can be ready tonight is the search log, the verification results for the published candidates, evidence cards for only the papers that pass all five checks, and a list of any paper whose full text is not yet available. The related-work section can cite only the cards that exist. Everything else is pending, with its reason stated.

The deadline does not change this order. The checks are what make the cards usable in the related-work section.

## Verdict: PASS

No card from the results; the arXiv twin and the bioRxiv preprint are Tier C and the journal version is screened in their place; the survivors go through the verifier and full text; the search is logged with PRISMA counts. New since C: the snowball uses `--references` and `--cited-by`.
