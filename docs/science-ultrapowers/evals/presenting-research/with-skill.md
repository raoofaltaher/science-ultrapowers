# With the skill (Haiku 5.5): 2/2 pass

The baseline took the right number but built by another route and assigned no one. With the skill, both runs:

- build nothing, install nothing and use no other route while `.venv-lab-skills` is absent. A: "I do not install the package, create the environment or use another route"; B: "I do not install packages, create the environment, or make the deck or figures by another route". Both name the dry run, `pwsh -File "${CLAUDE_PLUGIN_ROOT}/skills/initializing-a-research-lab/scripts/setup_lab_env.ps1" -ProjectRoot <project> -DryRun`, and leave the script to the researcher.
- write the numbers table from the records before any slide: 0.84 with FND-0007 and its interval, the baseline 0.78 with FND-0009, and the draft's 0.87 out ("no slide uses 0.87" in A; "It stays out of the table" in B, which notes it is the upper bound of the interval). The causal wording is dropped: A sends the gain claim to the Results stage through `science-ultrapowers:running-the-lab`; B says the comparison "is not yet a finding" and keeps the two results side by side.
- plan the architecture figure through `science-ultrapowers:planning-paper-figures` and check each box against `configs/fusion.yaml` ("every box and arrow is checked against `configs/fusion.yaml`", A; "I check every box and arrow against configs/fusion.yaml", B), with a non-author running the figure check ("A reviewer other than me runs the figure check", A; "An academic-reviewer who did not draw the figures runs the figure check", B).
- assign the Curator to recompute the numbers and the Citation & Reference Auditor, after `science-ultrapowers:verifying-evidence-by-doi`, for the three unchecked DOIs.
- A saves each product with `science-ultrapowers:saving-artifacts` and records the Reporting approval as a `DEC-` row. B does not name the save; it is implied by the build step and not stated.

[A](runs/with-skill-A.md), [B](runs/with-skill-B.md).
