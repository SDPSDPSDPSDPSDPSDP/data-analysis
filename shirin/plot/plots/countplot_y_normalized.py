from typing import Any, Dict, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd

from ..config import FigureSize
from ..formatting import format_optional_legend, format_ticks, format_xy_labels
from ..utils import (
    convert_palette_to_strings,
    create_label_map,
    ensure_column_is_string,
    filter_top_n_categories,
)
from .countplot_y import _calculate_figsize_height, _sort_pivot_table


def _calculate_normalized_counts(
    df: pd.DataFrame,
    y: str,
    hue: str
) -> pd.DataFrame:
    counts = df.groupby([y, hue]).size()
    normalized_counts = counts / counts.groupby(level=0).sum()
    return normalized_counts.rename("percentage").reset_index()

def _create_normalized_pivot(
    df: pd.DataFrame,
    y: str,
    hue: str
) -> pd.DataFrame:
    normalized_df = _calculate_normalized_counts(df, y, hue)
    normalized_pivot = normalized_df.pivot(
        index=y, columns=hue, values="percentage"
    )
    return normalized_pivot.fillna(0)

def _create_normalized_plot(
    df_pivot: pd.DataFrame,
    palette: Dict[Any, str]
) -> Any:
    colors = [palette[col] for col in df_pivot.columns]
    return df_pivot.plot(
        kind='barh',
        stacked=True,
        color=colors,
        edgecolor='none',
        alpha=1,
        width=0.8,
        ax=plt.gca()
    )

def _ensure_strings(df: pd.DataFrame, y: str, hue: str) -> pd.DataFrame:
    df = ensure_column_is_string(df, y)
    df = ensure_column_is_string(df, hue)
    return df

def _validate_palette_keys(
    df: pd.DataFrame,
    hue: str,
    palette: Dict[Any, str]
) -> None:
    unique_hue_values = df[hue].unique()
    missing_keys = [val for val in unique_hue_values if val not in palette]
    if missing_keys:
        raise ValueError(
            f"Palette missing keys for hue values: {missing_keys}"
        )


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
    _validate_palette_keys(df, hue, palette)
    
    df = _ensure_strings(df, y, hue)
    palette = convert_palette_to_strings(palette)
    
    if top_n is not None:
        df = filter_top_n_categories(df, y, top_n)

    normalized_pivot = _create_normalized_pivot(df, y, hue)
    normalized_pivot = _sort_pivot_table(normalized_pivot, order_type)
    figsize_height = _calculate_figsize_height(df, y, figsize_height)

    plt.figure(figsize=(FigureSize.WIDTH, figsize_height))
    plot = _create_normalized_plot(normalized_pivot, palette)
    
    normalized_df = _calculate_normalized_counts(df, y, hue)
    label_map = create_label_map(
        label_map if not plot_legend else label_map,
        normalized_df[hue].unique()
    )

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot=plot, x_grid=True, percentage_x=True)