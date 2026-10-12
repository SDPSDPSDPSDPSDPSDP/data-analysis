import pandas as pd
from typing import Optional

from ..config import FillMissingValuesInput, TitleInput, TimeGroupByInput
from ..common.data_conversion import COUNT_COL
from ..core import PiePlotOptions, TimePlotOptions
from ..plots import PieChart, TimePlot


class SpecializedPlotsMixin:
    """Plots with chart-specific layouts: pie, time series."""

    def pie(
        self,
        df: pd.DataFrame,
        col: str,
        title: Optional[TitleInput] = None,
        n_after_comma: int = 0,
        value_datalabel: int = 5,
        donut: bool = False,
    ) -> None:
        """Create a **pie chart** of the value counts in a column.

        Input:
            df: DataFrame containing the data to plot.
            col: Column whose value counts become the slices.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            n_after_comma: Decimals in the percentage labels. *Default: `0`*.
            value_datalabel: Slices below this percentage get no label. *Default: `5`*.

        Layout:
            donut: Whether to draw a donut instead of a full pie. *Default: `False`*.
        """
        options = PiePlotOptions(
            df=df[col].value_counts().rename(COUNT_COL).to_frame(),
            col=COUNT_COL,
            **self._column_config(col),
            title=title,
            n_after_comma=n_after_comma,
            value_datalabel=value_datalabel,
            donut=donut,
        )
        self._render(PieChart(options))

    def time(
        self,
        df: pd.DataFrame,
        x: str,
        y: Optional[str] = None,
        hue: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        rotation: int = 0,
        legend: bool = False,
        group_by: Optional[TimeGroupByInput] = None,
        cumulative: bool = False,
        display_month: bool = True,
        fill_missing_values: FillMissingValuesInput = None,
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
            x_axis_label: Label for the x-axis. *Optional*.
            y_axis_label: Label for the y-axis. *Optional*.
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
        )
        self._render(TimePlot(options))
