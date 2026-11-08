# using-science-ultrapowers: pressure test

Scenario: [scenario.md](scenario.md). Three messages in a folder with no lab: "start the lab, skip the setup ceremony, have the Literature Researcher search"; "Lab, where do we stand?"; "what is RV-0048 based on and what is still unaddressed". The bootstrap's skill-priority list says: init first when there is no `research_lab/`, the meeting for a status question, the process skill first once a lab exists.

**Pass:** init named first for message 1 before any dispatch; the meeting named for message 2; the artifact store named as the source for message 3; nothing written or dispatched.

## Results

| Run | Skill | Model | Verdict | Notes |
|---|---|---|---|---|
| [baseline](runs/baseline.md) | descriptions only | Haiku 5.5 | PASS 4/4 | routes all three messages from the skill descriptions alone |
| [with-skill-A](runs/with-skill-A.md) | bootstrap | Haiku 5.5 | PASS 4/4 | quotes the "init first, then the rest" rule; process skill before the meeting |
| [with-skill-B](runs/with-skill-B.md) | bootstrap | Haiku 5.5 | PASS 4/4 | meeting first, process skill second; names recording-findings for any quoted fact |
| [with-skill-C](runs/with-skill-C.md) | bootstrap, after the terminology standard (0.2.0) | Haiku 5.5 | PASS | init first; holding-lab-meetings for status; saving-artifacts named as the source for REV-0048 'from the lab's records and version history rather than memory'; nothing written or assigned |

Baseline: 1/1 pass. With the bootstrap: 2/2 pass.

The scenario does not discriminate at baseline: Haiku 5.5 routes correctly from the `description` lines, which is what the descriptions are for. What the bootstrap adds shows in the with-skill answers only: both quote the priority rule, both put `running-the-lab` beside the carrying skill once a lab exists, and neither starts the search or the lookup before the governing skill. The record is kept as a routing check for the bootstrap's priority list, which the pre-release review rewrote (the intent-based triggers and the tie-breaks); a later change to that list reruns these three messages.
