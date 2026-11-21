"""SVG markup for single shape marks, positioned through the chart's x/y scales (in points)."""

import math
from typing import Callable

from ..config import Layout, Marks
from .chart import Dots, Line, Rect, Wedge

Scale = Callable[[float], float]


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
        return f"{x:.2f} {y:.2f}"

    sweep = int((direction > 0) == r.horizontal)
    arc = f"A{radius:.2f} {radius:.2f} 0 0 {sweep} "
    d = (
        f"M{point(cut, side0)} L{point(p1 - direction * radius, side0)} {arc}{point(p1, side0 + radius)} "
        f"L{point(p1, side1 - radius)} {arc}{point(p1 - direction * radius, side1)} L{point(cut, side1)} Z"
    )
    return f'<path d="{d}" fill="{r.color}"/>'


def rect(r: Rect, sx: Scale, sy: Scale) -> str:
    if r.tuck is not None:
        return _tucked_pill(r, sx, sy)
    xa, xb = sorted((sx(r.x0), sx(r.x1)))
    ya, yb = sorted((sy(r.y0), sy(r.y1)))
    width, height = xb - xa, yb - ya
    radius = f' rx="{min(width, height) / 2:.2f}"' if r.rounded else ""
    return f'<rect x="{xa:.2f}" y="{ya:.2f}" width="{width:.2f}" height="{height:.2f}"{radius} fill="{r.color}"/>'


def _segments(line: Line, sx: Scale, sy: Scale) -> list[list[tuple[float, float]]]:
    segments: list[list[tuple[float, float]]] = [[]]
    for x, y in zip(line.xs, line.ys):
        if y != y:  # NaN breaks the line
            segments.append([])
        else:
            segments[-1].append((sx(x), sy(y)))
    return [seg for seg in segments if seg]


def _path(points: list[tuple[float, float]]) -> str:
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in points)


def line(line: Line, sx: Scale, sy: Scale) -> str:
    d = " ".join(_path(seg) for seg in _segments(line, sx, sy))
    return (
        f'<path d="{d}" fill="none" stroke="{line.color}" stroke-width="{Marks.LINE_WIDTH}" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
    )


def area(line: Line, sx: Scale, sy: Scale, bottom: float, gradient_id: str) -> str:
    """Area under the line down to `bottom`, fading out towards the bottom."""
    d = " ".join(_path([*seg, (seg[-1][0], bottom), (seg[0][0], bottom)]) + " Z" for seg in _segments(line, sx, sy))
    return (
        f'<linearGradient id="{gradient_id}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{line.color}" stop-opacity="{Marks.LINE_FILL_ALPHA}"/>'
        f'<stop offset="1" stop-color="{line.color}" stop-opacity="0"/></linearGradient>'
        f'<path d="{d}" fill="url(#{gradient_id})"/>'
    )


def dots(dots: Dots, sx: Scale, sy: Scale) -> str:
    return "".join(
        f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="{r:.2f}" fill="{dots.color}" fill-opacity="{dots.alpha}"/>'
        for x, y, r in zip(dots.xs, dots.ys, dots.radii)
        if y == y
    )


def wedge(w: Wedge, sx: Scale, sy: Scale) -> str:
    cx, cy, r = sx(0), sy(0), sx(w.radius) - sx(0)
    if w.end - w.start >= 1 - 1e-9:
        return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{w.color}"/>'

    def point(turn: float) -> str:
        angle = 2 * math.pi * turn
        return f"{cx + r * math.sin(angle):.2f} {cy - r * math.cos(angle):.2f}"

    large = 1 if w.end - w.start > 0.5 else 0
    return (
        f'<path d="M{cx:.2f} {cy:.2f} L{point(w.start)} A{r:.2f} {r:.2f} 0 {large} 1 {point(w.end)} Z" fill="{w.color}" '
        f'stroke="{w.color}" stroke-width="{Layout.WEDGE_SEAM}" stroke-linejoin="round"/>'
    )
