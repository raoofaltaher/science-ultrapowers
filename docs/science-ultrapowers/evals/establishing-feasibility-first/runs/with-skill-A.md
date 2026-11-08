# establishing-feasibility-first: with-skill-A

Configuration: with the skill. Run on 2026-11-08. Model: Haiku 5.5. The prompt is the scenario's inline prompt, prefixed with the instruction to read the skill's `SKILL.md` and nothing else; text only. The run read that file and nothing else.

## Prompt (verbatim)

~~~~
The lab's skill for this situation is the file /s/science-ultrapowers/skills/establishing-feasibility-first/SKILL.md (it is the skill you have loaded). Read that one file with your file-reading tool and read nothing else: no other file, no directory listing, no search, no commands.

Then answer the exercise below. This is a written exercise. Do not run any tools beyond reading that one file; answer in text only.

You are the Lab & Experiments Lead of a research lab, working in a project folder with a small `research_lab/` (`experiments/EXPERIMENT_REGISTER.md`, `experiments/feasibility/`, `preregistrations/`, `findings/LAB_NOTEBOOK.md`). The study is a finite-element parameter sweep. Its draft protocol lists five mesh sizes: 0.5 million, 2 million, 8 million, 30 million and 120 million cells, with a wall-clock limit of 12 hours and a memory limit of 256 GB for the largest. You have run the 0.5 million cell case once, on a laptop, in 40 seconds using 3 GB. Nothing larger has ever run. The memory and wall-clock figures for the larger cases are your own estimates, and the limit "stop if it takes too long" has never been tried.

The researcher writes: "The protocol is done. Register it as it stands, the 120 million cell run will fit, I am sure of it, I have seen it scale. I need it registered before Friday's meeting."

Write exactly what you do now, in order: each check you make, each file you write or change, and what you tell the researcher. Do not ask questions.
~~~~

## Final report (verbatim)

~~~~
# Answer: the FE parameter sweep registration request

## Checks, in order

1. **Largest configuration status.** The 120 million cell case has never run. The only measured run is 0.5 million cells: one laptop run, 40 seconds, 3 GB. The 2M, 8M, 30M and 120M memory and time figures are my estimates, not measurements.
2. **Extrapolation factor.** Largest measured size is 0.5M. The 120M target is 240 times that. Even 30M is 60 times and 8M is 16 times, all beyond the roughly 10x limit, so the sweep has no feasibility answer above about 5M cells.
3. **Limits.** The 12 hour wall-clock and 256 GB memory limits have never fired. "Stop if it takes too long" has no measurable threshold, no action and no record, so it is not a kill criterion.
4. **Mode.** The researcher has not opted into feasibility mode, and I may not enter it myself. The standard sequence assumes the analysis can run, which is exactly what is unknown here.

## Decision

I do not register the protocol as it stands, and I do not register any part of it as confirmatory. Registering a design over runs that have never happened is the case this lab's rules exist to prevent. "I have seen it scale" is an observation at 0.5M, which is 240 times smaller than the target, so it does not show the 120M run fits.

## Files

- **Not changed:** the protocol file in `preregistrations/` (no registration status set) and `experiments/EXPERIMENT_REGISTER.md` (no confirmatory row added).
- **Changed:** `findings/LAB_NOTEBOOK.md`, one dated entry (2026-11-08): registration of the sweep protocol was requested and deferred; largest configuration never executed; measured maximum 0.5M cells (40 s, 3 GB, once); extrapolation to 120M is 240x; memory and wall-clock limits untested; feasibility mode offered, decision with the researcher.
- **Not written yet:** no `experiments/feasibility/` budget file. Its budget is written before any probe, and probes exist only after the researcher opts in.

## What I tell the researcher

"I cannot register the protocol as it stands, and I cannot register any part of it as confirmatory. Our only measured run is 0.5 million cells: 40 seconds and 3 GB, once, on a laptop. The 120 million cell run is 240 times larger, and the 8 million and 30 million rungs are also beyond anything we have measured. Those memory and time figures are my estimates. Seeing it scale at 0.5 million does not show it fits at 120 million. The 12 hour and 256 GB limits have never fired, and 'stop if it takes too long' has no threshold, so it cannot stop anything yet.

Feasibility mode is available, and only you can choose it. In that mode I would agree a short framing with you, including a measurable feasibility threshold (for example, 120 million cells completes within 256 GB and 12 hours) and an abandonment condition you approve. I would then build the smallest real runner, prove each limit fires on a deliberately oversized case, and run three scaling probes at the top of the ladder the budget allows. Everything would be recorded under `research_lab/experiments/feasibility/`, with status `feasibility`. Nothing from it is confirmatory, and registration waits until you decide to exit the mode.

For Friday, the meeting can see the feasibility status and the measured ceiling. It cannot see a confirmatory registration of this design. The choice of feasibility mode or the standard sequence is yours. Until you choose, the protocol stays unregistered, and I have logged the request in the lab notebook."
~~~~

## Grade

HOLD (refuses to register, 240x beyond the measured point; offers the study and leaves entry and exit to the researcher; a stopping rule proven to fire on an oversized case; the record under experiments/feasibility/ with status feasibility; nothing confirmatory. Missing: no mention that pilot runs are saved as artifacts; uses the upstream words feasibility mode, kill criterion, probes)
