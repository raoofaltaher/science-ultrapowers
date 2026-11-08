---
name: preregistering-the-protocol
description: Use when a protocol is about to be approved at the Preregistration stage, before any confirmatory run or any outcome is looked at, when a result is about to be called confirmatory, or when a run deviates from its protocol
---

# Preregistering the Protocol

## Overview

Write the hypothesis, the exact analysis, the prediction and the decision rule. Register them before any outcome is seen. Then run exactly that.

**Core principle:** A prediction is evidence only if it was made before the result. If the analysis was chosen after the data, the data may have shaped the answer, and nobody can tell.

**Violating the letter of this rule is violating the spirit of this rule.**

## The binding rule

```
NO CONFIRMATORY CLAIM WITHOUT A REGISTERED PREDICTION FIRST
```

Looked at the outcomes first? That analysis is exploratory. It is never relabeled. To make a confirmatory claim, register the protocol and test it on runs that have not happened yet.

**No exceptions:**

- Do not reorder the analysis "lightly" after a peek.
- Do not add the covariate that "obviously" belongs after you saw the result.
- Do not move the cutoff to where it works.
- Do not keep an unregistered analysis as confirmatory because "it would have been my prediction anyway".
- Do not take the label from the researcher as a reason. The label records the order of events. Nobody can choose it.

## When to use

Use this skill at the Preregistration stage, and at every later point where the label confirmatory is about to be used:

- Before the Preregistration approval: the protocol is complete and the three approvals are given.
- Before any run, any outcome load, any plot of the outcome or any estimate that supports a claim.
- Before the Results approval: the registration check runs and its report is saved.
- When a run departs from its protocol.

Exploratory work is allowed. Label it exploratory. It is a hypothesis for the next protocol.

Decide with the researcher, and log the decision, for descriptive reporting with no inferential claim, method development on simulated data, re-analysis of public results and a pilot and feasibility study (`science-ultrapowers:establishing-feasibility-first`). In a pilot and feasibility study the registration waits for the exit of the study. Nothing produced before it is confirmatory.

## Do not register over runs that have never happened

A registration over configurations that never ran is rework, not protection. Before the registration, confirm:

- Every configuration in the protocol has run at least once, or is known to run from a measured point. An extrapolation is not a measured point.
- Every completion criterion has been observed on a real run of the workflow it judges.
- The cheapest run that could falsify the prediction has run.

The last item matters most. If a run that costs seconds could disconfirm the prediction, run it first. That run is a pilot run, recorded as a pilot and feasibility study. It cannot confirm the hypothesis, so it cannot contaminate the confirmatory test.

Where feasibility is unknown, offer the pilot and feasibility study to the researcher.

Seeds, folds and samples that already ran and were seen are exploratory. The registered protocol lists only unused ones. When the protocol changes for this reason, the three approvers approve the changed protocol before it is registered.

## Lock, register, execute, separate

1. **Lock.** Write the protocol on the template `PREREGISTRATION.md`. The sample size is fixed in advance, and nobody peeks and extends. The multiplicity plan gives the number of tests and the correction.
2. **Make it falsifiable.** State the result that would disconfirm the prediction. If no result could, reframe the prediction. The domains in `science-ultrapowers:scientific-critical-thinking` (researcher degrees of freedom, multiplicity, leakage) list the traps this step closes.
3. **Register.** The lead session runs the registration script (next section) before any outcome is touched.
4. **Execute.** Run the registered analysis unchanged. Refuse every "while I am here" addition.
5. **Separate.** Everything not registered is exploratory: a follow-up, a subgroup, another model. Report it under an exploratory heading.

## Registering

Keep the draft protocol uncommitted until it is registered. The script refuses a file that already has history, because a registration is the first commit of the file.

The lead session runs the registration. A role never runs it.

```
python "${CLAUDE_PLUGIN_ROOT}/skills/preregistering-the-protocol/scripts/preregister.py" register research_lab/experiments/preregistrations/<EXP-id>.md --input <raw input file> --task <TASK-id>
```

Repeat `--input` for each raw input. The command makes two commits that hold only the protocol file.

1. The registration commit carries the protocol alone, with the trailer `Preregistration: <protocol id>`, and the block `## Registered inputs` with one line `- <path> <blob hash>` for each input.
2. The time-stamp commit writes the line `Registered at commit: <registration hash>` into the file. It carries the trailer `Preregistration-Timestamp: <registration hash>`. The line goes after the YAML frontmatter when the file opens with one, else after the title.
3. The command prints JSON: the two commit hashes and the input checksums.

If the time-stamp commit fails, fix the cause and run the command again with `--timestamp-only`. A failed commit exits with code 1 and shows git's output.

After the command, in this order:

1. Save the registered protocol with `science-ultrapowers:saving-artifacts`: `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" save research_lab/experiments/preregistrations/<EXP-id>.md --role <role> --task <TASK-id>`.
2. Write the Preregistration approval row in `research_lab/decisions/DECISION_LOG.md`. Put the registration hash in the Evidence column.
3. Give the registration hash and the input checksums to the Lab & Experiments Lead. The lead copies them into the register row's `Preregistration` and `Input checksums` fields.

