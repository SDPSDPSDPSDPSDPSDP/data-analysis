import pandas as pd
import matplotlib.pyplot as plt
from typing import Any, Dict, Optional

from ..config import FigureSize, OrderTypeInput, FigureSizeInput
from ..formatting import format_optional_legend, format_ticks, format_xy_labels, format_datalabels_stacked_normalized
from ..utils.data_conversion import convert_palette_to_strings, ensure_column_is_string
from ..utils.data_filtering import filter_top_n_categories
from ..utils.label_mapping import create_label_map
from ..utils.sorting import sort_pivot_table


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
    figsize_height: FigureSizeInput = 'dynamic',
    order_type: OrderTypeInput = 'frequency',
    show_labels: bool = True,
) -> None:
    _validate_palette_keys(df, hue, palette)
    
    df = _ensure_strings(df, y, hue)
    original_palette = palette.copy()
    palette = convert_palette_to_strings(palette)
    
    if top_n is not None:
        df = filter_top_n_categories(df, y, top_n)

    normalized_pivot = _create_normalized_pivot(df, y, hue)
    
    # For frequency, use descending; for alphabetical, use ascending
    # Horizontal plots draw bottom-to-top, so reverse for correct display
    ascending = False if order_type == 'frequency' else True
    ascending = not ascending  # Reverse for horizontal orientation
    normalized_pivot = sort_pivot_table(normalized_pivot, order_type, ascending=ascending)
    
    figsize_height = _calculate_figsize_height(df, y, figsize_height)

    plt.figure(figsize=(FigureSize.WIDTH, figsize_height))
    colors = [palette[col] for col in normalized_pivot.columns]
    plot = normalized_pivot.plot(
        kind='barh',
        stacked=True,
        color=colors,
        edgecolor='none',
        alpha=1,
        width=0.8,
        ax=plt.gca()
    )
    
    normalized_df = _calculate_normalized_counts(df, y, hue)
    label_map = create_label_map(
        label_map if not plot_legend else label_map,
        normalized_df[hue].unique()
    )

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot=plot, x_grid=True, percentage_x=True)
    
    if show_labels:
        format_datalabels_stacked_normalized(plot, normalized_pivot, palette, orientation='horizontal') #type: ignore