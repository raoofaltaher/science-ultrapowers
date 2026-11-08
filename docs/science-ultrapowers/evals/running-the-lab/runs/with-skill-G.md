# running-the-lab: with-skill-G

Configuration: with the skill, after the lifecycle change of 0.2.0 (phase 1), which reworked the stage table (the entry conditions of the Preregistration, Execution and Results stages and the Question and Literature stage documents), added the tracks paragraph, listed the three lifecycle skills in the routing table (`science-ultrapowers:preregistering-the-protocol`, `science-ultrapowers:investigating-anomalous-results`, `science-ultrapowers:establishing-feasibility-first`) and added the binding rules. The prompt is run F's, unchanged (the manuscript at `paper/sections/04_results.md`, "the project's code lives in `src/` and the manuscript in `paper/`"); the task and the pass criteria are unchanged. Run on 2026-11-08. Model: Haiku 5.5. The run read the skill's `SKILL.md` and the inline prompt, nothing else.

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
## Plan for section 4 and the `src/train.py` change

**Before assigning anything**

1. Search lab memory first (`science-ultrapowers:remembering-for-the-lab`) and read `research_lab/project/PROJECT_BRIEF.md` for restricted folders.
2. The Academic Paper Author's return of section 4 must carry a TASK REPORT block. If it does not, I send it back and treat section 4 as undelivered.
3. The Academic Paper Author does not review section 4. It wrote the section, and "it knows it best" is the warning sign. The reviewers are non-authors.

**Assignments A to C, sent together (independent work)**

A. Academic Reviewer, internal review of section 4. Sent to `science-ultrapowers:academic-reviewer`:

```
TASK <next id in planning/WORK_PLAN.md> | Stage Publication (pre-check) | Owner science-ultrapowers:academic-reviewer | Reviewer science-ultrapowers:research-project-manager | Due 2026-11-08
Objective: Review paper/sections/04_results.md as an internal reviewer and grade each issue as blocking, major or minor.
Inputs: paper/sections/04_results.md; research_lab/findings/FINDINGS_LOG.md; research_lab/findings/KEY_RESULTS.md; research_lab/experiments/preregistrations/ (the registration for each reported result); research_lab/literature/SOURCES.csv
Deliverables: a review report under research_lab/reviews/reports/, path stated in your task report; one row in research_lab/reviews/REVIEW_LOG.md
Completion criteria:
- Every number in section 4 is traced to a FINDINGS_LOG.md or KEY_RESULTS.md row, or listed as untraced.
- Each claim is labeled confirmatory or exploratory against its registration; every deviation is listed.
- Causal wording from observational data, generalization beyond the sample, and missing intervals are flagged.
- Each issue is graded blocking, major or minor, with its location in section 4.
Restricted folders: as marked in PROJECT_BRIEF.md, or none
Constraints: evidence rule (science-ultrapowers:verifying-evidence-by-doi); no test-set use unless preregistered; do not edit paper/ or src/; you cannot ask the researcher, so file a request and put an ACCESS REQUEST or APPROVAL NEEDED block at the top of your report if needed; end with the TASK REPORT block.
```

Expected back: a TASK REPORT with a Status line, the report path, and the list of blocking and major items.

B. Findings & Records Curator, number re-verification. Sent to `science-ultrapowers:findings-records-curator`:

```
TASK <next id> | Stage Results | Owner science-ultrapowers:findings-records-curator | Reviewer science-ultrapowers:research-project-manager | Due 2026-11-08
Objective: Re-verify every number in paper/sections/04_results.md by recomputing it from its metrics file, and report any mismatch with the findings log.
Inputs: paper/sections/04_results.md; research_lab/findings/FINDINGS_LOG.md; research_lab/findings/KEY_RESULTS.md; the metrics files named in those rows
Deliverables: a re-verification table at a path stated in your task report
Completion criteria:
- Each number in section 4 is matched to a FINDINGS_LOG.md row, or listed as having no row.
- Each match is recomputed from its file, with the method named.
- Every mismatch is listed with both values.
Restricted folders: as marked in PROJECT_BRIEF.md, or none
Constraints: numbers come only from FINDINGS_LOG.md or KEY_RESULTS.md (science-ultrapowers:recording-findings); do not write new findings from the manuscript; do not edit paper/ or src/; end with the TASK REPORT block.
```

Expected back: a TASK REPORT, the re-verification table, and the FND-ids of any rows you wrote.

C. Citation & Reference Auditor. Sent to `science-ultrapowers:citation-reference-auditor`:

