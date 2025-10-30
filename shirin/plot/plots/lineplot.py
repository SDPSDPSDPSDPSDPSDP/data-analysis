import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional

from ..config import Colors, FigureSize
from ..formatting import format_ticks, format_xy_labels


def _data_preparation_for_lineplot(df: pd.DataFrame, x: str, y: str, fill_missing_values: str) -> pd.DataFrame:
    df = df.copy()

    if df[x].dtype != 'str':
        # Sort the DataFrame by the x column
        df = df.sort_values(by=x, ascending=True)

        # Create the full range from minimum to maximum values of x
        x_min = df[x].min()
        x_max = df[x].max()
        x_range = pd.Series(np.arange(x_min, x_max + 1) if df[x].dtype.kind in 'iufc' else pd.date_range(start=x_min, end=x_max))

        # Fill missing values in the DataFrame
        if fill_missing_values is not None:
            all_x = pd.DataFrame({x: x_range})
            df = pd.merge(all_x, df, on=x, how='left')  # Left join to fill missing x values
            if fill_missing_values == 'shift':
                df[y] = df[y].fillna(method='ffill')  # Fill missing y values by forward carry
            elif fill_missing_values == 'zero':
                df[y] = df[y].fillna(0)  # Fill missing y values with 0
            else:
                raise ValueError(f"Unsupported fill_missing_values strategy: {fill_missing_values}")

    # Convert column x to string type for subsequent purposes
    df[x] = df[x].astype(str)
    return df

def _format_dynamic_xticks(plot, dynamic_x_ticks: Optional[int] = None) -> None:
    if dynamic_x_ticks is not None:
        # Modify x-axis tick labels to show only every other label
        x_ticks = plot.get_xticks()  # Get the current tick positions
        labels = plot.get_xticklabels()  # Get the current tick labels
        new_labels = [label.get_text() if idx % dynamic_x_ticks == 0 else '' for idx, label in enumerate(labels)]
        plot.set_xticks(x_ticks)  # Reset the tick positions
        plot.set_xticklabels(new_labels)  # Update the tick labels

def lineplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    ylabel: str = '',
    xlabel: str = '',
    rotation: int = 0,
    dynamic_x_ticks: Optional[int] = None,
    fill_missing_values: Optional[str] = None
) -> None:

    # Prepare data
    df = _data_preparation_for_lineplot(df, x, y, fill_missing_values)

    # plot
    plt.figure(figsize=(FigureSize.WIDTH, FigureSize.HEIGHT*0.5))
    plot = sns.lineplot(data=df, x=x, y=y, alpha=1, linewidth=2, color=Colors.BLACK)

    # formatting
    format_xy_labels(plot, ylabel=ylabel, xlabel=xlabel)
    format_ticks(plot, y_grid=True, numeric_y=True, rotation=rotation)
    _format_dynamic_xticks(plot, dynamic_x_ticks)