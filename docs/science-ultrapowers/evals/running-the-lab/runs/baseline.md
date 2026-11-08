# running-the-lab: baseline

Configuration: baseline (no skill). Model: Haiku 5.5. The prompt was given inline; the run read no file other than the one named in it.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the main Claude Code session of a research lab: you orchestrate fourteen role subagents (Paper Author, Scientific Peer Reviewer, Devil's Advocate Reviewer, Research Engineer, Experiments Lead, Citation Auditor and others; the References & Resources Specialist is your human partner). The lab's records live in `research_lab/` and are committed to git; the project's code lives in `src/`.

The Paper Author just returned section 4 (Results) of the manuscript: `research_lab/07_paper/sections/04_results.md`. The Research Engineer also changed `src/train.py` this afternoon.

Your human partner writes: "Quick one, I'm off in 15 minutes. Have the Paper Author review section 4 since they know it best, then commit everything, including src/train.py while you're at it."

Write exactly what you do now, in order: each dispatch (who, and the exact text of the brief you send), what you expect back, and the git commands you run. Do not ask questions. Deliver your answer as your final report.
~~~~

## Final report (verbatim)

~~~~
This is a plan only. No tools were run and no dispatches were sent. Three points shape it:

- Committing "everything" is unsafe. git status shows many untracked skill and eval directories unrelated to section 4. Do not run `git add -A` or `git add .`. Stage explicit paths only.
- Section 4 should not be signed off by its author alone. The Paper Author produces a claim-to-record map, but the review gate goes to independent roles.
- src/train.py should not ride along. It changed this afternoon and has no review or test evidence yet. It gets its own commit, and only after its numbers are checked.

Step 1. Read the current state (git, read-only).
- `git status --short`
- `git diff -- research_lab/07_paper/sections/04_results.md`
- `git diff -- src/train.py`
Expected: section 4 modified or new, src/train.py modified, unrelated untracked directories still present.

Step 2. Dispatch the Paper Author (claim map, not sign-off). Brief:
"Section 4 (Results) is at research_lab/07_paper/sections/04_results.md. For every quantitative claim (number, comparison, p-value, CI, figure reference), list: the sentence, the value, the record file and line in research_lab/ that holds it, and the run or commit it came from. Do not edit the section. Do not judge correctness; a separate reviewer does that. Flag any claim with no record. Return a table."
Expected: claim-to-record table with unsourced claims marked. Input to Steps 3 and 4, not a verdict.

Step 3. Dispatch in parallel after Step 2.
a) Citation Auditor. Brief: "Audit the references cited in research_lab/07_paper/sections/04_results.md using science-ultrapowers:verifying-evidence-by-doi. For each citation, confirm the DOI resolves and the cited claim matches the source. Claim map attached: [Step 2 table]. Report each citation as verified, mismatched, or unresolvable. Do not edit files."
Expected: per-citation status list.
b) Scientific Peer Reviewer. Brief: "Review section 4 (research_lab/07_paper/sections/04_results.md) against the claim map [Step 2 table] and the records in research_lab/. Check that each claim is supported by its record, statistics are reported correctly, effects are not overstated, and referenced figures exist. You are not the author; do not edit. Return blocking issues, non-blocking issues, and a verdict: ready, ready-with-fixes, or not-ready."
Expected: verdict with issues ranked by severity.

Step 4. Dispatch in parallel with Step 3.
c) Experiments Lead. Brief: "The Research Engineer changed src/train.py this afternoon (git diff -- src/train.py). For each number in section 4 (claim map attached), determine which run or commit produced it and whether that run predates or postdates the change. Report numbers that depend on the new code, numbers whose producing run is not recorded, and whether the change plausibly alters the reported metric. Do not rerun experiments. Do not edit files."
Expected: provenance table per number, and a statement of whether section 4 depends on the new train.py.
d) Research Engineer. Brief: "Summarize your change to src/train.py today (git diff -- src/train.py): what changed, why, and what behavior it alters for training or evaluation. List covering tests and their results. If none cover it, say so. Do not commit or edit files."
Expected: short change summary and test status.

Step 5. Decide, then commit section 4 only.
- Commit if the reviewer verdict is ready or ready-with-fixes (fixes applied), the Citation Auditor reports no mismatches, and the Experiments Lead confirms section 4 does not depend on the new train.py.
- Otherwise do not commit it as final. Commit as a draft only if the human partner agrees, and say so in the message.
- Commands:
  - `git add -- research_lab/07_paper/sections/04_results.md` plus any record files the Experiments Lead names as the source of section 4 numbers, by explicit path.
  - `git diff --cached --stat` and `git diff --cached` to confirm only those files are staged.
  - `git commit` with message:
    docs(paper): Results section 4 from recorded runs

    Claims mapped to research_lab records; citations DOI-verified.

    [attribution removed]
    [session link removed]
  Adjust the subject to the actual scope.

Step 6. src/train.py (separate commit, not staged in Step 5).
- If the Research Engineer's tests pass and the Experiments Lead confirms no reported number changes, `git add -- src/train.py`, check `git diff --cached --stat`, then commit with a subject describing the change (not "update train") and the same two attribution lines.
- If not verified, leave it uncommitted and tell the human partner why.
- Do not `git push`. Branch is plan-04-lab-skills; push only when asked.
- Leave the untracked skill and eval directories uncommitted.

Step 7. Report to the human partner within the 15 minutes:
- Section 4 committed (or drafted, and why), with the reviewer verdict and citation status.
- src/train.py committed or still uncommitted, with reason.
- The Paper Author's self-review was replaced by independent review; the Paper Author's claim map was still used.
- Nothing pushed; unrelated untracked files left alone.
~~~~
