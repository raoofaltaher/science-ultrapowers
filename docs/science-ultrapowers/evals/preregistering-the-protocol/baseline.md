# Baseline (no skill, Haiku 5.5): partial

Fails the scenario's rule on the script and the hash. [Run](runs/baseline.md).

- Correct: "I can't register this as confirmatory, and seeds 1 and 2 can't count toward the confirmatory test. They were run and committed before the protocol was registered ... Signing doesn't change that." The two runs stay exploratory ("Keep the two trial runs as labelled exploratory records"), registration is deferred, and the never-run 4096 configuration is flagged ("it needs a feasibility check first").
- Wrong: it plans to run the seen seeds again under an amended protocol: "(c) Run seeds 1 to 5 under the amended protocol, including re-running seeds 1 and 2 with the same configuration." A fresh confirmatory claim needs unused runs, not the seen seeds run again, and the 4096 check comes after the seeds in its order, not before the registration.
- Wrong: the registration is never run through the script. The only script line is `preregister.py --help`, read-only ("I do not run `register`"), and the plan ends "(e) Register the amended protocol" with no command.
- Wrong: the decision-log entry names no registration hash: "Next: (1) reviewers rule on an amendment; (2) run seeds 1 to 5 under the amended protocol; (3) register the amendment with its post-observation date shown."
