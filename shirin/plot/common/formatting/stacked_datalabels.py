from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from ...config import FontSizes, Layout, Marks
from ...svg import Chart, Text
from .datalabels import percentage_label
from .text_contrast import get_text_color_for_background


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
            background = row_colors[index] if row_colors is not None else palette[str(category)]
            chart.texts.append(Text(
                x,
                y,
                percentage_label(value_percentage, 0, suffix),
                get_text_color_for_background(background),
                FontSizes.DATALABELS,
                alpha=Marks.INNER_LABEL_ALPHA,
                keep_color=True,
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
