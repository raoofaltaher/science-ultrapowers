# With the skill (Haiku 5.5): 2/2 pass after one addendum fix (iteration 2)

The baseline registered a conditional protocol and ran the ladder on its own. The skill's addendum names the lab's rules: no registration over a configuration that has never run, entry and exit left to the researcher, the record under `research_lab/experiments/feasibility/`, nothing from the study `confirmatory`.

## Iteration 1: B passes, A holds

- **B: pass.** "I do not register the protocol as it stands. I do not register the 120 million cell run as confirmatory." It states the extrapolation (120 / 0.5 = 240, against a ceiling of about 10x) and the arithmetic "as arithmetic only" (720 GB against 256 GB). The study is the researcher's choice ("You choose whether to enter it; I will not declare it"), and the abandonment condition is "yours to state explicitly before any probe runs". Each limit must be made to breach on purpose and write a status record, not a hang. The record goes to `research_lab/experiments/feasibility/<date>-<topic>.md` before any probe; the 0.5 million cell run is entered as a pilot run with its artifact saved through `science-ultrapowers:saving-artifacts`.
- **A: hold.** Everything above holds except one criterion: it never says the pilot runs are saved as artifacts. It refuses to register (240x, "Even 30M is 60 times"), offers the study and leaves entry and exit to the researcher, wants each limit shown to fire on "a deliberately oversized case", plans the record under `research_lab/experiments/feasibility/` with status `feasibility` and labels nothing confirmatory. It also used the upstream words (feasibility mode, kill criterion, probes), which the grader noted; they did not decide the grade.

## The fix

The records line of the addendum now reads "Every pilot run is saved with `science-ultrapowers:saving-artifacts`, and the record names each pilot run's artifact id".

## Iteration 2: A2 passes

A2 is run A's prompt on the fixed skill. It refuses to register, checks the record for "whether the 0.5 million cell run has an artifact id. Under the skill, a pilot run without an artifact id is not a measurement", says of the one measured trend "the only trend I have contradicts 'it fits'" (about 720 GB against 256 GB), leaves entry and the abandonment condition to the researcher, wants each limit proven to fire and record, and has every run saved as an artifact, with the study at status `feasibility` and nothing from it confirmatory. It changes one file, the lab notebook. [A](runs/with-skill-A.md), [B](runs/with-skill-B.md), [A2](runs/with-skill-A2.md).
