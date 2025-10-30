import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.container import BarContainer
from typing import List#, Dict
import pandas as pd

from ..config import TextColors, FontSizes

def _calculate_label_offset(
    patches: List[Patch], label_offset: float, orientation: str
) -> float:
    """Calculates label offset based on the largest dimension of patches."""
    dimension_getter = {'vertical': 'get_height', 'horizontal': 'get_width'}
    max_dimension = max(getattr(p, dimension_getter[orientation])() for p in patches)
    return max_dimension * label_offset

def _format_labels(
    patches: List[Patch],
    label_offset: float,
    formatting: str,
    orientation: str,
) -> None:
    """Formats labels for data visualization (both vertical and horizontal)."""
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
    """Adds text to the plot dynamically based on the orientation."""
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
    """Main entry point to format data labels on the plot."""
    patches: List[Patch] = plot.patches
    label_offset = _calculate_label_offset(patches, label_offset, orientation)
    _format_labels(patches, label_offset, formatting, orientation)

def format_datalabels_stacked(plot:BarContainer, pivot_data: pd.DataFrame, reverse: bool = False, orientation: str = 'horizontal') -> None:
    max_count = pivot_data.sum(axis=1).max()
    threshold = 0.04 * max_count
    ax = plt.gca()

    for index, row_values in enumerate(pivot_data.values):
        total = row_values.sum()
        cumulative_sum = 0

        for value in row_values:
            # calculating the percentage
            value_percentage = (value / total) * 100
            cumulative_sum += value
            
            # label formatting
            if value >= threshold: # only plot if the bar is visible
                if reverse:
                    color = TextColors.BLACK if cumulative_sum - value / 2 < max_count / 2 else TextColors.WHITE
                else:
                    color = TextColors.WHITE if cumulative_sum - value / 2 < max_count / 2 else TextColors.BLACK
                
                if orientation == 'horizontal':
                    ax.text(cumulative_sum - value / 2, index, 
                            f"{value_percentage:.0f}%", 
                            ha='center', va='center', 
                            color=color, 
                            fontsize=FontSizes.DATALABELS)
                else:  # vertical
                    ax.text(index, cumulative_sum - value / 2, 
                            f"{value_percentage:.0f}%", 
                            ha='center', va='center', 
                            color=color, 
                            fontsize=FontSizes.DATALABELS)
                
# def format_datalabels_stacked(
#     plot: BarContainer, 
#     pivot_data: pd.DataFrame, 
#     reverse: bool = False
# ) -> None:
#     """
#     Formats data labels for a stacked bar plot with dynamic text colors based on bar categories.

#     Args:
#         plot (BarContainer): The matplotlib plot object.
#         pivot_data (pd.DataFrame): The pivot data used to generate the plot.
#         reverse (bool): If True, reverse the color mapping for the categories.
#     """
#     max_count = pivot_data.sum(axis=1).max()
#     threshold = 0.04 * max_count  # Minimum size of bar to display label

#     # Handle the case for exactly two categories
#     if len(pivot_data.columns) == 2:
#         category_to_color = {
#             pivot_data.columns[0]: TextColors.WHITE if reverse else TextColors.BLACK,
#             pivot_data.columns[1]: TextColors.BLACK if reverse else TextColors.WHITE,
#         }
#     else:  # For more than two categories, use a default fallback
#         category_to_color = {
#             pivot_data.columns[0]: TextColors.WHITE if reverse else TextColors.BLACK,
#         }
#         for column in pivot_data.columns[1:]:
#             category_to_color[column] = TextColors.BLACK

#     for index, row_values in enumerate(pivot_data.values):  # Iterate through rows in the pivot data
#         total = row_values.sum()
#         cumulative_sum = plot.patches[index * len(row_values)].get_x()  # Starting position
#         for col_index, value in enumerate(row_values):
#             hue_category = pivot_data.columns[col_index]
#             text_color = category_to_color.get(hue_category, TextColors.BLACK)
            
#             # Draw percentage labels only for visible bars
#             if value >= threshold:
#                 value_percentage = (value / total) * 100
#                 plt.text(
#                     x=cumulative_sum + value / 2,
#                     y=index,
#                     s=f"{value_percentage:.0f}%",
#                     ha="center",
#                     va="center",
#                     color=text_color,
#                     fontsize=FontSizes.DATALABELS,
#                 )
#             cumulative_sum += value  # Update cumulative position for the next bar