import math
from typing import List, Optional, Tuple

from ....number_format import format_percentage
from ...config import FontSizes, Layout, Marks, TextColors
from ...svg import Chart, Text, Wedge
from ...svg.fonts import cap_height, wrap_text
from ...svg.marks import line_step


def _wrap_headline(headline: str) -> str:
    """Wrap each line of headline to Layout.SLICE_LABEL_MAX_WIDTH; newlines the caller put in stay."""
    return '\n'.join(
        line for part in headline.split('\n')
        for line in wrap_text(part, FontSizes.SLICE_LABEL, Layout.SLICE_LABEL_MAX_WIDTH)
    )


def _headline_text(x: float, y: float, headline: str, percentage: Optional[Text]) -> Text:
    """Headline above the drawn percentage, the pair centered on the slice's label point (shifts percentage down).

    percentage: None when the slice shows none; the headline then centers on the label point alone.
    """
    headline = _wrap_headline(headline)
    if percentage is None:
        return Text(x, y, headline, TextColors.BLACK, FontSizes.SLICE_LABEL, keep_color=True)
    headline_height = cap_height(FontSizes.SLICE_LABEL) + headline.count('\n') * line_step(FontSizes.SLICE_LABEL)
    percentage.dy = -(headline_height + Layout.SLICE_LABEL_GAP) / 2
    return Text(
        x, y, headline, TextColors.BLACK, FontSizes.SLICE_LABEL, va='bottom',
        dy=percentage.dy + cap_height(percentage.size) / 2 + Layout.SLICE_LABEL_GAP, keep_color=True,
    )


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
        percentage_text = Text(x, y, label, TextColors.BLACK, FontSizes.TEXT, keep_color=True)
        texts.append(percentage_text)
        if headline:
            headline_texts.append(_headline_text(x, y, headline, percentage_text if datalabels and label else None))
        start = end
    if donut:
        chart.donut_hole = Marks.DONUT_HOLE_RADIUS
    if datalabels:
        chart.texts += texts
    chart.texts += headline_texts
    return texts, headline_texts
