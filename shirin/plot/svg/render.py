"""Lays out a Chart and writes it as an SVG string."""
import dataclasses
import itertools
import math
from typing import Dict, List, Optional, Tuple
from xml.sax.saxutils import escape

from ..config import FontSizes, Layout, TextColors
from ..config.colors import BACKGROUND_COLOR, DARK_MODE_COLORS, GRID_COLOR
from . import marks
from .chart import Axis, Chart, Text
from .fonts import cap_height, font_css, text_width
from .header import header_rows as build_header
from .marks import Scale
from .ticks import date_ticks, nice_ticks

PT_PER_INCH = 72
PX_PER_PT = 4 / 3
_CLIP_IDS = itertools.count()

Ticks = List[Tuple[float, str]]


def _limits(axis: Axis, values: List[float]) -> Tuple[float, float]:
    if axis.lim is not None:
        return axis.lim
    values = [v for v in values if v == v]
    if not values:
        raise ValueError("Chart has no data to scale the axis on")
    lo, hi = min(values), max(values)
    if lo == hi:
        lo, hi = lo - 0.5, hi + 0.5
    pad = (hi - lo) * Layout.AXIS_MARGIN
    return (lo if lo in axis.sticky else lo - pad, hi if hi in axis.sticky else hi + pad)


def _ticks(axis: Axis, lo: float, hi: float) -> Ticks:
    if not axis.visible:
        return []
    if axis.ticks is not None:
        labels = axis.tick_labels if axis.tick_labels is not None else [axis.formatter(t) for t in axis.ticks]
        ticks = list(zip(axis.ticks, labels))
    elif axis.dates:
        ticks = list(zip(*date_ticks(lo, hi, fmt=axis.date_format)))
    else:
        ticks = [(t, axis.formatter(t)) for t in nice_ticks(lo, hi)]
    low, high = min(lo, hi) - 1e-9, max(lo, hi) + 1e-9
    return [(t, label) for t, label in ticks if low <= t <= high]


def _scale(lo: float, hi: float, start: float, end: float) -> Scale:
    return lambda v: start + (v - lo) / (hi - lo) * (end - start)


def _shorten_crowded_labels(texts: List[Text], sx: Scale, sy: Scale) -> List[Text]:
    """Copies with short_text swapped in when side-by-side labels overlap; the chart stays untouched."""
    spans = sorted(marks.place(t, sx, sy)[2:4] for t in texts if t.short_text)
    if not any(right[0] - left[1] < Layout.DATALABEL_MIN_SPACE for left, right in zip(spans, spans[1:])):
        return texts
    return [dataclasses.replace(t, text=t.short_text) if t.short_text else t for t in texts]


