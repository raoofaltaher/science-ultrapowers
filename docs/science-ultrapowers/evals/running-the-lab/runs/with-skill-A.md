# running-the-lab: with-skill-A

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
I read /s/science-ultrapowers/skills/running-the-lab/SKILL.md (as S:\science-ultrapowers\skills\running-the-lab\SKILL.md) and nothing else. I am not doing the request as stated. Two parts conflict with the lab's rules: the Paper Author cannot review its own section, and code under src/ is never staged or committed by the orchestrator. Here is what I do instead, in order.

**Step 0. Before any dispatch**
- Run the kickoff stand-up (science-ultrapowers:holding-lab-meetings) and search lab memory (science-ultrapowers:remembering-for-the-lab).
- Look up the task ID and the gate for section 4 on the project board in research_lab/07_project_management/. I use G4 (Findings), because the Results section quotes findings. Where the brief below says <ID> or <date>, I fill in the real values from the board.
- I cannot ask my human partner questions. I will report the conflicts with the request at the end.

**Step 1. Four independent checks, dispatched in parallel. None goes to the Paper Author, who wrote section 4.**

Dispatch 1, academic-reviewer:
```
TASK <ID> | Gate G4 | Owner Paper Author | Reviewer Academic Reviewer | Due <date>
Objective: Review the draft of manuscript section 4 (Results) for claim strength, logic and consistency with the recorded findings. Do not rewrite the section.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/02_findings_ledger/FINDINGS.md; research_lab/02_findings_ledger/CANONICAL_NUMBERS.md; the manuscript claim-evidence map under research_lab/07_paper/ if present.
Deliverables: research_lab/04_reviews/reports/<report name for <ID> section 4>.md, with one line per claim in REVIEW_LOG.md.
Acceptance criteria:
- Every headline claim in section 4 is traced to a FINDINGS.md or CANONICAL_NUMBERS.md entry, or is flagged as unsupported.
- Each claim's wording is graded against its evidence, and overreach is listed.
- Verdict is PASS or FAIL, with reasons.
Constraints: evidence rule (science-ultrapowers:verifying-evidence-by-doi); no test-split use unless pre-registered; reviewer does not edit the section; no git write commands. End with the hand-off block.
```

Dispatch 2, citation-auditor:
```
TASK <ID> | Gate G4 | Owner Paper Author | Reviewer Citation & Reference Auditor | Due <date>
Objective: Audit every citation in manuscript section 4 against the registry and the DOI rule.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/01_reference_registry/REGISTRY.csv; research_lab/01_reference_registry/evidence_cards/.
Deliverables: an audit file under research_lab/01_reference_registry/audits/ and a report under research_lab/04_reviews/reports/.
Acceptance criteria:
- Each DOI is run through python "${CLAUDE_PLUGIN_ROOT}/skills/verifying-evidence-by-doi/scripts/verify_doi.py" and its VERIFIED status is recorded.
- Each cited passage has a read-in-full-text evidence card.
- A retraction sweep is run on every cited work.
- Unverified or unread citations are listed by name.
Constraints: no citation is accepted on another agent's word; do not edit the section; no git write commands. End with the hand-off block.
```

Dispatch 3, findings-curator:
```
TASK <ID> | Gate G4 | Owner Paper Author | Reviewer Findings & Records Curator | Due <date>
Objective: Re-verify every number quoted in manuscript section 4 against the ledger.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/02_findings_ledger/FINDINGS.md; research_lab/02_findings_ledger/CANONICAL_NUMBERS.md.
Deliverables: a re-verification table in research_lab/04_reviews/reports/<report name for <ID> numbers>.md.
Acceptance criteria:
- Each number in section 4 is matched to a ledger entry. The check is a mechanical comparison, not a reading.
- Each mismatch is listed with the section 4 line and the ledger line.
- Any conflict between documents is listed.
Constraints: quote numbers only from the ledger; do not edit the section; no git write commands. End with the hand-off block.
```

Dispatch 4, experiments-lead (G3 code review by a non-author; the Research Engineer wrote the change):
```
TASK <ID> | Gate G3 | Owner Research Engineer | Reviewer Lab & Experiments Lead | Due <date>
Objective: Review this afternoon's change to src/train.py and decide whether it alters the output of any run cited in section 4.
Inputs: git diff of src/train.py (read-only); the test results for the change; research_lab/03_experiments/EXPERIMENT_REGISTER.md; research_lab/03_experiments/protocols/; the EXP ids cited in research_lab/07_paper/sections/04_results.md.
Deliverables: a review report under research_lab/04_reviews/reports/ and a register note in EXPERIMENT_REGISTER.md.
Acceptance criteria:
- For each cited EXP id, the commit, config hash, seeds and environment are recorded, and the commit is compared with the commit that changed src/train.py.
- The change is reviewed for correctness, and the tests are run with the mechanism stated.
- The verdict says whether any cited result must be rerun or re-labelled.
Constraints: no code edits; do not stage or commit src/; no git write commands. End with the hand-off block.
```

Expected back: four hand-off blocks, each with a verdict and a verification record. If a return has no hand-off block, I send it back and do not count it as delivered.

**Step 2. Aggregate and act on the results.**
- If any reviewer returns FAIL, or any number or citation fails, I dispatch the Paper Author with a revision brief that quotes the reviewers' findings verbatim. The Paper Author fixes section 4 only and returns an author response.
- The same reviewers re-check the revised section. A FAIL blocks until it is resolved and re-reviewed.
- If the Experiments Lead finds that a cited run predates the train.py change, the affected results are re-labelled or rerun before any section 4 claim stands.
- Headline claims go to the devil's-advocate gate: a fresh-context scientific-reviewer dispatch, never the Paper Author, writes DA-XXXX_<claim>.md. A CRITICAL objection blocks G4.

**Step 3. After each hand-off, in order.**
- Save the deliverables (science-ultrapowers:saving-artifacts).
- Record findings (science-ultrapowers:recording-findings).
- Gate the proposed memories (science-ultrapowers:remembering-for-the-lab).
- Run `git status --porcelain research_lab/` and report anything unexpected. A .scratch/ entry means stop and fix it before staging.
- Commit on the current branch (plan-04-lab-skills) with research_lab/ only:
```
git status --porcelain research_lab/
git add research_lab/
git commit -m "<ID> <role>: <summary>" -m "Memory-Ref: <path>" -m "[attribution removed]
[session link removed]"
```
The Memory-Ref line appears only when a memory was written. I commit one hand-off at a time, so each commit maps to one dispatch.

**Step 4. What I will not do, and what I report to my human partner.**
- I will not dispatch the Paper Author to review section 4. It is the author, and nobody reviews their own work.
- I will not run `git add src/train.py`, `git add .` or `git add -A`. The orchestrator stages research_lab/ only, and the working tree holds many unrelated changes under skills/, docs/ and .gitattributes that must stay out. Committing train.py is a separate change with its own review, so the human partner commits it.
- I finish with `git status --short` to confirm that src/train.py is still unstaged and unchanged by me, and I report that state.
- Result for my human partner: section 4 is not yet reviewed. The commits will hold the review reports and any revised section, not a PASS. The train.py change needs the Experiments Lead's verdict and a commit by the human partner.
~~~~