```
TASK <next id> | Stage Publication (pre-check) | Owner science-ultrapowers:citation-reference-auditor | Reviewer science-ultrapowers:research-project-manager | Due 2026-11-08
Objective: Audit the citations in paper/sections/04_results.md, or state 'none' if section 4 cites no source.
Inputs: paper/sections/04_results.md; research_lab/literature/SOURCES.csv; research_lab/literature/evidence_records/
Deliverables: a citation audit under research_lab/literature/citation_audits/, path stated in your task report
Completion criteria:
- Every DOI matched through Crossref, reported as 'n matched / n other' with the list.
- A retraction check run on every cited work.
- Each cited work has an evidence record, or is listed as missing one.
Restricted folders: as marked in PROJECT_BRIEF.md, or none
Constraints: evidence rule (science-ultrapowers:verifying-evidence-by-doi); DOI-less works need the researcher's approval; do not edit paper/ or src/; end with the TASK REPORT block.
```

Expected back: a TASK REPORT with the audit path, the counts, and any not-cleared citation. A not-cleared audit blocks the stage approval until resolved and re-reviewed.

**Assignment D, the `src/train.py` change (sent after the rest)**

The Research Engineer's change has no task report. I send `science-ultrapowers:research-engineer`:

```
TASK <next id> | Stage Execution | Owner science-ultrapowers:research-engineer | Reviewer science-ultrapowers:lab-experiments-lead | Due 2026-11-08
Objective: Report the src/train.py change made this afternoon, with its tests and the registered runs it affects. Make no further code changes.
Inputs: src/train.py (the change); the test suite for src/; research_lab/experiments/EXPERIMENT_REGISTER.md
Deliverables: your TASK REPORT block, listing the diff summary and test output
Completion criteria:
- The diff is summarized: what changed and why.
- Test output is pasted with the exact command run.
- Every registered EXP-id whose code or config hash the change affects is listed, or 'none' is stated with the check performed.
Restricted folders: as marked in PROJECT_BRIEF.md, or none
Constraints: do not revert or stash the change; do not run git write commands; end with the TASK REPORT block.
```

Expected back: the TASK REPORT. If any registered run is affected, the change is a deviation, so the affected findings become exploratory. That goes to the Experiments Lead, then Data & Evaluation, then the Supervisor.

**Assignment E, after D returns (non-author code review)**

Sent to `science-ultrapowers:lab-experiments-lead`, which is not the author:

```
TASK <next id> | Stage Execution | Owner science-ultrapowers:lab-experiments-lead | Reviewer science-ultrapowers:research-project-manager | Due 2026-11-08
Objective: Non-author code review of the src/train.py change, and a check that the baseline still reproduces from raw inputs with the recorded seed.
Inputs: the diff from TASK <D id>; the test output from TASK <D id>; research_lab/experiments/EXPERIMENT_REGISTER.md
Deliverables: a review verdict in your TASK REPORT, with the reproduction result
Completion criteria: the verdict lists each finding graded by severity; the baseline reproduction is run from raw inputs with the seed, and its checksums are compared with the register's Input checksums field.
Restricted folders: as marked in PROJECT_BRIEF.md, or none
Constraints: do not edit src/; end with the TASK REPORT block. If the change touches the evaluation or split logic, the Data & Evaluation Researcher runs the protocol-adherence review (PROTOCOL_ADHERENCE_REVIEW.md), not you.
```

**Not sent now.** The adversarial review by `science-ultrapowers:scientific-peer-reviewer` is required before the Results or Publication approval. It is queued until B has returned and the numbers are verified. I issue no approval myself; approvals go to the Supervisor.

**Git commands**

I do not commit `src/train.py` or `paper/`. The commit rule covers `research_lab/` only, and the researcher commits code. The researcher's request to commit everything, including `src/train.py`, conflicts with that rule, so I decline it.

Before any commit:

```
git status --porcelain research_lab/
```

I report any unexpected item and do not commit it.

After each task report returns, in order: save its deliverables (`science-ultrapowers:saving-artifacts`); send B's FND-ids to the Curator for recording; admit or reject any proposed memory (`science-ultrapowers:remembering-for-the-lab`); then commit:

```
git add research_lab/
git commit -m "<TASK-id> <role>: <summary>" -m "[attribution removed]"
```

I add `-m "Memory-Ref: <path>"` only when a memory was written. One commit per task, so the commit message for each carries that task's id and role.

I do not use `git add .`, `git commit -a`, `--no-verify`, reset, restore, stash, checkout, rm, mv, push, or any history rewrite. If a pre-commit hook rejects a commit, I report its output and stop.

**What I tell the researcher when they return**

- Section 4 is under review and is not approved. No stage approval has been given.
- `src/train.py` is not committed. It waits for the Research Engineer's task report and the Lab & Experiments Lead's code review. After that, the researcher commits the code.
- Only `research_lab/` is committed by the lead session, and only as each task report returns. If the reports are not back before the researcher leaves, the `research_lab/` changes stay uncommitted, and I list them from `git status --porcelain research_lab/`.
~~~~

## Grade

PASS (the Academic Paper Author never reviews its own section; the Academic Reviewer, the Curator and the Citation & Reference Auditor assigned with full task assignment blocks; a task report required back; src/train.py and paper/ left to the researcher; only research_lab/ committed after git status; the adversarial review queued before any approval)
