import os
import pandas as pd
from typing import Any, Dict, Optional, Union
import matplotlib.pyplot as plt

from .config import OrderTypeInput, StackedLabelTypeInput, FigureSizeInput, FillMissingValuesInput, TimeGroupByInput
from .core import (
    PlotExporter,
    CountPlotOptions,
    BarPlotOptions,
    HistogramOptions,
    LinePlotOptions,
    PiePlotOptions,
    NormalizedCountPlotOptions,
    TimePlotOptions,
    create_plot,
)
from .common.file_operations import calculate_value_counts


class PlotGraphs:
    """A comprehensive plotting interface for creating and exporting data visualizations.
    
    This class provides methods for creating various types of plots including **count plots**,
    **bar plots**, **histograms**, **line plots**, and **pie charts**. All plots can be automatically
    exported to files with customizable settings.
    
    Args:
        export: Whether to automatically export plots to files. *Default: `True`*.
        output_dir: Directory where exported plots will be saved. *Default: `'./plot_output/'`*.
        prefix: Optional prefix to add to all exported filenames. *Default: `None`*.
        format: File format for exported plots. **Options:** `'png'`, `'svg'`. *Default: `'png'`*.
    
    Example:
        >>> plot = PlotGraphs(export=True, output_dir='./charts/', prefix='analysis')
        >>> plot.countplot_x(df, x='category', output_name='category_counts')
    """

    def __init__(
        self,
        export: bool = True,
        output_dir: str = os.path.expanduser("./plot_output/"),
        prefix: Optional[str] = None,
        format: str = 'png'
    ) -> None:
        self._exporter = PlotExporter(
            enabled=export,
            output_dir=output_dir,
            prefix=prefix,
            format=format,
            auto_show=True
        )

    def _export_graph(self, output_name: str) -> None:
        self._exporter.export_and_show(output_name)

    def countplot_x(
        self,
        df: pd.DataFrame,
        x: str,
        hue: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
        xlabel: str = '',
        ylabel: str = 'Count',
        plot_legend: bool = True,
        legend_offset: float = 1.13,
        ncol: int = 2,
        top_n: Optional[int] = None,
        figsize_width: FigureSizeInput = 'dynamic',
        stacked: bool = False,
        stacked_labels: StackedLabelTypeInput = None,
        order_type: OrderTypeInput = 'frequency',
        normalized: bool = False,
        show_labels: bool = True,
        output_name: str = 'countplot_x'
    ) -> None:
        """Create a **vertical count plot** showing category frequencies.
        
        Args:
            df: DataFrame containing the data to plot.
            x: Column name for the x-axis categories.
            hue: Column name for grouping data by color. *Optional*.
            palette: Color scheme. Can be a seaborn palette name (`str`) or a `dict` mapping
                categories to hex colors. *Optional*.
            label_map: `Dict` mapping original category values to display labels. *Optional*.
            xlabel: Label for the x-axis. *Default: `''`*.
            ylabel: Label for the y-axis. *Default: `'Count'`*.
            plot_legend: Whether to show the legend. *Default: `True`*.
            legend_offset: Vertical position offset for legend. *Default: `1.13`*.
            ncol: Number of columns in the legend. *Default: `2`*.
            top_n: Show only the top N most frequent categories. *Optional*.
            figsize_width: Figure width. **Options:** `'dynamic'`, `'standard'`, or a numeric value.
                *Default: `'dynamic'`*.
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            stacked_labels: Type of labels for stacked bars. **Options:** `'standard'`, `'percentage'`,
                or `None`. *Default: `None`*.
            order_type: How to order categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
            normalized: Whether to normalize counts to percentages (_requires `hue` and dict `palette`_).
                *Default: `False`*.
            show_labels: Whether to show data labels on bars. *Default: `True`*.
            output_name: Name for the exported file. *Default: `'countplot_x'`*.
        """
        if normalized:
            if hue is None:
                raise ValueError("hue must be provided when normalized=True")
            if not isinstance(palette, dict):
                raise ValueError("palette must be a dictionary when normalized=True")
            options = NormalizedCountPlotOptions(
                df=df,
                axis_column=x,
                orientation='vertical',
                hue=hue,
                palette=palette,
                label_map=label_map,
                xlabel=xlabel,
                ylabel=ylabel,
                plot_legend=plot_legend,
                legend_offset=legend_offset,
                ncol=ncol,
                top_n=top_n,
                figsize=figsize_width,
                order_type=order_type,
                show_labels=show_labels
            )
            plot = create_plot('normalized_count', options)
            plot.render()
        else:
            options = CountPlotOptions(
                df=df,
                axis_column=x,
                orientation='vertical',
                hue=hue,
                palette=palette,
                label_map=label_map,
                xlabel=xlabel,
                ylabel=ylabel,
                plot_legend=plot_legend,
                legend_offset=legend_offset,
                ncol=ncol,
                top_n=top_n,
                figsize=figsize_width,
                stacked=stacked,
                stacked_labels=stacked_labels,
                order_type=order_type,
                normalized=False,
                show_labels=show_labels
            )
            plot = create_plot('count', options)
            plot.render()
        self._export_graph(output_name)

    def countplot_y(
        self,
        df: pd.DataFrame,
        y: str,
        hue: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
        xlabel: str = 'Count',
        ylabel: str = '',
        plot_legend: bool = True,
        legend_offset: float = 1.13,
        ncol: int = 2,
        top_n: Optional[int] = None,
        figsize_height: FigureSizeInput = 'dynamic',
        stacked: bool = False,
        stacked_labels: StackedLabelTypeInput = None,
        order_type: OrderTypeInput = 'frequency',
        normalized: bool = False,
        show_labels: bool = True,
        output_name: str = 'countplot_y'
    ) -> None:
        """Create a **horizontal count plot** showing category frequencies.
        
        Args:
            df: DataFrame containing the data to plot.
            y: Column name for the y-axis categories.
            hue: Column name for grouping data by color. *Optional*.
            palette: Color scheme. Can be a seaborn palette name (`str`) or a `dict` mapping
                categories to hex colors. *Optional*.
            label_map: `Dict` mapping original category values to display labels. *Optional*.
            xlabel: Label for the x-axis. *Default: `'Count'`*.
            ylabel: Label for the y-axis. *Default: `''`*.
            plot_legend: Whether to show the legend. *Default: `True`*.
            legend_offset: Vertical position offset for legend. *Default: `1.13`*.
            ncol: Number of columns in the legend. *Default: `2`*.
            top_n: Show only the top N most frequent categories. *Optional*.
            figsize_height: Figure height. **Options:** `'dynamic'`, `'standard'`, or a numeric value.
                *Default: `'dynamic'`*.
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            stacked_labels: Type of labels for stacked bars. **Options:** `'standard'`, `'percentage'`,
                or `None`. *Default: `None`*.
            order_type: How to order categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
            normalized: Whether to normalize counts to percentages (_requires `hue` and dict `palette`_).
                *Default: `False`*.
            show_labels: Whether to show data labels on bars. *Default: `True`*.
            output_name: Name for the exported file. *Default: `'countplot_y'`*.
        """
        if normalized:
            if hue is None:
                raise ValueError("hue must be provided when normalized=True")
            if not isinstance(palette, dict):
                raise ValueError("palette must be a dictionary when normalized=True")
            options = NormalizedCountPlotOptions(
                df=df,
                axis_column=y,
                orientation='horizontal',
                hue=hue,
                palette=palette,
                label_map=label_map,
                xlabel=xlabel,
                ylabel=ylabel,
                plot_legend=plot_legend,
                legend_offset=legend_offset,
                ncol=ncol,
                top_n=top_n,
                figsize=figsize_height,
                order_type=order_type,
                show_labels=show_labels
            )
            plot = create_plot('normalized_count', options)
            plot.render()
        else:
            options = CountPlotOptions(
                df=df,
                axis_column=y,
                orientation='horizontal',
                hue=hue,
                palette=palette,
                label_map=label_map,
                xlabel=xlabel,
                ylabel=ylabel,
                plot_legend=plot_legend,
                legend_offset=legend_offset,
                ncol=ncol,
                top_n=top_n,
                figsize=figsize_height,
                stacked=stacked,
                stacked_labels=stacked_labels,
                order_type=order_type,
                normalized=False,
                show_labels=show_labels
            )
            plot = create_plot('count', options)
            plot.render()
        self._export_graph(output_name)

    def histogram(
        self,
        df: pd.DataFrame,
        x: str,
        xlabel: str = '',
        ylabel: str = 'Count',
        xlimit: Optional[Union[float, int]] = None,
        bins: int = 100,
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
        hue: Optional[str] = None,
        stacked: Optional[bool] = None,
        plot_legend: bool = True,
        legend_offset: float = 1.13,
        ncol: int = 2,
        output_name: str = 'histogram'
    ) -> None:
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
            legend_offset=legend_offset,
            ncol=ncol
        )
        plot = create_plot('histogram', options)
        plot.render()
        self._export_graph(output_name)

    def pie(
        self,
        df: pd.DataFrame,
        col: str,
        palette: Dict[Any, str],
        label_map: Optional[Dict[Any, str]] = None,
        n_after_comma: int = 0,
        value_datalabel: int = 5,
        donut: bool = False,
        output_name: str = 'pie_value_counts'
    ) -> None:
        df_value_counts = calculate_value_counts(df, col)
        options = PiePlotOptions(
            df=df_value_counts.set_index(col),
            col='count',
            palette=palette,
            label_map=label_map,
            n_after_comma=n_after_comma,
            value_datalabel=value_datalabel,
            donut=donut
        )
        plot = create_plot('pie', options)
        plot.render()
        self._export_graph(output_name)


    def lineplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        hue: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
        xlabel: str = '',
        ylabel: str = '',
        plot_legend: bool = True,
        legend_offset: float = 1.13,
        ncol: int = 2,
        rotation: int = 0,
        fill_missing_values: FillMissingValuesInput = None,
        output_name: str = 'lineplot'
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
            legend_offset=legend_offset,
            ncol=ncol,
            rotation=rotation,
            fill_missing_values=fill_missing_values
        )
        plot = create_plot('line', options)
        plot.render()
        self._export_graph(output_name)

    def barplot_x(
        self,
        df: pd.DataFrame,
        x: str,
        value: str,
        hue: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
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
        output_name: str = 'barplot_x'
    ) -> None:
        """Create a **vertical bar plot** with pre-aggregated data.
        
        _Unlike countplot, this requires a column with pre-calculated values._
        
        Args:
            df: DataFrame containing the pre-aggregated data.
            x: Column name for the x-axis categories.
            value: Column name containing the values to plot.
            hue: Column name for grouping data by color. *Optional*.
            palette: Color scheme. Can be a seaborn palette name (`str`) or a `dict` mapping
                categories to hex colors. *Optional*.
            label_map: `Dict` mapping original category values to display labels. *Optional*.
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
            output_name: Name for the exported file. *Default: `'barplot_x'`*.
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
            percentage_labels=percentage_labels
        )
        plot = create_plot('bar', options)
        plot.render()
        self._export_graph(output_name)

    def barplot_y(
        self,
        df: pd.DataFrame,
        y: str,
        value: str,
        hue: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
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
        output_name: str = 'barplot_y'
    ) -> None:
        """Create a **horizontal bar plot** with pre-aggregated data.
        
        _Unlike countplot, this requires a column with pre-calculated values._
        
        Args:
            df: DataFrame containing the pre-aggregated data.
            y: Column name for the y-axis categories.
            value: Column name containing the values to plot.
            hue: Column name for grouping data by color. *Optional*.
            palette: Color scheme. Can be a seaborn palette name (`str`) or a `dict` mapping
                categories to hex colors. *Optional*.
            label_map: `Dict` mapping original category values to display labels. *Optional*.
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
            output_name: Name for the exported file. *Default: `'barplot_y'`*.
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
            percentage_labels=percentage_labels
        )
        plot = create_plot('bar', options)
        plot.render()
        self._export_graph(output_name)

    def timeplot(
        self,
        df: pd.DataFrame,
        x: str,
        group_by: TimeGroupByInput = 'day',
        xlabel: str = '',
        ylabel: str = 'Total',
        type: str = 'bar',
        display_month: bool = True,
        output_name: str = 'timeplot'
    ) -> None:
        """Create a **time series count plot** showing event frequencies over time.
        
        This plot counts occurrences of events in a datetime column and displays
        them as a bar chart with properly formatted date axes.
        
        Args:
            df: DataFrame containing the data to plot.
            x: Column name containing datetime values (`datetime64[ns]`).
            group_by: Time period to group counts by. **Options:** `'year'`, `'month'`, `'day'`.
                *Default: `'day'`*.
            xlabel: Label for the x-axis. *Default: `''`*.
            ylabel: Label for the y-axis. *Default: `'Count'`*.
            output_name: Name for the exported file. *Default: `'timeplot'`*.
        
        Example:
            >>> plot = PlotGraphs()
            >>> plot.timeplot(df, x='date', group_by='month', output_name='events_by_month')
        """
        options = TimePlotOptions(
            df=df,
            x=x,
            group_by=group_by,
            xlabel=xlabel,
            ylabel=ylabel,
            plot_type=type,
            display_month=display_month,
        )
        plot = create_plot('time', options)
        plot.render()
        self._export_graph(output_name)