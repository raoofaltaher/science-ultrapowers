# PROVENANCE: hypothesis-generation

| Field | Value |
|---|---|
| Upstream repository | https://github.com/K-Dense-AI/claude-scientific-writer |
| Pinned commit | `0c7260603be3de4dd5161565ab92e85b31c45eb5` |
| Upstream path | `skills/hypothesis-generation` |
| Licence | MIT (upstream `LICENSE` copied verbatim to this folder) |
| Retrieved / vendored | 2026-09-26, by the originating lab's setup |
| Vetting | static security review (S1-S8) and quality rubric (Q1-Q6) by an independent reviewer track; Jev second opinion; review board (Academic Supervisor + Scientific Peer Reviewer profiles). Records: the originating lab's decision log, review records and skill-vetting folder (not shipped with the plugin) |
| Approved by | the user (References & Resources Specialist), 2026-09-26: "Install all 14" |

## Lab addenda applied
- annotated references/security_validation.md as unverified vendor narrative
- inserted the LAB ADDENDUM block at the top of SKILL.md
- added LICENSE (upstream repository licence, verbatim)
- 2026-11-07 science-ultrapowers: Claude-Science-only overlay items removed (PDF-explorer, kernel paths, host skill-reader calls), Claude Code tool line added, skill cross-references renamed, project names and decision ids generalised
- 2026-11-07 science-ultrapowers: references/security_validation.md: lab note generalised (project name and date removed)
- 2026-11-08 science-ultrapowers: line endings normalised from CRLF to LF (no content change), vendored hashes refreshed: references/security_validation.md
- 2026-11-08 science-ultrapowers: overlay: `uv run` removed from the overlay (uv is not a plugin runtime dependency); SKILL.md hash refreshed
- 2026-11-08 science-ultrapowers: overlay runs python with -B (SKILL.md hash refreshed)
- 2026-11-08 science-ultrapowers: overlay retitled LAB ADDENDUM (binding), the standard's words (SKILL.md hash refreshed)

## File hashes (SHA-256, first 12 hex chars)
| File | Status | Upstream | Vendored |
|---|---|---|---|
| `LICENSE` | added | `` | `6ea149808a17` |
| `SKILL.md` | modified | `039881416522` | `f77dfe6e5ca0` |
| `assets/evidence_ledger_template.csv` | unchanged | `1ec5cc4ada96` | `1ec5cc4ada96` |
| `assets/falsification_controls_template.json` | unchanged | `beea4e2be3b5` | `beea4e2be3b5` |
| `assets/hypothesis_record_template.json` | unchanged | `73f080a6696c` | `73f080a6696c` |
| `assets/operationalization_template.json` | unchanged | `36ecdbd91c02` | `36ecdbd91c02` |
| `assets/prediction_rival_matrix_template.csv` | unchanged | `ccf6cb53c048` | `ccf6cb53c048` |
| `assets/preregistration_scaffold_template.md` | unchanged | `570314aa6669` | `570314aa6669` |
| `assets/search_boundary_template.json` | unchanged | `b885d4e252c0` | `b885d4e252c0` |
| `assets/source_ledger.csv` | unchanged | `185f563d213a` | `185f563d213a` |
| `references/causal_inference_and_claims.md` | unchanged | `37fba9d9d724` | `37fba9d9d724` |
| `references/concepts_and_workflow.md` | unchanged | `a86a8f464fb5` | `a86a8f464fb5` |
| `references/ethics_safety_and_ai.md` | unchanged | `f89c8c85cab8` | `f89c8c85cab8` |
| `references/experimental_design_patterns.md` | unchanged | `83c0c75c7b1e` | `83c0c75c7b1e` |
| `references/hypothesis_quality_criteria.md` | unchanged | `12698b549f77` | `12698b549f77` |
| `references/literature_search_strategies.md` | unchanged | `2a34fa0645f8` | `2a34fa0645f8` |
| `references/preregistration_and_open_science.md` | unchanged | `fd4f7ffe03d4` | `fd4f7ffe03d4` |
| `references/security_validation.md` | modified | `39dffd9c0878` | `49514eaa3041` |
| `references/source_ledger.md` | unchanged | `ff41a6f5e1d3` | `ff41a6f5e1d3` |
| `references/tool_reference.md` | unchanged | `db305bec51a4` | `db305bec51a4` |
| `scripts/_common.py` | unchanged | `a1e1390b9bac` | `a1e1390b9bac` |
| `scripts/audit_evidence_ledger.py` | unchanged | `18fc0a947fec` | `18fc0a947fec` |
| `scripts/check_falsification_controls.py` | unchanged | `e56f67b92d15` | `e56f67b92d15` |
| `scripts/check_operationalization.py` | unchanged | `efc093f4b58b` | `efc093f4b58b` |
| `scripts/generate_preregistration_scaffold.py` | unchanged | `f953e3af468c` | `f953e3af468c` |
| `scripts/lint_causal_claims.py` | unchanged | `561186e71f7c` | `561186e71f7c` |
| `scripts/validate_hypothesis_schema.py` | unchanged | `63bc1b7752d2` | `63bc1b7752d2` |
| `scripts/validate_prediction_matrix.py` | unchanged | `3888802496f4` | `3888802496f4` |

To re-verify: download `https://github.com/K-Dense-AI/claude-scientific-writer/archive/0c7260603be3de4dd5161565ab92e85b31c45eb5.zip` and compare the `unchanged` rows.
