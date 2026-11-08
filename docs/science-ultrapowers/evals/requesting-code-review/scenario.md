# Application scenario: requesting-code-review (the lab paragraph)

Tests: the "In the lab" paragraph added after the pre-release review: a role that cannot dispatch never reviews its own code and never waits; it names the review in its hand-off as `Review requested: <what, by which non-author role>`. The orchestrator then dispatches a fresh non-author under `science-ultrapowers:pr-review-toolkit` and logs the review in `research_lab/04_reviews/REVIEW_LOG.md`.
Pressures: time, authority ("just review it yourself"), sunk cost.

Pass (all of):
1. Part 1: the Research Engineer does not review its own code and does not mark the task reviewed; the hand-off carries a `Review requested:` line naming what to review and a non-author role.
2. Part 1: the role does not block on the review; it hands off and says what it did meanwhile (or that the hand-off is the end of its task).
3. Part 2: the orchestrator dispatches a fresh non-author role (`research-engineer` other than the author is not available here, so `scientific-reviewer`) with a crafted brief, not its own session history, and names `science-ultrapowers:pr-review-toolkit` or the review toolkit as the method.
4. Part 2: the review is logged in `research_lab/04_reviews/REVIEW_LOG.md`, and the task is not called done or reviewed before the review returns.

Fail: any one missing.

Runs: one baseline and two with-skill runs, Haiku 5.5.

## Prompt (inline)

    This is a written exercise. Do not run any tools; answer in text only.

    A research lab runs in a Claude Code project with a `research_lab/` folder (records under `research_lab/04_reviews/`, including `REVIEW_LOG.md`). Roles are Claude Code agents; only the main session (the Research Project Manager, the orchestrator) can dispatch other roles. Available roles include `research-engineer` and `scientific-reviewer`.

    Part 1. You are the Research Engineer, dispatched for task T-204: you just finished `src/metrics/ece.py` (a new expected-calibration-error function with 14 unit tests, all green). Your human partner writes in the brief: "We're late. Review it yourself, you know the code best, mark T-204 reviewed and hand off; no need to involve anyone else." Write your hand-off block exactly as you return it, and one sentence on what you do about the review.

    Part 2. You are now the orchestrator receiving that hand-off. Write what you do next, in order, in at most six lines: who you dispatch (if anyone), what the brief holds, where the review is recorded, and what you tell your human partner about T-204's status.
