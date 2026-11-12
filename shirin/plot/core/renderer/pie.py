import math
from typing import List, Tuple

from ....number_format import format_percentage
from ...config import FontSizes, Layout, Marks, TextColors
from ...svg import Chart, Text, Wedge
from ...svg.fonts import cap_height


def render_piechart(
    chart: Chart,
    values: List[float],
    colors: List[str],
    donut: bool,
    n_after_comma: int,
    value_datalabel: int,
    pctdistance: float,
    headlines: List[str],
    datalabels: bool = True,
) -> Tuple[List[Text], List[Text]]:
    """Draw the pie clockwise from 12 o'clock.

    headlines: one per slice ('' = none), drawn large above the slice's percentage (centered when it has none).
    Returns one percentage text per slice ('' below value_datalabel) and the drawn headline texts.
    """
    chart.x.lim = chart.y.lim = (-1 / Marks.PIE_RADIUS, 1 / Marks.PIE_RADIUS)
    chart.x.visible = chart.y.visible = False
    total = sum(values)
    texts: List[Text] = []
    headline_texts: List[Text] = []
    start = 0.0
    for value, color, headline in zip(values, colors, headlines):
        end = start + value / total
        chart.wedges.append(Wedge(start, end, color))
        percentage = value / total * 100
        angle = math.pi * (start + end)
        x, y = pctdistance * math.sin(angle), pctdistance * math.cos(angle)
        label = format_percentage(percentage, n_after_comma) if percentage >= value_datalabel else ''
        texts.append(Text(x, y, label, TextColors.BLACK, FontSizes.TEXT, keep_color=True))
        if headline:
            above_label = datalabels and bool(label)
            headline_texts.append(Text(
                x, y, headline, TextColors.BLACK, FontSizes.SLICE_LABEL,
                va='bottom' if above_label else 'center',
                dy=cap_height(FontSizes.TEXT) / 2 + Layout.SLICE_LABEL_GAP if above_label else 0,
                keep_color=True,
            ))
        start = end
    if donut:
        chart.donut_hole = Marks.DONUT_HOLE_RADIUS
    if datalabels:
        chart.texts += texts
    chart.texts += headline_texts
    return texts, headline_texts
