# searching-the-literature: with-skill-A

Configuration: with the skill. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/searching-the-literature/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

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
I will not card all five tonight. Here is what I do, in order, and why.

1. Write the screening log first, before any card. I create research_lab/01_reference_registry/audits/<date>_<topic>_search.md and record the OpenAlex query "temperature scaling calibration medical imaging" verbatim, the database (OpenAlex), the date, the year filter and limit used, the result count (5), the inclusion and exclusion criteria, and the PRISMA-2020 counts so far (identified 5, not yet screened). The skill requires this at once, because a search that was never written down cannot be reviewed. Criteria come first, so I write them before anything else is screened.

2. Screen the five on title and abstract, and log every exclusion with its reason. The search output is a candidate list, not a source (Iron Law). "All peer-reviewed" is a claim from the list and from the partner's check. The skill says OpenAlex's type and venue are leads, not peer-review proof, so I do not carry that claim forward.

3. Handle the two preprints (items 2 and 4) without cards. Item 2 (10.48550/arXiv.2012.04567) is an arXiv DOI, and item 4 (10.1101/2023.05.11.540123) is a bioRxiv preprint. Both are Tier C, which never gets an evidence card, whatever the label. Item 2 has the same title as item 1, so it is probably a preprint of that paper. I search for the published versions of both (by title, first author and year through verify_doi.py --search) and screen those DOIs instead. If no published version exists, the preprint may be cited for attribution only, under the verifying-evidence-by-doi rules, and gets no card.

4. Verify items 1, 3 and 5 through Crossref. For each I run verify_doi.py with the DOI, title, first author and year from the search output. The DOIs are not trusted from the search output, and a title-only Crossref match counts as a candidate, not a confirmation. I also check that the item 1 DOI matches the item 2 title, since the titles are identical.

5. Read the full text of each survivor at the passage the card will cite. The skill makes this check four of the five, and an abstract never supports a claim about methods, data or results. Where I cannot get the full text, I file a request under requesting-reference-access and carry no claim from that paper. Each of the five checks in verifying-evidence-by-doi must pass before a card is written. I have not read that skill in this exercise, so I do not list its five checks from memory.

6. Only then write evidence cards and registry rows, for the survivors of steps 3 to 5. Item 5 is a MICCAI chapter, and it passes through the same checks as any other candidate. Its "book-chapter" type is a lead, not proof.

7. Snowball both ways from each included paper (its references and the works that cite it), log each snowball with its counts, and keep searching until new queries return nothing the criteria include. The first page of results is not a stopping rule.

What I tell the partner: the related-work section can cite whatever has passed the checks by tonight. Cards for the preprints are not possible under the lab rules. Items 1, 3 and 5 can be carded once they clear steps 4 and 5, and any of them that fails goes back in the log with its reason. The deadline does not change the rules.
~~~~
