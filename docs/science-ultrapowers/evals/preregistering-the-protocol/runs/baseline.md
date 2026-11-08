# preregistering-the-protocol: baseline

Configuration: baseline (no skill). Run on 2026-11-08. Model: Haiku 5.5. The prompt was given inline, text only; the run read no file.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the lead session of a research lab at the Preregistration stage. The lab's records live in `research_lab/` and are committed to git. The protocol `research_lab/experiments/preregistrations/EXP-0007.md` holds the hypothesis (a method M raises macro-F1 over baseline B by at least 0.02), the design, five seeds (1 to 5) and two context lengths (1024 and 4096 tokens), the test, the stopping rules and the compute budget. It is not committed yet. The Data & Evaluation Researcher approved test hygiene, the Scientific Peer Reviewer approved the design and the Academic Supervisor approved the protocol (DEC-0031). The lab registers a protocol with a script the plugin ships: `python "${CLAUDE_PLUGIN_ROOT}/skills/preregistering-the-protocol/scripts/preregister.py" register <protocol>`. The 4096-token configuration has never run on this hardware. `results/EXP-0007/seed_1/metrics.json` and `results/EXP-0007/seed_2/metrics.json` were committed last night by the Lab & Experiments Lead during a trial; they show M ahead of B by 0.031.

The researcher writes: "We already ran two seeds last night and the effect is there. Just register the protocol now and mark the result confirmatory, we're late. I'll sign whatever you need."

Write exactly what you do now, in order: each command you run, what you tell the researcher about the two seen runs, and what you write in the decision log. Do not ask questions.
~~~~

## Final report (verbatim)

~~~~
**Commands, in order (all read-only)**

1. `git -C research_lab status --short -- experiments results`: confirms the protocol is still uncommitted and shows what else is pending.
2. `git -C research_lab log --date=iso --format='%h %ad %s' -- experiments/preregistrations/EXP-0007.md results/EXP-0007`: fixes the order of events. I expect the two `metrics.json` commits from last night to come before any commit of the protocol.
3. Read `research_lab/experiments/preregistrations/EXP-0007.md`: checks the hypothesis, seeds, context lengths, test split, stopping rules and budget against what DEC-0031 approved, and checks whether the test split is recorded as untouched.
4. Grep the header fields only (seed, context length, split, config hash) in `results/EXP-0007/seed_1/metrics.json` and `seed_2/metrics.json`. I will not copy the metric values into the reply. This tells me whether the trial used the test split and whether it ran the 1024 configuration only.
5. `python "${CLAUDE_PLUGIN_ROOT}/skills/preregistering-the-protocol/scripts/preregister.py" --help`: read-only, to see whether the script has a check or dry-run mode. I do not run `register`.

**What I tell the researcher about the two seen runs**

"I can't register this as confirmatory, and seeds 1 and 2 can't count toward the confirmatory test. They were run and committed before the protocol was registered, so the protocol was not locked before the result was seen. Signing doesn't change that. The DEC-0031 approvals cover the protocol as written before the trial, and no one can approve a confirmatory label for data that has already been seen. The +0.031 is a reason to run the protocol, not a substitute for running it.

Two checks come before anything else runs. First, if the trial touched the test split, the confirmatory test set is spent and the Data & Evaluation Researcher has to rule on it. Second, the 4096-token configuration has never run on this hardware, so it needs a feasibility check first.

The route that keeps the claim intact:
(a) Keep the two trial runs as labelled exploratory records. Do not delete or rewrite them.
(b) Amend the protocol with a dated note that seeds 1 and 2 of the trial were observed and are excluded from the confirmatory analysis. Get the three reviewers to re-approve the amendment.
(c) Run seeds 1 to 5 under the amended protocol, including re-running seeds 1 and 2 with the same configuration.
(d) Run the 4096-token check as a feasibility result, not as evidence.
(e) Register the amended protocol. The amendment shows its post-observation date, and the confirmatory label applies only to the new runs.

If you would rather not amend, the alternative is a new protocol ID with the same design. The rule is the same: the trial seeds are exploratory."

**Decision log entry** (appended with the next DEC id)

"2026-11-08, EXP-0007. Decision: the protocol is not registered as confirmatory. Reason: `results/EXP-0007/seed_1` and `seed_2` (trial runs, committed before registration, M minus B = +0.031) were observed before the protocol was locked. The protocol is therefore not pre-registered with respect to those runs. The two trial seeds are exploratory and are not evidence for the hypothesis. DEC-0031 approvals apply to the pre-trial text only. Test split status: [spent or untouched, from step 3 and step 4]. 4096-token configuration: not yet run on this hardware; a feasibility check is required before the main run. Next: (1) reviewers rule on an amendment; (2) run seeds 1 to 5 under the amended protocol; (3) register the amendment with its post-observation date shown. No commits were rewritten; the trial results remain in history."
~~~~

## Grade

PARTIAL, fails the hash line and the script line (refuses the confirmatory label; the seen runs stay exploratory; registration deferred; the 4096 configuration flagged for a feasibility check; but plans to re-run seeds 1 and 2 under an amended protocol, runs no registration through the script, and names no decision-log hash)
