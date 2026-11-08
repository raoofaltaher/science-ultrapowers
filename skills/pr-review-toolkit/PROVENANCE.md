# PROVENANCE: pr-review-toolkit

| Field | Value |
|---|---|
| Upstream repository | https://github.com/neuromechanist/research-skills |
| Pinned commit | `f0219bde233abb44d8a0c5d73f41ea27073e1493` |
| Upstream path | `plugins/project/skills/pr-review-toolkit` |
| Licence | BSD-3-Clause (upstream `LICENSE` copied verbatim to this folder) |
| Retrieved / vendored | 2026-09-26, by the originating lab's setup |
| Vetting | static security review (S1-S8) and quality rubric (Q1-Q6) by an independent reviewer track; Jev second opinion; review board (Academic Supervisor + Scientific Peer Reviewer profiles). Records: the originating lab's decision log, review records and skill-vetting folder (not shipped with the plugin) |
| Approved by | the user (References & Resources Specialist), 2026-09-26: "Install all 14" |

## Lab addenda applied
- removed agents/openai.yaml (another coding harness only)
- removed references/review-panel-protocol.md (another coding harness only)
- replaced 'Dispatch' section with lab delegation (Claude Code / inline)
- edited the frontmatter description: epic-dev reference replaced by the lab's G3 checkpoint
- edited the introduction: wording for other coding harnesses replaced
- added references/lab-ml-pipeline-checklist.md (lab-authored ML-pipeline checklist) and linked it from the Required Workflow
- replaced the upstream dispatch workflow step
- inserted the LAB ADDENDUM block at the top of SKILL.md
- added LICENSE (upstream repository licence, verbatim)
- 2026-11-07 science-ultrapowers: Claude-Science-only overlay items removed (PDF-explorer, kernel paths, host skill-reader calls), Claude Code tool line added, skill cross-references renamed, project names and decision ids generalised
- 2026-11-07 science-ultrapowers: references/lab-ml-pipeline-checklist.md: project-specific defect records, task and finding ids and the Claude-Science sidecar-loader item removed, items renumbered
- 2026-11-08 science-ultrapowers: overlay: `uv run` removed from the overlay (uv is not a plugin runtime dependency); SKILL.md hash refreshed
- 2026-11-08 science-ultrapowers: overlay retitled LAB ADDENDUM (binding), the standard's words (SKILL.md hash refreshed)

## File hashes (SHA-256, first 12 hex chars)
| File | Status | Upstream | Vendored |
|---|---|---|---|
| `LICENSE` | added | `` | `52c155c8e749` |
| `SKILL.md` | modified | `93e9ea5e98fa` | `aafce5512422` |
| `references/lab-ml-pipeline-checklist.md` | added | `` | `ffc44fb7d306` |
| `references/review-procedure.md` | unchanged | `4aa7246a27d4` | `4aa7246a27d4` |
| `references/review-rubrics.md` | unchanged | `18c8c25bb17a` | `18c8c25bb17a` |
| `agents/openai.yaml` | removed | `1e8aed9fef16` | n/a |
| `references/review-panel-protocol.md` | removed | `ec48e94e7522` | n/a |

To re-verify: download `https://github.com/neuromechanist/research-skills/archive/f0219bde233abb44d8a0c5d73f41ea27073e1493.zip` and compare the `unchanged` rows.
