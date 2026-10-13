"""Title, subtitle and legend rows above the plot area."""
from typing import Callable, List, Tuple

from ..config import FontSizes, Layout, TextColors
from . import marks
from .chart import Chart
from .fonts import cap_height, text_width

HeaderRow = Tuple[float, List[str]]


def _legend_rows(items: List[Tuple[str, str, str]], max_width: float) -> List[List[Tuple[str, str, str, float]]]:
    """One row of swatch + label items, wrapped when wider than the plot area."""
    rows: List[List[Tuple[str, str, str, float]]] = [[]]
    used = 0.0
    for color, label, value in items:
        width = Layout.SWATCH + Layout.SWATCH_GAP + text_width(f'{label} {value}'.strip(), FontSizes.LEGEND)
        if rows[-1] and used + Layout.LEGEND_ITEM_GAP + width > max_width:
            rows.append([])
            used = 0.0
        used += (Layout.LEGEND_ITEM_GAP if rows[-1] else 0) + width
        rows[-1].append((color, label, value, width))
    return [row for row in rows if row]


def header_rows(chart: Chart, plot_w: float, color: Callable[[str], str]) -> Tuple[List[HeaderRow], float]:
    """(width, svg items) per row and the plot top below them.

    Rows are drawn from x=0 and shifted to center over the plot once its final width is known.
    """
    rows: List[HeaderRow] = []
    top = float(Layout.PAD)

    def header_row(height: float) -> float:
        nonlocal top
        row_top = top
        top += height + Layout.ROW_GAP
        return row_top

    if chart.title or chart.subtitle:
        top += Layout.TITLE_TOP_GAP
    for text, size, bold, text_color in (
        (chart.title, FontSizes.TITLE, True, color(TextColors.BLACK)),
        (chart.subtitle, FontSizes.TEXT, False, color(TextColors.LIGHT_GREY)),
    ):
        if text:
            row_top = header_row(size)
            rows.append((text_width(text, size, bold), [marks.text(0, row_top + cap_height(size), text, size, text_color, bold=bold)]))
    legend_rows = _legend_rows(chart.legend, plot_w)
    if legend_rows and rows:
        top += Layout.LEGEND_GAP
    for row in legend_rows:
        row_top = header_row(Layout.SWATCH)
        x = 0.0
        items: List[str] = []
        for swatch, label, value, item_width in row:
            items.append(f'<circle cx="{x + Layout.SWATCH / 2:.2f}" cy="{row_top + Layout.SWATCH / 2:.2f}" r="{Layout.SWATCH / 2}" fill="{swatch}"/>')
            baseline = row_top + Layout.SWATCH / 2 + cap_height(FontSizes.LEGEND) / 2
            label_x = x + Layout.SWATCH + Layout.SWATCH_GAP
            items.append(marks.text(label_x, baseline, label, FontSizes.LEGEND, color(TextColors.DARK_GREY)))
            if value:
                value_x = label_x + text_width(f'{label} ', FontSizes.LEGEND)
                items.append(marks.text(value_x, baseline, value, FontSizes.LEGEND, color(TextColors.FAINT_GREY)))
            x += item_width + Layout.LEGEND_ITEM_GAP
        rows.append((x - Layout.LEGEND_ITEM_GAP, items))
    plot_top = top - Layout.ROW_GAP + Layout.PLOT_GAP if rows else top
    return rows, plot_top
