# Refactor check v3: remembering-for-the-lab, artifact scope

Why: in v2 every with-skill run refused the artifact proposal partly because the skill's never-store list said "artifacts", read as "facts about an artifact". The skill now says "artifact contents" and labels the scope row "Reading one artifact". This check confirms an artifact-scoped memory is written, while a result and an environment fix recipe are still refused.

Right calls:
- (a) gotcha | observed | `source` column of artifact 3f9a0c12 is the annotator batch id: SAVE under artifact/3f9a0c12/, entity artifact:3f9a0c12.
- (b) lesson | observed | LoRA rank 8 macro-F1 0.71 (run-22): REFUSE, a result for the findings ledger.
- (c) gotcha | observed | scheduler kills jobs writing over 50 GB to /tmp, set TMPDIR: REFUSE, a fix recipe / environment setup for the setup docs.

Pass: (a) is written with artifact scope; (b) is not stored; (c) is not stored as a procedure (its durable trap may be stored as a gotcha with the remedy as How to apply, the procedure itself goes to the job script or setup docs). (Widened after the runs: see README.)

## Prompt given to the agent (inline; with the skill only)

    This is a written exercise. Do not run any tools; answer in text only.

    You are the main Claude Code session acting as the Research Project Manager (the orchestrator) of a research lab. The project folder is a git repository; the lab's records live in `research_lab/`: findings in `research_lab/02_findings_ledger/FINDINGS.md`, decisions in `research_lab/00_project_knowledge/DECISIONS.md`, the task board in `research_lab/00_project_knowledge/TASK_BOARD.md`; versioned deliverables in the artifact store `research_lab/artifacts/`. The lab keeps long-term memory in `research_lab/memory/`: `MEMORY.md` is the index, one line per memory, and each memory is one Markdown file under `research_lab/memory/project/` or `research_lab/memory/artifact/<artifact_id>/`. `research_lab/lab.json` sets `memory.indexBudget` to 150, and `MEMORY.md` is 120 lines long today.

    Today's hand-offs proposed these memories:

        From T-130 (data-evaluation-researcher):
          (a) gotcha | observed | In the annotated tweet set (artifact 3f9a0c12), the `source` column holds the annotator's batch id, not where the tweet came from; a join on it with the crawler table silently mismatches 38% of rows.
          (b) lesson | observed | LoRA rank 8 fine-tuning reaches macro-F1 0.71 on the held-out cohort (run-22, 3 seeds).
        From T-131 (research-engineer):
          (c) gotcha | observed | The cluster scheduler kills any job that writes more than 50 GB to /tmp; set TMPDIR to the project scratch volume before training.

    Your human partner writes: "Save all of these to memory and commit, please."

    Write exactly what you do now, in order: for each proposal, whether it goes into research_lab/memory/ (and if so the file path and its frontmatter) or where it goes instead and why; any change to MEMORY.md; and the commit. Do not ask questions.
