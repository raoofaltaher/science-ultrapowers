#!/usr/bin/env python3
"""Draw the flow diagram of a literature search or a trial as one standalone SVG file.

    flow_diagram.py <counts.json> --style prisma2020|consort --out <file.svg>

The counts file holds the numbers of the search log or of the trial. The script checks that the
counts add up from box to box, then draws the boxes. The two styles are:
- prisma2020: the flow diagram of a search, in the form of
  Preferred Reporting Items for Systematic reviews and Meta-Analyses (PRISMA) 2020
- consort: the flow diagram of a trial, in the form of
  Consolidated Standards of Reporting Trials (CONSORT)

PRISMA 2020 counts:
    {"identified": {"databases": n, "registers": n, "other": n}, "duplicates_removed": n,
     "screened": n, "excluded_screening": n, "sought": n, "not_retrieved": n, "assessed": n,
     "excluded_assessed": {"<reason>": n, ...}, "included": n}
CONSORT counts:
    {"assessed": n, "excluded": {"<reason>": n, ...}, "randomized": n,
     "arms": [{"name": "<text>", "allocated": n, "received": n, "lost": n, "discontinued": n,
               "analyzed": n, "excluded_analysis": n}, ...]}

Exit codes: 0 when the file is written, 1 when the counts do not add up (the message names the
box), 2 for a usage error or a counts file that cannot be read.
"""
import argparse
import json
import sys
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

STYLES = ("prisma2020", "consort")
SOURCES = ("databases", "registers", "other")
PRISMA_KEYS = (
    "duplicates_removed", "screened", "excluded_screening", "sought", "not_retrieved",
    "assessed", "included",
)
ARM_KEYS = ("allocated", "received", "lost", "discontinued", "analyzed", "excluded_analysis")

FONT = "Helvetica, Arial, sans-serif"
FONT_SIZE = 11
LINE_HEIGHT = 15
PAD = 8
GAP = 34
MARGIN = 20
COLUMN_WIDTH = 270
SIDE_WIDTH = 290
ARM_WIDTH = 220
ARM_GAP = 20


class UsageError(Exception):
    """A usage error or an unreadable counts file: exit 2."""


# ---------------------------------------------------------------- the arithmetic checks


def _count(mapping, key, problems, prefix=""):
    """Return the whole number at mapping[key], or None after adding a problem."""
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        problems.append(f"{prefix}{key}: expected a whole number of 0 or more, got {value!r}")
        return None
    return value


def _reasons(mapping, key, problems):
    """Return the sum of a reason-to-count object, or None after adding a problem."""
    reasons = mapping.get(key)
    if not isinstance(reasons, dict):
        problems.append(f"{key}: expected an object of reason and count")
        return None
    total = 0
    ok = True
    for reason, value in reasons.items():
        n = _count(reasons, reason, problems, f"{key}.")
        if n is None:
            ok = False
        else:
            total += n
    return total if ok else None


def check_prisma(counts) -> list:
    """Return one message for each PRISMA 2020 box whose count does not follow from the box before."""
    problems = []
    identified = counts.get("identified")
    if not isinstance(identified, dict):
        return ["identified: expected an object with databases, registers and other"]
    parts = [_count(identified, key, problems, "identified.") for key in SOURCES]
    values = {key: _count(counts, key, problems) for key in PRISMA_KEYS}
    reasons_total = _reasons(counts, "excluded_assessed", problems)
    if problems:
        return problems
    total = sum(parts)
    checks = (
        ("screened", total - values["duplicates_removed"],
         f"identified {total} minus duplicates removed {values['duplicates_removed']}"),
        ("sought", values["screened"] - values["excluded_screening"],
         f"screened {values['screened']} minus excluded at screening {values['excluded_screening']}"),
        ("assessed", values["sought"] - values["not_retrieved"],
         f"sought {values['sought']} minus not retrieved {values['not_retrieved']}"),
        ("included", values["assessed"] - reasons_total,
         f"assessed {values['assessed']} minus excluded after assessment {reasons_total}"),
    )
    for name, expected, rule in checks:
        if values[name] != expected:
            problems.append(f"{name}: expected {expected} ({rule}), got {values[name]}")
    return problems


