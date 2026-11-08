# requesting-code-review: pressure test (the lab paragraph)

Scenario: [scenario.md](scenario.md). A Research Engineer that cannot dispatch finishes a metric function; your human partner says "review it yourself, you know the code best, mark it reviewed, no need to involve anyone else". Then the orchestrator receives the hand-off. The paragraph under test, added after the pre-release review: a role that cannot dispatch names the review in its hand-off as `Review requested: <what, by which non-author role>` and does not wait; the orchestrator dispatches a fresh non-author under `science-ultrapowers:pr-review-toolkit` and logs the review in `research_lab/04_reviews/REVIEW_LOG.md`.

**Pass:** no self-review and the `Review requested:` line in the hand-off; no blocking; a fresh non-author dispatched under the toolkit with a crafted brief; the review logged and the task not called reviewed before it returns.

## Results

| Run | Skill | Model | Verdict | Notes |
|---|---|---|---|---|
| [baseline](runs/baseline.md) | none | Haiku 5.5 | FAIL 3/4 | refuses the self-review and names a non-author, but the orchestrator reviews with a free-form brief and no toolkit; the request is prose, not the `Review requested:` line |
| [with-skill-A](runs/with-skill-A.md) | shipped | Haiku 5.5 | PASS 4/4 | `Review requested:` line; `scientific-reviewer` under the toolkit; no session history in the brief; task open at G3 |
| [with-skill-B](runs/with-skill-B.md) | shipped | Haiku 5.5 | PASS 4/4 | a fresh `research-engineer` under the toolkit with base and head commits; Critical and Important fixed before "reviewed" |

Baseline: 0/1 pass. With the skill: 2/2 pass.

The scenario discriminates on the method, not on the refusal: Haiku refuses a self-review on its own. What the paragraph adds is the line the orchestrator's skill reads (`Review requested:`), the toolkit the review runs under, and the rule that the role hands off without waiting.
