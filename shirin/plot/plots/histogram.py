from typing import Any, Dict, Literal, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from ..config import FigureSize
from ..formatting import format_optional_legend, format_ticks, format_xy_labels
from ..utils import handle_palette

def _limit_x_axis(
    df: pd.DataFrame,
    x: str,
    xlimit: Optional[Union[float, int]]
) -> pd.DataFrame:
    if xlimit is not None:
        return df[df[x] <= xlimit]
    return df

def _calculate_bins(df: pd.DataFrame, x: str, bins: int) -> int:
    max_value_x = int(df[x].max())
    return min(bins, max_value_x)

def _determine_multiple_strategy(
    hue: Optional[str],
    stacked: Optional[bool]
) -> Literal['stack', 'dodge']:
    if hue is None:
        return 'stack'
    if stacked is True:
        return 'stack'
    if stacked is False:
        return 'dodge'
    return 'stack'

def _convert_to_int(df: pd.DataFrame, x: str) -> pd.DataFrame:
    df = df.copy()
    df[x] = df[x].astype(int)
    return df

def _convert_hue_to_string(df: pd.DataFrame, hue: Optional[str]) -> pd.DataFrame:
    if hue is not None:
        df[hue] = df[hue].astype(str)
    return df

def _convert_dict_keys_to_string(d: Optional[dict]) -> Optional[dict]:
    if isinstance(d, dict):
        return {str(key): value for key, value in d.items()}
    return d

def _prepare_data_types(
    df: pd.DataFrame,
    x: str,
    hue: Optional[str],
    label_map: Optional[dict],
    palette: Any
) -> tuple[pd.DataFrame, Optional[dict], Any]:
    df = _convert_to_int(df, x)
    df = _convert_hue_to_string(df, hue)
    label_map = _convert_dict_keys_to_string(label_map)
    palette = _convert_dict_keys_to_string(palette)
    return df, label_map, palette

def _is_year_column(df: pd.DataFrame, x: str) -> bool:
    min_value = df[x].min()
    max_value = df[x].max()
    if 1600 < min_value and max_value < 2300:
        if len(str(min_value)) == 4 and len(str(max_value)) == 4:
            return False
    return True
 
def histogram(
    df: pd.DataFrame,
    x: str,
    xlabel: str = '',
    ylabel: str = 'Count',
    xlimit: Optional[Union[float, int]] = None,
    bins: int = 100,
    palette: Optional[Union[Dict[Any, str], str]] = None,
    label_map: Optional[Dict[str, str]] = None,
    hue: Optional[str] = None,
    stacked: Optional[bool] = None,
    plot_legend: bool = True,
    legend_offset: float = 1.13,
    ncol: int = 2
) -> None:
    df = _limit_x_axis(df, x, xlimit)
    bins = _calculate_bins(df, x, bins)
    color, palette = handle_palette(palette)
    multiple = _determine_multiple_strategy(hue, stacked)
    df, label_map, palette = _prepare_data_types(df, x, hue, label_map, palette)
        
    plt.figure(figsize=(FigureSize.WIDTH, FigureSize.HEIGHT * 0.7))
    plot = sns.histplot(
        data=df, x=x, hue=hue,
        color=color, palette=palette,
        bins=bins, multiple=multiple,
        alpha=1, edgecolor='white'
    )

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_ticks(
        plot, y_grid=True, numeric_x=_is_year_column(df, x), numeric_y=True
    )
    format_optional_legend(
        plot, hue, plot_legend, label_map, ncol, legend_offset
    )