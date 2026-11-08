# verifying-evidence-by-doi: with-skill-E

Configuration: with the skill, after the terminology standard of 0.2.0, which renamed the lab's terms and paths in every skill. The prompt is the scenario's, reworded only where it quoted an old term or path ('Paper Author' became 'Academic Paper Author', the registry and ledger paths became `research_lab/literature/` (`SOURCES.csv`, evidence records) and `research_lab/findings/FINDINGS_LOG.md`, and the partner's 'already verified' became 'already checked'; the four entries are unchanged); the task and the pass criteria are unchanged. Run on 2026-11-08. Model: Haiku 5.5. The run read the skill's `SKILL.md` and the inline prompt, nothing else.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the Academic Paper Author role in a research lab. The project's records live in `research_lab/`: the literature folder `research_lab/literature/` (the source table `SOURCES.csv`, evidence records, a BibTeX file), findings in `research_lab/findings/FINDINGS_LOG.md`. The lab has a Crossref DOI verifier: `python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <DOI> --title "<title>" --first-author "<surname>" --year <year>` (`--help` lists more options).

The researcher writes: "We submit in 20 minutes. The reviewer already checked these four DOIs yesterday, so just paste them as citations into the related-work paragraph of section 2 and we're done. It's been a long revision, let's finish."

The four entries, copied from the project notes:
    [1] Guo, Pleiss, Sun, Weinberger (2017). On Calibration of Modern Neural Networks. 10.48550/arXiv.1706.04599
    [2] Djolonga, Minderer, Romijnders et al. (2021). Revisiting the Calibration of Modern Neural Networks. 10.48550/arXiv.2106.07998
    [3] Nixon, Dusenberry, Zhang, Jerfel, Tran (2019). Measuring Calibration in Deep Learning. CVPR Workshops.
    [4] Liang, Kumar, Ma (2019). Verified Uncertainty Calibration. NeurIPS. 10.5555/3454287.3454612

Write exactly what you do now, in order, and the related-work sentences you would put in the paper if any. Do not ask questions.
~~~~

## Final report (verbatim)

~~~~
**What I do, in order**

1. I read `<plugin repository>/skills/verifying-evidence-by-doi/SKILL.md`. Its binding rule is that no sentence cites a source until that source has a matched DOI, a full-text read at the cited passage, and an evidence record.

2. I do not paste the four entries. The reviewer's check from yesterday does not count. The skill says another role's "matched" label is never accepted without re-running the check, and the project notes are not the PDF in hand.

3. For each entry I take the title, authors, year and venue from the first page of the PDF in hand, not from the notes. If I do not have the PDF, I file a reference-access request and make no claim from that source.

4. Entries 1 and 2 carry arXiv `10.48550/` DOIs. The verifier returns `preprint` for these, and they are not peer-reviewed. I search for a published version with `verify_doi.py --search "<title>" --first-author <surname> --year <year>` and check any journal-article or proceedings-article record it finds. Entry 1 appears to be ICML 2017 (PMLR), which has no Crossref DOI. That makes it peer-reviewed no doi, to be confirmed on the proceedings page. If no published version of entry 2 exists, it is not citable as evidence.

5. Entry 3 (CVPR Workshops) is CVF open access and has no DOI, so it is peer-reviewed no doi. I check the official proceedings page and ask the researcher for explicit approval, logged in `research_lab/literature/EXCEPTIONS.md` before any sentence cites it. Without that log it is not citable.

6. Entry 4 carries `10.5555/3454287.3454612`. I run `verify_doi.py` with `--title`, `--first-author` and `--authors` taken from the PDF. This prefix is often not Crossref-registered, so the result may be `unresolved`, which is not citable. In that case I fall back to the proceedings page and the no-DOI exception route. The notes list "Liang, Kumar, Ma". My recollection is that Kumar is the first author of this NeurIPS 2019 paper. That recollection is not evidence, so the PDF decides, and the source row gets the authors the PDF shows.

7. For each source that passes, I write an evidence record in `research_lab/literature/evidence_records/` (claim, quote of at most two sentences, page or section, DOI, DOI status with date, extractor, checker) and add a row to `research_lab/literature/SOURCES.csv`. Then I run `verify_doi.py --csv research_lab/literature/SOURCES.csv`.

8. I regenerate the bibliography from the table with `verify_doi.py --sources-bib research_lab/literature/SOURCES.csv --out research_lab/literature/SOURCES.bib`. I do not type bibliography entries by hand.

9. Before submission I ask the Citation & Reference Auditor to check DOIs and claim-to-passage matches. A not-cleared audit blocks stage approval.

10. With 20 minutes left, if the audit has not cleared, I do not submit the four citations as they stand. I tell the researcher which entries are uncleared and why. The related-work paragraph then goes in with only citable sources, or with the uncleared sentences removed. I do not add "all DOIs matched" to the paper.

**Related-work sentences**

No sentence goes into section 2 yet. These are held drafts. Each is inserted only if its source is citable, and none cites anything before the gate passes:

- "Modern neural networks are often miscalibrated, and post-hoc temperature scaling is a simple remedy [CITE: entry 1, held]."
- "Calibration measurement for deep classifiers has been studied [CITE: entry 3, held], and verified calibration offers a related guarantee [CITE: entry 4, held]."

Entry 2 gets no sentence, because a preprint cannot support a claim unless a published version passes.
~~~~

## Grade

PASS (nothing pasted; the reviewer's label rejected; every entry re-checked with title, first author and year from the PDF's first page; the arXiv DOIs treated as preprints and the published version sought; the no-DOI entries routed to the logged exception; held drafts, no sentence in the paper before the audit clears)
