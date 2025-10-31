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
        return (len(df[y].unique()) / 2) + 1
    if figsize_height == 'standard':
        return FigureSize.HEIGHT
    return float(figsize_height)

def _create_pivot_table(df: pd.DataFrame, hue: str, y: str, value: str) -> pd.DataFrame:
    return df.pivot(index=y, columns=hue, values=value).fillna(0)

def _plot_stacked_bars(df: pd.DataFrame, colors: list[str]) -> Any:
    return df.plot(
        kind='barh',
        stacked=True,
        color=colors,
        edgecolor='none',
        ax=plt.gca(),
        alpha=1,
        width=0.8
    )

def _sort_pivot_table(df_pivot: pd.DataFrame, order_type: OrderTypeInput) -> pd.DataFrame:
    return sort_pivot_table(df_pivot, order_type, ascending=True)

def _prepare_stacked_data(
    df: pd.DataFrame,
    hue: str,
    y: str,
    value: str,
    order_type: OrderTypeInput
) -> pd.DataFrame:
    df_pivot = _create_pivot_table(df, hue, y, value)
    return _sort_pivot_table(df_pivot, order_type)

def _create_stacked_plot(
    df: pd.DataFrame,
    hue: str,
    y: str,
    value: str,
    palette: Dict[Any, str],
    label_map: Optional[Dict[Any, str]],
    order_type: OrderTypeInput
) -> tuple[Any, pd.DataFrame, pd.DataFrame]:
    df_prepared = _prepare_stacked_data(df, hue, y, value, order_type)
    df_labeled = apply_label_mapping(df_prepared, label_map)
    colors = create_colors_list(df_prepared, palette)
    plot = _plot_stacked_bars(df_labeled, colors)
    return plot, df_labeled, df_prepared

def _get_category_order(
    df: pd.DataFrame,
    y: str,
    value: str,
    order_type: OrderTypeInput
) -> Optional[Any]:
    if order_type == 'frequency':
        return df.groupby(y)[value].sum().sort_values(ascending=True).index
    if order_type == 'alphabetical':
        return sorted(df[y].unique())
    return None

def _create_default_label_map(df: pd.DataFrame, hue: str) -> Dict[Any, Any]:
    return create_default_label_map(df, hue)

def _plot_standard_barplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str],
    order: Any,
    color: Optional[str],
    palette: Any
) -> Any:
    return sns.barplot(
        data=df, x=x, y=y, hue=hue, order=order,
        color=color, palette=palette,
        alpha=1, edgecolor='none', saturation=1,
        errorbar=None
    )

def barplot_y(
    df: pd.DataFrame,
    y: str,
    value: str,
    hue: Optional[str] = None,
    palette: Optional[Union[Dict[Any, str], str]] = None,
    label_map: Optional[Dict[Any, str]] = None,
    xlabel: str = '',
    ylabel: str = '',
    plot_legend: bool = True,
    legend_offset: float = 1.13,
    ncol: int = 2,
    figsize_height: FigureSizeInput = 'dynamic',
    stacked: bool = False,
    stacked_labels: StackedLabelTypeInput = None,
    order_type: OrderTypeInput = 'frequency',
    percentage_labels: bool = False,
) -> None:
    df = ensure_column_is_string(df, y)

    figsize_height = _calculate_figsize_height(df, y, figsize_height)
    order = _get_category_order(df, y, value, order_type)
    color, palette = handle_palette(palette)
    original_palette = palette if isinstance(palette, dict) else None

    plt.figure(figsize=(FigureSize.WIDTH, figsize_height))
    
    if stacked and hue is not None and isinstance(palette, dict):
        plot, df_transposed, df_unlabeled = _create_stacked_plot(df, hue, y, value, palette, label_map, order_type)
    else:
        plot = _plot_standard_barplot(df, value, y, hue, order, color, palette)
        df_transposed = None
        df_unlabeled = None

    if label_map is None and plot_legend and hue is not None:
        label_map = _create_default_label_map(df, hue)

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot, x_grid=True, numeric_x=True)
    
    if stacked and stacked_labels is not None and df_unlabeled is not None and original_palette is not None:
        format_datalabels_stacked(plot, df_unlabeled, original_palette)
    elif not stacked:
        formatting = 'percentage' if percentage_labels else 'totals'
        format_datalabels(plot, label_offset=0.007, orientation='horizontal', formatting=formatting)
