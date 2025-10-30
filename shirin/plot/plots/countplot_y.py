from typing import Any, Dict, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from ..config import FigureSize
from ..formatting import (
    format_datalabels,
    format_datalabels_stacked,
    format_optional_legend,
    format_ticks,
    format_xy_labels,
)
from ..utils import filter_top_n_categories, handle_palette

def _dynamic_figsize_height(
    df: pd.DataFrame, y: str, figsize_height: Union[str, float] = 'dynamic'
) -> float:
    """Calculate dynamic figure height based on number of categories."""
    if figsize_height == 'dynamic':
        return (len(df[y].value_counts()) / 2) + 1
    elif figsize_height == 'standard':
        return FigureSize.HEIGHT
    return float(figsize_height)

def _transpose_data_for_stacked_plot(
    df: pd.DataFrame, hue: str, y: str, order_type: str = 'frequency'
) -> pd.DataFrame:
    """Transpose data into pivot format for stacked horizontal bar plot."""
    # Create pivot table from value counts
    df_subset = df[[hue, y]].copy()
    value_counts = df_subset.value_counts()
    value_counts_frame = value_counts.to_frame(name="count").reset_index()
    df_transposed = value_counts_frame.pivot(index=y, columns=hue, values="count")
    df_transposed = df_transposed.fillna(0).astype(int)

    # Sort rows based on ordering type
    if order_type == 'frequency':
        df_transposed['_order'] = df_transposed.sum(axis=1)
        df_transposed = df_transposed.sort_values(by='_order', ascending=True)
        df_transposed = df_transposed.drop(columns=['_order'])
    elif order_type == 'alphabetical':
        df_transposed = df_transposed.sort_index(ascending=False)

    return df_transposed

def _generate_stacked_plot(
    df_transposed: pd.DataFrame, colors: list[str]
) -> Any:
    """Generate a stacked horizontal bar plot."""
    ax = plt.gca()
    return df_transposed.plot(
        kind='barh',
        stacked=True,
        color=colors,
        edgecolor='none',
        ax=ax,
        alpha=1,
        width=0.8
    )

def _stacked_plot(
    df: pd.DataFrame,
    hue: str,
    y: str,
    palette: Dict[Any, str],
    label_map: Optional[Dict[Any, str]],
    order_type: str
) -> tuple[Any, pd.DataFrame]:
    """Create stacked plot with properly formatted data and labels."""
    df_transposed = _transpose_data_for_stacked_plot(df, hue, y, order_type)

    colors = [palette[col] for col in df_transposed.columns]
    if label_map:
        df_transposed.columns = [
            label_map.get(col, col) for col in df_transposed.columns
        ]

    plot = _generate_stacked_plot(df_transposed, colors)
    return plot, df_transposed  

def countplot_y(
    df: pd.DataFrame,
    y: str,
    hue: Optional[str] = None,
    palette: Optional[Union[Dict[Any, str], str]] = None,
    label_map: Optional[Dict[Any, str]] = None,
    xlabel: str = 'Count',
    ylabel: str = '',
    plot_legend: bool = True,
    legend_offset: float = 1.13,
    ncol: int = 2,
    top_n: Optional[int] = None,
    figsize_height: Union[str, float] = 'dynamic',
    stacked: bool = False,
    stacked_labels: Optional[str] = None,
    order_type: str = 'frequency',
) -> None:
    """Create a horizontal count plot with optional stacking and customization.
    
    Args:
        df: Input DataFrame
        y: Column name for y-axis (categories)
        hue: Column name for color grouping
        palette: Color mapping or single color
        label_map: Mapping for legend labels
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        plot_legend: Whether to display legend
        legend_offset: Position offset for legend
        ncol: Number of columns in legend
        top_n: Limit to top N categories
        figsize_height: Figure height ('dynamic', 'standard', or numeric)
        stacked: Whether to create stacked bars
        stacked_labels: Label style for stacked bars ('reversed' or None)
        order_type: Sorting order ('frequency' or 'alphabetical')
    """
    df = df.copy()
    df[y] = df[y].astype(str)
    
    if top_n is not None:
        df = filter_top_n_categories(df, y, top_n)

    figsize_height = _dynamic_figsize_height(df, y, figsize_height)

    if order_type == 'frequency':
        order = df[y].value_counts().index
    elif order_type == 'alphabetical':
        order = sorted(df[y].unique())
    else:
        order = None

    color, palette = handle_palette(palette)

    plt.figure(figsize=(FigureSize.WIDTH, figsize_height))
    
    if stacked and hue is not None and isinstance(palette, dict):
        plot, df_transposed = _stacked_plot(df, hue, y, palette, label_map, order_type)
    else:
        plot = sns.countplot(
            data=df, y=y, hue=hue, order=order,
            color=color, palette=palette,
            alpha=1, edgecolor='none', saturation=1
        )
        df_transposed = None

    if label_map is None and plot_legend and hue is not None:
        label_map = {key: key for key in df[hue].unique()}

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot, x_grid=True, numeric_x=True)
    
    if stacked and stacked_labels is not None and df_transposed is not None:
        reverse = stacked_labels == 'reversed'
        format_datalabels_stacked(plot, df_transposed, reverse)
    elif not stacked:
        format_datalabels(plot, label_offset=0.007, orientation='horizontal')