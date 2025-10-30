from typing import Optional, Dict, Union
import matplotlib.pyplot as plt
import pandas as pd
from ..config import FigureSize
from ..formatting import format_optional_legend, format_ticks, format_xy_labels#, format_datalabels_stacked
from ..utils import filter_top_n_categories
from .countplot_y import _dynamic_figsize_height


def _calculate_normalized_counts(df: pd.DataFrame, y: str, hue: str) -> pd.DataFrame:
    """Calculate normalized counts (as percentages) for the bars."""
    counts = df.groupby([y, hue]).size()
    normalized_counts = counts / counts.groupby(level=0).sum()
    normalized_df = normalized_counts.rename("percentage").reset_index()
    return normalized_df


def countplot_y_normalized(
    df: pd.DataFrame,
    y: str,
    hue: str,
    palette: Dict[str|int|bool, str],
    label_map: Optional[Dict[str|int|bool, str]] = None,
    plot_legend: bool = True,
    legend_offset: float = 1.13,
    ncol: int = 2,
    top_n: Optional[int] = None,
    figsize_height: Union[str, float] = 'dynamic',
    ylabel: str = '',
    xlabel: str = 'Percentage',
    order_type: str = 'frequency',  # alphabetical
    # stacked_labels: Union[None, str] = None, # 'reverse' or 'standard',
) -> None:
    # Validate that all values in 'hue' column exist in the palette dictionary
    unique_hue_values = df[hue].unique()
    if not all(hue_value in palette for hue_value in unique_hue_values):
        missing_keys = [hue_value for hue_value in unique_hue_values if hue_value not in palette]
        raise ValueError(f"The palette dictionary is missing keys for hue values: {missing_keys}")

    # Copy the dataframe and ensure 'y' and 'hue' are strings for consistency
    df = df.copy()
    df[y] = df[y].astype(str)
    df[hue] = df[hue].astype(str)
    if palette is not None:
        palette = {str(k): str(v) for k, v in palette.items()}

    # Filter for top-n categories if required
    if top_n is not None:
        df = filter_top_n_categories(df, y, top_n)

    # Normalize the counts
    normalized_df = _calculate_normalized_counts(df, y, hue)

    # Transpose normalized dataframe for stacking
    normalized_pivot = normalized_df.pivot(index=y, columns=hue, values="percentage")
    normalized_pivot = normalized_pivot.fillna(0)  # Fill missing values with zero

    # Step 3: Sort the rows based on the selected ordering type
    if order_type == 'frequency':
        # Sort rows by total count in descending order
        normalized_pivot['order'] = normalized_pivot.sum(axis=1)  # Compute totals for each row
        normalized_pivot = normalized_pivot.sort_values(by='order', ascending=True)  # Sort rows
        del normalized_pivot['order']  # Remove 'order' column after sorting
    elif order_type == 'alphabetical':
        normalized_pivot = normalized_pivot.sort_index(ascending=False)  # Sort rows alphabetically by index
    # print(normalized_pivot)

    # Use dynamic figure height logic
    figsize_height = _dynamic_figsize_height(df, y, figsize_height)

    # Plot the stacked bar chart
    plt.figure(figsize=(FigureSize.WIDTH, figsize_height))  # Ensure the figure is properly initialized
    colors = [palette[col] for col in normalized_pivot.columns]
    ax = plt.gca()  # Explicitly create axes
    plot = normalized_pivot.plot(
        kind='barh',  # Horizontal bars
        stacked=True,
        color=colors,
        edgecolor='none',
        alpha=1,
        width=0.8,
        ax=ax  # Assign existing axes
    )


    # Apply label mapping to legend if specified
    if label_map is None and plot_legend:
        label_map = {str(key): str(key) for key in normalized_df[hue].unique()}  # Ensure label mapping keys are strings
    else:
        label_map = {str(key): str(value) for key, value in label_map.items()}  # Convert all keys and values to strings

    # Format the plot
    format_xy_labels(ax, ylabel=ylabel, xlabel=xlabel)
    format_optional_legend(ax, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot=ax, x_grid=True, percentage_x=True)
    # if stacked_labels is not None:
    #     reverse = stacked_labels == 'reversed'
    #     format_datalabels_stacked(plot, normalized_df, reverse)
    # plt.show()  # Ensure the figure is displayed properly