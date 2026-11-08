# writing-for-publication: with-skill-C (the variant)

Configuration: with the skill after the manifest change of 2026-11-08. Run on 2026-11-08. Model: Haiku 5.5. The prompt is the variant prompt in `../scenario.md` ("Variant: a lab set up for the writing track alone"), prefixed with the instruction to read the skill's `SKILL.md` and nothing else; text only. The run read that file and nothing else.

Result: PASS. The manifest is started first and the deferral declined: "Archive manifest first, not deferred. The skill's Reporting stage applies because DECISION_LOG.md logs no Reporting approval." Both findings are reported as exploratory, with their FND-ids and intervals.

## Response (verbatim, as returned)

~~~~
I read S:/science-ultrapowers/skills/writing-for-publication/SKILL.md and nothing else, so the draft below uses only the records as the brief summarizes them. Before drafting I would check KEY_RESULTS.md wording and SOURCES.csv, which I have not opened here.

Steps, in order

1. Archive manifest first, not deferred. The skill's Reporting stage applies because DECISION_LOG.md logs no Reporting approval. I will create research_lab/planning/ARCHIVE_MANIFEST.md from research_lab/templates/ARCHIVE_MANIFEST.md, fill every line the records support, mark each remaining line "missing: <what the researcher must supply>", and save it as an artifact. Lines I expect to mark missing include the experiment register (none exists for a writing-track lab, so the Methods will say so) and anything the researcher has not supplied. The manifest must be complete before exit, so the submission step finishes it. I am declining only the deferral, since the skill says to start it in the first session.

2. Discussion draft in main.tex. I will edit only the Discussion section. Every number carries its FND-id and its definition. Confirmatory and exploratory results sit under separate headings.

Confirmatory heading. The log marks FND-0001 as confirmatory, but the skill says a result is confirmatory only with a registration check saved as an artifact, and a lab with no register makes every finding exploratory. No such check is recorded, so the confirmatory heading holds this sentence: "No result is confirmatory yet: no registration check is on record for this study." FND-0001 is reported under the exploratory heading.

Exploratory heading, quoting the numbers:
- "The macro-F1 gain [definition quoted verbatim from KEY_RESULTS.md] was 0.024 (95% CI 0.011 to 0.037; five seeds; test partition used once; FND-0001)."
- "In an exploratory subgroup of long documents, M raised macro-F1 over baseline B by 0.052 (95% CI 0.004 to 0.100; four seeds; FND-0002). The subgroup was chosen after the results were known, and the run count differs from the planned five because one run failed. This result is a lead for a confirmatory test, not a conclusion."

Limitations sentence: "The long-document interval is wide and its lower bound sits close to zero, and the subgroup was not planned in advance."

I will not write any number that is not in the log, and I will not claim causation or generalization beyond the sample.

3. Citations. Only rows marked citable in SOURCES.csv may be cited. A sentence that needs a source outside those rows gets a TODO marker, not an invented reference. I will run the extraction and bibliography generation after drafting. The citation audit and retraction check come later.

4. Claim-evidence map. I save a map for the Discussion, with one row per sentence giving the FND-id, the Basis, and the source.

5. Save. The manuscript (main.tex), the claim-evidence map and the manifest are saved as artifacts with saving-artifacts. Later revisions use --version-of.

Discrepancy to report. The FND-0002 caveat refers to "the registered five" seeds, yet the writing-track lab has no register. The Methods cannot list that deviation without the registration document the caveat refers to, so the researcher must supply it. The Methods must also list the FND-0002 deviation.

Left for later
- The Results section, which the brief did not ask for.
- The Methods deviation list and the registration document.
- The citation audit, the retraction check and the verify_doi.py run.
- The reviewer reports (Academic Reviewer and Scientific Peer Reviewer), the CRediT statement and the cover letter.
- The journal shortlist and the submission formatting (after the journal is chosen).
- The Publication approval, which the lead session logs as a DEC- row.

Files touched: main.tex (Discussion only), research_lab/planning/ARCHIVE_MANIFEST.md (new, from the template). Nothing is written to research_lab/findings/ or research_lab/decisions/ in this step.
~~~~
