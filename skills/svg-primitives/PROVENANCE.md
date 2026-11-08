# PROVENANCE: svg-primitives

| Field | Value |
|---|---|
| Upstream repository | https://github.com/neuromechanist/research-skills |
| Pinned commit | `f0219bde233abb44d8a0c5d73f41ea27073e1493` |
| Upstream path | `plugins/figures/skills/svg-primitives` |
| Licence | BSD-3-Clause (upstream `LICENSE` copied verbatim to this folder) |
| Retrieved / vendored | 2026-09-26, by the originating lab's setup |
| Vetting | static security review (S1-S8) and quality rubric (Q1-Q6) by an independent reviewer track; Jev second opinion; review board (Academic Supervisor + Scientific Peer Reviewer profiles). Records: the originating lab's decision log, review records and skill-vetting folder (not shipped with the plugin) |
| Approved by | the user (References & Resources Specialist), 2026-09-26: "Install all 14" |

## Lab addenda applied
- removed examples/.gitignore (git housekeeping file; the skill store rejects dotfile paths)
- removed scripts/.gitignore (git housekeeping file; the skill store rejects dotfile paths)
- removed tests/.gitignore (git housekeeping file; the skill store rejects dotfile paths)
- edited scripts/svg_primitives/metrics.py: added the Windows font folders to _FONT_SEARCH_DIRS (upstream searched macOS/Linux folders only)
- inserted the LAB ADDENDUM block at the top of SKILL.md
- added LICENSE (upstream repository licence, verbatim)
- 2026-11-07 science-ultrapowers: Claude-Science-only overlay items removed (PDF-explorer, kernel paths, host skill-reader calls), Claude Code tool line added, skill cross-references renamed, project names and decision ids generalised
- 2026-11-07 science-ultrapowers: scripts/svg_primitives/metrics.py: comment generalised
- 2026-11-08 science-ultrapowers: line endings normalised from CRLF to LF (no content change), vendored hashes refreshed: scripts/svg_primitives/metrics.py
- 2026-11-08 science-ultrapowers: overlay runs python with -B (SKILL.md hash refreshed)
- 2026-11-08 science-ultrapowers: overlay retitled LAB ADDENDUM (binding), the standard's words (SKILL.md hash refreshed)

## File hashes (SHA-256, first 12 hex chars)
| File | Status | Upstream | Vendored |
|---|---|---|---|
| `LICENSE` | added | `` | `52c155c8e749` |
| `SKILL.md` | modified | `419db54fe526` | `efb9021d7fc1` |
| `examples/bracketed_grouping.py` | unchanged | `1b62db8cae36` | `1b62db8cae36` |
| `examples/eeg_pipeline.py` | unchanged | `c3ede85460a8` | `c3ede85460a8` |
| `examples/orthogonal_flowchart.py` | unchanged | `4804232436fd` | `4804232436fd` |
| `examples/stress_test.py` | unchanged | `d9bc8195b66c` | `d9bc8195b66c` |
| `examples/validation_demo.py` | unchanged | `6dd4ab7dd200` | `6dd4ab7dd200` |
| `references/api.md` | unchanged | `548fcdd2e3f0` | `548fcdd2e3f0` |
| `references/design.md` | unchanged | `403572fb9092` | `403572fb9092` |
| `references/font-metrics.md` | unchanged | `59fdf96a6d40` | `59fdf96a6d40` |
| `scripts/svg_primitives/__init__.py` | unchanged | `c21b04ca78ab` | `c21b04ca78ab` |
| `scripts/svg_primitives/annotations.py` | unchanged | `0163e34789be` | `0163e34789be` |
| `scripts/svg_primitives/arrows.py` | unchanged | `8ffbd9c3f756` | `8ffbd9c3f756` |
| `scripts/svg_primitives/canvas.py` | unchanged | `61e1c9e38a9f` | `61e1c9e38a9f` |
| `scripts/svg_primitives/geometry.py` | unchanged | `f776648a881f` | `f776648a881f` |
| `scripts/svg_primitives/groups.py` | unchanged | `5d2d36595fa1` | `5d2d36595fa1` |
| `scripts/svg_primitives/metrics.py` | modified | `1874cc983aa8` | `953afb915b6a` |
| `scripts/svg_primitives/shapes.py` | unchanged | `7a34fb8f1baf` | `7a34fb8f1baf` |
| `scripts/svg_primitives/validation.py` | unchanged | `918a7d4c6e3d` | `918a7d4c6e3d` |
| `tests/conftest.py` | unchanged | `dc903ab089f7` | `dc903ab089f7` |
| `tests/test_e2e.py` | unchanged | `8789ab95773c` | `8789ab95773c` |
| `examples/.gitignore` | removed | `a888b9df8940` | n/a |
| `scripts/.gitignore` | removed | `32dae3052f33` | n/a |
| `tests/.gitignore` | removed | `09b8bff34979` | n/a |

To re-verify: download `https://github.com/neuromechanist/research-skills/archive/f0219bde233abb44d8a0c5d73f41ea27073e1493.zip` and compare the `unchanged` rows.
