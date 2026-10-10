"""SVG markup for single marks, positioned through the chart's x/y scales (in points)."""
import math
from typing import Callable, List, Tuple
from xml.sax.saxutils import escape

from ..config import Layout
from .chart import Dots, Line, Rect, Text, Wedge
from .fonts import cap_height, is_large, text_width

ANCHOR = {'left': 'start', 'center': 'middle', 'right': 'end'}

Scale = Callable[[float], float]


def text(x: float, y: float, s: str, size: float, color: str, anchor: str = 'start', bold: bool = False, rotate: float = 0) -> str:
    attrs = f'x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}"'
    if anchor != 'start':
        attrs += f' text-anchor="{anchor}"'
    if bold:
        attrs += ' class="b"'
    elif is_large(size):
        attrs += ' class="l"'
    if rotate:
        attrs += f' transform="rotate({-rotate} {x:.2f} {y - cap_height(size) / 2:.2f})"'
    return f'<text {attrs}>{escape(s)}</text>'


def place(t: Text, sx: Scale, sy: Scale) -> Tuple[float, float, float, float, float]:
    """Anchor x, baseline y and bounding box (x0, x1, top) of a data text, in points."""
    width, height = text_width(t.text, t.size), cap_height(t.size)
    x, y = sx(t.x) + t.dx, sy(t.y) - t.dy
    baseline = {'bottom': y, 'center': y + height / 2, 'top': y + height}[t.va]
    x0 = {'left': x, 'center': x - width / 2, 'right': x - width}[t.ha]
    return x, baseline, x0, x0 + width, baseline - height


def rect(r: Rect, sx: Scale, sy: Scale) -> str:
    xa, xb = sorted((sx(r.x0), sx(r.x1)))
    ya, yb = sorted((sy(r.y0), sy(r.y1)))
    stroke = f' stroke="{r.stroke}" stroke-width="{Layout.HAIRLINE}"' if r.stroke else ''
    radius = f' rx="{min(xb - xa, yb - ya) / 2:.2f}"' if r.rounded else ''
    return f'<rect x="{xa:.2f}" y="{ya:.2f}" width="{xb - xa:.2f}" height="{yb - ya:.2f}"{radius} fill="{r.color}"{stroke}/>'


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


def line(line: Line, sx: Scale, sy: Scale) -> str:
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
