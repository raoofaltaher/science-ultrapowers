# Task assignment and task report

The project manager (the lead session) writes a task assignment when it assigns work to a role. The role answers with a task report. Both blocks are quoted verbatim in the session close.

## Task assignment

```
TASK <TASK-id> | Stage <Question / Literature / Preregistration / Execution / Results / Reporting / Publication> | Owner <role> | Reviewer <role> | Due <date>
Objective: <one sentence>
Inputs: <paths, EVR-ids, FND-ids, artifact ids>
Deliverables: <paths>
Completion criteria: <what the reviewer checks before the task counts as done>
Restricted folders: <folders the project brief marks restricted, or 'none'>
Constraints: evidence rule (science-ultrapowers:verifying-evidence-by-doi); no test-set use unless preregistered; <others>
```

## Task report

```
TASK REPORT <TASK-id> -> <next role>
Status: <done / done with concerns / needs context / blocked>
Deliverables: <paths>
Inputs: <artifact ids or paths each deliverable was computed from, or 'none'>
Checks performed: DOIs checked <n matched / n other + list>; evidence records <ids>; EXP-ids <ids>; tests <result>
Findings submitted: <statement | metrics file and row | scope> or 'none' (no FND-id yet)
Memories proposed: <type | basis | project or deliverable path | fact; why; how to apply> or 'none'
Review requested: <what, by which non-author role> or 'none'
Open issues and risks: <list>
Requests filed: <REQ-ids or 'none'>
Deviations from the assignment: <list or 'none'>
Next: <next role and action>
```
