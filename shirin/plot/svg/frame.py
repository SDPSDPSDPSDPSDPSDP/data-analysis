"""Sizes the plot area of a Chart: where it sits in the SVG and how data maps onto it."""
from dataclasses import dataclass
from typing import Callable, List

from ..config import FontSizes, Layout
from . import marks
from .axis import Ticks, fit_x_ticks, limits, scale, tick_label_width, ticks
from .chart import Chart, Text
from .fonts import cap_height
from .header import HeaderRow
from .header import header_rows as build_header
from .marks import Scale
from .plot_body import place_point_labels, shorten_crowded_labels

PT_PER_INCH = 72

Color = Callable[[str], str]


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
    y_label_width = cap_height(FontSizes.XYLABEL) if chart.y.label else 0
    if chart.y.sublabel:
        y_label_width += (Layout.SUBLABEL_GAP if chart.y.label else 0) + cap_height(FontSizes.XYSUBLABEL)
    if y_label_width:
        y_label_width += Layout.LABEL_GAP
    y_ticks_space = y_tick_width + Layout.TICK_GAP if y_tick_width else 0
    plot_left = Layout.PAD + y_label_width + y_ticks_space
    plot_h = chart.plot_height * PT_PER_INCH
    fixed_width = chart.width is not None
    width = chart.width * PT_PER_INCH if fixed_width else plot_left + plot_h + Layout.PAD  # type: ignore[operator]
    plot_w = width - plot_left - Layout.PAD

    header_rows, plot_top = build_header(chart, width - 2 * Layout.PAD, color)

    # First pass at this size: measure what sticks out of the plot area, then shrink or grow to fit it.
    sx, sy = scale(*x_lim, plot_left, plot_left + plot_w), scale(*y_lim, plot_top + plot_h, plot_top)
    texts = shorten_crowded_labels(place_point_labels(chart.texts, sx, sy), sx, sy)
    boxes = [marks.place(t, sx, sy)[2:] for t in texts if t.text]
    shown_x_ticks = fit_x_ticks(chart.x, x_ticks, sx)
    if shown_x_ticks and not chart.x.rotation:
        position, label = max(shown_x_ticks, key=lambda tick: sx(tick[0]))
        boxes.append((0, sx(position) + tick_label_width(chart.x, position, label, sx) / 2, plot_top))
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