A registered protocol is never edited. A change goes in a protocol deviation, below.

## The registration check

Before the Results approval, run the check on every protocol whose findings will be called confirmatory.

```
python "${CLAUDE_PLUGIN_ROOT}/skills/preregistering-the-protocol/scripts/preregister.py" check research_lab/experiments/preregistrations/<EXP-id>.md --outputs <results folder>
```

Repeat `--outputs` for each output folder. The command prints JSON. Each of its five items is clear, not clear or unprovable. Exit code 0 means every item is clear.

| Item | Clear when | If not clear |
|---|---|---|
| `registered` | A commit holds the protocol alone | The protocol was never registered. Register now. Every outcome seen so far is exploratory. |
| `timestamp` | The registration commit's hash is in the file and in a time-stamp commit | Run `--timestamp-only`. |
| `unaltered` | The file at the branch head equals the registered version, byte for byte | The file was edited. Record a protocol deviation. |
| `chronology` | Every output was committed after the registration | An output predates the registration. That analysis is exploratory. |
| `inputs` | Each input file matches its registered checksum | An input changed. Record a protocol deviation. |

Unprovable is never clear. An output on a parallel branch, an uncommitted output and a shallow clone never report clear. Commit the output on the registration's branch, or call the analysis exploratory.

Write the JSON to `research_lab/experiments/<EXP-id>-registration-check.json` and save it with `science-ultrapowers:saving-artifacts`. The Results approval cites the saved report.

The check proves the order of commits and the unchanged file. It does not prove what anyone saw.

## Deviations

A deviation from the registered protocol makes the affected finding exploratory. The size of the deviation does not change that.

When a run departs from the protocol:

1. Stop and write the deviation in the Deviations column of the experiment register: what changed, why and the effect.
2. Do not edit the registered file. An edit makes `unaltered` not clear.
3. Mark every finding that rests on the deviating analysis `exploratory`.
4. If the researcher wants a confirmatory test of the changed analysis, register a new protocol and test it on runs that have not happened.

## The basis of a finding

Each row of `research_lab/findings/FINDINGS_LOG.md` carries a `Basis` of `confirmatory` or `exploratory`.

- `confirmatory`: the analysis was planned in the registered protocol, ran as registered, and the registration check is clear. Cite the saved check report.
- `exploratory`: every other case. This includes a seen run, a deviation, an unregistered analysis and an unprovable item.

A verified row is never edited. A relabel to `confirmatory` needs a registered protocol and new runs, never an edit.

## Rationalizations and replies

| Excuse | Reality |
|---|---|
| "I will register after a quick look" | A look makes it exploratory. The look is the violation. |
| "This covariate obviously belongs" | Add it before any outcome is seen, or it is a researcher degree of freedom. |
| "The cutoff that works is the right one" | A cutoff chosen by its result is p-hacking. Fix it first. |
| "It would have been my prediction anyway" | Then writing it first cost nothing. You did not, so it is exploratory. |
| "Stopping early, it is already significant" | Optional stopping inflates false positives. Honor the fixed sample size. |
| "Register now, find out later if it runs" | A registration over configurations that never ran is rework. Run the cheapest falsifying run first. |
| "A pilot run first would contaminate my prediction" | A pilot run is not the confirmatory test. An informed prediction beats a falsified one. |
| "The researcher said to mark it confirmatory" | The researcher decides the plan. The researcher does not decide what already happened. Offer exploratory, or a new registration on unused runs. |
| "I will write the registration line by hand, it is quicker" | A hand-made line proves nothing. Run the script. |
| "The chronology is unprovable, so it is close enough" | Unprovable is never clear. Fix the branch or call it exploratory. |
| "The deviation was tiny" | A deviation from the registered protocol makes the affected finding exploratory, however small. |

## Warning signs

- The outcome is looked at before the registration.
- The test, covariates, exclusions or cutoff are chosen after a result.
- An analysis is added because the first one was not significant.
- The sample is extended because p was "almost there".
- An unregistered result is reported as confirmatory.
- A seen seed is listed in the protocol.
- A registration commit or a `Registered at commit:` line is written by hand.
- "It is about the spirit, this peek does not count."

**Any of these: that analysis is exploratory. Register a new confirmatory test on unused runs.**

## Checklist

Before the registration:

- [ ] The primary analysis is exact: model, variables, transformations, exclusions, covariates.
- [ ] A disconfirming result is stated, and the decision rule is independent of the result.
- [ ] The sample size is fixed, and the multiplicity plan is written.
- [ ] Every configuration has run, or the cheapest falsifying run has run.
- [ ] No seed, fold or sample in the protocol was seen.
- [ ] The three approvals are given.

After the registration:

- [ ] The registered protocol is saved and the hash is in `DECISION_LOG.md`.
- [ ] The registration check is clear and its report is saved before the Results approval.
- [ ] Each finding has a `Basis`, and none is `confirmatory` without a clear check.

Credit: the rules in this skill are reworded from the `preregistering-analysis` skill of K-Dense-AI/science-superpowers (MIT, Copyright (c) 2026 K-Dense, Inc.); the registration script is a rewrite of its `prereg.sh`.
