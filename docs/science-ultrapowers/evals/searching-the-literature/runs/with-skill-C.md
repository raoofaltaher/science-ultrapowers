# searching-the-literature: with-skill-C

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
I read /s/science-ultrapowers/skills/searching-the-literature/SKILL.md and nothing else. Answer to the exercise, in the order I would act:

1. I do not card all five tonight. The skill's Iron Law is "a search result is a candidate, never a source." Only the five checks in science-ultrapowers:verifying-evidence-by-doi, with the full text read at the cited passage, make a source. Each card needs that. A Crossref match plus an abstract is not a check.

2. I write the search log before anything else. The protocol requires `research_lab/01_reference_registry/audits/2026-11-08_<topic>_search.md` (the topic slug is mine to choose). It records the query verbatim, the database (OpenAlex), the date, the year filter and result limit actually used (if I do not know the limit, I say so), the result count (5), the inclusion and exclusion criteria, and the PRISMA-2020 counts. Protocol step 1 says criteria come before the first query. I ran the query without written criteria, so the log will say that and I will write the criteria now, dated as written after the search.

3. I sort the five candidates by tier, not by the database's "article" label:
   - #2 (10.48550/arXiv.2012.04567) is an arXiv DOI, so it is a preprint, Tier C. It gets no card. I search for its published version and screen that DOI instead. The skill allows citing a preprint only for attribution if no published version exists.
   - #4 (10.1101/2023.05.11.540123) is a bioRxiv preprint, Tier C, same rule.
   - #1, #3 and #5 are candidates, not sources. #1 shares its title with #2, so I check whether #2 is an earlier version of #1 and whether they are one work. #5 is listed as a MICCAI book chapter, which I verify rather than assume.

4. For each of #1, #3 and #5 I run the Crossref check with the DOI from the list and the title, first author and year: `python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <DOI> --title ... --first-author ... --year ...`. I do not type any DOI from memory. Then I run the rest of the five checks and read the full text at the passage I would cite. If I cannot get a full text, I file it under science-ultrapowers:requesting-reference-access and carry no claim from it until the text arrives.

5. Screening: title and abstract first, with every exclusion logged with its reason, then full text for what survives. I snowball backward and forward from each included paper and log those counts too. I stop only when new queries return nothing the criteria include. I do not stop after page one.

6. Answer to your partner: the three non-preprints can be carded once they pass the five checks, and I can work through them tonight. Two of the five are preprints by the list's own DOI prefixes (arXiv and bioRxiv), so "all peer-reviewed" does not hold for this list. Those two get no card under any deadline. For the related-work section they can be cited for attribution only, or replaced with their published versions if those verify. A list check by a person and a database type field are both leads and do not replace the five checks. Tonight's realistic output is three verified cards, a log, and a short list of published versions still to find, with no evidence card for any preprint.
~~~~
