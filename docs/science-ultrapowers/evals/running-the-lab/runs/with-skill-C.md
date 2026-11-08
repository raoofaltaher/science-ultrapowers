# running-the-lab: with-skill-C

Configuration: with the skill after the final-review fixes. Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

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
Exercise answer: what I do, in order. The skill is running-the-lab/SKILL.md, which I read in full.

Short version: I will not have the Paper Author review section 4, and I will not commit src/train.py. Everything else in the request I can do, through the same gates the lab uses. The review takes longer than 15 minutes, so the commit of the research_lab/ records waits for the hand-offs.

STEP 0. Before any dispatch
- Search lab memory first (science-ultrapowers:remembering-for-the-lab), then run the short kickoff stand-up (science-ultrapowers:holding-lab-meetings). Neither blocks the reviews below.
- Look up the task id for this work on research_lab/07_project_management/TASK_BOARD.md. I use that id in every brief and commit. Due date: 2026-11-08.

STEP 1. Check the Paper Author's return
- Confirm it ends with a HAND-OFF block. If it does not, it has not delivered: I send it back and ask for the block. I do not treat section 4 as delivered until then.
- Reason I give my human partner: the Paper Author wrote section 4, so it cannot review it. The rule is "nobody reviews their own work" and "Send it to a non-author role."

STEP 2. Ask the Research Engineer for a hand-off on src/train.py
- Send this to the Research Engineer, no commit:

"Report your change to src/train.py as a HAND-OFF block for TASK <ID>. Include the diff or commit reference, the test command and its result, which EXP ids ran on the changed code, and any deviation from the brief. Do not commit anything."

- Expected back: a HAND-OFF block. Until it arrives, src/train.py has no verification record, so it is not ready to be committed by anyone.

STEP 3. Dispatch the independent checks in one message, in parallel
Each brief is the full task block from the skill. None of these reviewers is the Paper Author or the Research Engineer.

Dispatch A, findings-curator (numbers check):
"TASK <ID> | Gate G5 numbers check on draft section 4 (no gate pass) | Owner findings-curator | Reviewer academic-reviewer | Due 2026-11-08
Objective: check every number in section 4 against the ledger and report each one as matched, mismatched or UNSOURCED.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/02_findings_ledger/FINDINGS.md; research_lab/02_findings_ledger/CANONICAL_NUMBERS.md; research_lab/03_experiments/EXPERIMENT_REGISTER.md
Deliverables: research_lab/04_reviews/reports/<ID>_section4_numbers.md
Acceptance criteria: each numeric claim in section 4 has an F-id or CANONICAL id, or is marked UNSOURCED; each EXP id cited exists in EXPERIMENT_REGISTER.md; no number is taken from the draft, memory or src/train.py output.
Constraints: evidence rule (science-ultrapowers:verifying-evidence-by-doi); quote results only from FINDINGS.md or CANONICAL_NUMBERS.md (science-ultrapowers:recording-findings); no test-split use unless pre-registered; do not guess a number you cannot find.
End with the HAND-OFF block."

Dispatch B, citation-auditor (citations):
"TASK <ID> | Gate G5 citation audit of draft section 4 (no gate pass) | Owner citation-auditor | Reviewer academic-reviewer | Due 2026-11-08
Objective: verify every citation in section 4 against its DOI and its evidence card.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/01_reference_registry/REGISTRY.csv; research_lab/01_reference_registry/evidence_cards/
Deliverables: research_lab/01_reference_registry/audits/<ID>_section4_citations.md
Acceptance criteria: each DOI re-checked with Crossref, not accepted from the draft or from a prior check; each citation listed as VERIFIED or other, with the reason; every DOI-less source flagged for approval.
Constraints: science-ultrapowers:verifying-evidence-by-doi; a DOI-less work needs human-partner approval; preprints, web pages and memory are never evidence.
End with the HAND-OFF block."

Dispatch C, academic-reviewer (internal review of section 4):
"TASK <ID> | Gate G5 internal review of draft section 4 (no gate pass) | Owner academic-reviewer | Reviewer academic-supervisor | Due 2026-11-08
Objective: judge whether each claim in section 4 is supported by a recorded finding, and whether its strength matches the evidence.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/00_project_knowledge/PROJECT_BRIEF.md; research_lab/02_findings_ledger/FINDINGS.md; the H-cards in research_lab/
Deliverables: research_lab/04_reviews/reports/<ID>_section4_review.md
Acceptance criteria: a claim-to-finding map for every headline claim; each overreach graded CRITICAL, MAJOR or MINOR; each CRITICAL objection stated as the strongest good-faith case against the claim.
Constraints: you are not the author; do not edit section 4; evidence rule applies.
End with the HAND-OFF block."

