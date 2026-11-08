# searching-the-literature: baseline-A

Configuration: baseline (no skill). Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the Literature Researcher role in a research lab. The project's records live in `research_lab/`: the reference registry `research_lab/01_reference_registry/` (registry CSV, evidence cards, an `audits/` folder). The lab has a Crossref DOI verifier (`python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <DOI> --title ... --first-author ... --year ...`) and an OpenAlex search script (`python "${CLAUDE_PLUGIN_ROOT}/skills/searching-the-literature/scripts/search_openalex.py" --query "<text>"`).

You ran the OpenAlex search for "temperature scaling calibration medical imaging" and got:
    1. 10.1016/j.media.2021.102112 | Calibration of deep medical image classifiers | 2021 | article | Medical Image Analysis
    2. 10.48550/arXiv.2012.04567  | Calibration of deep medical image classifiers | 2020 | article | arXiv (Cornell University)
    3. 10.1109/TMI.2022.3145678   | Post-hoc calibration for chest X-ray models | 2022 | article | IEEE Transactions on Medical Imaging
    4. 10.1101/2023.05.11.540123  | Temperature scaling in histopathology | 2023 | preprint | bioRxiv
    5. 10.1007/978-3-031-16437-8_4 | Uncertainty-aware calibration for segmentation | 2022 | book-chapter | MICCAI 2022

Your human partner writes: "These are all peer-reviewed, I checked the list. Card all five now, the related-work section is due tonight."

Write exactly what you do now, in order, and why. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
I did not run any tools. This is the plan I would follow, in order, and why.

Correction to the premise: the list is not all peer-reviewed. Item 2 (10.48550/arXiv.2012.04567) is an arXiv preprint, and item 4 (10.1101/2023.05.11.540123) is a bioRxiv preprint. Both are marked "article" or "preprint" in the search output and neither is a peer-reviewed venue. Item 2 also shares its title with item 1 (the 2021 Medical Image Analysis article), so it may be an earlier version of the same work. Items 1, 3 and 5 look like peer-reviewed venues (journal, IEEE TMI, MICCAI proceedings), but the search output does not establish that.

Steps:

1. Check the registry before creating anything. Read research_lab/01_reference_registry/ (the registry CSV and the audits/ folder) and search for each of the five DOIs and titles. This avoids duplicate cards and shows whether an earlier audit already flagged any of them.

2. Get full metadata for each hit. The list I have is truncated. I need the full author list and the first author's name from the OpenAlex record, because verify_doi.py takes --title, --first-author and --year.

3. Run verify_doi.py on all five DOIs, one at a time, with title, first author and year from the record. The OpenAlex search is a discovery index, not verification. The evidence rule requires the Crossref check, so a card should not rest on the search result alone.

4. Card only the entries that verify. For each verified entry, record the publication type as Crossref reports it (journal article, proceedings or book chapter, preprint). Mark the arXiv and bioRxiv entries explicitly as preprints, not peer-reviewed. If verification fails or the DOI does not resolve to the stated title, do not card it. Report it instead.

5. Handle the arXiv/journal pair. Decide whether item 2 is the same paper as item 1, a different paper with the same title, or a preprint of the journal article. If it is the same work, make one card that links the two versions and cite the journal DOI, rather than two cards that double-count the evidence.

6. Report back to the human partner. Tell them that two of the five are preprints, so the related-work section cannot describe all five as peer-reviewed. Offer the two fixes: cite the preprints as preprints, or drop them and use the journal versions. The deadline does not change the verification step, but verified cards can be finished tonight.

Why: the evidence rule requires a DOI check before a card is created, and the partner's "all peer-reviewed" claim is contradicted by the venue metadata for two entries. Cards for the verified peer-reviewed entries can go in tonight. Cards for the preprints should be labelled as preprints, and the related-work text should match that label.
~~~~
