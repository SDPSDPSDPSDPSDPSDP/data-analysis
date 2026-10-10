from typing import Any, Dict, Optional

from matplotlib.ticker import FuncFormatter
from matplotlib.axes import Axes

from ...config import TextColors
from ....number_format import format_thousands


def _configure_grid(plot: Axes, x_grid: bool = False, y_grid: bool = False) -> None:
    plot.set_axisbelow(True)
    if y_grid:
        plot.yaxis.grid(y_grid, zorder=1)
    if x_grid:
        plot.xaxis.grid(x_grid, zorder=1)


def _set_axis_formatter(axis: Any, numeric: bool, percentage: bool) -> None:
    if numeric and percentage:
        raise ValueError("Cannot format ticks as both 'numeric' and 'percentage'. Choose one.")
    if numeric:
        axis.set_major_formatter(FuncFormatter(lambda val, _: format_thousands(val)))
    elif percentage:
        axis.set_major_formatter(FuncFormatter(lambda val, _: f"{val * 100:.0f}%"))


def _customize_ticks(plot: Axes, rotation: int) -> None:
    plot.tick_params(axis='x', colors=TextColors.DARK_GREY, which='both', color='white', rotation=rotation)
    plot.tick_params(axis='y', colors=TextColors.DARK_GREY, which='both', color='white')


def format_categorical_tick_labels(
    plot: Axes,
    label_map: Optional[Dict[Any, str]],
    axis: str,
) -> None:
    if not label_map:
        return
    if axis not in ('x', 'y'):
        raise ValueError("axis must be either 'x' or 'y'")

    target = plot.xaxis if axis == 'x' else plot.yaxis
    tick_labels = [tick.get_text() for tick in target.get_ticklabels()]
    target.set_ticks(target.get_ticklocs())
    target.set_ticklabels([label_map.get(label, label) for label in tick_labels])


def format_ticks(
    plot: Axes,
    x_grid: bool = False,
    y_grid: bool = False,
    numeric_x: bool = False,
    numeric_y: bool = False,
    percentage_x: bool = False,
    percentage_y: bool = False,
    rotation: int = 0,
) -> None:
    _configure_grid(plot, x_grid, y_grid)
    _set_axis_formatter(plot.xaxis, numeric_x, percentage_x)
    _set_axis_formatter(plot.yaxis, numeric_y, percentage_y)
    _customize_ticks(plot, rotation=rotation)
