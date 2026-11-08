# searching-the-literature: baseline-B

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
No tools were run. This is the plan, in order, and why.

1. Read the registry and existing cards first. Open the registry CSV in research_lab/01_reference_registry/ and check the evidence-card format and the audits/ folder. Check whether any of the five DOIs are already registered, so nothing is carded twice. The OpenAlex output has no first authors, so take them from the full search record or from Crossref. Verification needs them.

2. Verify every DOI with verify_doi.py before carding. Run each DOI with its title, first author and year. The search hit is a lead, not a check. The evidence rule requires a Crossref match before any card is written. Keep the verifier output for the audit trail.

3. Classify each work by its Crossref type, not the OpenAlex label. The partner's premise that all five are peer-reviewed is wrong for at least two:
   - #2, 10.48550/arXiv.2012.04567: an arXiv preprint, not peer-reviewed unless a journal version exists. It has the same title as #1 (Medical Image Analysis, 2021), so it may be an earlier preprint of the same work. Check Crossref for is-preprint-of / has-preprint relations. If it is the same work, card it once as a preprint linked to the journal version, and do not count it as a second source.
   - #4, 10.1101/2023.05.11.540123: a bioRxiv preprint, not peer-reviewed. Card as a preprint, stated as such.
   - #1, #3, #5: Medical Image Analysis, IEEE TMI, and the MICCAI 2022 LNCS chapter are peer-reviewed venues, but each must still pass the Crossref check. The MICCAI item is a conference proceedings chapter, carded as peer-reviewed conference paper.

4. Check relevance against the query "temperature scaling calibration medical imaging". #3 (post-hoc calibration) and #5 (uncertainty-aware calibration) may be relevant, but the card's claim must match what the paper says. Read the abstract from Crossref or the publisher before writing the claim.

5. Card only what passes. A work that verifies with matching title, author and year gets an evidence card recording its status ("peer-reviewed journal", "peer-reviewed conference", or "preprint, not peer-reviewed") and the verifier result. Any DOI that fails, or whose Crossref title or author does not match, gets no verified card and goes on a hold list with the reason.

6. Report to the partner before the deadline with: which five verified and which are preprints; whether #2 duplicates #1; which failed and why. Do not card all five as peer-reviewed, because the related-work section would then contain a false claim. Card the verified peer-reviewed works tonight. Preprints are cited as preprints or dropped from the peer-reviewed claim; that choice is the partner's.

Why: carding the list as asked would enter two preprints, and possibly a duplicate, into the registry as peer-reviewed evidence, which the evidence rule exists to prevent. Verifying first takes minutes per DOI and still meets the deadline. Skipping it risks a false claim in a manuscript due tonight.
~~~~