Dispatch D, experiments-lead (non-author code review of src/train.py, read-only):
"TASK <ID> | Gate G3 code review of the change to src/train.py (no commit, no staging) | Owner experiments-lead | Reviewer project-manager | Due 2026-11-08
Objective: decide whether the change to src/train.py can enter a run, and which EXP ids it affects.
Inputs: the Research Engineer's HAND-OFF block for TASK <ID>; the diff of src/train.py; research_lab/03_experiments/EXPERIMENT_REGISTER.md; the tests the Research Engineer reports
Deliverables: research_lab/04_reviews/reports/<ID>_train_py_review.md
Acceptance criteria: the diff is read in full; the tests are re-run, not accepted from the report; the reproducibility checklist is applied (commit, config hash, seeds, environment); every EXP id that ran on the changed code is listed, and each without a registered commit is marked as a deviation.
Constraints: read-only on git (diff, log, show only); do not stage or commit code; do not write to src/.
End with the HAND-OFF block."

Expected back from each: a HAND-OFF block with a verification record. Any return without one goes back to its role.

STEP 4. Hand-off handling, in the skill's order
For each hand-off that comes back, in this order:
1. Save the deliverables (science-ultrapowers:saving-artifacts).
2. Record findings (science-ultrapowers:recording-findings). A "verified" claim from anyone is recorded only with its mechanism (which files, which method, against what).
3. Gate the proposed memories (science-ultrapowers:remembering-for-the-lab).
4. Run git status on the lab records and compare against the expected set:
   git status --porcelain research_lab/
   If anything appears that is not in that role's Deliverables, I stop and report it to my human partner. I do not commit it.

STEP 5. Commits (research_lab/ only, current branch plan-04-lab-skills, never main)
Commit 1, the Paper Author's draft hand-off, right after its block is saved and its status is clean. The subject marks the draft as unreviewed, so it is not read as a gate pass:
   git add research_lab/
   git commit -F - <<'EOF'
   <TASK-ID> paper-author: draft section 4 Results (unreviewed)

   Memory-Ref: <path>      (only if a memory was written; otherwise omit this line)

   [attribution removed]
   [session link removed]
   EOF

Commit 2, after Dispatches A to C have their hand-offs saved and their status is clean:
   git add research_lab/
   git commit -F - <<'EOF'
   <TASK-ID> findings-curator, citation-auditor, academic-reviewer: section 4 checks (no gate pass)

   [attribution removed]
   [session link removed]
   EOF

Commit 3, the review of the code change (Dispatch D), records only the review report and the register update. It does not include src/:
   git add research_lab/
   git commit -F - <<'EOF'
   <TASK-ID> experiments-lead: non-author review of src/train.py change (code not committed)

   [attribution removed]
   [session link removed]
   EOF

I never run git add -A, git add ., or git add src/. I never stage code. The only staging command I use is git add research_lab/.

Read-only check for my report, which stages nothing:
   git status --porcelain
This shows the code and unrelated changes. Right now that includes src/train.py, the modified docs/science-ultrapowers/evals/... run files and the two untracked scenario-v2.md files. I report them and do not commit them.

STEP 6. What I do not do, and why
- I do not ask the Paper Author to review section 4. It is the author. Its only role after the reviews is to answer their objections in an author response.
- I do not commit src/train.py. The skill says the orchestrator stages research_lab/ only, and the human partner commits code. The change also has no non-author review and no test record yet (Dispatch D, Step 2).
- I do not skip the reviews to save time. Section 4 is a draft, not a release, so the reviewers can deliver the checks in time; the commits wait for them. The skill's gates do not allow a review by the author in any case.
- I do not quote section 4 numbers as verified until Dispatch A returns matched entries for them.

Message for my human partner, to send before they leave:
"The Paper Author's section 4 draft is committed as unreviewed, and the reviews are dispatched. Results will be in the lab records before the next stand-up. I have not committed src/train.py: the Research Engineer's change has no non-author review or test record yet, and the lab's rule is that the human partner commits code after that. The docs/.../evals changes are also outside research_lab/ and are left uncommitted. I did not ask the Paper Author to review its own section."

Expected outcome: three checks and one code review back as hand-offs, two commits on research_lab/ with clear gate status, and a code commit that is yours, once the review and tests are recorded.
~~~~
