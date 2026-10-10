from typing import Dict, Optional
import pandas as pd

from ...config import FontSizes, Layout, TextColors
from ...svg import Chart, Rect, Text
from ....number_format import format_thousands
from .text_contrast import get_text_color_for_background


def _length(rect: Rect, orientation: str) -> float:
    return rect.height if orientation == 'vertical' else rect.width


def _add_text(chart: Chart, rect: Rect, text: str, orientation: str) -> None:
    gap = Layout.DATALABEL_GAP
    if orientation == 'vertical':
        label = Text((rect.x0 + rect.x1) / 2, rect.y1, text, TextColors.LIGHT_GREY, FontSizes.DATALABELS, 'center', 'bottom', dy=gap)
    else:
        label = Text(rect.x1, (rect.y0 + rect.y1) / 2, text, TextColors.LIGHT_GREY, FontSizes.DATALABELS, 'left', 'center', dx=gap)
    chart.texts.append(label)


def format_datalabels(
    chart: Chart,
    formatting: str = 'totals',
    orientation: str = 'vertical',
    suffix: Optional[str] = None,
) -> None:
    rects = chart.rects
    lengths = [_length(r, orientation) for r in rects]
    total = sum(lengths)
    suffix = suffix.strip() if suffix else ''

    for rect, length in zip(rects, lengths):
        if length <= 0:
            continue
        if formatting == 'percentage':
            percentage = length / total * 100 if total > 0 else 0
            text = f'{percentage:,.1f}%'.replace(',', '.')
        else:
            text = format_thousands(length)
        if suffix:
            text = f"{text} {suffix}"
        _add_text(chart, rect, text, orientation)


def _format_stacked_percentage(value_percentage: float, suffix: Optional[str]) -> str:
    if suffix is None:
        return f'{value_percentage:.0f}%'
    if suffix.strip() == '':
        return f'{value_percentage:.0f}'
    return f'{value_percentage:.0f} {suffix.strip()}'


def _add_stacked_labels(
    chart: Chart,
    pivot_data: pd.DataFrame,
    percentages,
    palette: Dict,
    orientation: str,
    suffix: Optional[str],
    threshold: float,
) -> None:
    for index, (row_values, row_percentages) in enumerate(zip(pivot_data.values, percentages)):
        cumulative_sum = 0
        for category, value, value_percentage in zip(pivot_data.columns, row_values, row_percentages):
            cumulative_sum += value
            if value < threshold:
                continue
            center = cumulative_sum - value / 2
            x, y = (center, index) if orientation == 'horizontal' else (index, center)
            chart.texts.append(Text(
                x,
                y,
                _format_stacked_percentage(value_percentage, suffix),
                get_text_color_for_background(palette[str(category)]),
                FontSizes.DATALABELS,
            ))


def format_datalabels_stacked(
    chart: Chart,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal',
    suffix: Optional[str] = None,
) -> None:
    values = pivot_data.values
    percentages = values / values.sum(axis=1, keepdims=True) * 100
    threshold = Layout.STACKED_LABEL_MIN_SHARE * pivot_data.sum(axis=1).max()
    _add_stacked_labels(chart, pivot_data, percentages, palette, orientation, suffix, threshold)


def format_datalabels_stacked_normalized(
    chart: Chart,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal',
    suffix: Optional[str] = None,
) -> None:
    _add_stacked_labels(chart, pivot_data, pivot_data.values * 100, palette, orientation, suffix, threshold=Layout.STACKED_LABEL_MIN_SHARE)
