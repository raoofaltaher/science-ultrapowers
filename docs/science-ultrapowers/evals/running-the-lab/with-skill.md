# With the skill (Haiku 5.5): 2/2 pass

The baseline would have committed the Engineer's code, dispatched with ad-hoc paragraphs and expected no hand-off block. With the skill, both runs:

- refuse the self-review: "the Paper Author wrote section 4. Nobody reviews their own work, and the reviewer is never the author" (B). Both dispatch independent non-author checks in parallel: a referee or academic review, the Curator's number re-check, the Citation Auditor, and a G3 review of `src/train.py` by the Experiments Lead, a non-author.
- send every dispatch as the full task brief block (`TASK <ID> | Gate <G#> | Owner ... | Reviewer ... | Due ...`, then Objective, Inputs, Deliverables, Acceptance criteria and Constraints with the evidence rule).
- require the hand-off block back ("If a return has no hand-off block, I send it back and do not count it as delivered", A).
- run `git status --porcelain research_lab/`, then `git add research_lab/` and commit with the `Memory-Ref` trailer only when a memory was written. They never run `git add src/`, `git add .` or `git add -A`, and leave `src/train.py` for your human partner to commit after its code review.

A also opens with the kickoff and the memory search, and sends headline claims to the devil's-advocate gate.

# After the final-review fixes (Haiku 5.5): 1/1 pass

The skill now names the toolkit as `science-ultrapowers:<skill>`, lists every lab file in its record map, and tells a role run as the main session to route its own hand-offs. Run C again refuses the self-review ("the Paper Author wrote section 4, so it cannot review it"). It sends the Curator, the Citation Auditor and the Academic Reviewer in parallel, each with the full brief block. It asks the Research Engineer for a hand-off and sends a G3 review of `src/train.py` to the Experiments Lead. It stages only `research_lab/` ("I never run git add -A, git add ., or git add src/"). [Run](runs/with-skill-C.md).

# After the generality rename (Haiku 5.5): 1/1 pass

The roster names the role "Research Engineer" (it was "ML Research Engineer"). Run D refuses the self-review, sends four non-author checks of section 4 and a G3 review of `src/train.py` with the full brief block, requires the hand-off block, and stages only `research_lab/` ("I will not run `git add .`, `git commit -a`, or any command that stages src/train.py"). [Run](runs/with-skill-D.md).

# After the pre-release review fixes (Haiku 5.5): 1/1 pass

The hand-off block gained its `Findings proposed`, `Memories proposed` and `Review requested` lines, the commit rule became a paragraph, the Findings Curator is dispatched by the orchestrator, and code reviews go through `science-ultrapowers:requesting-code-review`. Run E refuses the self-review, reads the hand-off's new lines, sends three non-author checks of section 4 with the full brief block, routes the `src/train.py` review through the code-review skill to the Experiments Lead, and stages only `research_lab/` after `git status` ("Never run git add . or git add src/"). [Run](runs/with-skill-E.md).

# After the terminology standard (0.2.0) (Haiku 5.5): 1/1 pass

The skills now use the lab's terminology standard (0.2.0). Run F, on the prompt reworded only in the old terms (task and pass criteria unchanged): PASS (the Academic Paper Author is refused as reviewer of their own section; the re-verification, the adversarial review and the citation audit go to non-authors with full task assignment blocks (id, stage, owner, reviewer, due, objective, inputs, deliverables, completion criteria, restricted folders, constraints); a task report block is required back; src/train.py and paper/ left to the researcher; only research_lab/ staged after git status). [Run](runs/with-skill-F.md).

# After the lifecycle (0.2.0, phase 1) (Haiku 5.5): 1/1 pass

The stage table, the tracks paragraph, the routing rows for the three lifecycle skills and the binding rules are new. Run G, on run F's prompt (task and pass criteria unchanged): PASS (the Academic Paper Author never reviews its own section; the Academic Reviewer, the Curator and the Citation & Reference Auditor assigned with full task assignment blocks; a task report required back; src/train.py and paper/ left to the researcher; only research_lab/ committed after git status; the adversarial review queued before any approval) [Run](runs/with-skill-G.md).
