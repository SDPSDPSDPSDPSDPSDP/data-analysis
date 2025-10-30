import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional, Union, Dict

from ..formatting import format_ticks, format_xy_labels, format_optional_legend
from ..config import FigureSize
from ..utils import handle_palette

def _limit_x_axis(data: pd.DataFrame, x: str, xlimit: Optional[Union[float, int]]) -> pd.DataFrame:
    if xlimit is not None:
        data = data[data[x] <= xlimit]
    return data

def _dynamic_bins(data: pd.DataFrame, x: str, bins: int) -> int:
    max_value_x: int = int(data[x].max())
    if max_value_x < bins:
        bins = max_value_x
    return bins

def _handle_stacking(hue: Optional[str] = None, stacked: Optional[bool] = None) -> Optional[str]:
    STANDARD_MULTIPLE = 'stack'
    if hue is not None:
        if stacked is True:
            multiple = 'stack'
        elif stacked is False:
            multiple = 'dodge'
        else:
            multiple = STANDARD_MULTIPLE
    else:
        multiple = STANDARD_MULTIPLE
    return multiple

def _ensure_correct_dtypes(data: pd.DataFrame, x: str, hue: str, label_map: dict, palette: dict):
    data = data.copy()
    if hue is not None:
        data[hue] = data[hue].astype(str)
    if label_map is not None:
        label_map = {str(key): value for key, value in label_map.items()}
    if palette is not None:
        palette = {str(key): value for key, value in palette.items()}

    data[x] = data[x].astype(int)

    return data, label_map, palette

def _detect_years(df: pd.DataFrame, x: str) -> bool:
    """
    Detect whether the column `x` in the DataFrame `df` contains year-like values (between 1600 and 2300).
    Returns True if `x` is numeric and not year-like, otherwise False.
    """
    numeric_x = True # standard is True

    min_value = df[x].min()
    max_value = df[x].max()

    len_min_value = len(str(min_value))
    len_max_value = len(str(max_value))

    if min_value > 1600 and max_value < 2300:
        if len_min_value == 4 and len_max_value == 4:
            numeric_x = False

    return numeric_x
 
def histogram(
    data: pd.DataFrame,
    x: str,
    xlabel: str = '',
    ylabel: str = 'Count',
    xlimit: Optional[Union[float, int]] = None,
    bins: int = 100,
    palette: Optional[Union[Dict[str, str], str]] = None,
    label_map: Optional[Dict[str, str]] = None,
    hue: Optional[str] = None,
    stacked: Optional[bool] = None,
    plot_legend: bool = True,
    legend_offset: float = 1.13,
    ncol: int = 2
) -> None:
    
    # Limit x-axis
    data = _limit_x_axis(data, x, xlimit)

    # Dynamic bins
    bins = _dynamic_bins(data, x, bins)

    # If palette is not provided, use the default grey color, if palette is a singular value, use color instead of palette
    color, palette = handle_palette(palette)
    multiple =_handle_stacking(hue, stacked)

    # ensure correct data types
    data, label_map, palette = _ensure_correct_dtypes(data, x, hue, label_map, palette)
        
    # Graph
    plt.figure(figsize=(FigureSize.WIDTH, FigureSize.HEIGHT*0.7))
    plot = sns.histplot(data=data, x=x, hue=hue, alpha=1, edgecolor='white', color=color, palette=palette, bins=bins, multiple=multiple)

    # Formatting the plot
    format_xy_labels(plot, xlabel=xlabel, ylabel=ylabel)
    format_ticks(plot, y_grid=True, numeric_x=_detect_years(data, x), numeric_y=True)
    format_optional_legend(plot, hue, plot_legend, label_map, ncol, legend_offset)

# sns.histplot(
#     data=df,
#     x=x,
#     hue=hue,
#     multiple='dodge',  # Stack the histograms for better visualization
#     palette=palette_has_content,
#     bins=100,
#     edgecolor='white',
#     alpha=1
# )
# plt.show()


# TO DO when needed: adding a palette
#     # legend if palette is an option
#     if hue is not None:
#         format_legend(label_map=label_map, ncol=2, bbox_to_anchor=(0, 1.04))
#     else:
#         if hasattr(plot, 'legend_') and plot.legend_ is not None:
#             plot.legend_.remove()