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
from ..utils.palette_handling import handle_palette
from ..utils.sorting import (
    apply_label_mapping,
    create_colors_list,
    create_default_label_map,
    get_category_order,
)
from ..utils.stacked_plots import prepare_stacked_data

def _calculate_figsize_width(
    df: pd.DataFrame,
    x: str,
    figsize_width: FigureSizeInput
) -> float:
    if figsize_width == 'dynamic':
        return (len(df[x].unique()) * 1) + 1
    if figsize_width == 'standard':
        return FigureSize.WIDTH
    return float(figsize_width)

def _create_stacked_plot(
    df: pd.DataFrame,
    hue: str,
    x: str,
    value: str,
    palette: Dict[Any, str],
    label_map: Optional[Dict[Any, str]],
    order_type: OrderTypeInput
) -> tuple[Any, pd.DataFrame]:
    df_prepared = prepare_stacked_data(df, hue, x, order_type, value_col=value)
    df_labeled = apply_label_mapping(df_prepared, label_map)
    colors = create_colors_list(df_prepared, palette)
    plot = df_labeled.plot(
        kind='bar',
        stacked=True,
        color=colors,
        edgecolor='none',
        ax=plt.gca(),
        alpha=1,
        width=0.4
    )
    return plot, df_prepared

def barplot_x(
    df: pd.DataFrame,
    x: str,
    value: str,
    hue: Optional[str] = None,
    palette: Optional[Union[Dict[Any, str], str]] = None,
    label_map: Optional[Dict[Any, str]] = None,
    xlabel: str = '',
    ylabel: str = '',
    plot_legend: bool = True,
    legend_offset: float = 1.13,
    ncol: int = 2,
    figsize_width: FigureSizeInput = 'dynamic',
    stacked: bool = False,
    stacked_labels: StackedLabelTypeInput = None,
    order_type: OrderTypeInput = 'frequency',
    percentage_labels: bool = False,
) -> None:
    df = ensure_column_is_string(df, x)

    figsize_width = _calculate_figsize_width(df, x, figsize_width)
    order = get_category_order(df, x, order_type, value_column=value)
    color, palette = handle_palette(palette)
    original_palette = palette if isinstance(palette, dict) else None

    plt.figure(figsize=(figsize_width, FigureSize.STANDARD_HEIGHT))
    
    if stacked and hue is not None and isinstance(palette, dict):
        plot, df_unlabeled = _create_stacked_plot(df, hue, x, value, palette, label_map, order_type)
    else:
        plot = sns.barplot(
            data=df, x=x, y=value, hue=hue, order=order,
            color=color, palette=palette,
            alpha=1, edgecolor='none', saturation=1,
            errorbar=None
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
        formatting = 'percentage' if percentage_labels else 'totals'
        format_datalabels(plot, label_offset=0.007, orientation='vertical', formatting=formatting) #type: ignore
