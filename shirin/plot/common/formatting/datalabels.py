from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from ....number_format import format_compact, format_percentage, format_thousands
from ...config import FontSizes, Layout, Marks, TextColors
from ...svg import Chart, Rect, Text
from .text_contrast import get_text_color_for_background


def _length(rect: Rect, orientation: str) -> float:
    return rect.height if orientation == 'vertical' else rect.width


def _add_text(chart: Chart, rect: Rect, text: str, orientation: str, short_text: Optional[str] = None) -> None:
    gap = Layout.DATALABEL_GAP
    if orientation == 'vertical':
        label = Text((rect.x0 + rect.x1) / 2, rect.y1, text, TextColors.FAINT_GREY, FontSizes.DATALABELS, 'center', 'bottom', dy=gap, short_text=short_text)
    else:
        label = Text(rect.x1, (rect.y0 + rect.y1) / 2, text, TextColors.FAINT_GREY, FontSizes.DATALABELS, 'left', 'center', dx=gap)
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

    for rect, length in zip(rects, lengths):
        if length <= 0:
            continue
        if formatting == 'percentage':
            _add_text(chart, rect, _percentage_label(length / total * 100 if total > 0 else 0, 1, suffix), orientation)
        else:
            _add_text(chart, rect, with_suffix(format_thousands(length), suffix), orientation, with_suffix(format_compact(length), suffix))


def with_suffix(text: str, suffix: Optional[str]) -> str:
    return f'{text} {suffix.strip()}' if suffix and suffix.strip() else text


def _percentage_label(percentage: float, decimals: int, suffix: Optional[str]) -> str:
    """A suffix replaces the '%' sign; an empty suffix drops it."""
    if suffix is None:
        return format_percentage(percentage, decimals)
    return with_suffix(format_thousands(percentage, decimals), suffix)


def _add_stacked_labels(
    chart: Chart,
    pivot_data: pd.DataFrame,
    percentages,
    palette: Dict,
    orientation: str,
    suffix: Optional[str],
    threshold: float,
    row_colors: Optional[List[str]] = None,
) -> None:
    """row_colors: background per row, overriding the palette color of each column."""
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
                _percentage_label(value_percentage, 0, suffix),
                get_text_color_for_background(row_colors[index] if row_colors is not None else palette[str(category)]),
                FontSizes.DATALABELS,
                alpha=Marks.INNER_LABEL_ALPHA,
            ))


def format_datalabels_stacked(
    chart: Chart,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal',
    suffix: Optional[str] = None,
) -> None:
    values = pivot_data.values
    totals = values.sum(axis=1, keepdims=True)
    percentages = np.divide(values * 100, totals, out=np.zeros(values.shape), where=totals != 0)
    threshold = Layout.STACKED_LABEL_MIN_SHARE * pivot_data.sum(axis=1).max()
    _add_stacked_labels(chart, pivot_data, percentages, palette, orientation, suffix, threshold)


def format_datalabels_stacked_normalized(
    chart: Chart,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal',
    suffix: Optional[str] = None,
    row_colors: Optional[List[str]] = None,
) -> None:
    _add_stacked_labels(
        chart, pivot_data, pivot_data.values * 100, palette, orientation, suffix,
        threshold=Layout.STACKED_LABEL_MIN_SHARE, row_colors=row_colors,
    )
