# Question design, the automation rule and calibration for Jev

## Question design

- One atomic judgment per question. Ask many in one call; they run in parallel and cannot see each other's answers.
- Choice options are mutually exclusive and include an explicit `none` or `other` option. Score levels are ordered and described.
- Keep weights, thresholds and composition in code. Never ask Jev to compute.
- The model is English-first with a 64k-token context (32k for the state plus the longest question). Accuracy drops with multi-hop questions and long irrelevant state.

## The automation rule

`jev_rule(answers, use_case, reversible)` returns `auto` only if all hold:

- the action is reversible;
- `thresholds.json` has an entry for the use case with `answer_field`, `operator`, `value`, `action`, `scope`, `study`, `approved_by`, `monitoring`;
- `approved_by` is a real decision id (`DEC-NNNN`, or the legacy `D-NN`; `None`, `""` and `"PENDING"` all mean not approved) that is the first cell of a table row in `research_lab/decisions/DECISION_LOG.md`; an id that is not listed there returns `review` with the reason "approved_by <id> not found in the decision log", and a value that is not a decision id returns `review` with the reason "approved_by <value> is not a decision id";
- `answer_field` (for example `same_work.probabilities['3']`, never the vendor's direction-agnostic `confidence`) resolves against the full answers dict (`jev_ask(...)["answers"]`, not one question's answer) to a number that satisfies `operator` and `value`.

Anything else is `review`. A legacy bare `{"threshold": t}` entry always means `review`.

## Reversible actions after calibration

| Task | Action that may be automated |
|---|---|
| Screening | order the queue; mark "likely include" |
| Candidate matching | pre-fill "likely same work" |
| Deduplication | group likely duplicates |
| Claim support | order which citations to re-read first |
| Evidence lint | insert TODO flags in a draft |
| Routing | propose an owner and a prioritization |
| Stage-approval checklist | return an incomplete task report with the missing items |

## Calibration protocol (before any `auto`)

1. The Decision Systems Specialist writes a preregistration, `research_lab/experiments/preregistrations/CAL-JEV-<nn>_preregistration.md`, for the use case: 100-200 items labelled by the lab (not by Jev), including hard and adversarial items. A study on a held-out benchmark uses its training and development items only.
2. Run the helper on every item and compute `calibration_report(y_true, answers)`: accuracy, expected calibration error, and coverage versus accuracy by threshold.
3. Choose the lowest threshold whose accuracy meets the preregistered target error rate. Propose it to the Academic Supervisor in this shape:

```
{"<use_case>": {"answer_field": "<path, for example same_work.probabilities['3']>",
 "operator": ">=" or "<=",
 "value": <explicit numeric constant>,
 "action": "<reversible action the rule covers>",
 "scope": "<what this covers and does not>",
 "study": "CAL-JEV-nn",
 "approved_by": "PENDING",
 "monitoring": "<re-evaluation trigger>"}}
```

   Write `value` as its own constant, never derived as `1 - t` at read time: binary floats make `1 - 0.80` equal `0.19999999999999996`. The threshold is field-specific and direction-aware; a naive 0.50 on `confidence` would auto-route many "different" pairs.
4. The Academic Supervisor reviews the study; on approval `approved_by` becomes the decision id (`DEC-NNNN`). Re-calibrate whenever the model version, the question wording or the data distribution changes.
