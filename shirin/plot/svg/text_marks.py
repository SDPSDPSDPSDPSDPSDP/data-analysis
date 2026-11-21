"""SVG markup and placement for data texts, positioned through the chart's x/y scales (in points)."""

from xml.sax.saxutils import escape

from ..config import FontSizes, Layout, Marks
from .chart import Text
from .fonts import cap_height, is_large, text_width
from .marks import Scale

ANCHOR = {"left": "start", "center": "middle", "right": "end"}


def text(
    x: float,
    y: float,
    s: str,
    size: float,
    color: str,
    anchor: str = "start",
    bold: bool = False,
    rotate: float = 0,
    alpha: float = 1,
    title: str = "",
    css_class: str = "",
) -> str:
    """title: smaller, faded text drawn right before s on the same baseline. css_class: style class from font_css."""
    attrs = f'x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}"'
    if alpha != 1:
        attrs += f' fill-opacity="{alpha}"'
    if anchor != "start":
        attrs += f' text-anchor="{anchor}"'
    if bold:
        attrs += ' class="b"'
    elif is_large(size):
        attrs += ' class="l"'
    elif css_class:
        attrs += f' class="{css_class}"'
    if rotate:
        attrs += f' transform="rotate({-rotate} {x:.2f} {y - cap_height(size) / 2:.2f})"'
    prefix = ""
    if title:
        title_alpha = Marks.POINT_LABEL_TITLE_ALPHA * alpha
        title_attrs = f'font-size="{FontSizes.POINT_LABEL_TITLES}" fill-opacity="{title_alpha}"'
        prefix = f"<tspan {title_attrs}>{escape(title)} </tspan>"
    return f"<text {attrs}>{prefix}{escape(s)}</text>"


def _title_width(title: str) -> float:
    return text_width(f"{title} ", FontSizes.POINT_LABEL_TITLES) if title else 0


def line_titles(t: Text) -> tuple[str, ...]:
    """One title per line of t, '' where a line has none."""
    line_count = t.text.count("\n") + 1
    if t.line_titles and len(t.line_titles) != line_count:
        raise ValueError(f"{len(t.line_titles)} line_titles for {line_count} lines in {t.text!r}")
    return t.line_titles or ("",) * line_count


def line_step(size: float) -> float:
    """Baseline to baseline distance between the lines of a multi-line data text."""
    return cap_height(size) + Layout.DATA_TEXT_LINE_GAP


def block_height(t: Text) -> float:
    """Top of the first line to the baseline of the last line of a data text, in points."""
    return cap_height(t.size) + t.text.count("\n") * line_step(t.size)


def place(t: Text, sx: Scale, sy: Scale) -> tuple[float, float, float, float, float]:
    """Anchor x, first line's baseline y and bounding box (x0, x1, top) of a data text, in points.

    A text with newlines is one block: va aligns the whole block, ha every line. Line titles widen their line.
    """
    lines = t.text.split("\n")
    titles = line_titles(t)
    width = max(_title_width(title) + text_width(line, t.size) for title, line in zip(titles, lines))
    first_line = cap_height(t.size)
    height = block_height(t)
    x, y = sx(t.x) + t.dx, sy(t.y) - t.dy
    top = {"bottom": y - height, "center": y - height / 2, "top": y}[t.va]
    x0 = {"left": x, "center": x - width / 2, "right": x - width}[t.ha]
    return x, top + first_line, x0, x0 + width, top
