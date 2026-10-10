from matplotlib.axes import Axes
from matplotlib.patches import Patch
from typing import Dict, List, Optional
import pandas as pd

from ...config import FontSizes, TextColors
from ....stats.number_format import format_thousands
from .text_contrast import get_text_color_for_background


def _length(patch: Patch, orientation: str) -> float:
    return patch.get_height() if orientation == 'vertical' else patch.get_width()


def _add_text(plot: Axes, patch: Patch, position: float, text: str, orientation: str) -> None:
    if orientation == 'vertical':
        x, y, ha, va = patch.get_x() + patch.get_width() / 2.0, position, 'center', 'bottom'
    else:
        x, y, ha, va = position, patch.get_y() + patch.get_height() / 2.0, 'left', 'center'
    plot.text(x, y, text, ha=ha, va=va, fontsize=FontSizes.DATALABELS, color=TextColors.LIGHT_GREY)


def format_datalabels(
    plot: Axes,
    label_offset: float = 0.01,
    formatting: str = 'totals',
    orientation: str = 'vertical',
    suffix: Optional[str] = None,
) -> None:
    patches: List[Patch] = plot.patches
    lengths = [_length(p, orientation) for p in patches]
    offset = max(lengths) * label_offset
    total = sum(lengths)
    suffix = suffix.strip() if suffix else ''

    for patch, length in zip(patches, lengths):
        if length <= 0:
            continue
        if formatting == 'percentage':
            percentage = length / total * 100 if total > 0 else 0
            text = f'{percentage:,.1f}%'.replace(',', '.')
        else:
            text = format_thousands(length)
        if suffix:
            text = f"{text} {suffix}"
        _add_text(plot, patch, length + offset, text, orientation)


def _format_stacked_percentage(value_percentage: float, suffix: Optional[str]) -> str:
    if suffix is None:
        return f'{value_percentage:.0f}%'
    if suffix.strip() == '':
        return f'{value_percentage:.0f}'
    return f'{value_percentage:.0f} {suffix.strip()}'


def _add_stacked_labels(
    plot: Axes,
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
            plot.text(
                x,
                y,
                _format_stacked_percentage(value_percentage, suffix),
                ha='center',
                va='center',
                color=get_text_color_for_background(palette.get(category, '#000000')),
                fontsize=FontSizes.DATALABELS,
            )


def format_datalabels_stacked(
    plot: Axes,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal',
    suffix: Optional[str] = None,
) -> None:
    values = pivot_data.values
    percentages = values / values.sum(axis=1, keepdims=True) * 100
    threshold = 0.04 * pivot_data.sum(axis=1).max()
    _add_stacked_labels(plot, pivot_data, percentages, palette, orientation, suffix, threshold)


def format_datalabels_stacked_normalized(
    plot: Axes,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal',
    suffix: Optional[str] = None,
) -> None:
    _add_stacked_labels(plot, pivot_data, pivot_data.values * 100, palette, orientation, suffix, threshold=0.04)
