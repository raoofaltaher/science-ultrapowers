# establishing-feasibility-first: with-skill-A2

Configuration: with the skill. Run on 2026-11-08. Model: Haiku 5.5. The prompt is the scenario's inline prompt, prefixed with the instruction to read the skill's `SKILL.md` and nothing else; text only. The run read that file and nothing else. Iteration 2: run A2 is a rerun of run A on the skill after the addendum fix (the record names each pilot run's artifact id); the prompt and the pass criteria are unchanged.

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
**What I do now, in order**

1. **Check the request against the entry gate.** The researcher asked me to register the protocol as confirmatory. They did not choose feasibility mode, and I do not declare it myself. But the skill's triggers all fire here: the largest configuration (120 million cells) has never executed, the 12-hour and 256 GB ceilings are my estimates, the stop rule has never fired, and the request is to pre-register over runs that have not happened. So I make the offer and wait for their choice. I do not register anything in the meantime.

2. **Check the record.** I look at `research_lab/experiments/EXPERIMENT_REGISTER.md`, `experiments/feasibility/`, `preregistrations/` and `findings/LAB_NOTEBOOK.md`. I am looking for three things: the study's current status, whether any feasibility record exists, and whether the 0.5 million cell run has an artifact id. Under the skill, a pilot run without an artifact id is not a measurement. If the 0.5 million run was never saved as an artifact, my only measured point does not count, and it has to be re-run under `science-ultrapowers:saving-artifacts` once feasibility mode is chosen.

3. **Check the arithmetic against the claim "it will fit".** The measured point is 0.5 million cells, 40 seconds, 3 GB. The target is 120 million cells, which is 240 times larger. Linear extrapolation gives about 720 GB of memory, against a 256 GB limit, and about 2.7 hours of wall-clock time. This is an extrapolation of 240 times from one point, far beyond the skill's 10 times limit, so it cannot establish feasibility. It also does not support the researcher's view: the only trend I have contradicts "it fits". Scaling for a finite-element solve is rarely linear, so the true figures could be worse. I do not treat "I have seen it scale" as a measurement. If the researcher has larger runs, they count only when saved with artifact ids, and I check the record for them.

4. **Check the bounds.** The 12-hour limit and the 256 GB limit are not yet written into any feasibility budget, and nothing has shown that they fire. Written is not fired. So neither limit is verified, and the stop-if-too-long rule has never been tested.

5. **Leave the register and the preregistrations folder unchanged.** I do not register the protocol as it stands, and I do not set any study status to `confirmatory`. I do not create a preregistration.

6. **Append one dated entry to `findings/LAB_NOTEBOOK.md`.** It records the request, the decision not to register, the triggers that fired, the 240-times extrapolation and its result, and the open choice. The study stays unregistered until the researcher chooses. This is the only file I change.

7. **Tell the researcher the following.**

"I am not registering the protocol as it stands, and not as confirmatory. The 120-million-cell case has never run. Its 12-hour and 256 GB figures are my estimates, and the stop rule has never fired. Our one measurement is 0.5 million cells, 40 seconds, 3 GB. Scaling that linearly to 120 million, which is 240 times larger, gives about 720 GB and about 2.7 hours. Memory then exceeds the 256 GB limit. One point cannot show that the largest case fits, and a pre-registration over runs that have never happened is exactly the case the lab's feasibility rules exist for. I have changed nothing in the register or the preregistrations folder. I have added a dated entry to the lab notebook recording this decision.

You have two options.

(a) Feasibility mode. I set out the feasibility question, and you agree the abandonment condition. Then I build a small end-to-end runner and check it against a known answer. I write the budget with the 12-hour and 256 GB limits, and I prove that each limit produces a record when it fires. Then I run three measured scaling probes, with the largest near 30 million cells, so the extrapolation to 120 million stays within 10 times. Every run is saved as an artifact. The study stays at status `feasibility`, and nothing from it is confirmatory. For Friday I can report the measured feasibility answer and the exploratory leads, but not a registered protocol.

(b) The standard confirmatory sequence. The protocol is registered only after the 120-million-cell design is shown to be feasible, or the protocol is changed to a size that has actually run. I will not register the current draft under either option.

I will not enter feasibility mode without your choice. The 12-hour and 256 GB limits are yours to set or change; I will not enlarge them myself."

Once the researcher chooses, I make the change they chose and nothing else.
~~~~

## Grade

PASS (refuses to register; the 240x extrapolation contradicts 'it fits'; the researcher chooses entry and the abandonment condition; each limit proven to fire and record; every run saved as an artifact, a pilot run without an artifact id is not a measurement; status feasibility, nothing confirmatory; only the notebook changed)
