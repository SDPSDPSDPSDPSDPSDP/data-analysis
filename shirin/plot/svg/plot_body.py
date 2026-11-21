"""SVG markup for every data mark of a chart: wedges, bars, areas, lines, dots and data labels."""

import dataclasses
import itertools
from typing import Callable

from ..config import Layout
from ..config.colors import BACKGROUND_COLOR
from . import marks
from .chart import Chart, Text, Wedge
from .fonts import wrap_text
from .marks import Scale

_CLIP_IDS = itertools.count()


def _wrapped(t: Text) -> Text:
    if t.wrap_width is None:
        return t
    # An empty line wraps to no lines; keep it so blank lines in the text stay.
    lines = [line for part in t.text.split("\n") for line in (wrap_text(part, t.size, t.wrap_width) or [""])]
    return dataclasses.replace(t, text="\n".join(lines), wrap_width=None)


def stack_texts(texts: list[Text]) -> list[Text]:
    """Copies with wrap_width texts wrapped and each `above` pair centered on its point: the lower text moves down,
    the upper one sits Layout.SLICE_LABEL_GAP above it.
    """
    out: dict[int, Text] = {id(t): _wrapped(t) for t in texts}
    for t in texts:
        if t.above is None:
            continue
        upper, lower = out[id(t)], out[id(t.above)]
        lower_dy = -(marks.block_height(upper) + Layout.SLICE_LABEL_GAP) / 2
        out[id(t.above)] = dataclasses.replace(lower, dy=lower_dy)
        upper_dy = lower_dy + marks.block_height(lower) / 2 + Layout.SLICE_LABEL_GAP
        out[id(t)] = dataclasses.replace(upper, va="bottom", dy=upper_dy, above=None)
    return [out[id(t)] for t in texts]


def shorten_crowded_labels(texts: list[Text], sx: Scale, sy: Scale) -> list[Text]:
    """Copies with short_text swapped in when side-by-side labels overlap; the chart stays untouched."""
    spans = sorted(marks.place(t, sx, sy)[2:4] for t in texts if t.short_text)
    gaps = (right[0] - left[1] for left, right in zip(spans, spans[1:]))
    if not any(gap < Layout.DATALABEL_MIN_SPACE for gap in gaps):
        return texts
    return [dataclasses.replace(t, text=t.short_text) if t.short_text else t for t in texts]


def place_point_labels(texts: list[Text], sx: Scale, sy: Scale) -> list[Text]:
    """Copies of below-right point labels moved above-right where their line falls to the right on screen.

    Decided on screen, not in data, because a flipped axis (x_limits=(1, 0)) turns a rising line into a falling one.
    """
    placed = []
    for t in texts:
        # Screen y grows downward: both deltas sharing a sign means the line runs down and right.
        falls = t.slope is not None and (sx(t.x + 1) - sx(t.x)) * (sy(t.y + t.slope) - sy(t.y)) > 0
        placed.append(dataclasses.replace(t, va="bottom", dy=-t.dy) if falls else t)
    return placed


def draw_marks(
    chart: Chart, texts: list[Text], sx: Scale, sy: Scale, plot_bottom: float, color: Callable[[str], str]
) -> list[str]:
    body: list[str] = []
    # Data colors are never themed: a user's white slice must stay white, not turn into the background.
    body += [marks.wedge(w, sx, sy) for w in chart.wedges if w.end > w.start]
    if chart.donut_hole:
        body.append(marks.wedge(Wedge(0, 1, color(BACKGROUND_COLOR), radius=chart.donut_hole), sx, sy))
    clip_ids: dict[int, str] = {}
    for r in chart.rects:
        if not (r.width and r.height):
            continue
        rect = marks.rect(r, sx, sy)
        if r.clip is not None:
            if id(r.clip) not in clip_ids:
                # Ids must be unique across every chart on the page, e.g. a notebook with many outputs.
                clip_ids[id(r.clip)] = f"clip{next(_CLIP_IDS)}"
                body.append(f'<clipPath id="{clip_ids[id(r.clip)]}">{marks.rect(r.clip, sx, sy)}</clipPath>')
            clip = f'<rect clip-path="url(#{clip_ids[id(r.clip)]})" '
            rect = rect.replace("<rect ", clip, 1)
        body.append(rect)
    body += [marks.area(line, sx, sy, plot_bottom, f"area{next(_CLIP_IDS)}") for line in chart.lines if line.fill]
    body += [marks.line(line, sx, sy) for line in chart.lines]
    body += [marks.dots(dots, sx, sy) for dots in chart.dots]
    for t in texts:
        if t.text:
            x, baseline = marks.place(t, sx, sy)[:2]
            text_color = t.color if t.keep_color else color(t.color)
            for i, (title, line) in enumerate(zip(marks.line_titles(t), t.text.split("\n"))):
                line_baseline = baseline + i * marks.line_step(t.size)
                body.append(
                    marks.text(
                        x,
                        line_baseline,
                        line,
                        t.size,
                        text_color,
                        marks.ANCHOR[t.ha],
                        alpha=t.alpha,
                        title=title,
                    )
                )
    return body
