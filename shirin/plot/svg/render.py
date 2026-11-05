"""Lays out a Chart and writes it as an SVG string."""
import math
from typing import List, Optional
from xml.sax.saxutils import escape

from ..config import FontSizes, Layout, TextColors
from ..config.colors import BACKGROUND_COLOR, DARK_MODE_COLORS, GRID_COLOR
from . import marks
from .axis import fit_x_ticks, limits, scale, tick_color, ticks
from .chart import Chart
from .fonts import cap_height, font_css, text_width
from .header import header_rows as build_header
from .plot_body import draw_marks, shorten_crowded_labels

PT_PER_INCH = 72
PX_PER_PT = 4 / 3


def to_svg(chart: Chart, font: Optional[str] = None, dark_mode: bool = False) -> str:
    theme = DARK_MODE_COLORS if dark_mode else {}

    def color(c: str) -> str:
        return theme.get(c, c)

    x_lim, y_lim = limits(chart.x, chart.data_values('x')), limits(chart.y, chart.data_values('y'))
    x_ticks, y_ticks = ticks(chart.x, *x_lim), ticks(chart.y, *y_lim)
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
    sx, sy = scale(*x_lim, plot_left, plot_left + plot_w), scale(*y_lim, plot_top + plot_h, plot_top)
    texts = shorten_crowded_labels(chart.texts, sx, sy)
    all_x_ticks, x_ticks = x_ticks, fit_x_ticks(chart.x, x_ticks, sx)
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
    sx, sy = scale(*x_lim, plot_left, plot_left + plot_w), scale(*y_lim, plot_top + plot_h, plot_top)
    x_ticks = fit_x_ticks(chart.x, all_x_ticks, sx)
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
    body += draw_marks(chart, texts, sx, sy, plot_bottom, color)

    if chart.y.label:
        # Rotated a quarter turn counterclockwise, so the baseline is the right edge of the text.
        x, y = Layout.PAD + cap_height(FontSizes.XYLABEL), plot_top + plot_h / 2
        body.append(
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{FontSizes.XYLABEL}" fill="{color(TextColors.BLACK)}" '
            f'text-anchor="middle" transform="rotate(-90 {x:.2f} {y:.2f})">{escape(chart.y.label)}</text>'
        )

    cap = cap_height(tick_size)
    x_tick_color, y_tick_color = color(tick_color(chart.x, chart.y)), color(tick_color(chart.y, chart.x))
    body += [marks.text(plot_left - Layout.TICK_GAP, sy(t) + cap / 2, label, tick_size, y_tick_color, 'end')
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
                body.append(marks.text(sx(t), tick_top + cap / 2, label, tick_size, x_tick_color, 'end', rotate=chart.x.rotation))
            else:
                body.append(marks.text(sx(t), tick_top + cap, label, tick_size, x_tick_color, 'middle'))
    if chart.x.sub_labels:
        bottom += Layout.ROW_GAP
        body += [marks.text(sx(t), bottom + cap, label, tick_size, color(TextColors.DARK_GREY), 'middle') for t, label in chart.x.sub_labels]
        bottom += tick_size
    if chart.x.label:
        bottom += Layout.LABEL_GAP
        label_baseline = bottom + cap_height(FontSizes.XYLABEL)
        label_color = color(TextColors.BLACK)
        body.append(marks.text(plot_left + plot_w / 2, label_baseline, chart.x.label, FontSizes.XYLABEL, label_color, 'middle'))
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
