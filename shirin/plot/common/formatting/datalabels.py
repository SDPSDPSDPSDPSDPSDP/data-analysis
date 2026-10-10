import matplotlib.pyplot as plt
from matplotlib.container import BarContainer
from matplotlib.patches import Patch
from typing import Dict, List, Optional
import pandas as pd

from ...config import FontSizes, TextColors
from ....stats.number_format import format_thousands
from .text_contrast import get_text_color_for_background


def _calculate_label_offset(
    patches: List[Patch], label_offset: float, orientation: str
) -> float:
    dimension_getter = {'vertical': 'get_height', 'horizontal': 'get_width'}
    max_dimension = max(getattr(p, dimension_getter[orientation])() for p in patches)
    return max_dimension * label_offset


def _format_labels(
    patches: List[Patch],
    label_offset: float,
    formatting: str,
    orientation: str,
    suffix: Optional[str] = None,
) -> None:
    if formatting == 'percentage':
        dimension_getter = {'vertical': 'get_height', 'horizontal': 'get_width'}
        total_dimension = sum(getattr(p, dimension_getter[orientation])() for p in patches)

    for patch in patches:
        dimension = patch.get_height() if orientation == 'vertical' else patch.get_width()
        if dimension > 0:
            if formatting == 'totals':
                text: str = format_thousands(dimension)

            elif formatting == 'percentage':
                percentage = (dimension / total_dimension * 100) if total_dimension > 0 else 0
                text = f'{percentage:,.1f}%'.replace(',', '.')
            if suffix is not None and suffix.strip() != '':
                text = f"{text} {suffix.strip()}"
            _add_text(patch, dimension + label_offset, text, orientation)


def _add_text(
    patch: Patch,
    position: float,
    text: str,
    orientation: str,
) -> None:
    if orientation == 'vertical':
        plt.text(
            patch.get_x() + patch.get_width() / 2.0,
            position,
            text,
            ha='center',
            va='bottom',
            fontsize=FontSizes.DATALABELS,
            color=TextColors.LIGHT_GREY,
        )
    elif orientation == 'horizontal':
        plt.text(
            position,
            patch.get_y() + patch.get_height() / 2.0,
            text,
            ha='left',
            va='center',
            fontsize=FontSizes.DATALABELS,
            color=TextColors.LIGHT_GREY,
        )


def format_datalabels(
    plot: BarContainer,
    label_offset: float = 0.01,
    formatting: str = 'totals',
    orientation: str = 'vertical',
    suffix: Optional[str] = None,
) -> None:
    patches: List[Patch] = plot.patches
    label_offset = _calculate_label_offset(patches, label_offset, orientation)
    _format_labels(patches, label_offset, formatting, orientation, suffix=suffix)


def _format_stacked_percentage(value_percentage: float, suffix: Optional[str]) -> str:
    if suffix is None:
        return f'{value_percentage:.0f}%'
    if suffix.strip() == '':
        return f'{value_percentage:.0f}'
    return f'{value_percentage:.0f} {suffix.strip()}'


def _add_stacked_labels(
    pivot_data: pd.DataFrame,
    percentages,
    palette: Dict,
    orientation: str,
    suffix: Optional[str],
    threshold: float,
) -> None:
    ax = plt.gca()
    for index, (row_values, row_percentages) in enumerate(zip(pivot_data.values, percentages)):
        cumulative_sum = 0
        for category, value, value_percentage in zip(pivot_data.columns, row_values, row_percentages):
            cumulative_sum += value
            if value < threshold:
                continue
            center = cumulative_sum - value / 2
            x, y = (center, index) if orientation == 'horizontal' else (index, center)
            ax.text(
                x,
                y,
                _format_stacked_percentage(value_percentage, suffix),
                ha='center',
                va='center',
                color=get_text_color_for_background(palette.get(category, '#000000')),
                fontsize=FontSizes.DATALABELS,
            )


def format_datalabels_stacked(
    plot: BarContainer,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal',
    suffix: Optional[str] = None,
) -> None:
    values = pivot_data.values
    percentages = values / values.sum(axis=1, keepdims=True) * 100
    threshold = 0.04 * pivot_data.sum(axis=1).max()
    _add_stacked_labels(pivot_data, percentages, palette, orientation, suffix, threshold)


def format_datalabels_stacked_normalized(
    plot: BarContainer,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal',
    suffix: Optional[str] = None,
) -> None:
    _add_stacked_labels(pivot_data, pivot_data.values * 100, palette, orientation, suffix, threshold=0.04)
