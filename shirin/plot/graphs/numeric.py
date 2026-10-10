import pandas as pd
from typing import Any, Dict, Optional, Union

from ..config import FillMissingValuesInput
from ..core import HistogramOptions, LinePlotOptions, ScatterPlotOptions
from ..common.resolve_palette import resolve_palette
from ..plots import Histogram, LinePlot, ScatterPlot


class NumericPlotsMixin:
    @resolve_palette
    def histogram(
        self,
        df: pd.DataFrame,
        x: str,
        hue: Optional[str] = None,
        xlabel: str = '',
        ylabel: str = 'Count',
        xlimit: Optional[Union[float, int]] = None,
        bins: int = 100,
        stacked: Optional[bool] = None,
        plot_legend: bool = True,
        title: str = '',
        subtitle: str = '',
        # injected by @resolve_palette
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
    ) -> None:
        """Create a **histogram** of a numeric column.

        Args:
            df: DataFrame containing the data to plot.
            x: Column name with the numeric values.
            hue: Column name for grouping data by color. *Optional*.
            xlabel: Label for the x-axis. *Default: `''`*.
            ylabel: Label for the y-axis. *Default: `'Count'`*.
            xlimit: Upper bound only: rows with `x` above it are dropped. *Optional*.
            bins: Maximum number of bins; whole-number data gets at most one bin per value.
                *Default: `100`*.
            stacked: With `hue`, `False` dodges the groups, otherwise they stack. *Optional*.
            plot_legend: Whether to show the legend. *Default: `True`*.
            title: Chart title above the plot. *Default: `''`*.
            subtitle: Grey line under the title. *Default: `''`*.
        """
        options = HistogramOptions(
            df=df,
            x=x,
            xlabel=xlabel,
            ylabel=ylabel,
            xlimit=xlimit,
            bins=bins,
            palette=palette,
            label_map=label_map,
            hue=hue,
            stacked=stacked,
            plot_legend=plot_legend,
            title=title,
            subtitle=subtitle,
        )
        self._render(Histogram(options))

    @resolve_palette
    def lineplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        hue: Optional[str] = None,
        xlabel: str = '',
        ylabel: str = '',
        plot_legend: bool = True,
        title: str = '',
        subtitle: str = '',
        rotation: int = 0,
        fill_missing_values: FillMissingValuesInput = None,
        # injected by @resolve_palette
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
    ) -> None:
        options = LinePlotOptions(
            df=df,
            x=x,
            y=y,
            hue=hue,
            palette=palette,
            label_map=label_map,
            xlabel=xlabel,
            ylabel=ylabel,
            plot_legend=plot_legend,
            title=title,
            subtitle=subtitle,
            rotation=rotation,
            fill_missing_values=fill_missing_values
        )
        self._render(LinePlot(options))

    @resolve_palette
    def scatterplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        hue: Optional[str] = None,
        size: Optional[str] = None,
        xlabel: str = '',
        ylabel: str = '',
        plot_legend: bool = True,
        title: str = '',
        subtitle: str = '',
        # injected by @resolve_palette
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
    ) -> None:
        """Create a **scatter plot** showing the relationship between two numeric columns.

        Args:
            df: DataFrame containing the data to plot.
            x: Column name for the x-axis values.
            y: Column name for the y-axis values.
            hue: Column name for grouping data by color. *Optional*.
            size: Column name for scaling point size. *Optional*.
            xlabel: Label for the x-axis. *Default: `''`*.
            ylabel: Label for the y-axis. *Default: `''`*.
            plot_legend: Whether to show the legend. *Default: `True`*.
            title: Chart title above the plot. *Default: `''`*.
            subtitle: Grey line under the title. *Default: `''`*.
        """
        options = ScatterPlotOptions(
            df=df,
            x=x,
            y=y,
            hue=hue,
            size=size,
            palette=palette,
            label_map=label_map,
            xlabel=xlabel,
            ylabel=ylabel,
            plot_legend=plot_legend,
            title=title,
            subtitle=subtitle,
        )
        self._render(ScatterPlot(options))
