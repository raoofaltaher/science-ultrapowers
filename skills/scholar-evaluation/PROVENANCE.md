# PROVENANCE: scholar-evaluation

| Field | Value |
|---|---|
| Upstream repository | https://github.com/K-Dense-AI/claude-scientific-writer |
| Pinned commit | `0c7260603be3de4dd5161565ab92e85b31c45eb5` |
| Upstream path | `skills/scholar-evaluation` |
| Licence | MIT (upstream `LICENSE` copied verbatim to this folder) |
| Retrieved / vendored | 2026-09-26, by the originating lab's setup |
| Vetting | static security review (S1-S8) and quality rubric (Q1-Q6) by an independent reviewer track; Jev second opinion; review board (Academic Supervisor + Scientific Peer Reviewer profiles). Records: the originating lab's decision log, review records and skill-vetting folder (not shipped with the plugin) |
| Approved by | the user (References & Resources Specialist), 2026-09-26: "Install all 14" |

## Lab overlays applied
- annotated references/security_validation.md as unverified vendor narrative
- removed allowed-tools from frontmatter
- inserted the LAB OVERLAY block at the top of SKILL.md
- added LICENSE (upstream repository licence, verbatim)
- 2026-11-07 science-ultrapowers: Claude-Science-only overlay items removed (PDF-explorer, kernel paths, host skill-reader calls), Claude Code tool line added, skill cross-references renamed, project names and decision ids generalised
- 2026-11-07 science-ultrapowers: references/security_validation.md: lab note generalised (project name and date removed)
- 2026-11-08 science-ultrapowers: line endings normalised from CRLF to LF (no content change), vendored hashes refreshed: references/security_validation.md
- 2026-11-08 science-ultrapowers: overlay: `uv run` removed from the overlay (uv is not a plugin runtime dependency); SKILL.md hash refreshed
- 2026-11-08 science-ultrapowers: overlay runs python with -B (SKILL.md hash refreshed)

## File hashes (SHA-256, first 12 hex chars)
| File | Status | Upstream | Vendored |
|---|---|---|---|
| `LICENSE` | added | `` | `6ea149808a17` |
| `SKILL.md` | modified | `902c41a08cb5` | `55797a93caaa` |
| `assets/evaluation_template.json` | unchanged | `8b7795313847` | `8b7795313847` |
| `assets/evidence_manifest_template.json` | unchanged | `51512b9f307d` | `51512b9f307d` |
| `assets/process_checklist_template.json` | unchanged | `de0897b2404f` | `de0897b2404f` |
| `assets/ratings_template.csv` | unchanged | `0c518d16760d` | `0c518d16760d` |
| `assets/rubric_template.json` | unchanged | `3d596eb51866` | `3d596eb51866` |
| `references/evaluation_framework.md` | unchanged | `b1d2a381f60b` | `b1d2a381f60b` |
| `references/local_tooling.md` | unchanged | `3490ea8227bc` | `3490ea8227bc` |
| `references/responsible_assessment.md` | unchanged | `f87e3da86244` | `f87e3da86244` |
| `references/security_validation.md` | modified | `ffbe10c98411` | `12c52e1e2157` |
| `references/source_ledger.md` | unchanged | `400dfa4999fb` | `400dfa4999fb` |
| `scripts/_common.py` | unchanged | `77f2c1776edf` | `77f2c1776edf` |
| `scripts/calculate_scores.py` | unchanged | `07a1cd73cca0` | `07a1cd73cca0` |
| `scripts/check_process.py` | unchanged | `a296cf1eeb3e` | `a296cf1eeb3e` |
| `scripts/check_traceability.py` | unchanged | `29f68f2f8429` | `29f68f2f8429` |
| `scripts/generate_report_scaffold.py` | unchanged | `4231b29d4b71` | `4231b29d4b71` |
| `scripts/summarize_agreement.py` | unchanged | `82e0e36c7875` | `82e0e36c7875` |
| `scripts/validate_rubric.py` | unchanged | `843244f4728b` | `843244f4728b` |
| `scripts/weight_sensitivity.py` | unchanged | `4a5ecd515e6a` | `4a5ecd515e6a` |

To re-verify: download `https://github.com/K-Dense-AI/claude-scientific-writer/archive/0c7260603be3de4dd5161565ab92e85b31c45eb5.zip` and compare the `unchanged` rows.
