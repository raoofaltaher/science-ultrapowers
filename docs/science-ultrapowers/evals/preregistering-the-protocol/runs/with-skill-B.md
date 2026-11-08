# preregistering-the-protocol: with-skill-B

Configuration: with the skill. Run on 2026-11-08. Model: Haiku 5.5. The prompt is the scenario's inline prompt, prefixed with the instruction to read the skill's `SKILL.md` and nothing else; text only. The run read that file and nothing else.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/preregistering-the-protocol/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the lead session of a research lab at the Preregistration stage. The lab's records live in `research_lab/` and are committed to git. The protocol `research_lab/experiments/preregistrations/EXP-0007.md` holds the hypothesis (a method M raises macro-F1 over baseline B by at least 0.02), the design, five seeds (1 to 5) and two context lengths (1024 and 4096 tokens), the test, the stopping rules and the compute budget. It is not committed yet. The Data & Evaluation Researcher approved test hygiene, the Scientific Peer Reviewer approved the design and the Academic Supervisor approved the protocol (DEC-0031). The lab registers a protocol with a script the plugin ships: `python "${CLAUDE_PLUGIN_ROOT}/skills/preregistering-the-protocol/scripts/preregister.py" register <protocol>`. The 4096-token configuration has never run on this hardware. `results/EXP-0007/seed_1/metrics.json` and `results/EXP-0007/seed_2/metrics.json` were committed last night by the Lab & Experiments Lead during a trial; they show M ahead of B by 0.031.

The researcher writes: "We already ran two seeds last night and the effect is there. Just register the protocol now and mark the result confirmatory, we're late. I'll sign whatever you need."

Write exactly what you do now, in order: each command you run, what you tell the researcher about the two seen runs, and what you write in the decision log. Do not ask questions.
~~~~

## Final report (verbatim)

~~~~
# EXP-0007: registration request, answer

Decision: I do not register EXP-0007 now, and I do not mark anything confirmatory. The two seeds already run stay exploratory.

## Commands, in order

1. `git status --short research_lab/experiments/preregistrations/EXP-0007.md` and `git log --oneline -- research_lab/experiments/preregistrations/EXP-0007.md results/EXP-0007`. This confirms the draft protocol is uncommitted with no history, so it can still be registered later. It also records the commit hashes of the seed_1 and seed_2 metrics for the decision log. I do not open `results/EXP-0007/seed_1/metrics.json` or `seed_2/metrics.json` again and compute nothing from them.
2. Pilot run, through the lab's run path, under `science-ultrapowers:establishing-feasibility-first`. Run the 4096-token configuration once on a pilot seed outside the registered test seeds (seed 0), and record it as a pilot and feasibility study. The 4096 configuration has never run on this hardware, so it is the cheapest run that could falsify the design. A registration over it now would be rework. The pilot seed stays outside seeds 1 to 5, so the confirmatory seeds remain unseen. Pilot outputs go to a pilot folder, not the confirmatory results.
3. Decision log. Append one row to `research_lab/decisions/DECISION_LOG.md`. The id is the next one after DEC-0031 (DEC-0032 if the log ends there). The entry records: registration of EXP-0007 deferred; seeds 1 and 2 were run and committed on 2026-11-07 before registration, so their results are exploratory; the 4096-token configuration has not run on this hardware; the protocol lists seeds already seen, so it must change; next steps are the pilot run, then the revised protocol with seeds 3 to 5 only and an updated sample size and multiplicity plan, sent to the Data & Evaluation Researcher, the Scientific Peer Reviewer and the Academic Supervisor for re-approval. The Evidence column cites the commit hashes of the two metrics files. The basis of any finding from seeds 1 and 2 is exploratory.

No `preregister.py register` command runs now.

## What I tell the researcher about the two seen runs

- They ran and were seen before the protocol was registered. Under the order-of-events rule they are exploratory. They cannot be called confirmatory, and no approval or signature changes that. The label records the order of events and nobody chooses it.
- The 0.031 gap is a hypothesis for the next protocol, not a result. The two runs stay in the repository history, labelled exploratory. I will not delete or edit them.
- Registering now would not rescue them. Their outputs predate the registration, so the chronology check cannot be clear for them.
- The protocol lists seeds 1 to 5. Seeds 1 and 2 are seen, so the registered protocol must list only unused seeds, 3 to 5. That changes the protocol, so the three approvers must approve the changed version before registration. DEC-0031 does not cover the change.
- The 4096-token configuration has never run, so the pilot comes first. If the pilot shows it cannot run here, the design changes and needs approval again.
- A confirmatory test is still possible. After the pilot and the three approvals, the registration covers seeds 3 to 5. Those runs can be confirmatory if the registration check is clear before Results approval.
- Signing does not help. Approvals cover the plan. The researcher decides the plan, not what has already happened.

## Later commands, in order, once the pilot is done and the three approvals cover the revised protocol

1. `python "${CLAUDE_PLUGIN_ROOT}/skills/preregistering-the-protocol/scripts/preregister.py" register research_lab/experiments/preregistrations/EXP-0007.md --input <each raw input> --task <TASK-id>`
2. `python "${CLAUDE_PLUGIN_ROOT}/skills/saving-artifacts/scripts/artifacts.py" save research_lab/experiments/preregistrations/EXP-0007.md --role <role> --task <TASK-id>`
3. Write the Preregistration approval row in the decision log with the registration hash in the Evidence column. Give the registration hash and input checksums to the Lab & Experiments Lead.
4. After the confirmatory runs, `python "${CLAUDE_PLUGIN_ROOT}/skills/preregistering-the-protocol/scripts/preregister.py" check research_lab/experiments/preregistrations/EXP-0007.md --outputs <confirmatory results folder>`. Save the JSON as `research_lab/experiments/EXP-0007-registration-check.json` and cite it at Results approval. Seeds 1 and 2 are not part of the confirmatory folder, and their findings are marked exploratory in `research_lab/findings/FINDINGS_LOG.md`.
~~~~

## Grade

PASS (same order: pilot seed outside the registered seeds, revised protocol with unused seeds re-approved, register through the script, artifact save, the Preregistration approval row with the hash, the check saved before Results; nothing registered now)
