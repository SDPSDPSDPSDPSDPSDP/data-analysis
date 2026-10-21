from typing import Optional, Union

import pandas as pd

from ..config import TitleInput
from ..core import HistogramOptions, ScatterPlotOptions
from ..plots import Histogram, ScatterPlot


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
            x_axis_label: Label for the x-axis. *Optional*.
            y_axis_label: Label for the y-axis. *Optional*.
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
            **self._column_config(hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            legend=legend,
        )
        self._render(ScatterPlot(options))
