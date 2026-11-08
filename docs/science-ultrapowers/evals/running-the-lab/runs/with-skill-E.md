# running-the-lab: with-skill-E

Configuration: with the skill, after the pre-release review fixes (hand-off block lines `Findings proposed`, `Memories proposed`, `Review requested`; the commit rule; the Findings Curator dispatched by the orchestrator; `science-ultrapowers:requesting-code-review` for code). Model: Haiku 5.5. The run read the skill file and the inline prompt, nothing else.

## Prompt (verbatim)

The prompt of [with-skill-C.md](with-skill-C.md), unchanged.

## Final report (verbatim)

Answer to the exercise (running-the-lab). The human partner's request conflicts with two standing rules, so I do not follow it as written. Everything else is done in the order below.

Summary for the human partner: I will not have the Paper Author review section 4 (the author cannot review their own work), and I will not commit src/train.py (only research_lab/ is committed; the human partner commits code). Section 4 is not passed by anyone when you return; the independent reviews are still running. src/train.py stays uncommitted until its non-author review is done.

Step 0. Search lab memory first.
Invoke science-ultrapowers:remembering-for-the-lab with the query: "section 4 results review; src/train.py change this afternoon; commit scope". Use any hits as context. No memory is written at this step.

Step 1. Check the Paper Author's return.
Confirm the return ends with a HAND-OFF block. If it has none, send it back to the Paper Author with the request for the block before anything else. Record its "Findings proposed" and "Review requested" lines for steps 3 and 4.

Step 2. Save the deliverable.
Invoke science-ultrapowers:saving-artifacts for research_lab/07_paper/sections/04_results.md, so the artifact store holds the section with its lineage (its inputs as listed in the hand-off).

Step 3. Dispatch the independent checks in parallel, in one message. None of them is the Paper Author.

3a. Academic Reviewer (academic-reviewer):
TASK <ID> | Gate pre-G6 dry run (no gate passed) | Owner paper-author | Reviewer academic-reviewer | Due 2026-11-08
Objective: Internal review of manuscript section 4 (Results) for claim strength, logic and clarity.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/02_findings_ledger/FINDINGS.md; research_lab/02_findings_ledger/CANONICAL_NUMBERS.md; research_lab/03_experiments/protocols/ (protocol for each claimed result)
Deliverables: research_lab/04_reviews/reports/<ID>_section4_internal-review.md; a line in research_lab/04_reviews/REVIEW_LOG.md
Acceptance criteria: every claim in section 4 is mapped to a ledger id or marked unsupported; each overstated or unsupported claim is listed with a severity; no number is quoted that is not in FINDINGS.md or CANONICAL_NUMBERS.md
Constraints: evidence rule (science-ultrapowers:verifying-evidence-by-doi); no test-split use unless pre-registered; do not edit section 4; end with the hand-off block
Expected back: a review report path and a hand-off block. Any return without the block is sent back.

3b. Findings & Records Curator (findings-curator):
TASK <ID> | Gate pre-G6 dry run | Owner paper-author | Reviewer findings-curator | Due 2026-11-08
Objective: Re-verify every number in section 4 against its source file.
Inputs: research_lab/07_paper/sections/04_results.md; FINDINGS.md; CANONICAL_NUMBERS.md; the metrics files named in the ledger
Deliverables: a number-check table in the hand-off block (no ledger write)
Acceptance criteria: each number is recomputed from its file and matched to its ledger row; each mismatch is listed with both values; conflicting numbers across documents are flagged for the Curator's own escalation path
Constraints: no new findings written from this brief; hand-off block required
Expected back: the table and the hand-off block.

3c. Citation & Reference Auditor (citation-auditor):
TASK <ID> | Gate pre-G6 dry run | Owner paper-author | Reviewer citation-auditor | Due 2026-11-08
Objective: Audit every citation in section 4.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/01_reference_registry/REGISTRY.csv; evidence_cards/
Deliverables: research_lab/01_reference_registry/audits/<ID>_section4-citations.md
Acceptance criteria: each DOI is checked with science-ultrapowers:verifying-evidence-by-doi and its result stated as VERIFIED or other; each citation is matched to an evidence card; any DOI-less work is listed for the human partner's approval
Constraints: evidence rule; check each DOI again, do not accept the Paper Author's claim; hand-off block required
Expected back: the audit path and the hand-off block.

Step 4. Dispatch the review of src/train.py (not the Research Engineer's own review).
Invoke science-ultrapowers:requesting-code-review, which sends the change to a non-author role. Use experiments-lead:

TASK <ID> | Gate G3 (execution) | Owner research-engineer | Reviewer experiments-lead | Due 2026-11-08
Objective: Non-author code review of this afternoon's change to src/train.py against the G3 reproducibility checklist.
Inputs: the diff of src/train.py from this afternoon (read with git diff and git log; do not modify or stage it); research_lab/03_experiments/protocols/ (the pre-registered protocol); research_lab/03_experiments/EXPERIMENT_REGISTER.md
Deliverables: research_lab/04_reviews/reports/<ID>_train-py_code-review.md; a line in REVIEW_LOG.md
Acceptance criteria: each changed hunk is classed as no-effect, behaviour-changing or protocol-deviating; any EXP run made on the old or new code is listed with its commit and config hash; seeds, splits and metric code are checked against the protocol; the review names the checks it ran
Constraints: no test-split use; the reviewer does not edit src/; no git write commands; hand-off block required
If the diff touches splits, seeds or evaluation code, also dispatch data-evaluation-researcher for a test-hygiene sign-off; that is a G2 condition for the protocol.

Step 5. Log the open items.
Write the pending checks and the gate status (G0 to G6 unchanged, section 4 not passed) to DECISIONS.md only if a gate decision is taken. Otherwise no entry; the reviews are logged in REVIEW_LOG.md as they arrive.

Step 6. Report any unexpected state, then commit research_lab/ only.
Run: git status --porcelain research_lab/
Run: git status --porcelain -- src/
Expected: the section 4 files and review reports under research_lab/. Anything else under research_lab/ is reported instead of committed. src/train.py is listed as modified and is not staged.
Stage and commit the research_lab/ files only (on the current branch):
git add research_lab/
git commit -m "<ID> paper-author: section 4 results draft saved; internal, citation and number reviews requested" -m "Memory-Ref: <path>"
Add the Memory-Ref line only if a memory was written in steps 0 or 1, which is not expected.
If the pre-commit hook rejects the commit, report its output and stop. Do not use --no-verify.
Never run git add . or git add src/ or stage train.py. Never run reset, restore, stash, checkout, rm, mv, push or history rewriting.

Step 7. What the human partner gets back.
- Section 4 is saved and committed as a draft, with its three independent reviews pending. It is not passed, and the Paper Author has no role in its review. The Paper Author receives the reviewers' findings afterwards for the author response.
- src/train.py is uncommitted, with its non-author review pending. The human partner commits the code after that review, and the reviewer will also state whether any run used the new code.
- No question is asked of the human partner in this flow. Any ACCESS REQUEST or APPROVAL NEEDED block returned by a role is relayed as a question, and the answer is recorded in ACCESS_REQUESTS.md.

## Verdict: PASS

Non-author reviewers with the full brief block; the hand-off block required; `src/train.py` left to your human partner; `research_lab/` only, after `git status`. New since D: the hand-off's `Findings proposed` and `Review requested` lines are read, the code review goes through `science-ultrapowers:requesting-code-review`, and the Findings Curator is dispatched by the orchestrator.
