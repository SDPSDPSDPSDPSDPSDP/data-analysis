from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from ..config import Colors, FigureSize, FillMissingValuesInput
from ..formatting import format_ticks, format_xy_labels


def _sort_by_column(df: pd.DataFrame, x: str) -> pd.DataFrame:
    return df.sort_values(by=x, ascending=True)

def _create_full_range(df: pd.DataFrame, x: str) -> pd.Series:
    x_min = df[x].min()
    x_max = df[x].max()
    if df[x].dtype.kind in 'iufc':
        return pd.Series(np.arange(x_min, x_max + 1))
    return pd.Series(pd.date_range(start=x_min, end=x_max))

def _fill_missing_with_shift(df: pd.DataFrame, y: str) -> pd.DataFrame:
    df[y] = df[y].ffill()
    return df

def _fill_missing_with_zero(df: pd.DataFrame, y: str) -> pd.DataFrame:
    df[y] = df[y].fillna(0)
    return df

def _merge_with_full_range(
    df: pd.DataFrame,
    x: str,
    x_range: pd.Series,
    y: str,
    fill_strategy: str
) -> pd.DataFrame:
    all_x = pd.DataFrame({x: x_range})
    df = pd.merge(all_x, df, on=x, how='left')
    
    if fill_strategy == 'shift':
        return _fill_missing_with_shift(df, y)
    if fill_strategy == 'zero':
        return _fill_missing_with_zero(df, y)
    raise ValueError(
        f"Unsupported fill_missing_values strategy: {fill_strategy}"
    )

def _prepare_lineplot_data(
    df: pd.DataFrame,
    x: str,
    y: str,
    fill_missing_values: FillMissingValuesInput
) -> pd.DataFrame:
    df = df.copy()
    if df[x].dtype == 'str':
        return df

    df = _sort_by_column(df, x)
    if fill_missing_values is not None:
        x_range = _create_full_range(df, x)
        df = _merge_with_full_range(df, x, x_range, y, fill_missing_values)

    df[x] = df[x].astype(str)
    return df

def _apply_dynamic_xticks(
    plot: Any,
    dynamic_x_ticks: Optional[int]
) -> None:
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
    fill_missing_values: FillMissingValuesInput = None
) -> None:
    df = _prepare_lineplot_data(df, x, y, fill_missing_values)

    plt.figure(figsize=(FigureSize.WIDTH, FigureSize.HEIGHT * 0.5))
    plot = sns.lineplot(
        data=df, x=x, y=y,
        alpha=1, linewidth=2, color=Colors.BLACK
    )

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_ticks(plot, y_grid=True, numeric_y=True, rotation=rotation)
    _apply_dynamic_xticks(plot, dynamic_x_ticks)