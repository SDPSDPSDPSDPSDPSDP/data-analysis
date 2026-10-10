import pandas as pd
from typing import Any, Dict, Optional, Union

from ..config import OrderTypeInput, StackedLabelTypeInput, FigureSizeInput
from ..core import BarPlotOptions
from ..common.resolve_palette import resolve_palette
from ..plots import BarPlot


class BarPlotsMixin:
    @resolve_palette
    def barplot_x(
        self,
        df: pd.DataFrame,
        x: str,
        value: str,
        hue: Optional[str] = None,
        xlabel: str = '',
        ylabel: str = '',
        plot_legend: bool = True,
        legend_offset: float = 1.13,
        ncol: int = 2,
        figsize_width: FigureSizeInput = 'dynamic',
        stacked: bool = False,
        stacked_labels: StackedLabelTypeInput = None,
        order_type: OrderTypeInput = 'frequency',
        percentage_labels: bool = False,
        suffix: Optional[str] = None,
        # injected by @resolve_palette
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
    ) -> None:
        """Create a **vertical bar plot** with pre-aggregated data.

        _Unlike countplot, this requires a column with pre-calculated values._

        Args:
            df: DataFrame containing the pre-aggregated data.
            x: Column name for the x-axis categories.
            value: Column name containing the values to plot.
            hue: Column name for grouping data by color. *Optional*.
            xlabel: Label for the x-axis. *Default: `''`*.
            ylabel: Label for the y-axis. *Default: `''`*.
            plot_legend: Whether to show the legend. *Default: `True`*.
            legend_offset: Vertical position offset for legend. *Default: `1.13`*.
            ncol: Number of columns in the legend. *Default: `2`*.
            figsize_width: Figure width. **Options:** `'dynamic'`, `'standard'`, or a numeric value.
                *Default: `'dynamic'`*.
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            stacked_labels: Type of labels for stacked bars. **Options:** `'standard'`, `'percentage'`,
                or `None`. *Default: `None`*.
            order_type: How to order categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
            percentage_labels: Whether to format data labels as percentages. *Default: `False`*.
            suffix: Optional suffix appended to each data label (e.g. `'%'` -> `'12 %'`).
                *Default: `None`*.
        """
        options = BarPlotOptions(
            df=df,
            axis_column=x,
            value=value,
            orientation='vertical',
            hue=hue,
            palette=palette,
            label_map=label_map,
            xlabel=xlabel,
            ylabel=ylabel,
            plot_legend=plot_legend,
            legend_offset=legend_offset,
            ncol=ncol,
            figsize=figsize_width,
            stacked=stacked,
            stacked_labels=stacked_labels,
            order_type=order_type,
            percentage_labels=percentage_labels,
            suffix=suffix,
        )

        self._render(BarPlot(options))

    @resolve_palette
    def barplot_y(
        self,
        df: pd.DataFrame,
        y: str,
        value: str,
        hue: Optional[str] = None,
        xlabel: str = '',
        ylabel: str = '',
        plot_legend: bool = True,
        legend_offset: float = 1.13,
        ncol: int = 2,
        figsize_height: FigureSizeInput = 'dynamic',
        stacked: bool = False,
        stacked_labels: StackedLabelTypeInput = None,
        order_type: OrderTypeInput = 'frequency',
        percentage_labels: bool = False,
        suffix: Optional[str] = None,
        # injected by @resolve_palette
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
    ) -> None:
        """Create a **horizontal bar plot** with pre-aggregated data.

        _Unlike countplot, this requires a column with pre-calculated values._

        Args:
            df: DataFrame containing the pre-aggregated data.
            y: Column name for the y-axis categories.
            value: Column name containing the values to plot.
            hue: Column name for grouping data by color. *Optional*.
            xlabel: Label for the x-axis. *Default: `''`*.
            ylabel: Label for the y-axis. *Default: `''`*.
            plot_legend: Whether to show the legend. *Default: `True`*.
            legend_offset: Vertical position offset for legend. *Default: `1.13`*.
            ncol: Number of columns in the legend. *Default: `2`*.
            figsize_height: Figure height. **Options:** `'dynamic'`, `'standard'`, or a numeric value.
                *Default: `'dynamic'`*.
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            stacked_labels: Type of labels for stacked bars. **Options:** `'standard'`, `'percentage'`,
                or `None`. *Default: `None`*.
            order_type: How to order categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
            percentage_labels: Whether to format data labels as percentages. *Default: `False`*.
            suffix: Optional suffix appended to each data label (e.g. `'%'` -> `'12 %'`).
                *Default: `None`*.
        """
        options = BarPlotOptions(
            df=df,
            axis_column=y,
            value=value,
            orientation='horizontal',
            hue=hue,
            palette=palette,
            label_map=label_map,
            xlabel=xlabel,
            ylabel=ylabel,
            plot_legend=plot_legend,
            legend_offset=legend_offset,
            ncol=ncol,
            figsize=figsize_height,
            stacked=stacked,
            stacked_labels=stacked_labels,
            order_type=order_type,
            percentage_labels=percentage_labels,
            suffix=suffix,
        )

        self._render(BarPlot(options))
