# remembering-for-the-lab: v6-with-skill-A (after the terminology standard, 0.2.0)

Configuration: with the skill, after the terminology standard of 0.2.0, which renamed the lab's terms and paths in every skill. The prompt is the scenario's, reworded only where it quoted an old term or path (the findings, decisions and work-plan paths took the new layout, 'artifact store' became 'artifact archive', 'stand-up' became 'session close', 'hand-offs' became 'task reports', the ids became TASK-, DEC- and FND- forms, and 'gotcha' became 'pitfall'; this is the scenario v1 prompt (five proposals, index at 150/150)); the task and the pass criteria are unchanged. Run on 2026-11-08. Model: Haiku 5.5. The run read the skill's `SKILL.md` and the inline prompt, nothing else.

## Prompt (verbatim)

~~~~
This is a written exercise. Do not run any tools; answer in text only.

You are the lead Claude Code session acting as the Research Project Manager of a research lab. The project folder is a git repository; the lab's records live in `research_lab/`: findings in `research_lab/findings/FINDINGS_LOG.md`, decisions in `research_lab/decisions/DECISION_LOG.md`, the work plan in `research_lab/planning/WORK_PLAN.md`. The lab keeps long-term memory in `research_lab/memory/`: `MEMORY.md` is the index, one line per memory, and each memory is one Markdown file under `research_lab/memory/project/` or `research_lab/memory/artifact/<artifact_id>/`. `research_lab/lab.json` sets `memory.indexBudget` to 150, and `MEMORY.md` is exactly 150 lines long today.

It is the session close. Today's task reports proposed these memories:

    From TASK-0118 (data-evaluation-researcher):
      (a) pitfall | observed | The annotation tool's CSV export silently drops every row whose text contains a line break unless it is exported with quoting=all; run-17 lost 212 of 9,480 rows this way before the re-export.
      (b) decision | stated | All calibration runs use 5-fold stratified cross-validation (DEC-0137).
    From TASK-0119 (literature-researcher):
      (c) directive | stated | The supervisor, Dr. Lindqvist, dislikes long emails; keep every update to her under five lines.
    From TASK-0120 (research-engineer):
      (d) lesson | inferred | Learning-rate warmup length probably explains why seed 2 is unstable.
      (e) lesson | observed | The run-18 sweep finished seeds 1-3; seeds 4 and 5 still need to run tomorrow.

The researcher writes: "Long day, I'm closing the laptop in five minutes. Just get today's proposed memories saved and committed so nothing gets lost."

Write exactly what you do now, in order: for each proposal, whether it goes into research_lab/memory/ (and if so the file path and its frontmatter) or where it goes instead and why; any change to MEMORY.md; and the commit. Do not ask questions.
~~~~

## Final report (verbatim)

~~~~
**Order of operations.** For each proposal I search first: `MEMORY.md`, then `research_lab/memory/`, then the records. The routing below assumes that search finds nothing already held, except where a record is named.

**1. (a) pitfall | observed | annotation CSV export.** Goes to memory.
- File: `research_lab/memory/project/annotation-csv-drops-multiline-rows.md` (project scope, since the tool is project-wide).
- Frontmatter:
  ```
  ---
  name: annotation-csv-drops-multiline-rows
  type: pitfall
  basis: observed
  entity: project
  learned_by: data-evaluation-researcher
  date: 2026-11-08
  ---
  ```
- Body (one sentence): "The annotation tool's default CSV export silently drops every row whose text contains a line break, with no error."
- Admission: checked (observed in run-17), durable, expensive to rediscover (212 rows were lost before anyone noticed), and not in the code or the lab records.
- The `quoting=all` fix is a fix recipe, so it stays out of memory (rule 2). The run-17 loss and the re-export are what happened, so they go to the TASK-0118 report and to the lab notebook or findings log that carries run-17.

**2. (b) decision | stated | 5-fold stratified CV (DEC-0137).** Not stored.
- DEC-0137 already holds this in `research_lab/decisions/DECISION_LOG.md`. Memory would only duplicate it (`RECORD_ONLY`), so I delete the proposal.

**3. (c) directive | stated | supervisor dislikes long emails.** Not in the lab.
- This is a preference of a person. It goes to the researcher's Claude Code user memory, as a single line: "Supervisor prefers update emails under five lines." Nothing about it is written under `research_lab/`.

**4. (d) lesson | inferred | warmup length and seed 2.** Not stored.
- An inferred hypothesis fails "checked". Storing it would only create a re-check item at prune.
- It goes to the TASK-0120 report as an open hypothesis, and to `research_lab/planning/WORK_PLAN.md` as a test to run.

**5. (e) lesson | observed | run-18 seeds 4 and 5.** Not stored.
- This is task state, and it will be stale tomorrow.
- The seeds 4 and 5 work goes to `research_lab/planning/WORK_PLAN.md` as tomorrow's item. The seeds 1-3 results go to the run-18 record named in the TASK-0120 report.

**Working notes.** I delete `research_lab/.working/2026-11-08-<session>/` once every proposal is routed. Nothing in it is committed.

**MEMORY.md.** It is exactly 150 lines, and `memory.indexBudget` is 150. Adding one line makes 151, which is a hard stop, so I prune first.
- I run `memory-lint` on `research_lab/memory` and remove or merge at least one entry it flags (a `RECORD_ONLY`, `NEAR_DUP` or stale entry). I cannot name that entry without reading `MEMORY.md`.
- Then I add one index line under `## Project`: `- [Annotation CSV drops multi-line rows](project/annotation-csv-drops-multiline-rows.md) — pitfall: the default export silently loses rows with line breaks`. The file then stands at 150 lines.
- If pruning cannot free a line today, (a) is not written to memory. The fact stays in the TASK-0118 record, so nothing is lost.
- The consistency check must exit 0 (`BUDGET`, `DANGLING`, `ORPHAN`, `FM_*`).

**Commit.** I stage `research_lab/` without `.working/`, and I commit on the project's current branch. I do not push, since that was not asked.

```
memory: annotation CSV export drops multi-line rows

Record the run-17 loss and the quoting fix in the TASK-0118 report;
plan seeds 4-5 in WORK_PLAN.

Memory-Ref: research_lab/memory/project/annotation-csv-drops-multiline-rows.md

[attribution removed]
```
~~~~

## Grade

PASS ((a) the only entry written, with basis: observed and type pitfall; (b) refused as RECORD_ONLY with DEC-0137; (c) routed to user memory as a fact about a person; (d) refused as inferred; (e) refused as task state and routed to the work plan; the 150-line index pruned before the one new line, else the entry is not written)
