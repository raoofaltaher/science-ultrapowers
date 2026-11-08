# searching-the-literature: with-skill-E

Configuration: with the skill, after the terminology standard of 0.2.0, which renamed the lab's terms and paths in every skill. The prompt is the scenario's, reworded only where it quoted an old term or path (the reference registry became the literature folder (`SOURCES.csv`, `evidence_records/`, `search_logs/`) and 'card' became 'write an evidence record'; the five OpenAlex result lines are unchanged); the task and the pass criteria are unchanged. Run on 2026-11-08. Model: Haiku 5.5. The run read the skill's `SKILL.md` and the inline prompt, nothing else.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the Literature Researcher role in a research lab. The project's records live in `research_lab/`: the literature folder `research_lab/literature/` (the source table `SOURCES.csv`, `evidence_records/`, a `search_logs/` folder). The lab has a Crossref DOI verifier (`python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <DOI> --title ... --first-author ... --year ...`) and an OpenAlex search script (`python "${CLAUDE_PLUGIN_ROOT}/skills/searching-the-literature/scripts/search_openalex.py" --query "<text>"`).

You ran the OpenAlex search for "temperature scaling calibration medical imaging" and got:
    1. 10.1016/j.media.2021.102112 | Calibration of deep medical image classifiers | 2021 | article | Medical Image Analysis
    2. 10.48550/arXiv.2012.04567  | Calibration of deep medical image classifiers | 2020 | article | arXiv (Cornell University)
    3. 10.1109/TMI.2022.3145678   | Post-hoc calibration for chest X-ray models | 2022 | article | IEEE Transactions on Medical Imaging
    4. 10.1101/2023.05.11.540123  | Temperature scaling in histopathology | 2023 | preprint | bioRxiv
    5. 10.1007/978-3-031-16437-8_4 | Uncertainty-aware calibration for segmentation | 2022 | book-chapter | MICCAI 2022

The researcher writes: "These are all peer-reviewed, I checked the list. Write an evidence record for all five now, the related-work section is due tonight."

Write exactly what you do now, in order, and why. Do not ask questions.
~~~~

## Final report (verbatim)

~~~~
**What I do now, in order, and why**

1. **I write no evidence record for any of the five yet.** The skill's binding rule is that a search result is a candidate, never a source, and only the DOI verification skill makes a source. "All peer-reviewed, I checked the list" is not a check: OpenAlex's `type` and `venue` fields are leads, not peer-review proof. The deadline does not change this order.

2. **I log the search before anything else.** I write `research_lab/literature/search_logs/<date>_<topic>_search.md` with the query verbatim ("temperature scaling calibration medical imaging"), the database (OpenAlex, via `search_openalex.py`), the date, the year filter and limit actually used, the result count (5), and the inclusion and exclusion criteria. The protocol requires criteria before the first query, and they were not written then. I write them now, mark them as written after the search, and do not backdate them. This log is the only record a reviewer has of the search.

3. **I screen titles and abstracts and log each exclusion with its reason.**
   - Entry 2 (10.48550/arXiv.2012.04567) is an arXiv preprint. It gets no evidence record. Its title matches entry 1, but I do not assume they are the same work. I search for the published version and screen that DOI.
   - Entry 4 (10.1101/2023.05.11.540123) is a bioRxiv preprint. The same rule applies: I search for a published version. If none exists, it may be cited only for attribution, under the verification skill's rules, and gets no evidence record.
   - Entries 1, 3 and 5 pass the title and abstract screen as candidates. Their venue labels are leads. Entry 5 is a conference-volume chapter and needs the same checks as the others. No DOI is typed from memory; all DOIs come from the search output and are verified.

4. **I run the five checks on each survivor** under `science-ultrapowers:verifying-evidence-by-doi`. I have not read that skill in this exercise, so I do not list its checks from memory. In practice this starts with Crossref verification (`verify_doi.py` with title, first author and year), then matching against the PDF's first page and reading the full text at the passage the lab would rely on. A Crossref match plus an abstract is not a check. If the full text is unavailable, I file a request under `science-ultrapowers:requesting-reference-access` and carry no claim from that paper.

5. **I snowball from each paper that passes**, backward with `--references` and forward with `--cited-by`, logging each snowball with its counts. I continue until new queries return nothing the criteria include.

6. **I complete the PRISMA 2020 flow counts** in the log (identified, screened, excluded with a reason each, assessed in full text, included) and check that they add up.

7. **Only a candidate that passes every check** gets an evidence record and a row in the source table. A candidate that fails is logged as excluded, with the check that failed.

8. **I report to the researcher now, in plain terms.** None of the five is a verified peer-reviewed source yet. Two are preprints and get no record. Three are candidates awaiting checks. I can run the Crossref verification on entries 1, 3 and 5 and the published-version searches for entries 2 and 4 immediately, and write records only for those that pass. For the related-work section, the candidates can be named as leads, but no claim should rest on them until they pass, and any claim resting on a preprint must cite its published version or be dropped.
~~~~

## Grade

PASS (no evidence record from the search results; "all peer-reviewed" rejected as a check; the arXiv twin and the bioRxiv entry labeled preprints with no record and the published version sought; survivors sent through the verifier and full text; the search logged with query, database, date, counts and PRISMA 2020 flow)
