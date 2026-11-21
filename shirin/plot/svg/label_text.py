"""Text pieces of the axis labels: tick descriptions and rotated y labels."""

from xml.sax.saxutils import escape

from ..config import FontSizes, Layout
from . import text_marks
from .fonts import cap_height


def description_height(lines: list[str]) -> float:
    n = len(lines)
    return n * cap_height(FontSizes.DESCRIPTION) + max(n - 1, 0) * Layout.DESCRIPTION_LINE_GAP


def description(x: float, top: float, lines: list[str], anchor: str, color: str) -> list[str]:
    """Wrapped description lines, the first one's cap top at top."""
    line_height = cap_height(FontSizes.DESCRIPTION) + Layout.DESCRIPTION_LINE_GAP
    first_baseline = top + cap_height(FontSizes.DESCRIPTION)
    return [
        text_marks.text(x, first_baseline + i * line_height, line, FontSizes.DESCRIPTION, color, anchor)
        for i, line in enumerate(lines)
    ]


def rotated_label(x: float, y: float, text: str, size: float, fill: str, css_class: str = "") -> str:
    """Rotated a quarter turn counterclockwise, so the baseline x is the right edge of the text."""
    class_attr = f' class="{css_class}"' if css_class else ""
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}"{class_attr} '
        f'text-anchor="middle" transform="rotate(-90 {x:.2f} {y:.2f})">{escape(text)}</text>'
    )
