from typing import Any, Dict, Optional

import pandas as pd

from ....number_format import format_percentage, format_thousands
from ...config import Layout
from ...svg import Axis, Chart


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
    if target.tick_labels is None:
        raise ValueError(f"Categorical {axis}-axis has no tick labels to map")
    target.tick_labels = [label_map.get(label, label) for label in target.tick_labels]


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


def format_period_ticks(chart: Chart, periods: pd.Series, positions: pd.Series, months: bool) -> None:
    """Month ticks with a year row below when months, else year ticks; positions are aligned to periods.

    Long monthly axes label every 2nd, 3rd or 6th month, or fall back to years.
    """
    step = next((s for s in Layout.MONTH_TICK_STEPS if len(periods) / s <= Layout.MAX_MONTH_TICKS), None)
    if months and step is not None:
        shown, fmt = (periods.dt.month - 1) % step == 0, '%b'
        chart.x.rotation = Layout.MONTH_TICK_ROTATION
        first_of_year = periods.groupby(periods.dt.year).idxmin()
        chart.x.sub_labels = [(positions[i], str(periods[i].year)) for i in first_of_year]
    else:
        shown, fmt = periods.dt.month == 1, '%Y'
    chart.x.ticks = list(positions[shown])
    chart.x.tick_labels = [d.strftime(fmt) for d in periods[shown]]
