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

## After the lifecycle (0.2.0, phase 1)

The scenario gained messages 4 and 5 and pass criteria 5 and 6: a manuscript to referee and a topic to survey, each in a folder with no lab. The bootstrap gained a tracks table and a sentence for the service tracks. The baseline for this form has the skill descriptions and no bootstrap.

| Run | Skill | Model | Verdict | Notes |
|---|---|---|---|---|
| [baseline-tracks](runs/baseline-tracks.md) | descriptions only | Haiku 5.5 | FAIL on messages 4 and 5 | messages 1 to 3 route correctly; message 4 names `reviewing-a-manuscript` and offers init but not `--track review`; message 5 names `synthesizing-the-literature` and no init |
| [with-skill-D](runs/with-skill-D.md) | bootstrap, after the lifecycle | Haiku 5.5 | HOLD | messages 1 to 3 and 5 pass; message 4 names init first and then `reviewing-a-manuscript` but not the `--track` flag |
| [with-skill-E](runs/with-skill-E.md) | bootstrap, after the lifecycle | Haiku 5.5 | PASS | init first for message 1; the session opening for 2; `running-the-lab` routing to `saving-artifacts` for 3; init with the review track then `reviewing-a-manuscript` for 4; init with the literature track then `synthesizing-the-literature` for 5; nothing read or searched |
| [with-skill-D2](runs/with-skill-D2.md) | bootstrap, after the primer fix | Haiku 5.5 | PASS | init first for message 1; the session opening for 2; `saving-artifacts` for 3; init with `--track review` then `reviewing-a-manuscript` for 4; init with `--track literature` then `synthesizing-the-literature` for 5; both named before any document is read |

The primer fix, after D held: the service-track sentence names the flag and the track skill ("A service track (literature, review, writing or dissemination) in a folder with no `research_lab/` starts with `science-ultrapowers:initializing-a-research-lab` and its flag `--track <track>`, then the track skill; name both before any document is read."). D2 reran D's prompt on the fixed bootstrap and passes.

Tracks scenario (messages 4 and 5): baseline 0/1 on message 4, with the skill 2/2 after one primer fix (E on the first form, D2 on the second).
