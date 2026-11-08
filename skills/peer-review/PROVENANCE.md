# PROVENANCE: peer-review

| Field | Value |
|---|---|
| Upstream repository | https://github.com/K-Dense-AI/claude-scientific-writer |
| Pinned commit | `0c7260603be3de4dd5161565ab92e85b31c45eb5` |
| Upstream path | `skills/peer-review` |
| License | MIT (upstream `LICENSE` copied verbatim to this folder) |
| Retrieved / vendored | 2026-09-26, by the originating lab's setup |
| Vetting | static security review (S1-S8) and quality rubric (Q1-Q6) by an independent reviewer track; Jev second opinion; review board (Academic Supervisor + Scientific Peer Reviewer profiles). Records: the originating lab's decision log, review records and skill-vetting folder (not shipped with the plugin) |
| Approved by | the user (References & Resources Specialist), 2026-09-26: "Install all 14" |

## Lab addenda applied
- annotated references/security_validation.md as unverified vendor narrative
- inserted the LAB ADDENDUM block at the top of SKILL.md
- added LICENSE (upstream repository license, verbatim)
- 2026-11-07 science-ultrapowers: Claude-Science-only overlay items removed (PDF-explorer, kernel paths, host skill-reader calls), Claude Code tool line added, skill cross-references renamed, project names and decision ids generalized
- 2026-11-07 science-ultrapowers: references/security_validation.md: lab note generalized (project name and date removed)
- 2026-11-08 science-ultrapowers: line endings normalized from CRLF to LF (no content change), vendored hashes refreshed: references/security_validation.md
- 2026-11-08 science-ultrapowers: overlay: `uv run` removed from the overlay (uv is not a plugin runtime dependency); SKILL.md hash refreshed
- 2026-11-08 science-ultrapowers: overlay runs python with -B (SKILL.md hash refreshed)
- 2026-11-08 science-ultrapowers: overlay retitled LAB ADDENDUM (binding), the standard's words (SKILL.md hash refreshed)

## File hashes (SHA-256, first 12 hex chars)
| File | Status | Upstream | Vendored |
|---|---|---|---|
| `LICENSE` | added | `` | `6ea149808a17` |
| `SKILL.md` | modified | `fed0262d707a` | `7f283e3b92cd` |
| `assets/citation_references_template.csv` | unchanged | `e00b259742a0` | `e00b259742a0` |
| `assets/claim_evidence_matrix_template.csv` | unchanged | `06e1215c998a` | `06e1215c998a` |
| `assets/reporting_checklist_template.csv` | unchanged | `02709793bc17` | `02709793bc17` |
| `assets/reporting_guidelines.json` | unchanged | `a3684d484981` | `a3684d484981` |
| `assets/review_intake_template.json` | unchanged | `14d7e00cdc71` | `14d7e00cdc71` |
| `assets/review_scaffold_template.md` | unchanged | `4e320c9a6238` | `4e320c9a6238` |
| `assets/source_ledger.csv` | unchanged | `a73e02a696c4` | `a73e02a696c4` |
| `assets/statistical_reproducibility_template.json` | unchanged | `071bfc0b1e1e` | `071bfc0b1e1e` |
| `assets/study_profile_template.json` | unchanged | `bc0c19b9ad47` | `bc0c19b9ad47` |
| `references/common_issues.md` | unchanged | `6a0979d6d64e` | `6a0979d6d64e` |
| `references/ethical_review_practice.md` | unchanged | `7a1b1cf1e02f` | `7a1b1cf1e02f` |
| `references/reporting_standards.md` | unchanged | `96ae056f8034` | `96ae056f8034` |
| `references/security_validation.md` | modified | `43b0b64acd16` | `a30c7a5eb283` |
| `references/statistical_reproducibility.md` | unchanged | `1075d96ade7f` | `1075d96ade7f` |
| `references/tool_reference.md` | unchanged | `ea9490c4e067` | `ea9490c4e067` |
| `scripts/_common.py` | unchanged | `78e751bd8024` | `78e751bd8024` |
| `scripts/audit_citations.py` | unchanged | `9521d624dce0` | `9521d624dce0` |
| `scripts/audit_statistics_reproducibility.py` | unchanged | `8daf60d78a27` | `8daf60d78a27` |
| `scripts/generate_review_scaffold.py` | unchanged | `3c2d6dc36e8e` | `3c2d6dc36e8e` |
| `scripts/lint_review.py` | unchanged | `623878c26ede` | `623878c26ede` |
| `scripts/select_reporting_guidelines.py` | unchanged | `9ccbbdeca6df` | `9ccbbdeca6df` |
| `scripts/validate_claim_evidence.py` | unchanged | `93490b289f28` | `93490b289f28` |
| `scripts/validate_review_intake.py` | unchanged | `bbea9af9a86c` | `bbea9af9a86c` |

To re-verify: download `https://github.com/K-Dense-AI/claude-scientific-writer/archive/0c7260603be3de4dd5161565ab92e85b31c45eb5.zip` and compare the `unchanged` rows.
