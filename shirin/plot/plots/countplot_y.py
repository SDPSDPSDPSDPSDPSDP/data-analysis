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
from ..utils import ensure_column_is_string, filter_top_n_categories, handle_palette

def _calculate_figsize_height(
    df: pd.DataFrame,
    y: str,
    figsize_height: Union[str, float]
) -> float:
    if figsize_height == 'dynamic':
        return (len(df[y].value_counts()) / 2) + 1
    if figsize_height == 'standard':
        return FigureSize.HEIGHT
    return float(figsize_height)

def _create_pivot_table(df: pd.DataFrame, hue: str, y: str) -> pd.DataFrame:
    df_subset = df[[hue, y]].copy()
    value_counts = df_subset.value_counts()
    value_counts_frame = value_counts.to_frame(name="count").reset_index()
    return value_counts_frame.pivot(index=y, columns=hue, values="count").fillna(0).astype(int)

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

def _sort_by_frequency(df_pivot: pd.DataFrame) -> pd.DataFrame:
    df_pivot['_order'] = df_pivot.sum(axis=1)
    df_sorted = df_pivot.sort_values(by='_order', ascending=True)
    return df_sorted.drop(columns=['_order'])

def _sort_alphabetically(df_pivot: pd.DataFrame) -> pd.DataFrame:
    return df_pivot.sort_index(ascending=False)

def _sort_pivot_table(df_pivot: pd.DataFrame, order_type: str) -> pd.DataFrame:
    if order_type == 'frequency':
        return _sort_by_frequency(df_pivot)
    if order_type == 'alphabetical':
        return _sort_alphabetically(df_pivot)
    return df_pivot

def _apply_label_mapping(
    df: pd.DataFrame,
    label_map: Optional[Dict[Any, str]]
) -> pd.DataFrame:
    if not label_map:
        return df
    df = df.copy()
    df.columns = [label_map.get(col, col) for col in df.columns]
    return df

def _create_colors_list(df: pd.DataFrame, palette: Dict[Any, str]) -> list[str]:
    return [palette[col] for col in df.columns]

def _prepare_stacked_data(
    df: pd.DataFrame,
    hue: str,
    y: str,
    order_type: str
) -> pd.DataFrame:
    df_pivot = _create_pivot_table(df, hue, y)
    return _sort_pivot_table(df_pivot, order_type)

def _create_stacked_plot(
    df: pd.DataFrame,
    hue: str,
    y: str,
    palette: Dict[Any, str],
    label_map: Optional[Dict[Any, str]],
    order_type: str
) -> tuple[Any, pd.DataFrame]:
    df_prepared = _prepare_stacked_data(df, hue, y, order_type)
    df_labeled = _apply_label_mapping(df_prepared, label_map)
    colors = _create_colors_list(df_prepared, palette)
    plot = _plot_stacked_bars(df_labeled, colors)
    return plot, df_labeled

def _get_category_order(
    df: pd.DataFrame,
    y: str,
    order_type: str
) -> Optional[Any]:
    if order_type == 'frequency':
        return df[y].value_counts().index
    if order_type == 'alphabetical':
        return sorted(df[y].unique())
    return None

def _create_default_label_map(df: pd.DataFrame, hue: str) -> Dict[Any, Any]:
    return {key: key for key in df[hue].unique()}

def _plot_standard_countplot(
    df: pd.DataFrame,
    y: str,
    hue: Optional[str],
    order: Any,
    color: Optional[str],
    palette: Any
) -> Any:
    return sns.countplot(
        data=df, y=y, hue=hue, order=order,
        color=color, palette=palette,
        alpha=1, edgecolor='none', saturation=1
    )  

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
    df = ensure_column_is_string(df, y)
    
    if top_n is not None:
        df = filter_top_n_categories(df, y, top_n)

    figsize_height = _calculate_figsize_height(df, y, figsize_height)
    order = _get_category_order(df, y, order_type)
    color, palette = handle_palette(palette)

    plt.figure(figsize=(FigureSize.WIDTH, figsize_height))
    
    if stacked and hue is not None and isinstance(palette, dict):
        plot, df_transposed = _create_stacked_plot(df, hue, y, palette, label_map, order_type)
    else:
        plot = _plot_standard_countplot(df, y, hue, order, color, palette)
        df_transposed = None

    if label_map is None and plot_legend and hue is not None:
        label_map = _create_default_label_map(df, hue)

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot, x_grid=True, numeric_x=True)
    
    if stacked and stacked_labels is not None and df_transposed is not None:
        reverse = stacked_labels == 'reversed'
        format_datalabels_stacked(plot, df_transposed, reverse)
    elif not stacked:
        format_datalabels(plot, label_offset=0.007, orientation='horizontal')