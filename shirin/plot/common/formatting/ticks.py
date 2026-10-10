from typing import Any, Dict, Optional

from ...svg import Axis, Chart
from ....number_format import format_percentage, format_thousands


def _set_axis_formatter(axis: Axis, numeric: bool, percentage: bool) -> None:
    if numeric and percentage:
        raise ValueError("Cannot format ticks as both 'numeric' and 'percentage'. Choose one.")
    if numeric:
        axis.formatter = format_thousands
    elif percentage:
        axis.formatter = lambda val: format_percentage(val * 100)


def format_categorical_tick_labels(
    chart: Chart,
    label_map: Optional[Dict[Any, str]],
    axis: str,
) -> None:
    if not label_map:
        return
    if axis not in ('x', 'y'):
        raise ValueError("axis must be either 'x' or 'y'")

    target = chart.x if axis == 'x' else chart.y
    target.tick_labels = [label_map.get(label, label) for label in target.tick_labels or []]


def format_ticks(
    chart: Chart,
    x_grid: bool = False,
    y_grid: bool = False,
    numeric_x: bool = False,
    numeric_y: bool = False,
    percentage_x: bool = False,
    percentage_y: bool = False,
    rotation: int = 0,
) -> None:
    chart.x.grid, chart.y.grid = x_grid, y_grid
    _set_axis_formatter(chart.x, numeric_x, percentage_x)
    _set_axis_formatter(chart.y, numeric_y, percentage_y)
    chart.x.rotation = rotation
