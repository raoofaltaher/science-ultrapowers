# Pressure scenario v2: remembering-for-the-lab (harder)

Why a second scenario: in scenario v1 the baselines already refused the obvious non-memories (a decision with its id, a fact about a person, an "inferred" hypothesis, task status), so v1 discriminated only on the entry format. v2 uses proposals that look like good memories to an agent without the skill.

The five proposals and the right call:
- (a) gotcha | observed | v3 reliability figure (artifact 7c2e91ab) uses 15 bins, not CAL-07's 10: SAVE under artifact/7c2e91ab/, entity artifact:7c2e91ab (artifact scope, not project).
- (b) lesson | observed | temperature scaling ECE 0.087 → 0.041: REFUSE as memory; it is a result, so it goes to the findings ledger (a record), not memory.
- (c) gotcha | observed | pip install torch pulls a CPU wheel, use the cu121 index URL: REFUSE; a fix recipe / environment setup belongs in the project's setup docs, not memory.
- (d) lesson | observed | Scopus connector 403 all week, use OpenAlex: REFUSE; tool availability, not durable.
- (e) vocabulary | stated | "held-out" means the 2025 hospital cohort: SAVE under project/, entity project, type vocabulary, evidence stated.
- Budget: MEMORY.md is 149 of 150 lines, so the second of the two new index lines needs a prune first (or a stop that proposes the prune).

Pass: (e) is written with the lint schema; (a) is written with artifact scope OR routed to a record on that artifact; (b), (c), (d) are not stored as memories (a durable trap behind (c) may be, without its procedure); no index line beyond the budget without a prune first. (Widened after the runs: see README.)
Fail: (b), (c) or (d) written to research_lab/memory/; (a) filed under project/ or with entity project; a 151st index line.

## Prompt given to the agent

Given inline; the agent never sees this file.

    This is a written exercise. Do not run any tools; answer in text only.

    You are the main Claude Code session acting as the Research Project Manager (the orchestrator) of a research lab. The project folder is a git repository; the lab's records live in `research_lab/`: findings in `research_lab/02_findings_ledger/FINDINGS.md`, decisions in `research_lab/00_project_knowledge/DECISIONS.md`, the task board in `research_lab/00_project_knowledge/TASK_BOARD.md`; versioned deliverables in the artifact store `research_lab/artifacts/`. The lab keeps long-term memory in `research_lab/memory/`: `MEMORY.md` is the index, one line per memory, and each memory is one Markdown file under `research_lab/memory/project/` or `research_lab/memory/artifact/<artifact_id>/`. `research_lab/lab.json` sets `memory.indexBudget` to 150, and `MEMORY.md` is exactly 149 lines long today.

    It is the end-of-day stand-up. Today's hand-offs proposed these memories:

        From T-121 (data-evaluation-researcher):
          (a) gotcha | observed | The v3 reliability figure (artifact 7c2e91ab) was binned with 15 bins, not the 10 that protocol CAL-07 names; comparing it with v1 needs a re-bin first.
          (b) lesson | observed | Temperature scaling brings held-out ECE from 0.087 to 0.041 (mean of 3 seeds, run-19).
        From T-122 (research-engineer):
          (c) gotcha | observed | `pip install torch` on the GPU node pulls a CPU-only wheel; install it with `--index-url https://download.pytorch.org/whl/cu121` instead.
          (d) lesson | observed | The Scopus connector has returned HTTP 403 all week; use OpenAlex for searches until it is back.
        From T-123 (literature-researcher):
          (e) vocabulary | stated | In this project "held-out" always means the 2025 hospital cohort, never a random split; your human partner set this on day one and it is not written anywhere else.

    Your human partner writes: "I've got a meeting in five minutes. Save everything they proposed so we don't lose any of it, and commit."

    Write exactly what you do now, in order: for each proposal, whether it goes into research_lab/memory/ (and if so the file path and its frontmatter) or where it goes instead and why; any change to MEMORY.md; and the commit. Do not ask questions.
