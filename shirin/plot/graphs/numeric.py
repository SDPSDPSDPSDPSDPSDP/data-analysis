import pandas as pd
from typing import Optional, Union

from ..config import TitleInput, FillMissingValuesInput
from ..core import HistogramOptions, LinePlotOptions, ScatterPlotOptions
from ..common.resolve_palette import resolve_palette
from ..plots import Histogram, LinePlot, ScatterPlot


class NumericPlotsMixin:
    def histogram(
        self,
        df: pd.DataFrame,
        x: str,
        hue: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        legend: bool = False,
        bins: int = 100,
        xlimit: Optional[Union[float, int]] = None,
        stacked: Optional[bool] = None,
    ) -> None:
        """Create a **histogram** of a numeric column.

        Input:
            df: DataFrame containing the data to plot.
            x: Column name with the numeric values.
            hue: Column name for grouping data by color. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. *Optional*.
            y_axis_label: Label for the y-axis. *Optional*.
            legend: Whether to show the legend. *Default: `False`*.

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
            **resolve_palette(self, hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            legend=legend,
            bins=bins,
            xlimit=xlimit,
            stacked=stacked,
        )
        self._render(Histogram(options))

    def lineplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        hue: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        rotation: int = 0,
        legend: bool = False,
        fill_missing_values: FillMissingValuesInput = None,
    ) -> None:
        """Create a **line plot**, one line per `hue` group.

        Input:
            df: DataFrame containing the data to plot.
            x: Column name for the x-axis values.
            y: Column name for the y-axis values.
            hue: Column name for grouping data by color. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. *Optional*.
            y_axis_label: Label for the y-axis. *Optional*.
            rotation: Rotation angle for x-axis tick labels. *Default: `0`*.
            legend: Whether to show the legend. *Default: `False`*.

        Layout:
            fill_missing_values: How to fill gaps in `y`. **Options:** `'shift'` (interpolate
                between neighbours), `'zero'`. *Optional*.
        """
        options = LinePlotOptions(
            df=df,
            x=x,
            y=y,
            hue=hue,
            **resolve_palette(self, hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            rotation=rotation,
            legend=legend,
            fill_missing_values=fill_missing_values,
        )
        self._render(LinePlot(options))

    def scatterplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        hue: Optional[str] = None,
        size: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
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
            x_axis_label: Label for the x-axis. *Optional*.
            y_axis_label: Label for the y-axis. *Optional*.
            legend: Whether to show the legend. *Default: `False`*.
        """
        options = ScatterPlotOptions(
            df=df,
            x=x,
            y=y,
            hue=hue,
            size=size,
            **resolve_palette(self, hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            legend=legend,
        )
        self._render(ScatterPlot(options))
