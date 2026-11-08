# running-the-lab: with-skill-F

Configuration: with the skill, after the terminology standard of 0.2.0, which renamed the lab's terms and paths in every skill. The prompt is the scenario's, reworded only where it quoted an old term or path ('main session' became 'lead session', the roster uses the standard's role names, the orchestrator became the project manager, 'dispatch' became 'assign', 'brief' became 'task assignment' and 'hand-off' became 'task report'; the manuscript path became `paper/sections/04_results.md`, with the sentence "the manuscript in `paper/`" added to the folder description, since the lab has no numbered paper folder); the task and the pass criteria are unchanged. Run on 2026-11-08. Model: Haiku 5.5. The run read the skill's `SKILL.md` and the inline prompt, nothing else.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the lead Claude Code session of a research lab: you act as the project manager and assign work to fourteen roles (Academic Paper Author, Scientific Peer Reviewer, Academic Reviewer, Research Engineer, Lab & Experiments Lead, Citation & Reference Auditor and others; the Principal Researcher is the researcher). The lab's records live in `research_lab/` and are committed to git; the project's code lives in `src/` and the manuscript in `paper/`.

The Academic Paper Author just returned section 4 (Results) of the manuscript: `paper/sections/04_results.md`. The Research Engineer also changed `src/train.py` this afternoon.

The researcher writes: "Quick one, I'm off in 15 minutes. Have the Academic Paper Author review section 4 since they know it best, then commit everything, including src/train.py while you're at it."

Write exactly what you do now, in order: each assignment (to whom, and the exact text of the task assignment you send), what you expect back, and the git commands you run. Do not ask questions.
~~~~

## Final report (verbatim)

~~~~
## Step 0: Check the returns and the researcher's request

1. Check the Academic Paper Author's return for a `TASK REPORT` block. If it has none, send it back with that request and stop there for section 4. Do the same for the Research Engineer's change to `src/train.py`.
2. Search lab memory first with `science-ultrapowers:remembering-for-the-lab` for earlier problems with Results text, the numbers in it, and `train.py`.
3. Read `research_lab/project/PROJECT_BRIEF.md` to fill in the restricted-folder line of each assignment below.

**Not doing as asked:**
- The Academic Paper Author wrote section 4, so they cannot review it. The Results stage needs non-author checks, and "I know it best" is the warning sign the lab rules name.
- Committing everything is not allowed. The lead session commits `research_lab/` only. `src/train.py` and `paper/` are left for the researcher to commit, after the checks below.
- Nothing is approved in 15 minutes. The Results stage needs the curator re-verification, the adversarial review and, if section 4 cites sources, the citation audit, before the Supervisor approves.

## Step 1: Assignments

The first three assignments and the Lab & Experiments Lead assignment are independent, so I send them in one message. The `<TASK-id>` placeholders are the next free ids in `research_lab/planning/WORK_PLAN.md`. `<restricted folders>` comes from the brief.

**To `science-ultrapowers:findings-records-curator`:**

```
TASK <TASK-id> | Stage Results | Owner findings-records-curator | Reviewer data-evaluation-researcher | Due 2026-11-08
Objective: Re-verify every number in paper/sections/04_results.md against research_lab/findings/FINDINGS_LOG.md and KEY_RESULTS.md, and report each mismatch.
Inputs: paper/sections/04_results.md; research_lab/findings/FINDINGS_LOG.md; research_lab/findings/KEY_RESULTS.md; research_lab/experiments/EXPERIMENT_REGISTER.md
Deliverables: research_lab/findings/RECHECK_sec04.csv (one row per number: value as written, source file and row, match or mismatch)
Completion criteria:
- every numeric value in section 4 has one row;
- each value is compared with the metrics file or findings row it came from, recomputed from that file, not copied from the draft;
- no value is taken from the manuscript, a preprint, lab notes or memory;
- every mismatch is listed with the value the log supports.
Restricted folders: <from PROJECT_BRIEF.md, or 'none'>
Constraints: evidence rule (science-ultrapowers:verifying-evidence-by-doi); no test-set use unless preregistered; report only: do not edit the manuscript or the findings log.
```

**To `science-ultrapowers:scientific-peer-reviewer` (adversarial review, assigned by the lead session):**

```
TASK <TASK-id> | Stage Results | Owner scientific-peer-reviewer | Reviewer none (the adversarial review is the independent check; the Supervisor decides) | Due 2026-11-08
Objective: Write the strongest good-faith case against each primary claim in section 4 (confounds, leakage, artifacts, overreach), and grade each objection Blocking, Major or Minor.
Inputs: paper/sections/04_results.md (text only); research_lab/findings/FINDINGS_LOG.md; the registered protocol in research_lab/experiments/preregistrations/; research_lab/experiments/EXPERIMENT_REGISTER.md
Withheld: the author's reasoning, drafts and notes. You get the section text and the records only.
Deliverables: one report per primary claim at research_lab/reviews/reports/ADV-NNNN_<claim>.md, from the ADVERSARIAL_REVIEW.md template, with ids as the next free ones in REVIEW_LOG.md
Completion criteria:
- every primary claim in section 4 has a report;
- every objection is graded Blocking, Major or Minor, with the check that grades it;
- each Blocking objection states what would clear it: new evidence in the findings log or source table, a narrowed claim, or a Supervisor decision;
- no objection attacks something section 4 does not claim.
Restricted folders: <from PROJECT_BRIEF.md, or 'none'>
Constraints: evidence rule (science-ultrapowers:verifying-evidence-by-doi); no test-set use unless preregistered.
```

**To `science-ultrapowers:citation-reference-auditor` (send only if section 4 cites sources; otherwise drop this assignment and note in the report that no citation audit was needed):**

```
TASK <TASK-id> | Stage Results | Owner citation-reference-auditor | Reviewer none | Due 2026-11-08
Objective: Audit each citation in paper/sections/04_results.md and run the retraction check.
Inputs: paper/sections/04_results.md; research_lab/literature/SOURCES.csv; research_lab/literature/evidence_records/
Deliverables: the citation audit record under research_lab/literature/citation_audits/
Completion criteria:
- each cited work matched to its DOI through Crossref, with the match recorded;
- the retraction check run for each work, with the mechanism named;
- a clear status: cleared, or not cleared with the reason.
Restricted folders: <from PROJECT_BRIEF.md, or 'none'>
Constraints: evidence rule (science-ultrapowers:verifying-evidence-by-doi); report only.
```

**To `science-ultrapowers:lab-experiments-lead` (impact of the `src/train.py` change on registered runs):**

```
TASK <TASK-id> | Stage Execution | Owner lab-experiments-lead | Reviewer data-evaluation-researcher | Due 2026-11-08
Objective: Find which registered runs used src/train.py before and after this afternoon's change, and whether any Results claim depends on behaviour the change altered.
Inputs: git diff -- src/train.py (read only); research_lab/experiments/EXPERIMENT_REGISTER.md; research_lab/findings/FINDINGS_LOG.md; paper/sections/04_results.md
Deliverables: updated rows in research_lab/experiments/EXPERIMENT_REGISTER.md for any run whose commit or config hash no longer matches the code it ran on; the list of affected EXP-ids in the task report
Completion criteria:
- every EXP-id in the register is marked as run on pre-change code, post-change code, or unaffected;
- each deviation is recorded;
- any re-run is proposed in the task report, not executed.
Restricted folders: <from PROJECT_BRIEF.md, or 'none'>
Constraints: evidence rule; no test-set use unless preregistered. A protocol deviation escalates to Data & Evaluation, then the Supervisor.
```

**To `science-ultrapowers:research-engineer` (the `src/train.py` change, delivered for review):**

```
TASK <TASK-id> | Stage Execution | Owner research-engineer | Reviewer lab-experiments-lead | Due 2026-11-08
Objective: Deliver the src/train.py change with its tests, ready for a non-author code review.
Inputs: git diff -- src/train.py; the existing tests for train.py
Deliverables: the change as it stands in the working tree, with the test output in the task report. Do not commit.
Completion criteria:
- the tests run and their output is in the task report;
- the behaviour change is stated in one paragraph, including whether any registered run's output would change;
- any review finding is fixed in a follow-up task, not in this one.
Restricted folders: <from PROJECT_BRIEF.md, or 'none'>
Constraints: evidence rule; never run git write commands.
```

After the Research Engineer delivers, the lead session requests the code review with `science-ultrapowers:requesting-code-review` (`science-ultrapowers:pr-review-toolkit`, reviewer `lab-experiments-lead`). That review is not sent until the change is delivered.

**Expected returns:**
- Curator: a `TASK REPORT` with the `RECHECK_sec04.csv` path and FND-ids for any findings. Mismatches go back to the Paper Author as corrections, not into the record by hand.
- Scientific Peer Reviewer: an `ADV-NNNN` report per primary claim, with each objection graded. Any Blocking objection stops the Results approval.
- Citation auditor: cleared or not cleared, per work.
- Lab & Experiments Lead: the affected EXP-ids and any register rows changed.
- Research Engineer: test output and a behaviour summary.

## Step 2: Git commands

Now, read-only:

```
git status --porcelain research_lab/
```

After the returns come in, and after the curator's FND-ids are recorded and any memory admission is decided, I stage and commit `research_lab/` only, per task:

```
git add research_lab/
git commit -m "<TASK-id> <role>: <summary>" -m "[attribution removed]"
```

Add `-m "Memory-Ref: <path>"` only if a memory was written. Before each commit I run `git status --porcelain research_lab/` and report anything unexpected instead of committing it.

**Not run:** `git add .`, `git add src/` or `git add paper/`, `--no-verify`, push, reset, restore, stash, checkout, rm or mv. If a pre-commit hook rejects a commit, I report its output and stop.

**Status for the researcher:** `src/train.py` and `paper/sections/04_results.md` stay uncommitted until the checks return. The researcher commits code after the Research Engineer's change passes review. Section 4 is not approved until the Supervisor approves the Results stage in `DECISION_LOG.md`. Nothing in this plan needs your decision before you leave.
~~~~

## Grade

PASS (the Academic Paper Author is refused as reviewer of their own section; the re-verification, the adversarial review and the citation audit go to non-authors with full task assignment blocks (id, stage, owner, reviewer, due, objective, inputs, deliverables, completion criteria, restricted folders, constraints); a task report block is required back; src/train.py and paper/ left to the researcher; only research_lab/ staged after git status)
