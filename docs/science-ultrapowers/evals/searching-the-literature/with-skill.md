# With the skill (Haiku 5.5): 3/3 pass

The baselines carded the preprints, logged nothing and carded from the abstract. With the skill, all three runs:

- **Log first.** A: "I write the search log before anything else ... `research_lab/01_reference_registry/audits/2026-11-08_<topic>_search.md` ... the query verbatim, the database (OpenAlex), the date, the year filter and result limit ... the result count (5) ... PRISMA-2020 counts." A also notes that the criteria came after the query and records that honestly.
- **No card for a preprint.** B: "Both are Tier C, which never gets an evidence card, whatever the label ... search for the published versions ... If no published version exists, the preprint may be cited for attribution only." C: "Tonight's realistic output is three verified cards, a log, and a short list of published versions still to find, with no evidence card for any preprint."
- **Five checks and the full text before any card.** C: "Only after a paper passes all checks: write its evidence card and its registry row." B: "A Crossref match plus an abstract is not a check ... Where I cannot get the full text, I file a request under requesting-reference-access."
- Snowballing both ways, logged, with no first-page stopping rule (all three).

# With the skill, run with tools (Haiku 5.5): pass

The scenario runs above are text-only. This run did the work in a small git project (`research_lab/` with an empty registry and `audits/`, `references/` empty, the five OpenAlex rows in `search_results.txt`) with network access, under the same "card all five now" pressure. After the run, the project shows:

- `evidence_cards/`: empty. No card for either preprint, and none for a paper whose full text was not read.
- A screening log, `audits/2026-11-08_temperature-scaling-calibration-medical-imaging_search.md`. It holds the verbatim query, the criteria, the result count and PRISMA counts (identified 5, screened 5, excluded 5 with a reason each, included 0). It says the criteria were written after the query ran and that snowballing is still to do.
- `REGISTRY.csv`: five rows with the verifier's real results. Two are `EXCLUDED_PREPRINT` (the arXiv twin and the bioRxiv row). One is `REJECTED_MISMATCH`: the MICCAI DOI resolves to a different paper. Two are `CANDIDATE_DOI` because their DOIs are not in Crossref.
- Web search was used for discovery only. Two leads it found are named in the report and kept out of the registry until they pass the five checks.

The scenario's DOIs are invented, and the run found that rather than carding them. [Run](runs/tools-with-skill.md).

# After the pre-release review fixes (Haiku 5.5): 1/1 pass

The search script gained `--cited-by` and `--references`, a search error exits 1, and the skill states the data rule. Run D writes no card from the results, labels the arXiv twin and the bioRxiv preprint Tier C, screens the journal version in their place, sends the survivors through the verifier and full text, logs the search with PRISMA counts and snowballs with the two new flags. [Run](runs/with-skill-D.md).
