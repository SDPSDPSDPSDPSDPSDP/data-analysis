import math
from typing import List

from ...config import FontSizes, Marks, TextColors
from ...svg import Chart, Text, Wedge
from ....number_format import format_percentage


def render_piechart(
    chart: Chart,
    values: List[float],
    colors: List[str],
    donut: bool,
    n_after_comma: int,
    value_datalabel: int,
    pctdistance: float,
) -> List[Text]:
    """Draw the pie clockwise from 12 o'clock; returns one percentage text per slice ('' below value_datalabel)."""
    chart.x.lim = chart.y.lim = (-1, 1)
    chart.x.visible = chart.y.visible = False
    total = sum(values)
    texts: List[Text] = []
    start = 0.0
    for value, color in zip(values, colors):
        end = start + value / total
        chart.wedges.append(Wedge(start, end, color))
        percentage = value / total * 100
        angle = math.pi * (start + end)
        texts.append(Text(
            pctdistance * math.sin(angle),
            pctdistance * math.cos(angle),
            format_percentage(percentage, n_after_comma) if percentage >= value_datalabel else '',
            TextColors.BLACK,
            FontSizes.TEXT,
        ))
        start = end
    if donut:
        chart.wedges.append(Wedge(0, 1, TextColors.WHITE, radius=Marks.DONUT_HOLE_RADIUS))
    chart.texts += texts
    return texts
