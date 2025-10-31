import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Any, Dict, Optional, Union

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

def _calculate_figsize_width(
    df: pd.DataFrame,
    x: str,
    figsize_width: FigureSizeInput
) -> float:
    if figsize_width == 'dynamic':
        return (len(df[x].value_counts()) * 1) + 1
    if figsize_width == 'standard':
        return FigureSize.WIDTH
    return float(figsize_width)

def _prepare_stacked_data(
    df: pd.DataFrame,
    hue: str,
    x: str,
    order_type: OrderTypeInput
) -> pd.DataFrame:
    df_subset = df[[hue, x]].copy()
    value_counts = df_subset.value_counts()
    value_counts_frame = value_counts.to_frame(name="count").reset_index()
    df_pivot = value_counts_frame.pivot(index=x, columns=hue, values="count").fillna(0).astype(int)
    return sort_pivot_table(df_pivot, order_type, ascending=False)

def _create_stacked_plot(
    df: pd.DataFrame,
    hue: str,
    x: str,
    palette: Dict[Any, str],
    label_map: Optional[Dict[Any, str]],
    order_type: OrderTypeInput
) -> tuple[Any, pd.DataFrame]:
    df_prepared = _prepare_stacked_data(df, hue, x, order_type)
    df_labeled = apply_label_mapping(df_prepared, label_map)
    colors = create_colors_list(df_prepared, palette)
    plot = df_labeled.plot(
        kind='bar',
        stacked=True,
        color=colors,
        edgecolor='none',
        ax=plt.gca(),
        alpha=1,
        width=0.6
    )
    return plot, df_prepared

def _get_category_order(
    df: pd.DataFrame,
    x: str,
    order_type: OrderTypeInput
) -> Optional[Any]:
    if order_type == 'frequency':
        return df[x].value_counts().index
    if order_type == 'alphabetical':
        return sorted(df[x].unique())
    return None


def countplot_x(
    df: pd.DataFrame,
    x: str,
    hue: Optional[str] = None,
    palette: Optional[Union[Dict[Any, str], str]] = None,
    label_map: Optional[Dict[Any, str]] = None,
    xlabel: str = '',
    ylabel: str = 'Count',
    plot_legend: bool = True,
    legend_offset: float = 1.13,
    ncol: int = 2,
    top_n: Optional[int] = None,
    figsize_width: FigureSizeInput = 'dynamic',
    stacked: bool = False,
    stacked_labels: StackedLabelTypeInput = None,
    order_type: OrderTypeInput = 'frequency',
) -> None:
    df = ensure_column_is_string(df, x)
    
    if top_n is not None:
        df = filter_top_n_categories(df, x, top_n)

    figsize_width = _calculate_figsize_width(df, x, figsize_width)
    order = _get_category_order(df, x, order_type)
    color, palette = handle_palette(palette)
    original_palette = palette if isinstance(palette, dict) else None

    plt.figure(figsize=(figsize_width, FigureSize.STANDARD_HEIGHT))
    
    if stacked and hue is not None and isinstance(palette, dict):
        plot, df_unlabeled = _create_stacked_plot(df, hue, x, palette, label_map, order_type)
    else:
        plot = sns.countplot(
            data=df, x=x, hue=hue, order=order,
            color=color, palette=palette,
            alpha=1, edgecolor='none', saturation=1
        )
        df_unlabeled = None

    if label_map is None and plot_legend and hue is not None:
        label_map = create_default_label_map(df, hue)

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot, y_grid=True, numeric_y=True)
    
    if stacked and stacked_labels is not None and df_unlabeled is not None and original_palette is not None:
        format_datalabels_stacked(plot, df_unlabeled, original_palette, orientation='vertical') #type: ignore
    elif not stacked:
        format_datalabels(plot, label_offset=0.007, orientation='vertical') #type: ignore
