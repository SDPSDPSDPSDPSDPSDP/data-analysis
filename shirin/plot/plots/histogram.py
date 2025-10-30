from typing import Any, Dict, Literal, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from ..config import FigureSize
from ..formatting import format_optional_legend, format_ticks, format_xy_labels
from ..utils import handle_palette

def _limit_x_axis(
    df: pd.DataFrame, x: str, xlimit: Optional[Union[float, int]]
) -> pd.DataFrame:
    """Filter dataframe to values below x-axis limit."""
    if xlimit is not None:
        return df[df[x] <= xlimit]
    return df

def _dynamic_bins(df: pd.DataFrame, x: str, bins: int) -> int:
    """Adjust bins dynamically if max value is less than requested bins."""
    max_value_x = int(df[x].max())
    return min(bins, max_value_x)

def _handle_stacking(
    hue: Optional[str] = None, stacked: Optional[bool] = None
) -> Literal['stack', 'dodge']:
    """Determine stacking strategy for histogram bars."""
    if hue is None:
        return 'stack'
    
    if stacked is True:
        return 'stack'
    elif stacked is False:
        return 'dodge'
    else:
        return 'stack'

def _ensure_correct_dtypes(
    df: pd.DataFrame, x: str, hue: Optional[str], label_map: Optional[dict], palette: Any
) -> tuple[pd.DataFrame, Optional[dict], Optional[dict]]:
    """Ensure correct data types for histogram plotting."""
    df = df.copy()
    df[x] = df[x].astype(int)
    
    if hue is not None:
        df[hue] = df[hue].astype(str)
    
    if label_map is not None:
        label_map = {str(key): value for key, value in label_map.items()}
    
    if isinstance(palette, dict):
        palette = {str(key): value for key, value in palette.items()}

    return df, label_map, palette

def _detect_years(df: pd.DataFrame, x: str) -> bool:
    """Detect whether column contains year values (1600-2300).
    
    Returns:
        True if not year-like (use numeric formatting)
        False if year-like (use year formatting)
    """
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
    """Create a histogram with optional grouping and customization.
    
    Args:
        df: Input DataFrame
        x: Column name for x-axis (numeric values)
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        xlimit: Maximum value for x-axis
        bins: Number of bins for histogram
        palette: Color mapping or single color
        label_map: Mapping for legend labels
        hue: Column name for color grouping
        stacked: Whether to stack bars (True) or dodge (False)
        plot_legend: Whether to display legend
        legend_offset: Position offset for legend
        ncol: Number of columns in legend
    """
    df = _limit_x_axis(df, x, xlimit)
    bins = _dynamic_bins(df, x, bins)
    color, palette = handle_palette(palette)
    multiple = _handle_stacking(hue, stacked)
    df, label_map, palette = _ensure_correct_dtypes(df, x, hue, label_map, palette)
        
    plt.figure(figsize=(FigureSize.WIDTH, FigureSize.HEIGHT * 0.7))
    plot = sns.histplot(
        data=df, x=x, hue=hue,
        color=color, palette=palette,
        bins=bins, multiple=multiple,
        alpha=1, edgecolor='white'
    )

    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_ticks(plot, y_grid=True, numeric_x=_detect_years(df, x), numeric_y=True)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)