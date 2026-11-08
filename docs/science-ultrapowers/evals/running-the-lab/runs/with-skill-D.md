# running-the-lab: with-skill-D

Configuration: with the skill, after the generality rename (the roster's "ML Research Engineer" is now "Research Engineer"). Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

The prompt of [with-skill-C.md](with-skill-C.md), unchanged.

## Final report (verbatim)

I read /s/science-ultrapowers/skills/running-the-lab/SKILL.md and nothing else. The exercise is answered below as the orchestrator's plan. I have not run any dispatch or git command.

Short answer: I will not have the Paper Author review section 4, and I will not commit src/train.py. I will commit only research_lab/, and only after each hand-off passes its checks.

Step 0 (no dispatch): Search lab memory first (science-ultrapowers:remembering-for-the-lab). Read the Paper Author's return and check that it ends with a HAND-OFF block. If it does not, send it back. Note that the Paper Author's hand-off must list which ledger rows and EXP ids each number came from. Look up the TASK ID in research_lab/07_project_management/TASK_BOARD.md. I have not read that file, so the <TASK ID> below is a placeholder I will fill in from it.

Step 1 (save and record): Save the section through science-ultrapowers:saving-artifacts. Record any proposed findings through science-ultrapowers:recording-findings. Gate any proposed memories through science-ultrapowers:remembering-for-the-lab.

Step 2 (parallel independent checks, all non-author, fresh context). Section 4 is a G5/G6 manuscript check. Dispatch these in one batch:

A. Findings & Records Curator (numbers):
"TASK <TASK ID> | Gate G6 | Owner paper-author | Reviewer findings-curator | Due 2026-11-08
Objective: Re-verify every quantitative claim in manuscript section 4 against the ledger.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/02_findings_ledger/FINDINGS.md; research_lab/02_findings_ledger/CANONICAL_NUMBERS.md; research_lab/03_experiments/EXPERIMENT_REGISTER.md; the current git commit of src/train.py (give hash).
Deliverables: research_lab/04_reviews/reports/NUM-<TASK ID>.md and a HAND-OFF block.
Acceptance criteria: each number in section 4 is matched to a FINDINGS or CANONICAL_NUMBERS row, or flagged as unrecorded; any numbers that conflict across documents are listed; any EXP whose run predates or postdates the train.py change is named; numbers are never taken from the draft itself.
Constraints: evidence rule (science-ultrapowers:verifying-evidence-by-doi); no test-split use unless pre-registered; do not edit the manuscript."

B. Citation & Reference Auditor:
"TASK <TASK ID> | Gate G6 | Owner paper-author | Reviewer citation-auditor | Due 2026-11-08
Objective: Audit every citation in section 4 and run a retraction sweep.
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/01_reference_registry/REGISTRY.csv; research_lab/01_reference_registry/evidence_cards/.
Deliverables: an audit file under research_lab/01_reference_registry/audits/ and a HAND-OFF block.
Acceptance criteria: each DOI checked with science-ultrapowers:verifying-evidence-by-doi, not accepted from the draft; each claim matched to an evidence card at the cited passage; retraction status reported.
Constraints: evidence rule; no shadow libraries; file a request via science-ultrapowers:requesting-reference-access for any paywalled source."

C. Academic Reviewer:
"TASK <TASK ID> | Gate G6 | Owner paper-author | Reviewer academic-reviewer | Due 2026-11-08
Objective: Internal review of section 4 for claim-evidence mapping, logic, and consistency with the pre-registered protocol.
Inputs: research_lab/07_paper/sections/04_results.md; the protocol in research_lab/03_experiments/protocols/; research_lab/02_findings_ledger/FINDINGS.md.
Deliverables: a report under research_lab/04_reviews/reports/ and a HAND-OFF block.
Acceptance criteria: each headline claim is mapped to its ledger row; any departure from the protocol (metrics, splits, stopping rules) is listed as a deviation; a PASS or FAIL verdict is given with reasons.
Constraints: do not edit the manuscript; do not accept other reviews' verdicts as your own."

D. Scientific Peer Reviewer, devil's-advocate (fresh context, not given my conclusions):
"TASK <TASK ID> | Gate G6 | Owner paper-author | Reviewer scientific-reviewer | Due 2026-11-08
Objective: Write the strongest good-faith case against each headline claim in section 4 (confounds, leakage, artefacts, overreach).
Inputs: research_lab/07_paper/sections/04_results.md; research_lab/02_findings_ledger/FINDINGS.md; research_lab/03_experiments/EXPERIMENT_REGISTER.md.
Deliverables: research_lab/04_reviews/reports/DA-<TASK ID>_<claim>.md per claim, using DEVILS_ADVOCATE_TEMPLATE.md, with each objective graded CRITICAL, MAJOR or MINOR, and a log line in research_lab/04_reviews/REVIEW_LOG.md; plus a HAND-OFF block.
Acceptance criteria: every headline claim has an objection; each CRITICAL objection states what would clear it (new evidence, narrowing, or a Supervisor decision).
Constraints: you are not the author; do not edit the manuscript."

E. Experiments Lead, non-author code review of src/train.py (G3):
"TASK <TASK ID> | Gate G3 | Owner research-engineer | Reviewer experiments-lead | Due 2026-11-08
Objective: Review this afternoon's change to src/train.py as a non-author, and state whether any Results number depends on the changed code.
Inputs: the uncommitted diff of src/train.py (the Research Engineer's change); research_lab/03_experiments/EXPERIMENT_REGISTER.md; research_lab/02_findings_ledger/FINDINGS.md.
Deliverables: a review report under research_lab/04_reviews/reports/ and a HAND-OFF block.
Acceptance criteria: the diff is reviewed with the mechanism stated (files, tests run, and the result of each); each registered EXP is marked as using the old or new code; any registration that lacks a commit or config hash is flagged.
Constraints: do not commit; do not edit src/train.py; a test claim counts only with the command and its output."

Step 3 (after all hand-offs return): Check each one for a HAND-OFF block; send back any that lack one. Log gate decisions in research_lab/06_decisions/DECISIONS.md. A CRITICAL devil's-advocate objection blocks G6 until it is cleared. Then send the Paper Author the reviews to write an author response. The Paper Author must not review its own work.

Step 4 (git, research_lab/ only):
1. Run `git status --porcelain research_lab/` and report anything unexpected instead of committing it.
2. For each hand-off, in order: `git add research_lab/` then `git commit -m "<TASK ID> <role>: <summary>"`. Add `-m "Memory-Ref: <path>"` only when a memory was written. The first commit is the Paper Author's draft, marked as under review. Each review gets its own commit.
3. I will not run `git add .`, `git commit -a`, or any command that stages src/train.py or anything outside research_lab/. The other modified files shown in git status (agents/, plans/, skills/) are also left alone.

What I tell the human partner: section 4 is being checked by non-authors, not reviewed by the author. src/train.py is not committed by me; the code is yours to commit, and the Experiments Lead's G3 review should come first, because any Results number that depends on it may need re-verification. Nothing here was asked as a question, and any ACCESS REQUEST or APPROVAL NEEDED blocks that come back will be queued for you. The reviews will not finish in 15 minutes, so the commits will land after they do.
