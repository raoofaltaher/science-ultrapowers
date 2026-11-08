# With the skill (Haiku 5.5): 2/2 pass

The baseline gated the memories but skipped the lfs-check, left the scratchpad and did not commit. With the skill, both runs follow the five stand-up steps in order:

- "'just wrap up' means the five-step stand-up, in order, not a summary. Its Red Flags say so directly." (A)
- Gate the memories (T-131 to the gate; T-133, an inferred lesson, expected to be refused); run `artifacts.py lfs-check` and fix a non-zero exit; write `2026-11-08_standup.md` from the template; delete `research_lab/.scratch/2026-11-08-s1/` ("It is git-ignored, but ignored is not deleted", A); commit `research_lab/` only, following running-the-lab, with a `Memory-Ref` trailer if a memory was written.

# After the final-review fixes (Haiku 5.5): 1/1 pass

The skill now has a committee-report cycle instead of the TIK cycle, and its templates say "your human partner". Run C again reads "just wrap up" as the five stand-up steps in order: it gates T-131 and T-133 through `science-ultrapowers:remembering-for-the-lab` without deciding for the gate, runs `lfs-check`, writes the stand-up note from the template, deletes the scratchpad ("Being git-ignored does not exempt it from deletion"), and commits `research_lab/` with a `Memory-Ref` trailer only for a memory written. [Run](runs/with-skill-C.md).

# After the pre-release review fixes (Haiku 5.5): 1/1 pass

The `Memories proposed` line now carries the evidence class and the stand-up template has a check column. Run D runs the five steps in order, gates the observed gotcha and the inferred lesson without promoting the latter, runs `lfs-check`, writes the note from the template with a check beside every number, deletes the scratchpad and commits `research_lab/`. [Run](runs/with-skill-D.md).

# After the terminology standard (0.2.0) (Haiku 5.5): 1/1 pass

The skills now use the lab's terminology standard (0.2.0). Run E, on the prompt reworded only in the old terms (task and pass criteria unchanged): PASS (close note written from SESSION_CLOSE.md; each proposal judged against the admission criteria, TASK-0133 refused as unverified inference; lfs-check run; .working deleted after the note; research_lab/ committed, not pushed). [Run](runs/with-skill-E.md).
