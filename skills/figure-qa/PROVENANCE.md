# PROVENANCE: figure-qa

| Field | Value |
|---|---|
| Upstream repository | https://github.com/neuromechanist/research-skills |
| Pinned commit | `f0219bde233abb44d8a0c5d73f41ea27073e1493` |
| Upstream path | `plugins/figures/skills/figure-qa` |
| License | BSD-3-Clause (upstream `LICENSE` copied verbatim to this folder) |
| Retrieved / vendored | 2026-09-26, by the originating lab's setup |
| Vetting | static security review (S1-S8) and quality rubric (Q1-Q6) by an independent reviewer track; Jev second opinion; review board (Academic Supervisor + Scientific Peer Reviewer profiles). Records: the originating lab's decision log, review records and skill-vetting folder (not shipped with the plugin) |
| Approved by | the user (References & Resources Specialist), 2026-09-26: "Install all 14" |

## Lab addenda applied
- added schemas/theme.schema.json (from plugins/figures/schemas/, unmodified; lib/theme.py loads it from ../schemas)
- added scripts/check_svg.py (from plugins/figures/agents/figure-qa-scripts/check_svg.py; theme/validator paths patched)
- added scripts/check_raster.py (from plugins/figures/agents/figure-qa-scripts/check_raster.py; theme/validator paths patched)
- added scripts/check_plot_script.py (from plugins/figures/agents/figure-qa-scripts/check_plot_script.py; theme/validator paths patched)
- added scripts/validate_fonts.py (from plugins/figures/skills/scientific-figure/scripts/, unmodified)
- added lib/theme.py (from plugins/figures/lib/, unmodified)
- added references/figure-qa-agent-procedure.md (copied from plugins/figures/agents/figure-qa.md; edited as logged below)
- replaced 'Dispatch' section with lab delegation (Claude Code / inline)
- updated engine paths in SKILL.md to vendored scripts/
- edited references/figure-qa-agent-procedure.md: plugin-root lookup replaced by skill-local paths
- edited references/figure-qa-procedure.md: plugin script lookup replaced by skill-local scripts/
- annotated references/iterate-loop.md (AI generation not installed) and replaced its Agent dispatch
- inserted the LAB ADDENDUM block at the top of SKILL.md
- added LICENSE (upstream repository license, verbatim)
- 2026-11-07 science-ultrapowers: Claude-Science-only overlay items removed (PDF-explorer, kernel paths, host skill-reader calls), Claude Code tool line added, skill cross-references renamed, project names and decision ids generalized
- 2026-11-07 science-ultrapowers: references/iterate-loop.md: other-harness sentences removed; references/figure-qa-procedure.md and references/figure-qa-agent-procedure.md: project name removed; scripts/check_svg.py: comment generalized; lib/theme.py and schemas/theme.schema.json: advisory image-generator model fields removed
- 2026-11-08 science-ultrapowers: line endings normalized from CRLF to LF (no content change), vendored hashes refreshed: references/figure-qa-agent-procedure.md, references/figure-qa-procedure.md, references/iterate-loop.md, scripts/check_plot_script.py, scripts/check_raster.py, scripts/check_svg.py
- 2026-11-08 science-ultrapowers: overlay runs python with -B (SKILL.md hash refreshed)
- 2026-11-08 science-ultrapowers: overlay retitled LAB ADDENDUM (binding), the standard's words (SKILL.md hash refreshed)
- 2026-11-08 science-ultrapowers: the lab's own lines in the body use the standard's paths and words (SKILL.md hash refreshed)

## File hashes (SHA-256, first 12 hex chars)
| File | Status | Upstream | Vendored |
|---|---|---|---|
| `LICENSE` | added | `` | `52c155c8e749` |
| `SKILL.md` | modified | `ed3e58bfe469` | `193aca2a885f` |
| `lib/theme.py` | added | `` | `77a61a048aff` |
| `references/figure-qa-agent-procedure.md` | added | `` | `d8aabcd669c8` |
| `references/figure-qa-procedure.md` | modified | `c35717f669b5` | `5a4f2c1a36f2` |
| `references/iterate-loop.md` | modified | `a4f2cff07dbf` | `7831baa8ea01` |
| `schemas/theme.schema.json` | added | `` | `564212f3330a` |
| `scripts/check_plot_script.py` | added | `` | `4fd18fddb8d9` |
| `scripts/check_raster.py` | added | `` | `1fb5ee12e2a2` |
| `scripts/check_svg.py` | added | `` | `27dd0aa333c9` |
| `scripts/validate_fonts.py` | added | `` | `a632bcbd9b98` |

To re-verify: download `https://github.com/neuromechanist/research-skills/archive/f0219bde233abb44d8a0c5d73f41ea27073e1493.zip` and compare the `unchanged` rows.
