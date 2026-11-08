---
name: investigating-anomalous-results
description: Use when a result is surprising, impossible or contradicts a sanity check, when a workflow fails, a model does not converge or a replication fails, and before you adjust anything
---
> **LAB ADDENDUM (binding).** Adopted third-party skill: `K-Dense-AI/science-superpowers` @ `0374bdf82c23` (MIT). Where anything below conflicts with the lab's rules, the lab's rules win.
>
> 1. **Evidence rule wins.** Facts and citations come only through `science-ultrapowers:verifying-evidence-by-doi` (peer-reviewed, DOI matched through Crossref, full text read, evidence record). Never cite from web search, model memory or preprints.
> 2. **Records.** Numbers and results come only from `science-ultrapowers:recording-findings`. Every anomaly is logged in `research_lab/findings/LAB_NOTEBOOK.md` and in the `Deviations` column of the experiment register. A real finding is submitted in the task report as `exploratory`, never as `confirmatory`.
> 3. **No pre-approved tools.** This copy grants no tools, so normal permission prompts apply.
> 4. **Tools in Claude Code:** read files with the file reader, edit with the file tools, and read the skill's bundled files under `${CLAUDE_PLUGIN_ROOT}/skills/investigating-anomalous-results/`.
> 5. **Skill-specific:** The three skills named under Related Skills at the end of this file read as `science-ultrapowers:recording-findings`, `science-ultrapowers:preregistering-the-protocol` and the Execution criteria of `science-ultrapowers:running-the-lab`. The escalation path is the Lab & Experiments Lead, then the Data & Evaluation Researcher, then the Academic Supervisor.
>
> Provenance, license and change log: `PROVENANCE.md`.


# Investigating Anomalous Results

## Overview

Random tweaks waste time and manufacture false findings. Quietly dropping the inconvenient data point, moving the cutoff, or re-running until it "works" does not fix the problem — it fabricates a result.

**Core principle:** ALWAYS find the root cause before adjusting anything. An adjustment made before you understand the cause is, at best, noise and, at worst, fraud.

**Violating the letter of this process is violating the spirit of it.**

The first question for any anomaly: **is this a code bug, a data issue, or a real finding?** You cannot answer by guessing, and you must not "fix" it until you know — because a real finding is not something to fix.

## The binding rule

```
NO ADJUSTMENTS WITHOUT ROOT-CAUSE INVESTIGATION FIRST
```

No dropping data, changing a test, transforming a variable, re-running with new parameters, or "cleaning" until Phase 1 is complete. If you have not found the cause, you cannot justify the adjustment.

## When to Use

- A result is surprising, too good, or contradicts what is known
- An impossible value (negative count, probability > 1, age of 500)
- A workflow errors or a model does not converge
- A result contradicts a sanity check or a simple cross-tab
- A replication or robustness check disagrees with the primary result
- Performance that is suspiciously high (often leakage)

**Use this ESPECIALLY when:**
- The anomaly is *convenient* (it supports your hypothesis) — that is when the urge to skip investigation is strongest
- Under time pressure
- You have already tried one quick adjustment

## The Four Phases

Complete each before the next.

### Phase 1: Characterize the Anomaly

**Before any adjustment:**

1. **Read the output or error carefully.** The exact value, the exact message, the stack trace. Note shapes, counts, and where in the workflow it appears.
2. **Reproduce it deterministically.** Fixed seed, same data version. Does it happen every time? If it is not reproducible, gather more data — do not guess.
3. **Check recent changes.** What changed in the code, the data version, or the environment since it last looked right? `git diff`, data provenance, package versions.
4. **Gather evidence at each workflow stage.** Instrument raw → cleaned → derived → result. Print shapes, ranges, null counts, and key summaries at each boundary. This reveals *where* the anomaly enters.

```
raw:     N=10342, outcome mean=0.31, nulls=0
cleaned: N=10298, outcome mean=0.31, nulls=0      <- 44 dropped, expected
derived: N=10298, feature mean=4e7                <- WRONG: unit blew up here
result:  coefficient enormous                     <- symptom; cause is upstream
```

5. **Classify the cause** with the evidence: code bug, data issue, or real finding. Do not proceed assuming one without evidence.

