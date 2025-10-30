from typing import Optional, Dict, Union
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from ..config import FigureSize
from ..formatting import format_optional_legend, format_ticks, format_datalabels, format_xy_labels, format_datalabels_stacked
from ..utils import filter_top_n_categories, handle_palette

def _dynamic_figsize_height(df: pd.DataFrame, y: str, figsize_height: Union[str, float] = 'dynamic') -> float:
    if figsize_height == 'dynamic':
        figsize_height = (len(df[y].value_counts()) / 2) + 1
    elif figsize_height == 'standard':
        figsize_height = FigureSize.HEIGHT
    return figsize_height

def _transpose_data_for_stacked_plot(df_input, col_hue, col_label, order_type: str = 'frequency'):
    df = df_input.copy()

    # Step 1: Create a pivot table to reorganize the data
    df_subset = df[[col_hue, col_label]].copy()
    value_counts = df_subset.value_counts()
    value_counts_frame = value_counts.to_frame(name="count").reset_index()
    df_transposed = value_counts_frame.pivot(index=col_label, columns=col_hue, values="count")

    # Step 2: Fill any missing values with zero
    df_transposed = df_transposed.fillna(0).astype(int)

    # Step 3: Sort the rows based on the selected ordering type
    if order_type == 'frequency':
        # Sort rows by total count in descending order 
        df_transposed['order'] = df_transposed.sum(axis=1)  # Compute the total count for each row
        df_transposed = df_transposed.sort_values(by='order', ascending=True)  # Sort rows by total count
        del df_transposed['order']  # Remove the 'order' column after sorting
    elif order_type == 'alphabetical':
        df_transposed = df_transposed.sort_index(ascending=False)  # Sort rows alphabetically by index

    return df_transposed

def _generate_stacked_plot(df_transposed, colors):

    ax = plt.gca()
    plot = df_transposed.plot(
        kind='barh',  # Horizontal bars
        stacked=True,
        color=colors,
        edgecolor='none',
        ax=ax,
        alpha=1,
        width=0.8
    )

    return plot

def _stacked_plot(df, hue, y, palette, label_map, order_type):
    # prepare data
    df_transposed = _transpose_data_for_stacked_plot(df, hue, y, order_type)

    # palette
    colors = [palette[col] for col in df_transposed.columns]
    if label_map:
        df_transposed.columns = [label_map[col] if col in label_map else col for col in df_transposed.columns]

    # plot
    plot = _generate_stacked_plot(df_transposed, colors)
    return plot, df_transposed  

def countplot_y(
    df: pd.DataFrame,
    y: str,
    hue: Optional[str] = None,
    palette: Optional[Union[Dict[str|int|bool, str], str]] = None,
    label_map: Optional[Dict[str|int|bool, str]] = None,
    legend_offset: float = 1.13,
    ncol: int = 2,
    plot_legend: bool = True,
    top_n: Optional[int] = None,
    figsize_height: Union[str, float] = 'dynamic',
    ylabel: str = '',
    xlabel: str = 'Count',
    stacked: bool = False,
    stacked_labels: Union[None, str] = None, # 'reverse' or 'standard',
    order_type: str = 'frequency',
) -> None:
    
    # ensure y is string (not category type, or integer)
    df = df.copy()
    df[y] = df[y].astype(str)
    
    # Filter data for top-n categories if applicable
    if top_n is not None:
        df = filter_top_n_categories(df, y, top_n)

    # Determine figure height based on settings
    # If figsize_height is a numeric value, use it directly
    figsize_height = _dynamic_figsize_height(df, y, figsize_height)

    # Set order to reflect the frequency of values in data[y]
    if order_type == 'frequency':
        order = df[y].value_counts().index
    elif order_type == 'alphabetical':
        order = sorted(df[y].unique())

    # If palette is not provided, use the default grey color, if palette is a singular value, use color instead of palette
    color, palette = handle_palette(palette)

    # Initialize the figure and construct the count plot
    plt.figure(figsize=(FigureSize.WIDTH, figsize_height))
    
    if stacked:
        plot, df_transposed = _stacked_plot(df, hue, y, palette, label_map, order_type)

    else:
        plot = sns.countplot(data=df, y=y, alpha=1, edgecolor='none', color=color, order=order, hue=hue, palette=palette, saturation=1)

    if label_map is None and plot_legend and hue is not None:
        label_map = {key: key for key in df[hue].unique()}

    # Formatting the plot
    format_xy_labels(plot, ylabel=ylabel, xlabel=xlabel)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot, x_grid=True, numeric_x=True)
    if not stacked:
        format_datalabels(plot, label_offset=0.007, orientation='horizontal')
    elif stacked:
        if stacked_labels is not None:
            reverse = stacked_labels == 'reversed'
            format_datalabels_stacked(plot, df_transposed, reverse)