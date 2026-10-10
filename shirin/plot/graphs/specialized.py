import pandas as pd
from typing import Any, Dict, Optional

from ..config import TimeGroupByInput
from ..config.colors import Colors
from ..core import AccuracyPlotOptions, PiePlotOptions, TimePlotOptions
from ..common.resolve_palette import resolve_palette
from ..plots import AccuracyPlot, PieChart, TimePlot


class SpecializedPlotsMixin:
    """Plots with chart-specific layouts: pie, time series, accuracy."""

    @resolve_palette
    def pie(
        self,
        df: pd.DataFrame,
        col: str,
        n_after_comma: int = 0,
        value_datalabel: int = 5,
        donut: bool = False,
        title: str = '',
        subtitle: str = '',
        # injected by @resolve_palette
        palette: Optional[Dict[Any, str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
    ) -> None:
        # Reserved name: a user column called 'count' must not collide with the counts.
        options = PiePlotOptions(
            df=df[col].value_counts().rename('__count__').to_frame(),
            col='__count__',
            palette=palette,
            label_map=label_map,
            n_after_comma=n_after_comma,
            value_datalabel=value_datalabel,
            donut=donut,
            title=title,
            subtitle=subtitle,
        )
        self._render(PieChart(options))

    def timeplot(
        self,
        df: pd.DataFrame,
        x: str,
        group_by: TimeGroupByInput = 'day',
        palette: Optional[str] = None,
        xlabel: str = '',
        ylabel: str = 'Total',
        plot_type: str = 'bar',
        display_month: bool = True,
        cumulative: bool = False,
        rotation: int = 0,
        title: str = '',
        subtitle: str = '',
    ) -> None:
        """Create a **time series count plot** showing event frequencies over time.

        This plot counts occurrences of events in a datetime column and displays
        them as a bar chart with properly formatted date axes.

        Args:
            df: DataFrame containing the data to plot.
            x: Column name containing datetime values (`datetime64[ns]`).
            group_by: Time period to group counts by. **Options:** `'year'`, `'month'`, `'day'`.
                *Default: `'day'`*.
            palette: Color for the bars (single color string, e.g. `'#FF5733'`). *Optional*.
            xlabel: Label for the x-axis. *Default: `''`*.
            ylabel: Label for the y-axis. *Default: `'Total'`*.
            plot_type: Chart type. **Options:** `'bar'`, `'line'`. *Default: `'bar'`*.
            display_month: Show month ticks (with year labels below) when grouping by month;
                `False` shows only years. *Default: `True`*.
            cumulative: Whether to calculate cumulative values by group. *Default: `False`*.
            rotation: Rotation angle for x-axis labels when grouping by day. *Default: `0`*.
            title: Chart title above the plot. *Default: `''`*.
            subtitle: Grey line under the title. *Default: `''`*.

        Example:
            >>> plot = PlotGraphs()
            >>> plot.timeplot(df, x='date', group_by='month')
        """
        options = TimePlotOptions(
            df=df,
            x=x,
            group_by=group_by,
            palette=palette,
            xlabel=xlabel,
            ylabel=ylabel,
            plot_type=plot_type,
            display_month=display_month,
            cumulative=cumulative,
            rotation=rotation,
            title=title,
            subtitle=subtitle,
        )
        self._render(TimePlot(options))

    def accuracy(
        self,
        df: pd.DataFrame,
        experiment: str,
        accuracy: str,
        color_correct: str = Colors.GOOD_GREEN,
        color_incorrect: str = Colors.BAD_RED,
        experiment_label: str = '',
        accuracy_label: str = '',
        orientation: str = 'vertical',
        reverse_order: bool = False,
        plot_legend: bool = False,
        suffix: Optional[str] = None,
        title: str = '',
        subtitle: str = '',
    ) -> None:
        """Create a **stacked accuracy bar plot** from pre-computed accuracy values.

        Each bar is split into two segments: *Correct* (the accuracy fraction) at
        the bottom and *Incorrect* (1 − accuracy) stacked on top.

        Args:
            df: DataFrame with one row per run / category.
            experiment: Column name for the bar categories (e.g. ``'run_name'``).
            accuracy: Column name containing accuracy values as fractions in **[0, 1]**
                (e.g. ``0.78`` for 78 %).
            color_correct: Hex colour for the correct segment. *Default: ``Colors.GOOD_GREEN``*.
            color_incorrect: Hex colour for the incorrect segment. *Default: ``Colors.BAD_RED``*.
            experiment_label: Label for the category axis. *Default: ``''``*.
            accuracy_label: Label for the value axis. *Default: ``''``*.
            orientation: Direction of the bars. **Options:** ``'vertical'`` (bars grow upward),
                ``'horizontal'`` (bars grow rightward). *Default: ``'vertical'``*.
            reverse_order: Whether to reverse the default sorting order.
                - Vertical default is highest accuracy first; with ``True`` lowest is first.
                - Horizontal default is highest at the top; with ``True`` lowest is at the top.
                *Default: ``False``*.
            plot_legend: Whether to show the legend. *Default: ``False``*.
            suffix: Optional suffix appended to stacked labels.
                When omitted, accuracy labels keep their default ``%`` formatting.
            title: Chart title above the plot. *Default: ``''``*.
            subtitle: Grey line under the title. *Default: ``''``*.

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
            xlabel=experiment_label,
            ylabel=accuracy_label,
            orientation=orientation,
            reverse_order=reverse_order,
            plot_legend=plot_legend,
            suffix=suffix,
            title=title,
            subtitle=subtitle,
        )

        self._render(AccuracyPlot(options))
