from typing import Optional, Tuple, Union

import pandas as pd

from ..config import TitleInput
from ..core import HistogramOptions, LinePlotOptions, ScatterPlotOptions
from ..plots import Histogram, LinePlot, ScatterPlot


class NumericPlotsMixin:
    def histogram(
        self,
        df: pd.DataFrame,
        x: str,
        hue: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[TitleInput] = None,
        y_axis_label: Optional[TitleInput] = None,
        legend: bool = False,
        bins: int = 100,
        xlimit: Optional[Union[float, int]] = None,
        stacked: Optional[bool] = None,
        suffix: Optional[str] = None,
    ) -> None:
        """Create a **histogram** of a numeric column.

        Input:
            df: DataFrame containing the data to plot.
            x: Column name with the numeric values.
            hue: Column name for grouping data by color. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. Pass `['label', 'sublabel']` to add a grey second line. *Optional*.
            y_axis_label: Label for the y-axis. Pass `['label', 'sublabel']` to add a grey second line. *Optional*.
            legend: Whether to show the legend. *Default: `False`*.
            suffix: Text appended to each x tick label (e.g. `'%'` -> `'12 %'`). *Optional*.

        Layout:
            bins: Maximum number of bins; whole-number data gets at most one bin per value.
                *Default: `100`*.
            xlimit: Upper bound only: rows with `x` above it are dropped. *Optional*.
            stacked: With `hue`, `False` dodges the groups, otherwise they stack. *Optional*.
        """
        options = HistogramOptions(
            df=df,
            x=x,
            hue=hue,
            **self._column_config(hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            legend=legend,
            bins=bins,
            xlimit=xlimit,
            stacked=stacked,
            suffix=suffix,
        )
        self._render(Histogram(options))

    def scatter(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        hue: Optional[str] = None,
        size: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[TitleInput] = None,
        y_axis_label: Optional[TitleInput] = None,
        legend: bool = False,
    ) -> None:
        """Create a **scatter plot** showing the relationship between two numeric columns.

        Input:
            df: DataFrame containing the data to plot.
            x: Column name for the x-axis values.
            y: Column name for the y-axis values.
            hue: Column name for grouping data by color. *Optional*.
            size: Column name for scaling point size. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. Pass `['label', 'sublabel']` to add a grey second line. *Optional*.
            y_axis_label: Label for the y-axis. Pass `['label', 'sublabel']` to add a grey second line. *Optional*.
            legend: Whether to show the legend. *Default: `False`*.
        """
        options = ScatterPlotOptions(
            df=df,
            x=x,
            y=y,
            hue=hue,
            size=size,
            **self._column_config(hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            legend=legend,
        )
        self._render(ScatterPlot(options))

    def line(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        hue: Optional[str] = None,
        marks: Optional[str] = None,
        mark_labels: Optional[str] = 'y',
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[TitleInput] = None,
        y_axis_label: Optional[TitleInput] = None,
        legend: bool = False,
        percentage_x: bool = False,
        percentage_y: bool = False,
        x_limits: Optional[Tuple[float, float]] = None,
        y_limits: Optional[Tuple[float, float]] = None,
    ) -> None:
        """Create a **line plot** of two numeric columns, one line per `hue` group.

        Input:
            df: DataFrame containing the data to plot.
            x: Numeric column for the x-axis. Duplicate x values (per hue) are averaged.
            y: Numeric column for the y-axis.
            hue: Column name for grouping data by color. *Optional*.
            marks: Boolean column; rows with `True` get a dot on the line. *Optional*.
            mark_labels: Text next to each mark: `'y'`, `'x'`, `'both'` (as `(x; y)`) or `None` for
                dots only. Formatted like the axis, so `%` when `percentage_x`/`percentage_y`. *Default: `'y'`*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. Pass `['label', 'sublabel']` to add a grey second line. *Optional*.
            y_axis_label: Label for the y-axis. Pass `['label', 'sublabel']` to add a grey second line. *Optional*.
            legend: Whether to show the legend. *Default: `False`*.
            percentage_x: Show x ticks as percentages of fractions (`0.25` -> `'25%'`). *Default: `False`*.
            percentage_y: Same for the y ticks. *Default: `False`*.

        Layout:
            x_limits: `(low, high)` range of the x-axis; `high < low` flips the axis. *Optional*.
            y_limits: Same for the y-axis. *Optional*.

        Example:
            >>> plot = PlotGraphs()
            >>> plot.line(df, x='coverage', y='accuracy', marks='marked', mark_labels='both', percentage_x=True,
            ...           x_axis_label=['Coverage', 'share of docs at or above the threshold'], x_limits=(1, 0))
        """
        options = LinePlotOptions(
            df=df,
            x=x,
            y=y,
            hue=hue,
            marks=marks,
            mark_labels=mark_labels,
            **self._column_config(hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            legend=legend,
            percentage_x=percentage_x,
            percentage_y=percentage_y,
            x_limits=x_limits,
            y_limits=y_limits,
        )
        self._render(LinePlot(options))
