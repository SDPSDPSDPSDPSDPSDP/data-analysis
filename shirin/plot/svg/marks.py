"""SVG markup for single marks, positioned through the chart's x/y scales (in points)."""
import math
from typing import Callable, List, Tuple
from xml.sax.saxutils import escape

from ..config import FontSizes, Layout, Marks
from .chart import Dots, Line, Rect, Text, Wedge
from .fonts import cap_height, is_large, text_width

ANCHOR = {'left': 'start', 'center': 'middle', 'right': 'end'}

Scale = Callable[[float], float]


def text(
    x: float, y: float, s: str, size: float, color: str, anchor: str = 'start', bold: bool = False, rotate: float = 0, alpha: float = 1,
    title: str = '', css_class: str = '',
) -> str:
    """title: smaller, faded text drawn right before s on the same baseline. css_class: style class from font_css."""
    attrs = f'x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}"'
    if alpha != 1:
        attrs += f' fill-opacity="{alpha}"'
    if anchor != 'start':
        attrs += f' text-anchor="{anchor}"'
    if bold:
        attrs += ' class="b"'
    elif is_large(size):
        attrs += ' class="l"'
    elif css_class:
        attrs += f' class="{css_class}"'
    if rotate:
        attrs += f' transform="rotate({-rotate} {x:.2f} {y - cap_height(size) / 2:.2f})"'
    prefix = ''
    if title:
        title_alpha = Marks.POINT_LABEL_TITLE_ALPHA * alpha
        title_attrs = f'font-size="{FontSizes.POINT_LABEL_TITLES}" fill-opacity="{title_alpha}"'
        prefix = f'<tspan {title_attrs}>{escape(title)} </tspan>'
    return f'<text {attrs}>{prefix}{escape(s)}</text>'


def _title_width(title: str) -> float:
    return text_width(f'{title} ', FontSizes.POINT_LABEL_TITLES) if title else 0


def line_titles(t: Text) -> Tuple[str, ...]:
    """One title per line of t, '' where a line has none."""
    line_count = t.text.count('\n') + 1
    if t.line_titles and len(t.line_titles) != line_count:
        raise ValueError(f"{len(t.line_titles)} line_titles for {line_count} lines in {t.text!r}")
    return t.line_titles or ('',) * line_count


def line_step(size: float) -> float:
    """Baseline to baseline distance between the lines of a multi-line data text."""
    return cap_height(size) + Layout.DATA_TEXT_LINE_GAP


def place(t: Text, sx: Scale, sy: Scale) -> Tuple[float, float, float, float, float]:
    """Anchor x, first line's baseline y and bounding box (x0, x1, top) of a data text, in points.

    A text with newlines is one block: va aligns the whole block, ha every line. Line titles widen their line.
    """
    lines = t.text.split('\n')
    titles = line_titles(t)
    width = max(_title_width(title) + text_width(line, t.size) for title, line in zip(titles, lines))
    first_line = cap_height(t.size)
    height = first_line + (len(lines) - 1) * line_step(t.size)
    x, y = sx(t.x) + t.dx, sy(t.y) - t.dy
    top = {'bottom': y - height, 'center': y - height / 2, 'top': y}[t.va]
    x0 = {'left': x, 'center': x - width / 2, 'right': x - width}[t.ha]
    return x, top + first_line, x0, x0 + width, top


def _tucked_pill(r: Rect, sx: Scale, sy: Scale) -> str:
    """Pill r cut to start just inside the front pill (same base, ends at r.tuck): flat start, rounded end.

    The cut sits where the front pill still covers the full bar thickness, so no edge of r lines up with its edges.
    """
    along, across = (sx, sy) if r.horizontal else (sy, sx)
    base, end = (r.x0, r.x1) if r.horizontal else (r.y0, r.y1)
    side0, side1 = sorted(across(v) for v in ((r.y0, r.y1) if r.horizontal else (r.x0, r.x1)))
    p0, front_end, p1 = along(base), along(r.tuck), along(end)  # type: ignore[arg-type]
    thickness = side1 - side0
    direction = 1 if p1 > p0 else -1
    front_radius = min(abs(front_end - p0), thickness) / 2
    radius = min(abs(p1 - p0), thickness) / 2
    cut = p1 - direction * max(direction * (p1 - (front_end - direction * front_radius)), radius)

    def point(a: float, c: float) -> str:
        x, y = (a, c) if r.horizontal else (c, a)
        return f'{x:.2f} {y:.2f}'

    sweep = int((direction > 0) == r.horizontal)
    arc = f'A{radius:.2f} {radius:.2f} 0 0 {sweep} '
    d = (f'M{point(cut, side0)} L{point(p1 - direction * radius, side0)} {arc}{point(p1, side0 + radius)} '
         f'L{point(p1, side1 - radius)} {arc}{point(p1 - direction * radius, side1)} L{point(cut, side1)} Z')
    return f'<path d="{d}" fill="{r.color}"/>'


