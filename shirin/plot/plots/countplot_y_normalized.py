from typing import Any, Dict, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd

from ..config import FigureSize
from ..formatting import format_optional_legend, format_ticks, format_xy_labels
from ..utils import filter_top_n_categories
from .countplot_y import _dynamic_figsize_height


def _calculate_normalized_counts(
    df: pd.DataFrame, y: str, hue: str
) -> pd.DataFrame:
    """Calculate normalized counts (as percentages) for the bars."""
    counts = df.groupby([y, hue]).size()
    normalized_counts = counts / counts.groupby(level=0).sum()
    return normalized_counts.rename("percentage").reset_index()


def countplot_y_normalized(
    df: pd.DataFrame,
    y: str,
    hue: str,
    palette: Dict[Any, str],
    label_map: Optional[Dict[Any, str]] = None,
    xlabel: str = 'Percentage',
    ylabel: str = '',
    plot_legend: bool = True,
    legend_offset: float = 1.13,
    ncol: int = 2,
    top_n: Optional[int] = None,
    figsize_height: Union[str, float] = 'dynamic',
    order_type: str = 'frequency',
) -> None:
    """Create a normalized horizontal stacked count plot.
    
    Args:
        df: Input DataFrame
        y: Column name for y-axis (categories)
        hue: Column name for color grouping
        palette: Color mapping dictionary
        label_map: Mapping for legend labels
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        plot_legend: Whether to display legend
        legend_offset: Position offset for legend
        ncol: Number of columns in legend
        top_n: Limit to top N categories
        figsize_height: Figure height ('dynamic', 'standard', or numeric)
        order_type: Sorting order ('frequency' or 'alphabetical')
    """
    # Validate palette contains all hue values
    unique_hue_values = df[hue].unique()
    if not all(hue_value in palette for hue_value in unique_hue_values):
        missing_keys = [val for val in unique_hue_values if val not in palette]
        raise ValueError(
            f"The palette dictionary is missing keys for hue values: {missing_keys}"
        )

    df = df.copy()
    df[y] = df[y].astype(str)
    df[hue] = df[hue].astype(str)
    if palette is not None:
        palette = {str(k): str(v) for k, v in palette.items()}

    if top_n is not None:
        df = filter_top_n_categories(df, y, top_n)

    normalized_df = _calculate_normalized_counts(df, y, hue)
    normalized_pivot = normalized_df.pivot(index=y, columns=hue, values="percentage")
    normalized_pivot = normalized_pivot.fillna(0)

    # Sort rows based on ordering type
    if order_type == 'frequency':
        normalized_pivot['_order'] = normalized_pivot.sum(axis=1)
        normalized_pivot = normalized_pivot.sort_values(by='_order', ascending=True)
        normalized_pivot = normalized_pivot.drop(columns=['_order'])
    elif order_type == 'alphabetical':
        normalized_pivot = normalized_pivot.sort_index(ascending=False)

    figsize_height = _dynamic_figsize_height(df, y, figsize_height)

    plt.figure(figsize=(FigureSize.WIDTH, figsize_height))
    colors = [palette[col] for col in normalized_pivot.columns]
    ax = plt.gca()
    plot = normalized_pivot.plot(
        kind='barh',
        stacked=True,
        color=colors,
        edgecolor='none',
        alpha=1,
        width=0.8,
        ax=ax
    )

    if label_map is None and plot_legend:
        label_map = {str(key): str(key) for key in normalized_df[hue].unique()}
    elif label_map is not None:
        label_map = {str(key): str(value) for key, value in label_map.items()}

    format_xy_labels(ax, xlabel=xlabel, ylabel=ylabel)
    format_optional_legend(ax, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot=ax, x_grid=True, percentage_x=True)