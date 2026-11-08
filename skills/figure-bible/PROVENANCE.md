# PROVENANCE: figure-bible

| Field | Value |
|---|---|
| Upstream repository | https://github.com/neuromechanist/research-skills |
| Pinned commit | `f0219bde233abb44d8a0c5d73f41ea27073e1493` |
| Upstream path | `plugins/figures/skills/figure-bible` |
| Licence | BSD-3-Clause (upstream `LICENSE` copied verbatim to this folder) |
| Retrieved / vendored | 2026-09-26, by the originating lab's setup |
| Vetting | static security review (S1-S8) and quality rubric (Q1-Q6) by an independent reviewer track; Jev second opinion; review board (Academic Supervisor + Scientific Peer Reviewer profiles). Records: the originating lab's decision log, review records and skill-vetting folder (not shipped with the plugin) |
| Approved by | the user (References & Resources Specialist), 2026-09-26: "Install all 14" |

## Lab addenda applied
- added schemas/theme.schema.json (from plugins/figures/schemas/, unmodified; lib/theme.py loads it from ../schemas)
- added lib/theme.py (from plugins/figures/lib/, unmodified)
- patched scripts/init_theme.py: library path -> vendored lib/
- patched scripts/validate_theme.py: library path -> vendored lib/
- removed the advisory image-generator model fields (see the second 2026-11-07 line below)
- inserted the LAB ADDENDUM block at the top of SKILL.md
- added LICENSE (upstream repository licence, verbatim)
- 2026-11-07 science-ultrapowers: Claude-Science-only overlay items removed (PDF-explorer, kernel paths, host skill-reader calls), Claude Code tool line added, skill cross-references renamed, project names and decision ids generalised
- 2026-11-07 science-ultrapowers: lib/theme.py, schemas/theme.schema.json, examples/nature-neuro.theme.json, scripts/init_theme.py, references/theme-fields.md and SKILL.md: advisory image-generator model fields (and their init_theme.py flags and summary row) removed; scripts/validate_theme.py: comment generalised
- 2026-11-08 science-ultrapowers: line endings normalised from CRLF to LF (no content change), vendored hashes refreshed: scripts/init_theme.py, scripts/validate_theme.py
- 2026-11-08 science-ultrapowers: overlay runs python with -B (SKILL.md hash refreshed)
- 2026-11-08 science-ultrapowers: overlay retitled LAB ADDENDUM (binding), the standard's words (SKILL.md hash refreshed)

## File hashes (SHA-256, first 12 hex chars)
| File | Status | Upstream | Vendored |
|---|---|---|---|
| `LICENSE` | added | `` | `52c155c8e749` |
| `SKILL.md` | modified | `ed0dcf5b4525` | `85dd7d24e70a` |
| `examples/nature-neuro.theme.json` | modified | `a3418e5b7830` | `f9153c775f67` |
| `lib/theme.py` | added | `` | `77a61a048aff` |
| `references/theme-fields.md` | modified | `a5e34e820d9b` | `64c92cadcd90` |
| `schemas/theme.schema.json` | added | `` | `564212f3330a` |
| `scripts/init_theme.py` | modified | `e1e220e6bdc5` | `4be740f91105` |
| `scripts/validate_theme.py` | modified | `df543fda57b6` | `2b5f930a45bc` |

To re-verify: download `https://github.com/neuromechanist/research-skills/archive/f0219bde233abb44d8a0c5d73f41ea27073e1493.zip` and compare the `unchanged` rows.
