import matplotlib.pyplot as plt
from matplotlib.container import BarContainer
from matplotlib.patches import Patch
from typing import Dict, List, Optional
import pandas as pd

from ...config import FontSizes, TextColors
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
                text: str = f'{dimension:,.0f}'.replace(',', '.')
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


def format_datalabels_stacked(
    plot: BarContainer,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal',
    suffix: Optional[str] = None,
) -> None:
    max_count = pivot_data.sum(axis=1).max()
    threshold = 0.04 * max_count
    ax = plt.gca()

    for index, row_values in enumerate(pivot_data.values):
        total = row_values.sum()
        cumulative_sum = 0

        for col_index, value in enumerate(row_values):
            category = pivot_data.columns[col_index]
            bg_color = palette.get(category, '#000000')
            text_color = get_text_color_for_background(bg_color)

            value_percentage = (value / total) * 100
            cumulative_sum += value

            if value >= threshold:
                text = _format_stacked_percentage(value_percentage, suffix)
                if orientation == 'horizontal':
                    ax.text(
                        cumulative_sum - value / 2,
                        index,
                        text,
                        ha='center',
                        va='center',
                        color=text_color,
                        fontsize=FontSizes.DATALABELS,
                    )
                else:
                    ax.text(
                        index,
                        cumulative_sum - value / 2,
                        text,
                        ha='center',
                        va='center',
                        color=text_color,
                        fontsize=FontSizes.DATALABELS,
                    )


def format_datalabels_stacked_normalized(
    plot: BarContainer,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal',
    suffix: Optional[str] = None,
) -> None:
    threshold = 0.04
    ax = plt.gca()

    for index, row_values in enumerate(pivot_data.values):
        cumulative_sum = 0

        for col_index, value in enumerate(row_values):
            category = pivot_data.columns[col_index]
            bg_color = palette.get(category, '#000000')
            text_color = get_text_color_for_background(bg_color)

            value_percentage = value * 100
            cumulative_sum += value

            if value >= threshold:
                text = _format_stacked_percentage(value_percentage, suffix)
                if orientation == 'horizontal':
                    ax.text(
                        cumulative_sum - value / 2,
                        index,
                        text,
                        ha='center',
                        va='center',
                        color=text_color,
                        fontsize=FontSizes.DATALABELS,
                    )
                else:
                    ax.text(
                        index,
                        cumulative_sum - value / 2,
                        text,
                        ha='center',
                        va='center',
                        color=text_color,
                        fontsize=FontSizes.DATALABELS,
                    )