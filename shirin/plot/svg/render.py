"""Lays out a Chart and writes it as an SVG string."""
import math
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple
from xml.sax.saxutils import escape

from ..config import FigureSize, FontSizes, Layout, TextColors
from ..config.colors import BACKGROUND_COLOR, GRID_COLOR
from ..config.theme import Theme
from . import marks
from .axis import Ticks, fit_x_ticks, limits, scale, tick_color, tick_label_width, ticks
from .chart import Chart, Text
from .fonts import TTF_FILES, cap_height, font_css, text_width
from .header import HeaderRow
from .header import header_rows as build_header
from .marks import Scale
from .plot_body import draw_marks, shorten_crowded_labels

PT_PER_INCH = 72
PX_PER_PT = 4 / 3

Color = Callable[[str], str]


def to_png(svg: str) -> bytes:
    """Rasterize a chart SVG. Satoshi is passed as TTF since the rasterizer cannot read the embedded woff2."""
    import resvg_py

    return resvg_py.svg_to_bytes(svg_string=svg, font_files=TTF_FILES, zoom=FigureSize.PNG_SCALE)


@dataclass(frozen=True)
class Frame:
    """Where the plot area sits in the SVG, in points, and how data coordinates map onto it."""

    width: float
    left: float
    top: float
    plot_w: float
    plot_h: float
    sx: Scale
    sy: Scale
    x_ticks: Ticks
    y_ticks: Ticks
    texts: List[Text]  # data labels, shortened where they would overlap
    header_rows: List[HeaderRow]

    @property
    def right(self) -> float:
        return self.left + self.plot_w

    @property
    def bottom(self) -> float:
        return self.top + self.plot_h


def layout(chart: Chart, color: Color) -> Frame:
    """Size the plot area so ticks, header and data labels sticking out of it all fit in the SVG."""
    x_lim, y_lim = limits(chart.x, chart.data_values('x')), limits(chart.y, chart.data_values('y'))
    x_ticks, y_ticks = ticks(chart.x, *x_lim), ticks(chart.y, *y_lim)

    y_tick_width = max((tick_label_width(chart.y, t, label) for t, label in y_ticks), default=0)
    y_label_width = cap_height(FontSizes.XYLABEL) + Layout.LABEL_GAP if chart.y.label else 0
    y_ticks_space = y_tick_width + Layout.TICK_GAP if y_tick_width else 0
    plot_left = Layout.PAD + y_label_width + y_ticks_space
    plot_h = chart.plot_height * PT_PER_INCH
    fixed_width = chart.width is not None
    width = chart.width * PT_PER_INCH if fixed_width else plot_left + plot_h + Layout.PAD  # type: ignore[operator]
    plot_w = width - plot_left - Layout.PAD

    header_rows, plot_top = build_header(chart, width - 2 * Layout.PAD, color)

    # First pass at this size: measure what sticks out of the plot area, then shrink or grow to fit it.
    sx, sy = scale(*x_lim, plot_left, plot_left + plot_w), scale(*y_lim, plot_top + plot_h, plot_top)
    texts = shorten_crowded_labels(chart.texts, sx, sy)
    boxes = [marks.place(t, sx, sy)[2:] for t in texts if t.text]
    shown_x_ticks = fit_x_ticks(chart.x, x_ticks, sx)
    if shown_x_ticks and not chart.x.rotation:
        position, label = shown_x_ticks[-1]
        boxes.append((0, sx(position) + tick_label_width(chart.x, position, label) / 2, plot_top))
    right_overflow = max([0.0] + [right - (plot_left + plot_w) for _, right, _ in boxes])
    plot_top += max([0.0] + [plot_top - top for _, _, top in boxes])
    if fixed_width:
        plot_w -= right_overflow
    else:
        width = max([width + right_overflow] + [row_width + 2 * Layout.PAD for row_width, _ in header_rows])

    sx, sy = scale(*x_lim, plot_left, plot_left + plot_w), scale(*y_lim, plot_top + plot_h, plot_top)
    return Frame(
        width=width, left=plot_left, top=plot_top, plot_w=plot_w, plot_h=plot_h, sx=sx, sy=sy,
        x_ticks=fit_x_ticks(chart.x, x_ticks, sx), y_ticks=y_ticks, texts=texts, header_rows=header_rows,
    )


def _header(frame: Frame) -> List[str]:
    return [
        f'<g transform="translate({max(Layout.PAD, (frame.width - w) / 2):.2f} 0)">{"".join(items)}</g>'
        for w, items in frame.header_rows
    ]


