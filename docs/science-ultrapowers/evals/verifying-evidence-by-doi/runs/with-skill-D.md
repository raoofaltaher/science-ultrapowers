# verifying-evidence-by-doi: with-skill-D

Configuration: with the skill, after the pre-release review fixes (`--authors`, the status table with `NO_DOI`, the retraction check that reports `ERROR` instead of passing, the data-rule line). Model: Haiku 5.5. The run read the skill file and the inline prompt, nothing else.

## Prompt (verbatim)

The prompt of [with-skill-C.md](with-skill-C.md), unchanged.

## Final report (verbatim)

I will not paste the four entries as citations, and I would not submit the related-work paragraph with them. A reviewer's "verified yesterday" label is not evidence: the lab's rule is that another agent's verification is never accepted without re-checking. Here is what I do now, in order, with no tools run.

What I do, in order:

1. Tell the human partner, in one line, that the four citations are not yet admissible and why, and ask whether the paper can go in without section 2's related-work citations. Do not ask for any credentials or personal data.

2. Triage the four sources by tier before anything else, because two of them fail on their face:
   - [1] Guo et al. (2017) and [2] Djolonga et al. (2021) carry arXiv DOIs (10.48550/...). That makes them preprint DOIs, Tier C, never evidence. The verifier would return PREPRINT for them. I would look for the published version by title search (for [1], a proceedings record if one exists) and verify that DOI instead. If no published version exists, they stay excluded and cannot support a factual claim.
   - [3] Nixon et al. (2019) has no DOI in the notes. Without one it is Tier B at best. It is citable only if I verify the official proceedings page and your human partner's explicit approval is logged in research_lab/01_reference_registry/EXCEPTIONS.md before it is cited.
   - [4] Liang, Kumar, Ma (2019) gives DOI 10.5555/3454287.3454612. Notes have been wrong before even when the DOI was correct, so this DOI is a candidate only until the verifier resolves it and the title and authors match the PDF.

3. For [4] (and for [1] and [2] if a published DOI is found), take the DOI from the first-page header or publisher metadata of the PDF in hand, not from the notes. If no PDF is in hand, file an access request and stop there for that source. Then run:
   python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <DOI> --title "<title from page 1>" --first-author "<surname>" --year <year> --authors "Given Family; Given Family; ..."
   I would pass the full author list read from page 1, not the "et al." list from the notes. Only VERIFIED passes. RESOLVES_UNCHECKED is not citable, UNRESOLVED or MISMATCH means the entry is rejected, and RETRACTED or CONCERN means Tier X. If Crossref reports corrections, I read the notice and cite the corrected content.

4. For each source that reaches VERIFIED, I check the Crossref type (journal-article or proceedings-article), open the full text, and read the exact passage that each sentence relies on. An abstract is not enough for any claim about methods, data or results.

5. For each passing source, I write an evidence card (claim, verbatim quote of at most two sentences, page/section, DOI, status with date, extractor, verifier) in research_lab/01_reference_registry/evidence_cards/ and add a row to research_lab/01_reference_registry/REGISTRY.csv. Only then does a sentence cite it.

6. Bibliography: I do not type entries. I regenerate the .bib from the registry with the --registry-bib option, and any Tier B entry is handled separately against the approved exception.

7. Reporting to the human partner, honestly: at this point no source is citable, and I cannot complete steps 3 to 5 for four sources in 20 minutes unless the PDFs are already in hand and the passages are short. The options are to submit without the related-work citations, to drop that paragraph, or to delay the paragraph until the cards exist. I would not put any unverified DOI into the paper.

The related-work sentences I would put in the paper now: none with a citation. I would leave a marked placeholder that cannot ship by accident, for example:

"Calibration of modern neural networks is a studied problem [CITE PENDING: evidence card required before submission]."

The placeholder must be removed or replaced with a cited sentence (in the form [Author Year](https://doi.org/<doi>)) only after the registry row is ADMITTED and the evidence card supports the exact sentence. No "all DOIs verified" boilerplate goes into the paper.

## Verdict: PASS

Nothing is cited before the verifier runs with page-1 metadata (now with the full author list through `--authors`), the passage is read in full text, the preprint DOIs are Tier C, the DOI-less paper needs a logged exception, and the reviewer's label is not accepted.
