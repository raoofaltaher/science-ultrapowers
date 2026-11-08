# PROVENANCE: pptx-posters

| Field | Value |
|---|---|
| Upstream repository | https://github.com/K-Dense-AI/claude-scientific-writer |
| Pinned commit | `0c7260603be3de4dd5161565ab92e85b31c45eb5` |
| Upstream path | `skills/pptx-posters` |
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
| `SKILL.md` | modified | `d4e0fe7be2b8` | `eea224bb79eb` |
| `assets/generation_dependencies.json` | unchanged | `f18b76e1b22a` | `f18b76e1b22a` |
| `assets/poster_manifest_template.json` | unchanged | `89a90c38b843` | `89a90c38b843` |
| `assets/poster_quality_checklist.md` | unchanged | `5ba7398846ab` | `5ba7398846ab` |
| `references/manifest_spec.md` | unchanged | `2a825c09c339` | `2a825c09c339` |
| `references/poster_content_guide.md` | unchanged | `dea961f67f1d` | `dea961f67f1d` |
| `references/poster_design_principles.md` | unchanged | `7fac4022b656` | `7fac4022b656` |
| `references/poster_layout_design.md` | unchanged | `0ef48f1b9e34` | `0ef48f1b9e34` |
| `references/pptx_security.md` | unchanged | `a349556e4be4` | `a349556e4be4` |
| `references/security_validation.md` | modified | `3f958506b558` | `b31e46da2556` |
| `references/source_ledger.md` | unchanged | `e5a047a34f49` | `e5a047a34f49` |
| `scripts/_common.py` | unchanged | `5ab02f9993a7` | `5ab02f9993a7` |
| `scripts/_manifest.py` | unchanged | `4b59a232f6a1` | `4b59a232f6a1` |
| `scripts/_pptx.py` | unchanged | `7c350c4aa56d` | `7c350c4aa56d` |
| `scripts/check_layout.py` | unchanged | `d49588b8c965` | `d49588b8c965` |
| `scripts/check_palette.py` | unchanged | `f9bfc91cfc9c` | `f9bfc91cfc9c` |
| `scripts/generate_poster.py` | unchanged | `062aedd0068c` | `062aedd0068c` |
| `scripts/inspect_pptx.py` | unchanged | `76b504075af9` | `76b504075af9` |
| `scripts/inventory_images.py` | unchanged | `07c6df85ca9f` | `07c6df85ca9f` |
| `scripts/plan_export.py` | unchanged | `76bee77a5f4d` | `76bee77a5f4d` |
| `scripts/validate_manifest.py` | unchanged | `e888bc04fca0` | `e888bc04fca0` |

To re-verify: download `https://github.com/K-Dense-AI/claude-scientific-writer/archive/0c7260603be3de4dd5161565ab92e85b31c45eb5.zip` and compare the `unchanged` rows.
