# remembering-for-the-lab: v5-with-skill-A (after the pre-release fixes)

Configuration: with the skill as shipped after the pre-release review (the `Memories proposed` line form with type, evidence, scope and fact; the learned_by fallback). Model: Haiku 5.5. Prompt: [scenario-v3.md](scenario-v3.md), given inline; the run read the skill file and the prompt, nothing else.

## Final report (verbatim)

No tools were run for this exercise. Everything below is the sequence I would follow, not something I did.

Step 0: Recall before writing, for all three proposals together. Read research_lab/memory/MEMORY.md, search research_lab/memory/ for the artifact id 3f9a0c12, the source column, the batch id, the join, the cluster scheduler, /tmp and TMPDIR, then check DECISIONS.md, FINDINGS.md, LAB_NOTEBOOK.md and REVIEW_LOG.md, and run git log --grep on those terms. If an entry already covers a proposal, I update that entry and do not add a new one. Nothing is written until this pass is done.

Step 1: Proposal (a), the source column in artifact 3f9a0c12.
- Gate: it is observed, it is a silent 38% mismatch that is costly to rediscover, and it is not in the code. It passes only if the artifact's own metadata or the records do not already document the column. If they do, it is derivable and I save nothing.
- Assuming it passes, the scope is "reading one artifact", so the file is research_lab/memory/artifact/3f9a0c12/source-column-is-batch-id.md.
- Frontmatter, in the field names of research_lab/memory/README.md (which I have not read in this exercise, so the exact field set comes from there): entity: artifact:3f9a0c12; type: gotcha; evidence: observed; learned_by: data-evaluation-researcher; date: 2026-11-08.
- Body, at most three sentences and a fact only: "In the annotated tweet set, the source column holds the annotator's batch id, not the tweet's origin. A join on it with the crawler table silently mismatches 38% of rows." No code, no tweet data, no join recipe.

Step 2: Proposal (b), LoRA rank 8 reaching macro-F1 0.71 on run-22.
- This is a result, not a memory. It fails the gate on "not derivable from the lab records": it belongs in the findings ledger, FINDINGS.md, which is a record. Its status is RECORD_ONLY, so I save nothing.
- If Step 0 finds that FINDINGS.md does not hold this result, I tell my human partner that the ledger is missing it, so the findings process can record it. It does not go to memory.

Step 3: Proposal (c), the scheduler's 50 GB /tmp limit.
- Gate: observed, expensive to rediscover (jobs are killed), and not in the code. It passes unless the cluster documentation or git history already states the limit, in which case it is derivable and I save nothing.
- Assuming it passes, the scope is the project, so the file is research_lab/memory/project/cluster-scheduler-tmp-limit.md.
- Frontmatter: entity: project; type: gotcha; evidence: observed; learned_by: research-engineer; date: 2026-11-08.
- Body, one sentence: "The cluster scheduler kills any job that writes more than 50 GB to /tmp."
- The "set TMPDIR to the project scratch volume" part is a fix recipe, and rule 2 forbids storing those. It is left out of memory. It belongs in the training configuration or in a runbook, and that is for the research engineer to decide, not for memory.

Step 4: MEMORY.md.
- Today it has 120 lines against a budget of 150. Adding two index lines makes 122, so no prune is needed.
- I add one line under "## Artifacts" for the 3f9a0c12 file and one line under "## Project" for the scheduler file, each in the format the README gives. No other line changes.
- If Step 2 or a passed-gate check removes an entry, the count changes accordingly. I recheck the count against 150 after writing.

Step 5: Lint.
- Run node "${CLAUDE_PLUGIN_ROOT}/skills/remembering-for-the-lab/scripts/memory-lint.mjs" research_lab/memory. It must exit 0. The codes that matter here are ORPHAN and DANGLING (the index and the files must match one to one), FM_* (frontmatter), and NEAR_DUP (against any existing entry found in Step 0). I fix any finding before committing.

Step 6: Commit.
- Stage only the paths I wrote: research_lab/memory/MEMORY.md, research_lab/memory/artifact/3f9a0c12/source-column-is-batch-id.md and research_lab/memory/project/cluster-scheduler-tmp-limit.md. I do not use git add -A, because the working tree holds unrelated changes.
- Commit with this message, one Memory-Ref line per saved file:

memory: record two lab gotchas from T-130 and T-131

Memory-Ref: research_lab/memory/artifact/3f9a0c12/source-column-is-batch-id.md
Memory-Ref: research_lab/memory/project/cluster-scheduler-tmp-limit.md

RAOOF A.

Reply to my human partner: I save two of the three proposals, (a) and (c), as described above, and the commit covers those two files plus the index. I do not save (b), because the lab's findings ledger already holds that result, or it should, and I flag the gap if it does not. I also leave the TMPDIR fix out of memory, because memory holds facts, not fix recipes. If the recall pass or the gate checks above show that any proposal is derivable, I save nothing for it and say which gate step failed.

## Verdict: PASS

(a) written with artifact scope and its evidence class; (b) refused as a record-only result; (c) stored as a gotcha without the procedure; recall before writing; the index budget checked; lint before the commit; only the written paths staged. The attribution line comes from the run's own session, not from the skill.
