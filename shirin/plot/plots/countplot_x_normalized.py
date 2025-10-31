from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import pandas as pd

from ..config import FigureSize, OrderTypeInput, FigureSizeInput
from ..formatting import format_optional_legend, format_ticks, format_xy_labels, format_datalabels_stacked_normalized
from ..utils.data_conversion import convert_palette_to_strings, ensure_column_is_string
from ..utils.data_filtering import filter_top_n_categories
from ..utils.label_mapping import create_label_map
from ..utils.sorting import sort_pivot_table
from .countplot_x import _calculate_figsize_width


def _calculate_normalized_counts(
    df: pd.DataFrame,
    x: str,
    hue: str
) -> pd.DataFrame:
    counts = df.groupby([x, hue]).size()
    normalized_counts = counts / counts.groupby(level=0).sum()
    return normalized_counts.rename("percentage").reset_index()

def _create_normalized_pivot(
    df: pd.DataFrame,
    x: str,
    hue: str
) -> pd.DataFrame:
    normalized_df = _calculate_normalized_counts(df, x, hue)
    normalized_pivot = normalized_df.pivot(
        index=x, columns=hue, values="percentage"
    )
    return normalized_pivot.fillna(0)

def _ensure_strings(df: pd.DataFrame, x: str, hue: str) -> pd.DataFrame:
    df = ensure_column_is_string(df, x)
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


def countplot_x_normalized(
    df: pd.DataFrame,
    x: str,
    hue: str,
    palette: Dict[Any, str],
    label_map: Optional[Dict[Any, str]] = None,
    xlabel: str = '',
    ylabel: str = 'Percentage',
    plot_legend: bool = True,
    legend_offset: float = 1.13,
    ncol: int = 2,
    top_n: Optional[int] = None,
    figsize_width: FigureSizeInput = 'dynamic',
    order_type: OrderTypeInput = 'frequency',
    show_labels: bool = True,
) -> None:
    _validate_palette_keys(df, hue, palette)
    
    df = _ensure_strings(df, x, hue)
    original_palette = palette.copy()
    palette = convert_palette_to_strings(palette)
    
    if top_n is not None:
        df = filter_top_n_categories(df, x, top_n)

    normalized_pivot = _create_normalized_pivot(df, x, hue)
    normalized_pivot = sort_pivot_table(normalized_pivot, order_type, ascending=False)
    figsize_width = _calculate_figsize_width(df, x, figsize_width)

    plt.figure(figsize=(figsize_width, FigureSize.STANDARD_HEIGHT))
    colors = [palette[col] for col in normalized_pivot.columns]
    plot = normalized_pivot.plot(
        kind='bar',
        stacked=True,
        color=colors,
        edgecolor='none',
        alpha=1,
        width=0.6,
        ax=plt.gca()
    )
    
    normalized_df = _calculate_normalized_counts(df, x, hue)
    label_map = create_label_map(
        label_map if not plot_legend else label_map,
        normalized_df[hue].unique()
    )

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot=plot, y_grid=True, percentage_y=True)
    
    if show_labels:
        format_datalabels_stacked_normalized(plot, normalized_pivot, original_palette, orientation='vertical') #type: ignore
