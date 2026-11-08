# Baseline (no skill, Haiku 5.5): fail

[Run](runs/baseline.md).

- Wrong (criteria 1 and 5): it registers the protocol today. "I will not register the protocol as it stands ... I will register a version that marks that level as conditional and schedules the checks that would settle it." The protocol "is still registered for Friday covering 0.5M to 30M", with the 120 million level a dated amendment away. A conditional registration is still a registration over a configuration that has never run.
- Wrong (criteria 1 and 2): it projects the ladder from one point ("Memory, linear upper bound: 3 GB × 240 = 720 GB", "Linear scaling gives about 9,600 s") and then runs the ladder itself: "I run 2M, then 8M, then 30M, each with the 12-hour and 256 GB limits enforced". Nobody offers the researcher the study or the choice of entering it; the question is never asked, so the researcher's confidence is the only opt-in there is.
- Partly right (criterion 3): it tries the stop rule on the 0.5M case with a 20-second limit and expects "a partial record is written with the stop reason". The rule is tested only after it has been written into the plan, and no abandonment condition is asked of the researcher.
- Partly right (criterion 4): it writes `experiments/feasibility/` files, but no pilot run is saved as an artifact, and the register rows it adds mix `planned` and `conditional` entries.
- Right: "the 120M run will fit" is unsupported, and it will not describe it as feasible "until a measurement on this code and this mesh shows it".
