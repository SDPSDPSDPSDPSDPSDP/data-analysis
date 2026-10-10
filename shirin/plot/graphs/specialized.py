import pandas as pd
from typing import Optional

from ..config import TitleInput, TimeGroupByInput
from ..config.colors import Colors
from ..core import AccuracyPlotOptions, PiePlotOptions, TimePlotOptions
from ..common.resolve_palette import resolve_palette
from ..plots import AccuracyPlot, PieChart, TimePlot


class SpecializedPlotsMixin:
    """Plots with chart-specific layouts: pie, time series, accuracy."""

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

    def accuracy(
        self,
        df: pd.DataFrame,
        experiment: str,
        accuracy: str,
        title: Optional[TitleInput] = None,
        experiment_label: Optional[str] = None,
        accuracy_label: Optional[str] = None,
        suffix: Optional[str] = None,
        legend: bool = False,
        orientation: str = 'vertical',
        reverse_order: bool = False,
        color_correct: str = Colors.GOOD_GREEN,
        color_incorrect: str = Colors.BAD_RED,
    ) -> None:
        """Create a **stacked accuracy bar plot** from pre-computed accuracy values.

        Each bar is split into two segments: *Correct* (the accuracy fraction) at
        the bottom and *Incorrect* (1 - accuracy) stacked on top.

        Input:
            df: DataFrame with one row per run / category.
            experiment: Column name for the bar categories (e.g. `'run_name'`).
            accuracy: Column name containing accuracy values as fractions in **[0, 1]**
                (e.g. `0.78` for 78 %).

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            experiment_label: Label for the category axis. *Optional*.
            accuracy_label: Label for the value axis. *Optional*.
            suffix: Text appended to stacked labels. When omitted, accuracy labels keep their
                default `%` formatting. *Optional*.
            legend: Whether to show the legend. *Default: `False`*.

        Layout:
            orientation: Direction of the bars. **Options:** `'vertical'` (bars grow upward),
                `'horizontal'` (bars grow rightward). *Default: `'vertical'`*.
            reverse_order: Put the lowest accuracy first (left, or top when horizontal) instead of
                the highest. *Default: `False`*.
            color_correct: Hex colour for the correct segment. *Default: `Colors.GOOD_GREEN`*.
            color_incorrect: Hex colour for the incorrect segment. *Default: `Colors.BAD_RED`*.

        Example:
            >>> df = pd.DataFrame({'run_name': ['medium', 'nano', 'small'],
            ...                    'accuracy':  [0.78,     0.78,   0.78]})
            >>> plot.accuracy(
            ...     df,
            ...     experiment='run_name',
            ...     accuracy='accuracy',
            ...     experiment_label='Experiment Name',
            ...     accuracy_label='Accuracy',
            ...     orientation='horizontal',
            ... )
        """
        options = AccuracyPlotOptions(
            df=df,
            axis_column=experiment,
            value_column=accuracy,
            palette={'Correct': color_correct, 'Incorrect': color_incorrect},
            title=title,
            x_axis_label=experiment_label,
            y_axis_label=accuracy_label,
            suffix=suffix,
            legend=legend,
            orientation=orientation,
            reverse_order=reverse_order,
        )

        self._render(AccuracyPlot(options))