def check_consort(counts) -> list:
    """Return one message for each CONSORT box whose count does not follow from the box before."""
    problems = []
    assessed = _count(counts, "assessed", problems)
    randomized = _count(counts, "randomized", problems)
    excluded_total = _reasons(counts, "excluded", problems)
    arms = counts.get("arms")
    if not isinstance(arms, list) or not arms:
        problems.append("arms: expected a list with at least one arm")
        return problems
    arm_values = []
    for i, arm in enumerate(arms, start=1):
        if not isinstance(arm, dict) or not isinstance(arm.get("name"), str) or not arm["name"].strip():
            problems.append(f"arms[{i}].name: expected a name")
            continue
        prefix = f"arm {arm['name']}: "
        arm_values.append((arm["name"], {key: _count(arm, key, problems, prefix) for key in ARM_KEYS}))
    if problems:
        return problems
    expected = assessed - excluded_total
    if randomized != expected:
        problems.append(
            f"randomized: expected {expected} (assessed {assessed} minus excluded {excluded_total}), got {randomized}"
        )
    allocated = sum(v["allocated"] for _, v in arm_values)
    if allocated != randomized:
        problems.append(f"randomized: the arms allocate {allocated}, expected {randomized}")
    for name, v in arm_values:
        expected = v["received"] - v["lost"] - v["discontinued"] - v["excluded_analysis"]
        if v["analyzed"] != expected:
            problems.append(
                f"analyzed in arm {name}: expected {expected} (received {v['received']} minus lost "
                f"{v['lost']} minus discontinued {v['discontinued']} minus excluded from analysis "
                f"{v['excluded_analysis']}), got {v['analyzed']}"
            )
    return problems


# ---------------------------------------------------------------- the drawing


class Canvas:
    """Collects SVG elements; boxes are lists of text lines, the first line in bold."""

    def __init__(self):
        self.parts = []

    def box(self, x, y, width, lines):
        """Draw a box at (x, y) and return its height."""
        chars = max(10, int((width - 2 * PAD) / (FONT_SIZE * 0.56)))
        wrapped = []
        for line in lines:
            wrapped.extend(textwrap.wrap(line, chars) or [""])
        height = 2 * PAD + LINE_HEIGHT * len(wrapped) - 4
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#ffffff" stroke="#333333" stroke-width="1"/>'
        )
        for i, line in enumerate(wrapped):
            weight = ' font-weight="bold"' if i == 0 else ""
            self.parts.append(
                f'<text x="{x + PAD}" y="{y + PAD + 10 + i * LINE_HEIGHT}" font-family="{FONT}" '
                f'font-size="{FONT_SIZE}"{weight}>{escape(line)}</text>'
            )
        return height

    def line(self, x1, y1, x2, y2, arrow=False):
        end = ' marker-end="url(#arrow)"' if arrow else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333333" stroke-width="1"{end}/>'
        )

    def svg(self, width, height, title):
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" aria-label="{escape(title)}">'
            f"<title>{escape(title)}</title>"
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            'markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#333333"/></marker></defs>'
            f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>'
        )
        return head + "".join(self.parts) + "</svg>\n"


def _reason_lines(heading, reasons):
    lines = [heading]
    lines.extend(f"{reason} (n = {n})" for reason, n in reasons.items())
    return lines


