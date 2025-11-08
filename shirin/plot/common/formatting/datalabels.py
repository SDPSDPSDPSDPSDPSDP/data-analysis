import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.container import BarContainer
from typing import List, Dict
import pandas as pd

from ...config import TextColors, FontSizes
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
) -> None:
    for patch in patches:
        dimension = patch.get_height() if orientation == 'vertical' else patch.get_width()
        if dimension > 0:
            if formatting == 'totals':
                text: str = f'{dimension:,.0f}'.replace(",", ".")
            elif formatting == 'percentage':
                text: str = f'{dimension:,.1f}%'.replace(",", ".")
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
            ha="center", va="bottom",
            fontsize=FontSizes.DATALABELS,
            color=TextColors.LIGHT_GREY
        )
    elif orientation == 'horizontal':
        plt.text(
            position,
            patch.get_y() + patch.get_height() / 2.0,
            text,
            ha="left", va="center",
            fontsize=FontSizes.DATALABELS,
            color=TextColors.LIGHT_GREY
        )


def format_datalabels(
    plot: BarContainer,
    label_offset: float = 0.01,
    formatting: str = 'totals',
    orientation: str = 'vertical',
) -> None:
    patches: List[Patch] = plot.patches
    label_offset = _calculate_label_offset(patches, label_offset, orientation)
    _format_labels(patches, label_offset, formatting, orientation)


def format_datalabels_stacked(
    plot: BarContainer,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal'
) -> None:
    max_count = pivot_data.sum(axis=1).max()
    threshold = 0.04 * max_count
    ax = plt.gca()

    for index, row_values in enumerate(pivot_data.values):
        total = row_values.sum()
        cumulative_sum = 0

        for col_index, value in enumerate(row_values):
            # Get the category name and its color
            category = pivot_data.columns[col_index]
            bg_color = palette.get(category, '#000000')  # Default to black if not found
            
            # Determine text color based on background luminance
            text_color = get_text_color_for_background(bg_color)
            
            # Calculate percentage
            value_percentage = (value / total) * 100
            cumulative_sum += value
            
            # Only show label if bar is visible enough
            if value >= threshold:
                if orientation == 'horizontal':
                    ax.text(
                        cumulative_sum - value / 2, index,
                        f"{value_percentage:.0f}%",
                        ha='center', va='center',
                        color=text_color,
                        fontsize=FontSizes.DATALABELS
                    )
                else:  # vertical
                    ax.text(
                        index, cumulative_sum - value / 2,
                        f"{value_percentage:.0f}%",
                        ha='center', va='center',
                        color=text_color,
                        fontsize=FontSizes.DATALABELS
                    )


def format_datalabels_stacked_normalized(
    plot: BarContainer,
    pivot_data: pd.DataFrame,
    palette: Dict,
    orientation: str = 'horizontal'
) -> None:
    threshold = 0.04  # Show label only if segment is at least 4%
    ax = plt.gca()

    for index, row_values in enumerate(pivot_data.values):
        cumulative_sum = 0

        for col_index, value in enumerate(row_values):
            # Get the category name and its color
            category = pivot_data.columns[col_index]
            bg_color = palette.get(category, '#000000')  # Default to black if not found
            
            # Determine text color based on background luminance
            text_color = get_text_color_for_background(bg_color)
            
            # Calculate percentage (value is already normalized between 0-1)
            value_percentage = value * 100
            cumulative_sum += value
            
            # Only show label if bar is visible enough
            if value >= threshold:
                if orientation == 'horizontal':
                    ax.text(
                        cumulative_sum - value / 2, index,
                        f"{value_percentage:.0f}%",
                        ha='center', va='center',
                        color=text_color,
                        fontsize=FontSizes.DATALABELS
                    )
                else:  # vertical
                    ax.text(
                        index, cumulative_sum - value / 2,
                        f"{value_percentage:.0f}%",
                        ha='center', va='center',
                        color=text_color,
                        fontsize=FontSizes.DATALABELS
                    )