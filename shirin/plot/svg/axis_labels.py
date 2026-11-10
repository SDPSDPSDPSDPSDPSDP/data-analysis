"""Tick labels, their descriptions and axis labels around the plot area."""
import math
from typing import List, Tuple
from xml.sax.saxutils import escape

from ..config import FontSizes, Layout, TextColors
from . import marks
from .axis import description_lines, tick_color
from .chart import Chart
from .fonts import cap_height, text_width
from .frame import Color, Frame

SUBLABEL_CLASS = 's'  # tighter letter spacing, see font_css


def _description_height(lines: List[str]) -> float:
    n = len(lines)
    return n * cap_height(FontSizes.DESCRIPTION) + max(n - 1, 0) * Layout.DESCRIPTION_LINE_GAP


def _description(x: float, top: float, lines: List[str], anchor: str, color: str) -> List[str]:
    """Wrapped description lines, the first one's cap top at top."""
    line_height = cap_height(FontSizes.DESCRIPTION) + Layout.DESCRIPTION_LINE_GAP
    first_baseline = top + cap_height(FontSizes.DESCRIPTION)
    return [marks.text(x, first_baseline + i * line_height, line, FontSizes.DESCRIPTION, color, anchor)
            for i, line in enumerate(lines)]


def _rotated_label(x: float, y: float, text: str, size: float, fill: str, css_class: str = '') -> str:
    """Rotated a quarter turn counterclockwise, so the baseline x is the right edge of the text."""
    class_attr = f' class="{css_class}"' if css_class else ''
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}"{class_attr} '
        f'text-anchor="middle" transform="rotate(-90 {x:.2f} {y:.2f})">{escape(text)}</text>'
    )


def y_axis(chart: Chart, frame: Frame, color: Color) -> List[str]:
    items: List[str] = []
    x, y = float(Layout.PAD), frame.top + frame.plot_h / 2
    if chart.y.label:
        x += cap_height(FontSizes.XYLABEL)
        items.append(_rotated_label(x, y, chart.y.label, FontSizes.XYLABEL, color(TextColors.BLACK)))
    if chart.y.sublabel:
        x += (Layout.SUBLABEL_GAP if chart.y.label else 0) + cap_height(FontSizes.XYSUBLABEL)
        sublabel_color = color(TextColors.LIGHT_GREY)
        items.append(_rotated_label(x, y, chart.y.sublabel, FontSizes.XYSUBLABEL, sublabel_color, SUBLABEL_CLASS))
    cap = cap_height(FontSizes.TICKS)
    x = frame.left - Layout.TICK_GAP
    y_tick_color = color(tick_color(chart.y, chart.x))
    description_color = color(TextColors.LIGHT_GREY)
    for t, label in frame.y_ticks:
        if not label:
            continue
        lines = description_lines(chart.y, t)
        if not lines:
            items.append(marks.text(x, frame.sy(t) + cap / 2, label, FontSizes.TICKS, y_tick_color, 'end'))
            continue
        # Label and description together are centered on the tick.
        top = frame.sy(t) - (cap + Layout.DESCRIPTION_GAP + _description_height(lines)) / 2
        items.append(marks.text(x, top + cap, label, FontSizes.TICKS, y_tick_color, 'end'))
        items += _description(x, top + cap + Layout.DESCRIPTION_GAP, lines, 'end', description_color)
    return items


def x_axis(chart: Chart, frame: Frame, color: Color) -> Tuple[List[str], float]:
    """Tick labels, sub labels (e.g. years under months) and axis label below the plot, plus their bottom edge."""
    tick_size, cap, sx = FontSizes.TICKS, cap_height(FontSizes.TICKS), frame.sx
    items: List[str] = []
    bottom = frame.bottom
    labelled_ticks = [(t, label) for t, label in frame.x_ticks if label]
    if labelled_ticks:
        tick_top = frame.bottom + Layout.TICK_GAP
        rotation = math.radians(chart.x.rotation)

        def rotated_height(label: str) -> float:
            return text_width(label, tick_size) * math.sin(rotation) + cap * math.cos(rotation)

        bottom = tick_top + max(rotated_height(label) for _, label in labelled_ticks)
        x_tick_color = color(tick_color(chart.x, chart.y))
        for t, label in labelled_ticks:
            if chart.x.rotation:
                items.append(marks.text(sx(t), tick_top + cap / 2, label, tick_size, x_tick_color, 'end', rotate=chart.x.rotation))
            else:
                items.append(marks.text(sx(t), tick_top + cap, label, tick_size, x_tick_color, 'middle'))
    if chart.x.descriptions:
        if chart.x.rotation:
            raise ValueError("Tick descriptions do not work with rotated x tick labels")
        bottom += Layout.DESCRIPTION_GAP
        description_color = color(TextColors.LIGHT_GREY)
        shown_lines = [(t, description_lines(chart.x, t, sx)) for t, _ in labelled_ticks]
        for t, lines in shown_lines:
            items += _description(sx(t), bottom, lines, 'middle', description_color)
        bottom += max(_description_height(lines) for _, lines in shown_lines)
    if chart.x.sub_labels:
        bottom += Layout.ROW_GAP
        sub_label_color = color(TextColors.DARK_GREY)
        items += [marks.text(sx(t), bottom + cap, label, tick_size, sub_label_color, 'middle')
                  for t, label in chart.x.sub_labels]
        bottom += tick_size
    center = frame.left + frame.plot_w / 2
    if chart.x.label:
        bottom += Layout.LABEL_GAP
        label_baseline = bottom + cap_height(FontSizes.XYLABEL)
        label_color = color(TextColors.BLACK)
        items.append(marks.text(center, label_baseline, chart.x.label, FontSizes.XYLABEL, label_color, 'middle'))
        bottom += FontSizes.XYLABEL
    if chart.x.sublabel:
        bottom += Layout.SUBLABEL_GAP if chart.x.label else Layout.LABEL_GAP
        sublabel_baseline = bottom + cap_height(FontSizes.XYSUBLABEL)
        sublabel_color = color(TextColors.LIGHT_GREY)
        items.append(marks.text(
            center, sublabel_baseline, chart.x.sublabel, FontSizes.XYSUBLABEL, sublabel_color, 'middle',
            css_class=SUBLABEL_CLASS,
        ))
        bottom += FontSizes.XYSUBLABEL
    return items, bottom
