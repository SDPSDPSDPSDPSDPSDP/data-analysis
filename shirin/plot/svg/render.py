"""Writes a laid-out Chart as an SVG string."""
from typing import List, Optional

from ..config import FigureSize, Layout
from ..config.colors import BACKGROUND_COLOR, GRID_COLOR
from ..config.theme import Theme
from .axis_labels import x_axis, y_axis
from .chart import Chart
from .fonts import TTF_FILES, font_css
from .frame import Color, Frame, layout
from .plot_body import draw_marks

PX_PER_PT = 4 / 3


def to_png(svg: str) -> bytes:
    """Rasterize a chart SVG. Satoshi is passed as TTF since the rasterizer cannot read the embedded woff2."""
    import resvg_py

    return resvg_py.svg_to_bytes(svg_string=svg, font_files=TTF_FILES, zoom=FigureSize.PNG_SCALE)


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


def to_svg(chart: Chart, font: Optional[str] = None, dark_mode: bool = False) -> str:
    color = Theme(dark_mode).color
    frame = layout(chart, color)
    x_axis_items, bottom = x_axis(chart, frame, color)
    height = bottom + Layout.PAD
    return ''.join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{frame.width * PX_PER_PT:.0f}" height="{height * PX_PER_PT:.0f}" '
        f'viewBox="0 0 {frame.width:.2f} {height:.2f}">',
        f'<style>{font_css(font, bool(chart.title))}</style>',
        f'<rect width="100%" height="100%" rx="{Layout.CORNER_RADIUS}" fill="{color(BACKGROUND_COLOR)}"/>',
        *_header(frame),
        *_grid(chart, frame, color),
        *draw_marks(chart, frame.texts, frame.sx, frame.sy, frame.bottom, color),
        *y_axis(chart, frame, color),
        *x_axis_items,
        '</svg>',
    ])
