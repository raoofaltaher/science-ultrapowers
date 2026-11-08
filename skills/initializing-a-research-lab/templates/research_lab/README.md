# {{NAME}} research lab

This folder is the record of the research lab that works on {{NAME}}{{DESCRIPTION_SENTENCE}} It indexes and governs the project's existing folders and never replaces them. Set up {{DATE}} by science-ultrapowers {{PLUGIN_VERSION}}. The rules are in `science-ultrapowers:running-the-lab`; start every session from `project/PROJECT_BRIEF.md`.

| Folder | Contents |
|---|---|
| `project/` | `PROJECT_BRIEF.md` (start here) and any digests of the project's code, data and documents |
| `literature/` | the source table `SOURCES.csv`, `EXCEPTIONS.md`, `evidence_records/`, `search_logs/`, `citation_audits/` |
| `findings/` | the findings log `FINDINGS_LOG.md`, the key results table `KEY_RESULTS.md`, `LAB_NOTEBOOK.md` |
| `experiments/` | `EXPERIMENT_REGISTER.md`, `preregistrations/`, `feasibility/` (pilot and feasibility studies) |
| `reviews/` | `REVIEW_LOG.md` and the review reports in `reports/` |
| `requests/` | `ACCESS_REQUESTS.md`, the queue for the researcher |
| `decisions/` | `DECISION_LOG.md` and the meeting notes in `lab_meetings/` |
| `planning/` | the work plan `WORK_PLAN.md`, `ROADMAP_STATUS.md`, `RISK_REGISTER.md` |
| `automation/` | `JEV_CALLS.jsonl` (every Jev call) and `thresholds.json` (the thresholds the Academic Supervisor approved for automation) |
| `tool_vetting/` | vetting records for any third-party skill added to the lab |
| `templates/` | evidence record, hypothesis record, preregistration, internal review, referee report, citation audit, task report, method proposal, adversarial review, protocol-adherence review, response matrix, synthesis matrix, archive manifest, meeting notes |
| `artifacts/` | the versioned artifact archive (`archive/`) |
| `memory/` | lab memory: the `MEMORY.md` index, `project/` and `artifact/` entries |
| `.working/` | working notes only; ignored by git and deleted at each session close |

Full-text PDFs live in `references/` at the project root, which git ignores.