def _grid(chart: Chart, frame: Frame, color: Color) -> List[str]:
    grid = f'stroke="{color(GRID_COLOR)}" stroke-width="{Layout.HAIRLINE}"'
    sx, sy = frame.sx, frame.sy
    lines: List[str] = []
    if chart.y.grid:
        lines += [
            f'<line x1="{frame.left:.2f}" x2="{frame.right:.2f}" y1="{sy(t):.2f}" y2="{sy(t):.2f}" {grid}/>'
            for t, _ in frame.y_ticks
        ]
    if chart.x.grid:
        lines += [
            f'<line x1="{sx(t):.2f}" x2="{sx(t):.2f}" y1="{frame.top:.2f}" y2="{frame.bottom:.2f}" {grid}/>'
            for t, _ in frame.x_ticks
        ]
    return lines


def _y_axis(chart: Chart, frame: Frame, color: Color) -> List[str]:
    items: List[str] = []
    if chart.y.label:
        # Rotated a quarter turn counterclockwise, so the baseline is the right edge of the text.
        x, y = Layout.PAD + cap_height(FontSizes.XYLABEL), frame.top + frame.plot_h / 2
        items.append(
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{FontSizes.XYLABEL}" fill="{color(TextColors.BLACK)}" '
            f'text-anchor="middle" transform="rotate(-90 {x:.2f} {y:.2f})">{escape(chart.y.label)}</text>'
        )
    cap, description_cap = cap_height(FontSizes.TICKS), cap_height(FontSizes.DESCRIPTION)
    x = frame.left - Layout.TICK_GAP
    y_tick_color, description_color = color(tick_color(chart.y, chart.x)), color(TextColors.LIGHT_GREY)
    descriptions = dict(chart.y.descriptions)
    for t, label in frame.y_ticks:
        if not label:
            continue
        description = descriptions.get(t)
        if description is None:
            items.append(marks.text(x, frame.sy(t) + cap / 2, label, FontSizes.TICKS, y_tick_color, 'end'))
            continue
        # Label and description together are centered on the tick.
        top = frame.sy(t) - (cap + Layout.DESCRIPTION_GAP + description_cap) / 2
        items.append(marks.text(x, top + cap, label, FontSizes.TICKS, y_tick_color, 'end'))
        description_baseline = top + cap + Layout.DESCRIPTION_GAP + description_cap
        items.append(marks.text(x, description_baseline, description, FontSizes.DESCRIPTION, description_color, 'end'))
    return items


def _x_axis(chart: Chart, frame: Frame, color: Color) -> Tuple[List[str], float]:
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
        shown = {t for t, _ in labelled_ticks}
        description_cap = cap_height(FontSizes.DESCRIPTION)
        bottom += Layout.DESCRIPTION_GAP
        description_color = color(TextColors.LIGHT_GREY)
        items += [marks.text(sx(t), bottom + description_cap, description, FontSizes.DESCRIPTION, description_color, 'middle')
                  for t, description in chart.x.descriptions if t in shown]
        bottom += description_cap
    if chart.x.sub_labels:
        bottom += Layout.ROW_GAP
        sub_label_color = color(TextColors.DARK_GREY)
        items += [marks.text(sx(t), bottom + cap, label, tick_size, sub_label_color, 'middle')
                  for t, label in chart.x.sub_labels]
        bottom += tick_size
    if chart.x.label:
        bottom += Layout.LABEL_GAP
        label_baseline = bottom + cap_height(FontSizes.XYLABEL)
        label_color = color(TextColors.BLACK)
        items.append(marks.text(frame.left + frame.plot_w / 2, label_baseline, chart.x.label, FontSizes.XYLABEL, label_color, 'middle'))
        bottom += FontSizes.XYLABEL
    return items, bottom


def to_svg(chart: Chart, font: Optional[str] = None, dark_mode: bool = False) -> str:
    color = Theme(dark_mode).color
    frame = layout(chart, color)
    x_axis, bottom = _x_axis(chart, frame, color)
    height = bottom + Layout.PAD
    return ''.join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{frame.width * PX_PER_PT:.0f}" height="{height * PX_PER_PT:.0f}" '
        f'viewBox="0 0 {frame.width:.2f} {height:.2f}">',
        f'<style>{font_css(font, bool(chart.title))}</style>',
        f'<rect width="100%" height="100%" rx="{Layout.CORNER_RADIUS}" fill="{color(BACKGROUND_COLOR)}"/>',
        *_header(frame),
        *_grid(chart, frame, color),
        *draw_marks(chart, frame.texts, frame.sx, frame.sy, frame.bottom, color),
        *_y_axis(chart, frame, color),
        *x_axis,
        '</svg>',
    ])
