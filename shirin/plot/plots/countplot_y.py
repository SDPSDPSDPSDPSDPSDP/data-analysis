from typing import Any, Dict, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from ..config import FigureSize, OrderTypeInput, StackedLabelTypeInput, FigureSizeInput
from ..formatting import (
    format_datalabels,
    format_datalabels_stacked,
    format_optional_legend,
    format_ticks,
    format_xy_labels,
)
from ..utils.data_conversion import ensure_column_is_string
from ..utils.data_filtering import filter_top_n_categories
from ..utils.palette_handling import handle_palette
from ..utils.sorting import (
    apply_label_mapping,
    create_colors_list,
    create_default_label_map,
    sort_pivot_table,
)

def _calculate_figsize_height(
    df: pd.DataFrame,
    y: str,
    figsize_height: FigureSizeInput
) -> float:
    if figsize_height == 'dynamic':
        return (len(df[y].value_counts()) / 2) + 1
    if figsize_height == 'standard':
        return FigureSize.HEIGHT
    return float(figsize_height)

def _prepare_stacked_data(
    df: pd.DataFrame,
    hue: str,
    y: str,
    order_type: OrderTypeInput
) -> pd.DataFrame:
    df_subset = df[[hue, y]].copy()
    value_counts = df_subset.value_counts()
    value_counts_frame = value_counts.to_frame(name="count").reset_index()
    df_pivot = value_counts_frame.pivot(index=y, columns=hue, values="count").fillna(0).astype(int)
    return sort_pivot_table(df_pivot, order_type, ascending=False)

def _create_stacked_plot(
    df: pd.DataFrame,
    hue: str,
    y: str,
    palette: Dict[Any, str],
    label_map: Optional[Dict[Any, str]],
    order_type: OrderTypeInput
) -> tuple[Any, pd.DataFrame]:
    df_prepared = _prepare_stacked_data(df, hue, y, order_type)
    df_labeled = apply_label_mapping(df_prepared, label_map)
    colors = create_colors_list(df_prepared, palette)
    plot = df_labeled.plot(
        kind='barh',
        stacked=True,
        color=colors,
        edgecolor='none',
        ax=plt.gca(),
        alpha=1,
        width=0.8
    )
    return plot, df_prepared

def _get_category_order(
    df: pd.DataFrame,
    y: str,
    order_type: OrderTypeInput
) -> Optional[Any]:
    if order_type == 'frequency':
        return df[y].value_counts().sort_values(ascending=False).index
    if order_type == 'alphabetical':
        return sorted(df[y].unique())
    return None

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
    figsize_height: FigureSizeInput = 'dynamic',
    stacked: bool = False,
    stacked_labels: StackedLabelTypeInput = None,
    order_type: OrderTypeInput = 'frequency',
) -> None:
    df = ensure_column_is_string(df, y)
    
    if top_n is not None:
        df = filter_top_n_categories(df, y, top_n)

    figsize_height = _calculate_figsize_height(df, y, figsize_height)
    order = _get_category_order(df, y, order_type)
    color, palette = handle_palette(palette)
    original_palette = palette if isinstance(palette, dict) else None

    plt.figure(figsize=(FigureSize.WIDTH, figsize_height))
    
    if stacked and hue is not None and isinstance(palette, dict):
        plot, df_unlabeled = _create_stacked_plot(df, hue, y, palette, label_map, order_type)
    else:
        plot = sns.countplot(
            data=df, y=y, hue=hue, order=order,
            color=color, palette=palette,
            alpha=1, edgecolor='none', saturation=1
        )
        df_unlabeled = None

    if label_map is None and plot_legend and hue is not None:
        label_map = create_default_label_map(df, hue)

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot, x_grid=True, numeric_x=True)
    
    if stacked and stacked_labels is not None and df_unlabeled is not None and original_palette is not None:
        format_datalabels_stacked(plot, df_unlabeled, original_palette) #type: ignore
    elif not stacked:
        format_datalabels(plot, label_offset=0.007, orientation='horizontal') #type: ignore