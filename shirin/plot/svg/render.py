"""Lays out a Chart (see PLAN.md for the layout spec) and writes it as an SVG string."""
import math
from typing import Callable, List, Optional, Tuple
from xml.sax.saxutils import escape

from ..config import FontSizes, Layout, TextColors
from ..config.colors import GRID_COLOR
from .chart import Axis, Chart, Dots, Line, Rect, Text, Wedge
from .fonts import cap_height, font_css, text_width
from .ticks import date_ticks, nice_ticks

PT_PER_INCH = 72
PX_PER_PT = 4 / 3
MARGIN = 0.05
_ANCHOR = {'left': 'start', 'center': 'middle', 'right': 'end'}

Scale = Callable[[float], float]
Ticks = List[Tuple[float, str]]


def _limits(axis: Axis, values: List[float]) -> Tuple[float, float]:
    if axis.lim is not None:
        return axis.lim
    values = [v for v in values if v == v]  # drop NaN
    if not values:
        raise ValueError("Chart has no data to scale the axis on")
    lo, hi = min(values), max(values)
    if lo == hi:
        lo, hi = lo - 0.5, hi + 0.5
    pad = (hi - lo) * MARGIN
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
    return [(t, label if axis.show_tick_labels else '') for t, label in ticks if low <= t <= high]


def _scale(lo: float, hi: float, start: float, end: float) -> Scale:
    return lambda v: start + (v - lo) / (hi - lo) * (end - start)


def _legend_rows(items: List[Tuple[str, str]], max_width: float) -> List[List[Tuple[str, str, float]]]:
    """One row of swatch + label items, wrapped when wider than the plot area."""
    rows: List[List[Tuple[str, str, float]]] = [[]]
    used = 0.0
    for color, label in items:
        width = Layout.SWATCH + Layout.SWATCH_GAP + text_width(label, FontSizes.LEGEND)
        if rows[-1] and used + Layout.LEGEND_ITEM_GAP + width > max_width:
            rows.append([])
            used = 0.0
        used += (Layout.LEGEND_ITEM_GAP if rows[-1] else 0) + width
        rows[-1].append((color, label, width))
    return [row for row in rows if row]


def _text(x: float, y: float, s: str, size: float, color: str, anchor: str = 'start', bold: bool = False, rotate: float = 0) -> str:
    attrs = f'x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}"'
    if anchor != 'start':
        attrs += f' text-anchor="{anchor}"'
    if bold:
        attrs += ' class="b"'
    if rotate:
        attrs += f' transform="rotate({-rotate} {x:.2f} {y - cap_height(size) / 2:.2f})"'
    return f'<text {attrs}>{escape(s)}</text>'


def _place(t: Text, sx: Scale, sy: Scale) -> Tuple[float, float, float, float, float]:
    """Anchor x, baseline y and bounding box (x0, x1, top) of a data text, in points."""
    width, height = text_width(t.text, t.size), cap_height(t.size)
    x, y = sx(t.x) + t.dx, sy(t.y) - t.dy
    baseline = {'bottom': y, 'center': y + height / 2, 'top': y + height}[t.va]
    x0 = {'left': x, 'center': x - width / 2, 'right': x - width}[t.ha]
    return x, baseline, x0, x0 + width, baseline - height


def _rect(r: Rect, sx: Scale, sy: Scale) -> str:
    xa, xb = sorted((sx(r.x0), sx(r.x1)))
    ya, yb = sorted((sy(r.y0), sy(r.y1)))
    stroke = f' stroke="{r.stroke}" stroke-width="0.5"' if r.stroke else ''
    return f'<rect x="{xa:.2f}" y="{ya:.2f}" width="{xb - xa:.2f}" height="{yb - ya:.2f}" fill="{r.color}"{stroke}/>'


