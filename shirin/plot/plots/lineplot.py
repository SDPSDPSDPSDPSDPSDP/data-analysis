from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from ..config import Colors, FigureSize
from ..formatting import format_ticks, format_xy_labels


def _data_preparation_for_lineplot(
    df: pd.DataFrame, x: str, y: str, fill_missing_values: Optional[str]
) -> pd.DataFrame:
    """Prepare data for line plot by sorting and filling missing values."""
    df = df.copy()

    if df[x].dtype == 'str':
        return df

    df = df.sort_values(by=x, ascending=True)

    x_min = df[x].min()
    x_max = df[x].max()
    if df[x].dtype.kind in 'iufc':
        x_range = pd.Series(np.arange(x_min, x_max + 1))
    else:
        x_range = pd.Series(pd.date_range(start=x_min, end=x_max))

    if fill_missing_values is not None:
        all_x = pd.DataFrame({x: x_range})
        df = pd.merge(all_x, df, on=x, how='left')
        
        if fill_missing_values == 'shift':
            df[y] = df[y].ffill()
        elif fill_missing_values == 'zero':
            df[y] = df[y].fillna(0)
        else:
            raise ValueError(
                f"Unsupported fill_missing_values strategy: {fill_missing_values}"
            )

    df[x] = df[x].astype(str)
    return df

def _format_dynamic_xticks(plot: Any, dynamic_x_ticks: Optional[int] = None) -> None:
    """Format x-axis ticks to show only every nth label."""
    if dynamic_x_ticks is None:
        return
        
    x_ticks = plot.get_xticks()
    labels = plot.get_xticklabels()
    new_labels = [
        label.get_text() if idx % dynamic_x_ticks == 0 else '' 
        for idx, label in enumerate(labels)
    ]
    plot.set_xticks(x_ticks)
    plot.set_xticklabels(new_labels)

def lineplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    xlabel: str = '',
    ylabel: str = '',
    rotation: int = 0,
    dynamic_x_ticks: Optional[int] = None,
    fill_missing_values: Optional[str] = None
) -> None:
    """Create a line plot with optional data filling and customization.
    
    Args:
        df: Input DataFrame
        x: Column name for x-axis
        y: Column name for y-axis
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        rotation: Rotation angle for x-axis labels
        dynamic_x_ticks: Show every nth tick label
        fill_missing_values: Strategy for missing values ('shift' or 'zero')
    """
    df = _data_preparation_for_lineplot(df, x, y, fill_missing_values)

    plt.figure(figsize=(FigureSize.WIDTH, FigureSize.HEIGHT * 0.5))
    plot = sns.lineplot(
        data=df, x=x, y=y,
        alpha=1, linewidth=2, color=Colors.BLACK
    )

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_ticks(plot, y_grid=True, numeric_y=True, rotation=rotation)
    _format_dynamic_xticks(plot, dynamic_x_ticks)