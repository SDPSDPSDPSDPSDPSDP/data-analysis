from typing import Optional

import pandas as pd

from ..config import FillMissingValuesInput, TimeGroupByInput, TitleInput
from ..core import TimePlotOptions
from ..plots import TimePlot
from .host import PlotHost


class TimePlotsMixin(PlotHost):
    """Time series: one value per date or period along the x-axis."""

    def time(
        self,
        df: pd.DataFrame,
        x: str,
        y: Optional[str] = None,
        hue: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[TitleInput] = None,
        y_axis_label: Optional[TitleInput] = None,
        rotation: int = 0,
        legend: bool = False,
        group_by: Optional[TimeGroupByInput] = None,
        cumulative: bool = False,
        display_month: bool = True,
        fill_missing_values: FillMissingValuesInput = None,
        fill: bool = False,
    ) -> None:
        """Create a **time plot**: a line over `x`, one line per `hue` group.

        Input:
            df: DataFrame containing the data to plot.
            x: Column name for the x-axis values, usually dates.
            y: Column name for the y-axis values. Without `y` the plot counts the rows per
                `x` value. *Optional*.
            hue: Column name for grouping data by color. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. Pass `['label', 'sublabel']` to add a grey second line. *Optional*.
            y_axis_label: Label for the y-axis. Pass `['label', 'sublabel']` to add a grey second line. *Optional*.
            rotation: Rotation angle for x-axis tick labels. *Default: `0`*.
            legend: Whether to show the legend. *Default: `False`*.
            display_month: Show month ticks (with year labels below) when grouping by month;
                `False` shows only years. *Default: `True`*.

        Layout:
            group_by: Group dates in `x` per period and sum `y` (or count rows) per period.
                Empty periods count as zero. **Options:** `'year'`, `'month'`, `'day'`. *Optional*.
            cumulative: Running total over `x`, per `hue` group. *Default: `False`*.
            fill_missing_values: How to fill gaps in `y`. **Options:** `'shift'` (interpolate
                between neighbours), `'zero'`. *Optional*.
            fill: Shade the area under each line with a gradient that fades out towards
                the bottom. *Default: `False`*.

        Example:
            >>> plot = PlotGraphs()
            >>> plot.time(df, x='date', group_by='month', cumulative=True)
        """
        options = TimePlotOptions(
            df=df,
            x=x,
            y=y,
            hue=hue,
            **self._column_config(hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            rotation=rotation,
            legend=legend,
            group_by=group_by,
            cumulative=cumulative,
            display_month=display_month,
            fill_missing_values=fill_missing_values,
            fill=fill,
        )
        self._render(TimePlot(options))
