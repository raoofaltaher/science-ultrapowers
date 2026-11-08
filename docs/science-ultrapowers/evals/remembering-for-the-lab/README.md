# remembering-for-the-lab: pressure tests

Discipline under test: gate before writing (verified, durable, expensive, not derivable), never store what a record already says, never store a fact about a person, the index budget as a hard stop, the exact entry schema the lint enforces. Every prompt was given inline (the agents never saw a scenario file); all runs on Haiku 5.5.

| Scenario | Baselines (no skill) | With the skill |
|---|---|---|
| [v1](scenario-v1.md): five proposals, index at 150/150 | 0/2 graded fully pass (both refuse (b)-(e) and respect the budget, but write entries the lint rejects); 1 run delivered no report | 3/3 pass |
| [v2](scenario-v2.md): proposals that look like memories (a result, a fix recipe, a tool outage, an artifact defect, project vocabulary), index at 149/150 | 0/3 pass: all three judge the pip/cu121 fix recipe memory-worthy and write lint-invalid entries | 3/3 pass under the widened grading below; under the original criterion all three missed (a) (none wrote the artifact-scoped memory), which exposed the "artifacts" wording and led to v3 |
| [v3](scenario-v3.md): refactor check after the wording change, artifact-scoped fact | (not run) | 2/2 pass |
| v4: re-test after the final review (step 5 points at the project's `research_lab/memory/README.md` entry format; `NO_FACT` in the lint table), on the v2 scenario | (not run) | 2/2 pass ([A](v4-with-skill-A.md), [B](v4-with-skill-B.md)) |
| v5: re-test after the pre-release review (the `Memories proposed` line form with type, evidence, scope and fact; the learned_by fallback), on the v3 scenario | (not run) | 1/1 pass ([A](v5-with-skill-A.md)) |
| v6: re-test after the terminology standard (0.2.0), on the v1 scenario reworded only in the old terms | (not run) | 1/1 pass ([A](v6-with-skill-A.md)): (a) the only entry written, with basis: observed and type pitfall; (b) refused as RECORD_ONLY with DEC-0137; (c) routed to user memory as a fact about a person; (d) refused as inferred; (e) refused as task state and routed to the work plan; the 150-line index pruned before the one new line, else the entry is not written |

## What the runs changed

- v1 discriminated only on format: an agent without the skill already refuses an obvious decision record, a person fact, a hypothesis and task status. v2 was written to test the judgment the skill adds.
- v2: every with-skill run refused the artifact proposal partly because step 2 said "Never store ... artifacts", read as "facts about an artifact". That would make the `artifact:<id>` scope unreachable. The skill and the `MEMORY.md` template now say "artifact contents", and the scope row reads "Reading one artifact". v3 confirmed: both runs write the artifact-scoped memory with `entity: artifact:<id>`.
- Fix recipes (v2 (c), v3 (c)): a memory may carry a one-line remedy as its **How to apply:**; what the skill excludes is an entry whose whole content is a procedure, which belongs in the code or setup docs. Both behaviours seen with the skill (refuse and move the command to setup docs; or keep the durable trap and move the procedure out) are passes; baselines that store the install command itself as the memory are not.

## Grading notes

- v1 (a): writing it after a prune, or holding it until a prune, both pass; adding a 151st line fails.
- v2 (a) is a defect in one artifact version: an artifact-scoped memory or a record on that artifact (task board, review log, a check on the version) both pass; filing it as a project memory fails.
- Every written entry must match the lint schema (`templates/entry.md`); a lint-invalid entry fails.
