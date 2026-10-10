import pandas as pd
from typing import Optional

from ..config import TitleInput, TimeGroupByInput
from ..core import PiePlotOptions, TimePlotOptions
from ..common.resolve_palette import resolve_palette
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
        # Reserved name: a user column called 'count' must not collide with the counts.
        options = PiePlotOptions(
            df=df[col].value_counts().rename('__count__').to_frame(),
            col='__count__',
            **resolve_palette(self, col),
            title=title,
            n_after_comma=n_after_comma,
            value_datalabel=value_datalabel,
            donut=donut,
        )
        self._render(PieChart(options))

    def timeplot(
        self,
        df: pd.DataFrame,
        x: str,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        display_month: bool = True,
        rotation: int = 0,
        group_by: TimeGroupByInput = 'day',
        plot_type: str = 'bar',
        cumulative: bool = False,
    ) -> None:
        """Create a **time series count plot** showing event frequencies over time.

        This plot counts occurrences of events in a datetime column and displays
        them as a bar chart with properly formatted date axes.

        Input:
            df: DataFrame containing the data to plot.
            x: Column name containing datetime values (`datetime64[ns]`).

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. *Optional*.
            y_axis_label: Label for the y-axis. *Optional*.
            display_month: Show month ticks (with year labels below) when grouping by month;
                `False` shows only years. *Default: `True`*.
            rotation: Rotation angle for x-axis labels when grouping by day. *Default: `0`*.

        Layout:
            group_by: Time period to group counts by. **Options:** `'year'`, `'month'`, `'day'`.
                *Default: `'day'`*.
            plot_type: Chart type. **Options:** `'bar'`, `'line'`. *Default: `'bar'`*.
            cumulative: Whether to calculate cumulative values by group. *Default: `False`*.

        Example:
            >>> plot = PlotGraphs()
            >>> plot.timeplot(df, x='date', group_by='month')
        """
        options = TimePlotOptions(
            df=df,
            x=x,
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            display_month=display_month,
            rotation=rotation,
            group_by=group_by,
            plot_type=plot_type,
            cumulative=cumulative,
        )
        self._render(TimePlot(options))
