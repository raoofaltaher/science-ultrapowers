---
name: figure-qa
description: Use this skill to QA a scientific figure for journal compliance, alignment, palette correctness, and text legibility. Triggers on "QA this figure", "check this figure", "review my figure", "is this figure paper-ready", "validate figure", "check the text in this figure", or when invoked after a figures skill produces output (unless the caller passes no-qa). Dispatches on input type (SVG, raster PNG/JPG/TIFF, Python plot script, or composed-figure directory), runs the programmatic checks including OCR of expected strings and palette compliance against the project theme, adds a vision rubric pass, and returns a report with a machine-readable JSON verdict that drives the generate, QA, fix loop.
version: 0.2.0
---
> **LAB ADDENDUM (binding).** Adopted third-party skill: `neuromechanist/research-skills` @ `f0219bde233a` (BSD-3-Clause). Where anything below conflicts with the lab's rules, the lab's rules win.
>
> 1. **Evidence rule wins.** Facts and citations come only through `science-ultrapowers:verifying-evidence-by-doi` (peer-reviewed, DOI matched through Crossref, full text read, evidence record). Never cite from web search, model memory or preprints.
> 2. **Records.** Numbers and results come only from `science-ultrapowers:recording-findings` (FND-ids, `KEY_RESULTS.md`); work moves through the `science-ultrapowers:running-the-lab` stage approvals.
> 3. **No pre-approved tools.** Any upstream `allowed-tools` grant was removed from this copy, so normal permission prompts apply.
> 4. **Not installed in this lab:** `agent-fanout` -> `science-ultrapowers:running-the-lab` (task assignments + delegation); `ai-full-figure` -> not installed (sends prompts to external image APIs); `plot-styling` -> `figure-bible`; `scientific-figure` -> `figure-bible` + `svg-primitives` (+ adopted `validate_fonts.py` in `figure-qa`); `svg-figure` -> `svg-primitives`; `transparent-icons` -> not installed (external image APIs).
> 5. **Tools in Claude Code:** read PDFs with the file reader, edit with the file tools, run bundled scripts with `python -B "${CLAUDE_PLUGIN_ROOT}/skills/figure-qa/scripts/<script>"`; packages the figure and poster skills need live in the project's `.venv-lab-skills` (see `science-ultrapowers:initializing-a-research-lab`).
> 6. **Skill-specific:** The deterministic engine (`scripts/check_svg.py`, `check_raster.py`, `check_plot_script.py`), the theme library (`lib/theme.py`) and the font validator (`scripts/validate_fonts.py`, from `scientific-figure`) are adopted into this folder with paths patched. Needs: lxml, svgelements, shapely, pillow, pytesseract, jsonschema, plus the Tesseract OCR binary; if OCR reports a missing `eng.traineddata`, set `TESSDATA_PREFIX` to the `share\tessdata` folder of the environment that provides Tesseract. `schemas/theme.schema.json` is adopted too. Journals without a profile (e.g. Springer Nature): use `generic` and check the journal's artwork guidelines.
>
> Provenance, license and change log: `PROVENANCE.md`.


# Figure QA

Routes a scientific figure to an independent, fresh-context QA reviewer that detects the input type, runs the deterministic checks (fonts, palette, geometry, alpha, resolution, rendered text) with the helper scripts, and adds a vision-language model (VLM) rubric judgment for the aesthetic dimensions.
This skill is a thin dispatcher: the detection logic, exit-code contract, VLM rubric, report shape, and the iterate loop all live in `references/`, and the deterministic engine lives in this folder's `scripts/` (vendored by the lab overlay).

## When to use

Activate when a figure needs a journal-submission QA pass, or after a figures skill (`figures:scientific-figure`, `figures:svg-figure`, `figures:svg-primitives`, `figures:transparent-icons`, `figures:ai-full-figure`, `figures:plot-styling`) produces output, unless the caller passes `no-qa`.

## What to pass to the reviewer

Every dispatch carries the same briefing, so the right checks run:

- the figure path and, when known, the input type
- the target journal (`nature`, `science`, `cell`, `pnas`, `poster`, `slide`, or `generic`)
- the theme path (`figures/theme.json`) so palette compliance is judged against the project bible rather than a fixed allow-list
- every verbatim string the figure was asked to render (titles, panel letters, labels); without this list the raster text check is silently off
- the physical width in millimetres for raster inputs, so text height converts to points

## Why a fresh-context reviewer

A QA pass is more trustworthy from a reviewer that did not just author the figure.
Run it in a separate context and pass only the briefing above.
On tools without subagents, run the procedure inline.
For several candidates, issue one dispatch per candidate in a single message so they run in parallel on the Sonnet tier.

## Dispatch (lab overlay: replaces the upstream dispatch branches)

Run the reviewer in a **fresh context** and pass only framing (figure file paths, target journal, mode), never the authoring rationale. The reviewer reads `references/figure-qa-agent-procedure.md` from this skill's folder before producing findings.

- **Claude Code:** delegate to the academic-reviewer or research-engineer (not the figure's author) subagent with the same framing; for panel mode issue one Agent call per lens in a single message, then one synthesis call.
- **Inline fallback:** the figure's author may run the deterministic checks as a self-check before submitting; the gate check (G5/G6) is run by a non-author. Use it when delegation is unavailable or the user wants an in-thread check, following the procedure file directly.

Independence: nobody reviews their own work (`science-ultrapowers:running-the-lab`). Log the result in `research_lab/04_reviews/` (`REVIEW_LOG.md`).

## The report and the loop

The report keeps its markdown sections and ends with one fenced JSON block: `status` (`ship`, `revise`, `block`), `findings[]` each with `check`, `severity`, `message`, `action` (`regenerate`, `edit`, `overlay`, `rescale`, `recolor`, `none`) and a `hint`, plus `measurements` and the five VLM scores.
Generation skills branch on that block.
`references/iterate-loop.md` defines the generate, QA, fix, regenerate loop (N candidates in parallel, one targeted change per iteration, stop at `ship` or after three iterations) that `figures:ai-full-figure` follows.

## The brain (do not duplicate into dispatch or agent shells)

- `references/figure-qa-procedure.md`: no-qa opt-out, script location, type detection, per-branch checks including the raster text check and theme palette compliance, exit-code contract, VLM rubric, the exact report shape, and the finding-to-action table.
- `references/iterate-loop.md`: the candidate, QA, fix loop with its worker briefing and stopping conditions.
- `scripts/check_{svg,raster,plot_script}.py` (vendored into this folder by the lab overlay): the deterministic engine. `check_raster.py --json --expect-text "..." --palette figures/theme.json --width-mm 89 --journal nature` is the text and palette check; `check_svg.py --json --palette figures/theme.json` covers SVG geometry, fonts, and palette.