def to_svg(chart: Chart, font: Optional[str] = None, dark_mode: bool = False) -> str:
    theme = DARK_MODE_COLORS if dark_mode else {}

    def color(c: str) -> str:
        return theme.get(c, c)

    x_lim, y_lim = _limits(chart.x, chart.data_values('x')), _limits(chart.y, chart.data_values('y'))
    x_ticks, y_ticks = _ticks(chart.x, *x_lim), _ticks(chart.y, *y_lim)
    tick_size = FontSizes.TICKS

    y_tick_width = max((text_width(label, tick_size) for _, label in y_ticks), default=0)
    y_label_width = cap_height(FontSizes.XYLABEL) + Layout.LABEL_GAP if chart.y.label else 0
    plot_left = Layout.PAD + y_label_width + (y_tick_width + Layout.TICK_GAP if y_tick_width else 0)
    plot_h = chart.plot_height * PT_PER_INCH
    fixed_width = chart.width is not None
    width = chart.width * PT_PER_INCH if fixed_width else plot_left + plot_h + Layout.PAD  # type: ignore[operator]
    plot_w = width - plot_left - Layout.PAD

    header_rows, plot_top = build_header(chart, width - 2 * Layout.PAD, color)

    # Data labels and the last x tick label may stick out of the plot area: make room for them.
    sx, sy = _scale(*x_lim, plot_left, plot_left + plot_w), _scale(*y_lim, plot_top + plot_h, plot_top)
    texts = _shorten_crowded_labels(chart.texts, sx, sy)
    boxes = [marks.place(t, sx, sy)[2:] for t in texts if t.text]
    if x_ticks and not chart.x.rotation:
        position, label = x_ticks[-1]
        boxes.append((0, sx(position) + text_width(label, tick_size) / 2, plot_top))
    right_overflow = max([0.0] + [box[1] - (plot_left + plot_w) for box in boxes])
    plot_top += max([0.0] + [plot_top - box[2] for box in boxes])
    if fixed_width:
        plot_w -= right_overflow
    else:
        width = max([width + right_overflow] + [row_width + 2 * Layout.PAD for row_width, _ in header_rows])
    sx, sy = _scale(*x_lim, plot_left, plot_left + plot_w), _scale(*y_lim, plot_top + plot_h, plot_top)
    plot_bottom = plot_top + plot_h
    header = [
        f'<g transform="translate({max(Layout.PAD, (width - w) / 2):.2f} 0)">{"".join(items)}</g>'
        for w, items in header_rows
    ]

    body: List[str] = []
    grid = f'stroke="{color(GRID_COLOR)}" stroke-width="{Layout.HAIRLINE}"'
    if chart.y.grid:
        body += [f'<line x1="{plot_left:.2f}" x2="{plot_left + plot_w:.2f}" y1="{sy(t):.2f}" y2="{sy(t):.2f}" {grid}/>' for t, _ in y_ticks]
    if chart.x.grid:
        body += [f'<line x1="{sx(t):.2f}" x2="{sx(t):.2f}" y1="{plot_top:.2f}" y2="{plot_bottom:.2f}" {grid}/>' for t, _ in x_ticks]
    body += [marks.wedge(dataclasses.replace(w, color=color(w.color)), sx, sy) for w in chart.wedges if w.end > w.start]
    clip_ids: Dict[int, str] = {}
    fades: List[str] = []  # drawn after every segment, else the next segment covers them
    for r in chart.rects:
        if not (r.width and r.height):
            continue
        rect = marks.rect(r, sx, sy)
        # Ids must be unique across every chart on the page, e.g. a notebook with many outputs.
        fade = marks.fade(r, sx, sy, f'fade{next(_CLIP_IDS)}') if r.fade_to is not None else ''
        if r.clip is not None:
            if id(r.clip) not in clip_ids:
                clip_ids[id(r.clip)] = f'clip{next(_CLIP_IDS)}'
                body.append(f'<clipPath id="{clip_ids[id(r.clip)]}">{marks.rect(r.clip, sx, sy)}</clipPath>')
            clip = f'<rect clip-path="url(#{clip_ids[id(r.clip)]})" '
            rect, fade = rect.replace('<rect ', clip, 1), fade.replace('<rect ', clip, 1)
        body.append(rect)
        fades.append(fade)
    body += fades
    body += [marks.area(line, sx, sy, plot_bottom, f'area{next(_CLIP_IDS)}') for line in chart.lines if line.fill]
    body += [marks.line(dataclasses.replace(line, color=color(line.color)), sx, sy) for line in chart.lines]
    body += [marks.dots(dataclasses.replace(dots, color=color(dots.color)), sx, sy) for dots in chart.dots]
    for t in texts:
        if t.text:
            x, baseline = marks.place(t, sx, sy)[:2]
            # Black/white labels sit on a bar or wedge and already contrast with it.
            text_color = t.color if t.color in (TextColors.BLACK, TextColors.WHITE) else color(t.color)
            body.append(marks.text(x, baseline, t.text, t.size, text_color, marks.ANCHOR[t.ha], alpha=t.alpha))

    if chart.y.label:
        # Rotated a quarter turn counterclockwise, so the baseline is the right edge of the text.
        x, y = Layout.PAD + cap_height(FontSizes.XYLABEL), plot_top + plot_h / 2
        body.append(
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{FontSizes.XYLABEL}" fill="{color(TextColors.BLACK)}" '
            f'text-anchor="middle" transform="rotate(-90 {x:.2f} {y:.2f})">{escape(chart.y.label)}</text>'
        )

    cap = cap_height(tick_size)
    body += [marks.text(plot_left - Layout.TICK_GAP, sy(t) + cap / 2, label, tick_size, color(TextColors.DARK_GREY), 'end')
             for t, label in y_ticks if label]
    bottom = plot_bottom
    labelled_x_ticks = [(t, label) for t, label in x_ticks if label]
    if labelled_x_ticks:
        tick_top = plot_bottom + Layout.TICK_GAP
        rotation = math.radians(chart.x.rotation)
        bottom = tick_top + max(text_width(label, tick_size) * math.sin(rotation) + cap * math.cos(rotation)
                                for _, label in labelled_x_ticks)
        for t, label in labelled_x_ticks:
            if chart.x.rotation:
                body.append(marks.text(sx(t), tick_top + cap / 2, label, tick_size, color(TextColors.DARK_GREY), 'end', rotate=chart.x.rotation))
            else:
                body.append(marks.text(sx(t), tick_top + cap, label, tick_size, color(TextColors.DARK_GREY), 'middle'))
    if chart.x.sub_labels:
        bottom += Layout.ROW_GAP
        body += [marks.text(sx(t), bottom + cap, label, tick_size, color(TextColors.DARK_GREY), 'middle') for t, label in chart.x.sub_labels]
        bottom += tick_size
    if chart.x.label:
        bottom += Layout.LABEL_GAP
        body.append(marks.text(plot_left + plot_w / 2, bottom + cap_height(FontSizes.XYLABEL), chart.x.label, FontSizes.XYLABEL, color(TextColors.BLACK), 'middle'))
        bottom += FontSizes.XYLABEL
    height = bottom + Layout.PAD

    return ''.join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width * PX_PER_PT:.0f}" height="{height * PX_PER_PT:.0f}" '
        f'viewBox="0 0 {width:.2f} {height:.2f}">',
        f'<style>{font_css(font, bool(chart.title))}</style>',
        f'<rect width="100%" height="100%" rx="{Layout.CORNER_RADIUS}" fill="{color(BACKGROUND_COLOR)}"/>',
        *header,
        *body,
        '</svg>',
    ])
