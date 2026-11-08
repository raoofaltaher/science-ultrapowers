---
name: pr-review-toolkit
description: "Review pull requests and recent code changes across specialized lenses: general code quality, tests, error handling and silent failures, comments and docs, type design, and simplification. Use when the user asks to review a PR, review recent changes, check tests, check error handling, check comments, analyze types, simplify/refine an implementation, run \"review-pr\", or at a gate-3 (G3) code-review checkpoint."
---
> **LAB OVERLAY (binding).** Vendored third-party skill: `neuromechanist/research-skills` @ `f0219bde233a` (BSD-3-Clause). Where anything below conflicts with the lab's rules, the lab's rules win.
>
> 1. **Evidence rule wins.** Facts and citations come only through `science-ultrapowers:verifying-evidence-by-doi` (peer-reviewed, Crossref-verified DOI, full text read, evidence card). Never cite from web search, model memory or preprints.
> 2. **Records.** Numbers and results come only from `science-ultrapowers:recording-findings` (F-ids, `CANONICAL_NUMBERS.md`); work moves through the `science-ultrapowers:running-the-lab` gates.
> 3. **No pre-approved tools.** Any upstream `allowed-tools` grant was removed from this copy, so normal permission prompts apply.
> 4. **Tools in Claude Code:** read PDFs with the file reader, edit with the file tools, read the skill's bundled files under `${CLAUDE_PLUGIN_ROOT}/skills/pr-review-toolkit/`; packages the figure and poster skills need live in the project's `.venv-lab-skills` (see `science-ultrapowers:initializing-a-research-lab`).
> 5. **Not installed in this lab:** `epic-dev` -> `science-ultrapowers:running-the-lab` gates; `project-preflight` -> the linter, type checker, security scanner and tests the project brief names.
> 6. **Skill-specific:** Satisfies the G3 'code review by a non-author': the reviewer must be a fresh-context Research Engineer (or Scientific Reviewer) who did not write the change. The upstream dispatch branches and panel protocol were removed. For ML-pipeline changes apply `references/lab-ml-pipeline-checklist.md` (lab-authored after a first-hand read of this skill).
>
> Provenance, licence and change log: `PROVENANCE.md`.


# PR Review Toolkit

Portable PR review skill adapted for the project plugin. The upstream Anthropic
`pr-review-toolkit` inspired the review lenses; this implementation keeps the
procedure and rubrics in `references/` so every lab reviewer (a Claude Code
subagent or an inline check) uses the same source of truth.

## Review Lenses

- `code`: project rules, bugs, contracts, maintainability, security, and performance.
- `tests`: behavioral coverage, edge cases, negative paths, and brittle tests.
- `errors`: silent failures, broad catches, hidden fallbacks, and unhelpful user-facing errors.
- `comments`: comment accuracy, stale documentation, redundant comments, and missing rationale.
- `types`: invariants, validation boundaries, encapsulation, and illegal states.
- `simplify`: clarity and refactoring opportunities while preserving behavior.
- `all`: all applicable lenses. This is the default.

## Dispatch (lab overlay: replaces the upstream dispatch branches)

Run the reviewer in a **fresh context** and pass only framing (branch or PR scope, target module, lenses, mode), never the authoring rationale. The reviewer reads `references/review-procedure.md` and `references/review-rubrics.md` from this skill's folder before producing findings.

- **Claude Code:** delegate to the research-engineer (fresh context, not the author) or scientific-reviewer subagent with the same framing; for panel mode issue one Agent call per lens in a single message, then one synthesis call.
- **Inline fallback:** only when the agent running it did not write the change or manuscript under review; otherwise delegate as above, because an author reviewing their own work breaks the lab's independence rule (G3/G6). Use it when delegation is unavailable or the user wants an in-thread check, following the procedure file directly.

Independence: nobody reviews their own work (`science-ultrapowers:running-the-lab`). Log the result in `research_lab/04_reviews/` (`REVIEW_LOG.md`).

## Inputs To Collect

- Scope: PR number, branch range, staged changes, unstaged changes, or explicit files.
- Lens selection: one or more of `code`, `tests`, `errors`, `comments`, `types`, `simplify`, or `all`.
- Mode: advisory review by default; `pre-merge` selects the bounded panel when available; `single` and `inline` opt out; edit mode is allowed only when the user explicitly asks to simplify/refine or implement review fixes.
- Overrides: user-supplied model, effort, panel size, lens grouping, or fallback choice always wins over defaults.

## Required Workflow

1. Read `references/review-procedure.md`.
2. Read `references/review-rubrics.md`; for changes under `src/`, `config/` or the train/evaluate/test/predict/calibration scripts, also read `references/lab-ml-pipeline-checklist.md` (lab overlay).
3. (Lab overlay) Dispatch as described in the Dispatch section below (fresh-context reviewer via lab delegation, or inline).
4. Inspect the local project rules before generic preferences: nearest `AGENTS.md`, `CLAUDE.md`, `.rules/`, and relevant framework guidance.
5. Determine the diff scope with `git status`, `git diff`, `git diff --cached`, `gh pr view`, or `gh pr diff` as appropriate.
6. Select applicable lenses. Use `code` for every review unless the user explicitly excludes it.
7. If a panel ran, account for every reviewer and synthesize/deduplicate findings; independently verify load-bearing claims and close completed one-off agents.
8. Report findings first, ordered by severity, with concrete file and line references.
9. If no actionable findings exist, say so clearly and list any residual test gaps or verification limits.

## Output Shape

Use this structure unless the user asks for a different format:

```markdown
**Findings**
- Critical: ...
- Important: ...
- Moderate: ...

**Questions**
- ...

**Residual Risk**
- ...
```

For `simplify` in edit mode, make the smallest behavior-preserving patch, run the
relevant tests or checks, and summarize what changed.

## Attribution

Inspired by Anthropic's `pr-review-toolkit` plugin in
`anthropics/claude-code/plugins/pr-review-toolkit`. The upstream plugin README
identifies the plugin license as MIT; this project implementation is written as
an original project skill with attribution rather than a verbatim copy.