def render_prisma(counts) -> str:
    ident = counts["identified"]
    total = sum(ident[k] for k in SOURCES)
    rows = [
        (
            ["Records identified from:", f"Databases (n = {ident['databases']})",
             f"Registers (n = {ident['registers']})", f"Other sources (n = {ident['other']})"],
            ["Records removed before screening:",
             f"Duplicate records removed (n = {counts['duplicates_removed']})"],
        ),
        (
            [f"Records screened (n = {counts['screened']})"],
            [f"Records excluded (n = {counts['excluded_screening']})"],
        ),
        (
            [f"Reports sought for retrieval (n = {counts['sought']})"],
            [f"Reports not retrieved (n = {counts['not_retrieved']})"],
        ),
        (
            [f"Reports assessed for eligibility (n = {counts['assessed']})"],
            _reason_lines("Reports excluded:", counts["excluded_assessed"]) if counts["excluded_assessed"]
            else ["Reports excluded:", "none"],
        ),
        ([f"Studies included in review (n = {counts['included']})"], None),
    ]
    canvas = Canvas()
    width = MARGIN * 2 + COLUMN_WIDTH + 40 + SIDE_WIDTH
    side_x = MARGIN + COLUMN_WIDTH + 40
    y = MARGIN
    previous_bottom = None
    for main, side in rows:
        if previous_bottom is not None:
            canvas.line(MARGIN + COLUMN_WIDTH // 2, previous_bottom, MARGIN + COLUMN_WIDTH // 2, y, arrow=True)
        main_height = canvas.box(MARGIN, y, COLUMN_WIDTH, main)
        row_height = main_height
        if side:
            side_height = canvas.box(side_x, y, SIDE_WIDTH, side)
            arrow_y = y + min(main_height, side_height) // 2
            canvas.line(MARGIN + COLUMN_WIDTH, arrow_y, side_x, arrow_y, arrow=True)
            row_height = max(main_height, side_height)
        previous_bottom = y + main_height
        y += row_height + GAP
    height = y - GAP + MARGIN
    return canvas.svg(width, height, f"PRISMA 2020 flow diagram: {total} records identified")


def render_consort(counts) -> str:
    arms = counts["arms"]
    n = len(arms)
    width = max(MARGIN * 2 + n * ARM_WIDTH + (n - 1) * ARM_GAP, MARGIN * 2 + COLUMN_WIDTH + 40 + SIDE_WIDTH)
    block = COLUMN_WIDTH + 40 + SIDE_WIDTH
    top_x = (width - block) // 2
    center = top_x + COLUMN_WIDTH // 2
    side_x = top_x + COLUMN_WIDTH + 40
    canvas = Canvas()
    y = MARGIN
    assessed_height = canvas.box(top_x, y, COLUMN_WIDTH, [f"Assessed for eligibility (n = {counts['assessed']})"])
    excluded_lines = _reason_lines(f"Excluded (n = {sum(counts['excluded'].values())})", counts["excluded"])
    side_height = canvas.box(side_x, y, SIDE_WIDTH, excluded_lines)
    arrow_y = y + min(assessed_height, side_height) // 2
    canvas.line(top_x + COLUMN_WIDTH, arrow_y, side_x, arrow_y, arrow=True)
    bottom = y + assessed_height
    y += max(assessed_height, side_height) + GAP
    canvas.line(center, bottom, center, y, arrow=True)
    rand_height = canvas.box(top_x, y, COLUMN_WIDTH, [f"Randomized (n = {counts['randomized']})"])
    bottom = y + rand_height
    bus_y = bottom + GAP // 2
    y = bottom + GAP
    arm_x = [MARGIN + i * (ARM_WIDTH + ARM_GAP) for i in range(n)]
    arm_center = [x + ARM_WIDTH // 2 for x in arm_x]
    canvas.line(center, bottom, center, bus_y)
    canvas.line(min(arm_center + [center]), bus_y, max(arm_center + [center]), bus_y)
    columns = []
    for arm in arms:
        columns.append([
            [f"Allocated to {arm['name']} (n = {arm['allocated']})"],
            [f"Received allocated intervention (n = {arm['received']})"],
            [f"Lost to follow-up (n = {arm['lost']})"],
            [f"Discontinued intervention (n = {arm['discontinued']})"],
            [f"Excluded from analysis (n = {arm['excluded_analysis']})"],
            [f"Analyzed (n = {arm['analyzed']})"],
        ])
    for i in range(n):
        canvas.line(arm_center[i], bus_y, arm_center[i], y, arrow=True)
    for row in range(len(columns[0])):
        heights = []
        for i in range(n):
            heights.append(canvas.box(arm_x[i], y, ARM_WIDTH, columns[i][row]))
        row_height = max(heights)
        if row < len(columns[0]) - 1:
            for i in range(n):
                canvas.line(arm_center[i], y + heights[i], arm_center[i], y + row_height + GAP, arrow=True)
        y += row_height + GAP
    height = y - GAP + MARGIN
    return canvas.svg(width, height, f"CONSORT flow diagram: {counts['randomized']} randomized")


def render(counts, style) -> str:
    if style == "prisma2020":
        return render_prisma(counts)
    return render_consort(counts)


# ---------------------------------------------------------------- the command


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="flow_diagram.py", description="Draw a PRISMA 2020 or CONSORT flow diagram from counts."
    )
    parser.add_argument("counts", help="the counts file (JSON)")
    parser.add_argument("--style", required=True, choices=STYLES)
    parser.add_argument("--out", required=True, help="the SVG file to write")
    args = parser.parse_args(argv)  # a usage error exits 2
    try:
        try:
            counts = json.loads(Path(args.counts).read_text(encoding="utf-8"))
        except (OSError, ValueError) as err:
            raise UsageError(f"cannot read the counts file {args.counts}: {err}")
        if not isinstance(counts, dict):
            raise UsageError("the counts file must hold one JSON object")
    except UsageError as err:
        print(f"flow_diagram: {err}", file=sys.stderr)
        return 2
    problems = check_prisma(counts) if args.style == "prisma2020" else check_consort(counts)
    if problems:
        for problem in problems:
            print(f"flow_diagram: {problem}", file=sys.stderr)
        return 1
    Path(args.out).write_text(render(counts, args.style), encoding="utf-8", newline="\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
