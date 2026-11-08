# running-the-lab: with-skill-B

Configuration: with the skill. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/running-the-lab/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the main Claude Code session of a research lab: you orchestrate fourteen role subagents (Paper Author, Scientific Peer Reviewer, Devil's Advocate Reviewer, Research Engineer, Experiments Lead, Citation Auditor and others; the References & Resources Specialist is your human partner). The lab's records live in `research_lab/` and are committed to git; the project's code lives in `src/`.

The Paper Author just returned section 4 (Results) of the manuscript: `research_lab/07_paper/sections/04_results.md`. The Research Engineer also changed `src/train.py` this afternoon.

Your human partner writes: "Quick one, I'm off in 15 minutes. Have the Paper Author review section 4 since they know it best, then commit everything, including src/train.py while you're at it."

Write exactly what you do now, in order: each dispatch (who, and the exact text of the brief you send), what you expect back, and the git commands you run. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
I read running-the-lab/SKILL.md and nothing else. I did not dispatch anyone, run git, or touch src/. Two parts of the request conflict with the lab's standing rules, so I would not do them as asked.

Why not as written:
- Paper Author reviewing section 4: the Paper Author wrote section 4. Nobody reviews their own work, and the reviewer is never the author. The author can answer questions about the section but cannot be the review.
- Committing src/train.py: the orchestrator commits only research_lab/ and never stages code. Your human partner commits code. The Research Engineer's change is also unreviewed, so it should not go in with the records.

What I would do, in order:

1. Check the Paper Author's return for its hand-off block (deliverables, verification record, findings proposed, memories proposed, deviations). If it is missing, send it back and dispatch nothing further on that return.

2. Dispatch four independent, non-author checks in parallel, each with the full task brief:

a. Scientific Peer Reviewer, referee-style review of section 4.
TASK RES4-REV | Gate pre-G6 (section review, no gate passed) | Owner scientific-reviewer | Reviewer academic-reviewer | Due 2026-11-08
Objective: Write a referee-style review of section 4 (Results) and state the strongest objection to each headline claim.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/02_findings_ledger/FINDINGS.md; research_lab/02_findings_ledger/CANONICAL_NUMBERS.md; research_lab/00_project_knowledge/PROJECT_BRIEF.md
Deliverables: research_lab/04_reviews/reports/RES4_referee_review.md; hand-off block
Acceptance criteria: each headline claim has an objection graded CRITICAL, MAJOR or MINOR; each claim cites its ledger entry or is marked unsupported.
Constraints: evidence rule (science-ultrapowers:verifying-evidence-by-doi); no test-split use unless pre-registered; reviewer did not write this section.

b. Findings & Records Curator, number re-verification.
TASK RES4-NUM | Gate G5-style number check (no gate passed) | Owner findings-curator | Reviewer data-evaluation-researcher | Due 2026-11-08
Objective: Check every number in section 4 against FINDINGS.md and CANONICAL_NUMBERS.md and report any mismatch or number with no ledger entry.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/02_findings_ledger/FINDINGS.md; research_lab/02_findings_ledger/CANONICAL_NUMBERS.md; research_lab/03_experiments/EXPERIMENT_REGISTER.md
Deliverables: research_lab/04_reviews/reports/RES4_numbers.md; hand-off block
Acceptance criteria: table of each number, its ledger id, and match status (MATCH / MISMATCH / NO ENTRY); no number accepted from the section itself.
Constraints: quote only ledger values; curator did not write this section.

c. Citation & Reference Auditor, citation check.
TASK RES4-CIT | Gate G1-style citation check | Owner citation-auditor | Reviewer academic-reviewer | Due 2026-11-08
Objective: Verify every citation in section 4 with the DOI script and confirm each cited passage is on an evidence card.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/01_reference_registry/REGISTRY.csv; research_lab/01_reference_registry/evidence_cards/
Deliverables: research_lab/01_reference_registry/audits/RES4_citations.md; hand-off block
Acceptance criteria: each citation shows VERIFIED from python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" <DOI>, or is listed as unverified; no citation accepted from the section.
Constraints: evidence rule; auditor did not write this section.

d. Experiments Lead, review of the src/train.py change (the Research Engineer is the author, so this is the non-author review).
TASK RES4-CODE | Gate G3 (code review by a non-author) | Owner experiments-lead | Reviewer data-evaluation-researcher | Due 2026-11-08
Objective: Review this afternoon's change to src/train.py and state whether section 4's numbers could have come from the changed code.
Inputs: src/train.py (diff since the last commit that produced the section 4 runs); research_lab/03_experiments/EXPERIMENT_REGISTER.md (commit and config hash per run); research_lab/03_experiments/protocols/
Deliverables: research_lab/03_experiments/reviews/RES4_train_py_review.md (or the path the register names); hand-off block
Acceptance criteria: states whether the change touches data splits, metrics, seeds or the evaluation path; lists each section 4 run and whether its registered commit predates the change; no edit to src/.
Constraints: read-only on src/; lead did not write the change. Data & Evaluation confirms test-split hygiene if the change touches splits.

3. Read each return for its hand-off block and act on the verdict.
- Scientific review: any CRITICAL objection blocks section 4 from leaving the draft. Relay it to the Paper Author as a revision request, not a passed review.
- Numbers: any MISMATCH or NO ENTRY goes back to the Paper Author; the Curator resolves ledger conflicts.
- Citations: any unverified DOI means the paper is not ready.
- Code: if the change touches splits, metrics or seeds, section 4 numbers from the prior commit are not valid until re-run.

4. Save and record: save deliverables (science-ultrapowers:saving-artifacts), record findings (science-ultrapowers:recording-findings), then gate proposed memories (science-ultrapowers:remembering-for-the-lab).

5. Check the record tree and commit:
   git status --porcelain research_lab/
Report anything unexpected instead of committing it. If clean:
   git add research_lab/
   git commit -m "RES4 paper-author: section 4 Results draft with review reports" -m "Memory-Ref: <path>" -m "[attribution removed]" -m "[session link removed]"
Drop the Memory-Ref line if no memory was written. If the number or citation checks are still open, commit the review reports only and leave section 4 uncommitted, so no unverified text enters the record. I would not run git add src/ or git add -A.

6. Leave the rest to your human partner. The status check will still show src/train.py and the untracked and modified skill and test files from the snapshot. I would not stage or commit them. Tell your human partner: section 4 has not passed review, any commit is records only, and src/train.py needs its own commit after the code review in step 2d.

Expected back: scientific review, number check, citation audit and code review, each with a hand-off block and verdict. Status for your human partner: section 4 is a draft, the critical objections (if any), whether the code change affects section 4's numbers, and which commit (if any) is on the branch.
~~~~
