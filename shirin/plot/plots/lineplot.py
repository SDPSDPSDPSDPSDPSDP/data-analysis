import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Any, Dict, Optional, Union

from ..config import Colors, FigureSize, FillMissingValuesInput
from ..formatting import format_ticks, format_xy_labels, format_optional_legend
from ..utils.palette_handling import handle_palette
from ..utils.sorting import create_default_label_map


def _sort_by_column(df: pd.DataFrame, x: str) -> pd.DataFrame:
    return df.sort_values(by=x, ascending=True)

def _create_full_range(df: pd.DataFrame, x: str) -> pd.Series:
    x_min = df[x].min()
    x_max = df[x].max()
    if df[x].dtype.kind in 'iufc':
        return pd.Series(np.arange(x_min, x_max + 1))
    return pd.Series(pd.date_range(start=x_min, end=x_max))

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
        df[y] = df[y].ffill()
        return df
    if fill_strategy == 'zero':
        df[y] = df[y].fillna(0)
        return df
    raise ValueError(
        f"Unsupported fill_missing_values strategy: {fill_strategy}"
    )

def _prepare_lineplot_data(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str],
    fill_missing_values: FillMissingValuesInput
) -> pd.DataFrame:
    df = df.copy()
    if df[x].dtype == 'str':
        return df

    df = _sort_by_column(df, x)
    if fill_missing_values is not None:
        if hue is not None:
            # For hue plots, fill missing values per hue group
            dfs = []
            for hue_value in df[hue].unique():
                df_group = df[df[hue] == hue_value].copy()
                assert isinstance(df_group, pd.DataFrame)
                x_range = _create_full_range(df_group, x)
                df_merged = _merge_with_full_range(df_group, x, x_range, y, fill_missing_values)
                df_merged[hue] = hue_value
                dfs.append(df_merged)
            df = pd.concat(dfs, ignore_index=True)
        else:
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
    hue: Optional[str] = None,
    palette: Optional[Union[Dict[Any, str], str]] = None,
    label_map: Optional[Dict[Any, str]] = None,
    xlabel: str = '',
    ylabel: str = '',
    plot_legend: bool = True,
    legend_offset: float = 1.13,
    ncol: int = 2,
    rotation: int = 0,
    dynamic_x_ticks: Optional[int] = None,
    fill_missing_values: FillMissingValuesInput = None
) -> None:
    df = _prepare_lineplot_data(df, x, y, hue, fill_missing_values)

    color, palette = handle_palette(palette)
    
    # When no hue and no palette, use black
    if hue is None and palette is None and color is not None:
        color = Colors.BLACK

    plt.figure(figsize=(FigureSize.WIDTH, FigureSize.HEIGHT * 0.5))
    plot = sns.lineplot(
        data=df, x=x, y=y, hue=hue,
        alpha=1, linewidth=2, color=color, palette=palette
    )

    if label_map is None and plot_legend and hue is not None:
        label_map = create_default_label_map(df, hue)

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)
    format_ticks(plot, y_grid=True, numeric_y=True, rotation=rotation)
    _apply_dynamic_xticks(plot, dynamic_x_ticks)