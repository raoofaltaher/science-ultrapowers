# Baselines (no skill, Haiku 5.5): 0/3 pass

All three reject "these are all peer-reviewed", identify #2 (arXiv) and #4 (bioRxiv) as preprints, notice that #2 is the twin of #1, and plan to run the verifier on every DOI. They fail the lab's rules in three ways:

- **Preprints still get evidence cards.** A: "Card them as preprints and mark them so the related-work text cannot cite them as peer-reviewed". B: "Preprints are cited as preprints or dropped". C: "card it once as a preprint linked to the journal version".
- **The search is not logged.** No run records the search string, database, date or result counts in `research_lab/01_reference_registry/audits/`, and none gives screening counts.
- **No full-text reading before carding.** Cards rest on the Crossref match plus the abstract: "Read the abstract from Crossref or the publisher before writing the claim" (B).
