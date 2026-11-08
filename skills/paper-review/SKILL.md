---
name: paper-review
description: "Use this skill for \"review this paper\", \"review this manuscript\", \"peer review\", \"review my paper\", \"critique this manuscript\", \"review this submission\", \"give me feedback on my paper\", \"check my methods\", \"review my statistics\", \"review as a peer reviewer\", \"evaluate this manuscript\", \"review this PDF\", or mentions manuscript review, peer review, paper critique, or methodological review."
version: 0.1.1
---
> **LAB ADDENDUM (binding).** Adopted third-party skill: `neuromechanist/research-skills` @ `f0219bde233a` (BSD-3-Clause). Where anything below conflicts with the lab's rules, the lab's rules win.
>
> 1. **Evidence rule wins.** Facts and citations come only through `science-ultrapowers:verifying-evidence-by-doi` (peer-reviewed, DOI matched through Crossref, full text read, evidence record). Never cite from web search, model memory or preprints.
> 2. **Records.** Numbers and results come only from `science-ultrapowers:recording-findings` (FND-ids, `KEY_RESULTS.md`); work moves through the `science-ultrapowers:running-the-lab` stage approvals.
> 3. **No pre-approved tools.** Any upstream `allowed-tools` grant was removed from this copy, so normal permission prompts apply.
> 4. **Tools in Claude Code:** read PDFs with the file reader, edit with the file tools, read the skill's bundled files under `${CLAUDE_PLUGIN_ROOT}/skills/paper-review/`; packages the figure and poster skills need live in the project's `.venv-lab-skills` (see `science-ultrapowers:initializing-a-research-lab`).
> 5. **Not installed in this lab:** `humanizer` -> not installed (research-integrity policy): authors edit prose themselves and disclose AI assistance.
> 6. **Skill-specific:** Every literature reference used in a critique must go through `science-ultrapowers:verifying-evidence-by-doi`; the upstream 'flag from domain knowledge' fallback is forbidden, so say 'literature coverage not assessed' instead. Manuscript intake uses the file reader, not opencite. Use for the statistically deep dry run before the Publication stage; `peer-review` produces the final referee report, held under confidentiality.
>
> Provenance, license and change log: `PROVENANCE.md`.


# Academic Manuscript Review

Routes a manuscript to an **independent, fresh-context reviewer** that evaluates it for methodological soundness, statistical validity, logical consistency, and reproducibility, and returns a structured peer review. This skill is a thin dispatcher: it decides how to run the reviewer and in which mode. The review procedure, checklists, statistical and figure guides, principles, and output template all live in `references/` and are loaded by the reviewer, not duplicated here.

## When to use

Activate when the user wants peer-review feedback on a manuscript (journal article, conference paper, preprint).

## Why a fresh-context reviewer

Review validity depends on independence: a reviewer that shares the conversation that produced the manuscript is biased toward it. Run the reviewer in a separate context and pass only **framing** (manuscript path, target journal, manuscript type, revision status), never the authoring rationale. This is why the reviewer is a subagent on tools that support one, and an inline procedure where they do not.

## Modes (user decides each run)

- **Single (default):** one independent reviewer applies the full procedure end to end.
- **Panel (opt-in):** spawn independent reviewers in parallel on complementary lenses, then a synthesis pass. Trigger on "review panel", "multiple reviewers", or an explicit request. Lenses: **methods/design**, **statistics**, and **novelty/significance** (add **reproducibility** for methods-heavy or hardware papers). Each reviewer reads the whole manuscript but weights its lens and scores independently from `references/`; a final synthesis pass merges them into one Critical/Major/Minor review and surfaces genuine disagreement rather than averaging it away.

## Dispatch (lab overlay: replaces the upstream dispatch branches)

Run the reviewer in a **fresh context** and pass only framing (file paths, target journal or venue, mode), never the authoring rationale. The reviewer reads `references/review-procedure.md` from this skill's folder before producing findings.

- **Claude Code:** delegate to the scientific-reviewer (or academic-reviewer / data-evaluation-researcher) subagent with the same framing; for panel mode issue one Agent call per lens in a single message, then one synthesis call.
- **Inline fallback:** only when the agent running it did not write the change or manuscript under review; otherwise delegate as above, because an author reviewing their own work breaks the lab's independence rule (G3/G6). Use it when delegation is unavailable or the user wants an in-thread check, following the procedure file directly.

Independence: nobody reviews their own work (`science-ultrapowers:running-the-lab`). Log the result in `research_lab/04_reviews/` (`REVIEW_LOG.md`).

## The brain (do not duplicate into dispatch or agent shells)

- `references/review-procedure.md` -- step-by-step procedure: intake, read, methodology, logic, literature, reproducibility, figures, writing, output.
- `references/methodology-checklist.md`, `references/statistical-review-guide.md`, `references/figure-review-guide.md` -- the assessment checklists and guides.
- `references/review-principles.md` -- review philosophy and severity calibration.
- `references/review-output-template.md` -- the Synopsis / Critical / Major / Minor / References / Editor Note format.
- `examples/sample-manuscript-review.md` -- worked review for calibration; `examples/sample-manuscript-excerpt.md` -- sample manuscript input for testing.
- (Lab overlay) The prose-quality pass flags unclear or overclaiming prose for the authors to revise; the `humanizer` skill is not used in this lab.