def rect(r: Rect, sx: Scale, sy: Scale) -> str:
    if r.tuck is not None:
        return _tucked_pill(r, sx, sy)
    xa, xb = sorted((sx(r.x0), sx(r.x1)))
    ya, yb = sorted((sy(r.y0), sy(r.y1)))
    width, height = xb - xa, yb - ya
    radius = f' rx="{min(width, height) / 2:.2f}"' if r.rounded else ''
    return f'<rect x="{xa:.2f}" y="{ya:.2f}" width="{width:.2f}" height="{height:.2f}"{radius} fill="{r.color}"/>'


def fade(r: Rect, sx: Scale, sy: Scale, gradient_id: str) -> str:
    """Gradient band centered on the rect's end edge, so the next stack segment blends in."""
    half = Layout.STACK_BLEND / 2
    if r.horizontal:
        ya, yb = sorted((sy(r.y0), sy(r.y1)))
        x, y, w, h, direction = sx(r.x1) - half, ya, 2 * half, yb - ya, 'x2="1" y2="0"'
    else:
        xa, xb = sorted((sx(r.x0), sx(r.x1)))
        x, y, w, h, direction = xa, sy(r.y1) - half, xb - xa, 2 * half, 'x1="0" y1="1" x2="0" y2="0"'
    return (f'<linearGradient id="{gradient_id}" {direction}><stop offset="0" stop-color="{r.color}"/>'
            f'<stop offset="1" stop-color="{r.fade_to}"/></linearGradient>'
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="url(#{gradient_id})"/>')


def _segments(line: Line, sx: Scale, sy: Scale) -> List[List[Tuple[float, float]]]:
    segments: List[List[Tuple[float, float]]] = [[]]
    for x, y in zip(line.xs, line.ys):
        if y != y:  # NaN breaks the line
            segments.append([])
        else:
            segments[-1].append((sx(x), sy(y)))
    return [seg for seg in segments if seg]


def _path(points: List[Tuple[float, float]]) -> str:
    return 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in points)


def line(line: Line, sx: Scale, sy: Scale) -> str:
    d = ' '.join(_path(seg) for seg in _segments(line, sx, sy))
    return (f'<path d="{d}" fill="none" stroke="{line.color}" stroke-width="{Marks.LINE_WIDTH}" '
            'stroke-linejoin="round" stroke-linecap="round"/>')


def area(line: Line, sx: Scale, sy: Scale, bottom: float, gradient_id: str) -> str:
    """Area under the line down to `bottom`, fading out towards the bottom."""
    d = ' '.join(_path(seg + [(seg[-1][0], bottom), (seg[0][0], bottom)]) + ' Z' for seg in _segments(line, sx, sy))
    return (f'<linearGradient id="{gradient_id}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{line.color}" stop-opacity="{Marks.LINE_FILL_ALPHA}"/>'
            f'<stop offset="1" stop-color="{line.color}" stop-opacity="0"/></linearGradient>'
            f'<path d="{d}" fill="url(#{gradient_id})"/>')


def dots(dots: Dots, sx: Scale, sy: Scale) -> str:
    return ''.join(
        f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="{r:.2f}" fill="{dots.color}" fill-opacity="{dots.alpha}"/>'
        for x, y, r in zip(dots.xs, dots.ys, dots.radii) if y == y
    )


def wedge(w: Wedge, sx: Scale, sy: Scale) -> str:
    cx, cy, r = sx(0), sy(0), sx(w.radius) - sx(0)
    if w.end - w.start >= 1 - 1e-9:
        return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{w.color}"/>'

    def point(turn: float) -> str:
        angle = 2 * math.pi * turn
        return f'{cx + r * math.sin(angle):.2f} {cy - r * math.cos(angle):.2f}'

    large = 1 if w.end - w.start > 0.5 else 0
    return (
        f'<path d="M{cx:.2f} {cy:.2f} L{point(w.start)} A{r:.2f} {r:.2f} 0 {large} 1 {point(w.end)} Z" fill="{w.color}" '
        f'stroke="{w.color}" stroke-width="{Layout.WEDGE_SEAM}" stroke-linejoin="round"/>'
    )