def _line(line: Line, sx: Scale, sy: Scale) -> str:
    segments: List[List[Tuple[float, float]]] = [[]]
    for x, y in zip(line.xs, line.ys):
        if y != y:  # NaN breaks the line
            segments.append([])
        else:
            segments[-1].append((sx(x), sy(y)))
    d = ' '.join('M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in seg) for seg in segments if seg)
    out = [f'<path d="{d}" fill="none" stroke="{line.color}" stroke-width="{line.width}" '
           f'stroke-linejoin="round" stroke-linecap="round" opacity="{line.alpha}"/>']
    if line.marker_radius:
        out += [f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{line.marker_radius}" fill="{line.color}"/>'
                for seg in segments for x, y in seg]
    return ''.join(out)


def _dots(dots: Dots, sx: Scale, sy: Scale) -> str:
    return ''.join(
        f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="{r:.2f}" fill="{dots.color}" fill-opacity="{dots.alpha}"/>'
        for x, y, r in zip(dots.xs, dots.ys, dots.radii) if y == y
    )


def _wedge(w: Wedge, sx: Scale, sy: Scale) -> str:
    cx, cy, r = sx(0), sy(0), sx(w.radius) - sx(0)
    if w.end - w.start >= 1 - 1e-9:
        return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{w.color}"/>'

    def point(turn: float) -> str:
        angle = 2 * math.pi * turn
        return f'{cx + r * math.sin(angle):.2f} {cy - r * math.cos(angle):.2f}'

    large = 1 if w.end - w.start > 0.5 else 0
    return f'<path d="M{cx:.2f} {cy:.2f} L{point(w.start)} A{r:.2f} {r:.2f} 0 {large} 1 {point(w.end)} Z" fill="{w.color}"/>'


def to_svg(chart: Chart, font: Optional[str] = None) -> str:
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

    # Rows are drawn from x=0 and shifted to center over the plot once its final width is known.
    header_rows: List[Tuple[float, List[str]]] = []
    top = float(Layout.PAD)

    def header_row(height: float) -> float:
        nonlocal top
        row_top = top
        top += height + Layout.ROW_GAP
        return row_top

    for text, size, bold, color in (
        (chart.title, FontSizes.TITLE, True, TextColors.BLACK),
        (chart.subtitle, FontSizes.TEXT, False, TextColors.LIGHT_GREY),
    ):
        if text:
            row_top = header_row(size)
            header_rows.append((text_width(text, size, bold), [_text(0, row_top + cap_height(size), text, size, color, bold=bold)]))
    for row in _legend_rows(chart.legend, plot_w):
        row_top = header_row(Layout.SWATCH)
        x = 0.0
        items: List[str] = []
        for color, label, item_width in row:
            items.append(f'<rect x="{x:.2f}" y="{row_top:.2f}" width="{Layout.SWATCH}" height="{Layout.SWATCH}" fill="{color}"/>')
            baseline = row_top + Layout.SWATCH / 2 + cap_height(FontSizes.LEGEND) / 2
            items.append(_text(x + Layout.SWATCH + Layout.SWATCH_GAP, baseline, label, FontSizes.LEGEND, TextColors.DARK_GREY))
            x += item_width + Layout.LEGEND_ITEM_GAP
        header_rows.append((x - Layout.LEGEND_ITEM_GAP, items))
    plot_top = top - Layout.ROW_GAP + Layout.PLOT_GAP if header_rows else top

    # Data labels and the last x tick label may stick out of the plot area: make room for them.
    sx, sy = _scale(*x_lim, plot_left, plot_left + plot_w), _scale(*y_lim, plot_top + plot_h, plot_top)
    boxes = [_place(t, sx, sy)[2:] for t in chart.texts if t.text]
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
        f'<g transform="translate({max(Layout.PAD, min(plot_left + (plot_w - w) / 2, width - Layout.PAD - w)):.2f} 0)">{"".join(items)}</g>'
        for w, items in header_rows
    ]

    body: List[str] = []
    grid = 'stroke="{}" stroke-width="0.5" stroke-dasharray="1 1.5"'.format(GRID_COLOR)
    if chart.y.grid:
        body += [f'<line x1="{plot_left:.2f}" x2="{plot_left + plot_w:.2f}" y1="{sy(t):.2f}" y2="{sy(t):.2f}" {grid}/>' for t, _ in y_ticks]
    if chart.x.grid:
        body += [f'<line x1="{sx(t):.2f}" x2="{sx(t):.2f}" y1="{plot_top:.2f}" y2="{plot_bottom:.2f}" {grid}/>' for t, _ in x_ticks]
    body += [_wedge(w, sx, sy) for w in chart.wedges if w.end > w.start]
    body += [_rect(r, sx, sy) for r in chart.rects if r.width and r.height]
    body += [_line(line, sx, sy) for line in chart.lines]
    body += [_dots(dots, sx, sy) for dots in chart.dots]
    for t in chart.texts:
        if t.text:
            x, baseline = _place(t, sx, sy)[:2]
            body.append(_text(x, baseline, t.text, t.size, t.color, _ANCHOR[t.ha]))

    if chart.y.label:
        # Rotated a quarter turn counterclockwise, so the baseline is the right edge of the text.
        x, y = Layout.PAD + cap_height(FontSizes.XYLABEL), plot_top + plot_h / 2
        body.append(
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{FontSizes.XYLABEL}" fill="{TextColors.BLACK}" '
            f'text-anchor="middle" transform="rotate(-90 {x:.2f} {y:.2f})">{escape(chart.y.label)}</text>'
        )

    cap = cap_height(tick_size)
    body +=[_text(plot_left - Layout.TICK_GAP, sy(t) + cap / 2, label, tick_size, TextColors.DARK_GREY, 'end')
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
                body.append(_text(sx(t), tick_top + cap / 2, label, tick_size, TextColors.DARK_GREY, 'end', rotate=chart.x.rotation))
            else:
                body.append(_text(sx(t), tick_top + cap, label, tick_size, TextColors.DARK_GREY, 'middle'))
    if chart.x.sub_labels:
        bottom += Layout.ROW_GAP
        body += [_text(sx(t), bottom + cap, label, tick_size, TextColors.DARK_GREY, 'middle') for t, label in chart.x.sub_labels]
        bottom += tick_size
    if chart.x.label:
        bottom += Layout.LABEL_GAP
        body.append(_text(plot_left + plot_w / 2, bottom + cap_height(FontSizes.XYLABEL), chart.x.label, FontSizes.XYLABEL, TextColors.BLACK, 'middle'))
        bottom += FontSizes.XYLABEL
    height = bottom + Layout.PAD

    return ''.join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width * PX_PER_PT:.0f}" height="{height * PX_PER_PT:.0f}" '
        f'viewBox="0 0 {width:.2f} {height:.2f}">',
        f'<style>{font_css(font, bool(chart.title))}</style>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        *header,
        *body,
        '</svg>',
    ])