### Phase 2: Pattern Analysis

1. **Find a working comparison.** A subset, variable, site, or time period that behaves as expected. What is different about the anomalous one?
2. **Compare against a reference.** A known correct result, a textbook expectation, a prior estimate from the survey. Read the reference method completely — do not skim.
3. **List every difference** between working and anomalous, however small. Do not assume "that can't matter."

### Phase 3: Hypothesis and Test

1. **Form a single hypothesis:** "The anomaly is caused by X because Y." Write it down. Be specific.
2. **Test minimally** on the smallest slice that exhibits it. One variable at a time.
3. **Verify before continuing.** Confirmed → Phase 4. Not confirmed → new hypothesis. Do not stack adjustments.
4. **When you do not know, say so.** "I don't understand why the derived feature inflates" — then investigate or ask. Do not pretend.

### Phase 4: Resolution

Resolve according to the cause you established:

- **Code bug:** Write a minimal failing check that reproduces it, fix the code at the source (not a downstream patch), re-run the affected steps, confirm the anomaly is gone and other results unchanged.
- **Data issue:** Handle it per a documented rule. If the rule was not preregistered, the decision is a deviation — record it, and the affected analysis becomes exploratory. Dropping observations is legitimate ONLY when root cause shows they are invalid measurements (for example, a sensor error), and that justification is documented. Never drop data because it is inconvenient.
- **Real finding:** It is a result, not a defect. Do NOT "fix" it. If it was not what you preregistered, it is an exploratory finding — report it as such, and preregister a fresh confirmatory test (ideally on new or held-out data) before claiming it.

**If 3+ adjustments fail:** STOP. The workflow or the design may be wrong — repeated failures that each reveal a new problem indicate a structural issue, not a series of small bugs. Discuss the design with the researcher before another attempt. Re-opening the design or the preregistration must be documented as a deviation.

## Warning signs - STOP and Investigate

- "Let me just drop that outlier and re-run"
- "I'll adjust the threshold until it's significant"
- "Probably a fluke, let me re-run with a different seed" (changing the seed to change the result)
- "The result I want appeared, no need to dig into why the first run didn't"
- "Quick adjustment now, understand it later"
- Proposing an adjustment before tracing where the anomaly enters the workflow
- **An adjustment that happens to make the result support your hypothesis**

**All of these mean: STOP. Return to Phase 1.**

## The Researcher's Signals That You Are Doing It Wrong

- "Is that even possible?" — you reported a value without sanity-checking it
- "Why did that point get dropped?" — you adjusted without documenting the cause
- "Did you check leakage?" — suspiciously good performance you did not investigate
- "That seems too clean" — question the workflow, not just the result

## Rationalizations and replies

| Excuse | Reality |
|--------|---------|
| "It's clearly an outlier, just remove it" | "Clearly" is a guess. Find why it is extreme; document it if you remove it. |
| "Re-running with a new seed fixed it" | You changed the result by chance, not the cause. Investigate. |
| "The good result is the right one" | Convenient results need MORE scrutiny, not less. |
| "Emergency, no time to investigate" | Investigation is faster than retracting a wrong finding. |
| "Tweak the model, then understand it" | The first tweak sets a false trail. Understand first. |
| "Performance is just high, ship it" | Suspiciously high performance is usually leakage. Check. |

## Quick Reference

| Phase | Activities | Success Criteria |
|-------|-----------|------------------|
| 1. Characterize | Read, reproduce, check changes, instrument stages, classify | Know WHERE and WHICH (bug/data/finding) |
| 2. Pattern | Working comparison, reference, list differences | Identify the difference |
| 3. Hypothesis | Single theory, minimal test | Confirmed or new hypothesis |
| 4. Resolution | Fix bug / document data rule / report real finding | Anomaly explained, not just hidden |

## Related Skills

- **science-ultrapowers:recording-findings** — confirm the resolution actually holds
- **science-ultrapowers:preregistering-the-protocol** — a real but unregistered finding needs a fresh confirmatory preregistration
- **the Execution criteria of science-ultrapowers:running-the-lab** — deterministic reproduction depends on fixed seeds and pinned environments
