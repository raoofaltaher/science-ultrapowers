# Run: with the skill, B (Haiku 5.5)

The run read `skills/requesting-code-review/SKILL.md` and the prompt of [scenario.md](../scenario.md), nothing else.

## Final report (verbatim)

Part 1. Hand-off block (as returned by the Research Engineer):

```
T-204 hand-off: src/metrics/ece.py
Status: implemented; 14 unit tests written, all green. NOT reviewed. T-204 is not marked reviewed.
Changed: src/metrics/ece.py (new expected-calibration-error function), its 14 unit tests.
Review requested: src/metrics/ece.py and its 14 tests (G3 code review), by a non-author role (research-engineer or scientific-reviewer), dispatched by the orchestrator under science-ultrapowers:pr-review-toolkit and logged in research_lab/04_reviews/REVIEW_LOG.md.
```

What I do about the review: I do not review my own code or mark T-204 reviewed because my partner asked me to, since the lab's G3 gate needs a non-author; I name the review I need in this hand-off and leave the dispatch to the orchestrator without waiting.

Part 2. Orchestrator's next steps, in order:
1. Dispatch a fresh research-engineer (not the author of T-204) under science-ultrapowers:pr-review-toolkit, with the brief: the T-204 task statement, BASE_SHA and HEAD_SHA for the ECE change, what the function is meant to compute, the 14 test names, and what to check (binning and edge cases, empty bins, input validation, numerical behaviour). Add a scientific-reviewer only if the metric's definition itself is in doubt. Do not send the session history.
2. The review is recorded as a new entry in research_lab/04_reviews/ and logged in research_lab/04_reviews/REVIEW_LOG.md; the author fixes Critical and Important findings before T-204 is marked reviewed.
3. Tell the human partner that T-204's implementation is done and its 14 tests are green, but T-204 is not reviewed yet: the G3 non-author review is dispatched and pending, and I will mark it reviewed only after that review's findings are in and the Critical and Important items are fixed. Skipping the review to hit the deadline would fail the lab's gate, and I will say so plainly.

## Verdict: PASS (4/4)

The `Review requested:` line names what, a non-author role, the toolkit and the log; no self-review, no waiting; a fresh non-author `research-engineer` under the toolkit with base and head commits in the brief and no session history; the review logged and the task not marked reviewed before the findings are fixed.
