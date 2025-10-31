import os
import pandas as pd
from typing import Any, Dict, Optional, Union
import matplotlib.pyplot as plt

from .config import OrderTypeInput, StackedLabelTypeInput, FigureSizeInput, FillMissingValuesInput
from .plots import (
    barplot_x,
    barplot_y,
    countplot_x,
    countplot_x_normalized,
    countplot_y,
    countplot_y_normalized,
    histogram,
    lineplot,
    pie_base,
)
from .utils.file_operations import (
    calculate_value_counts,
    validate_format,
    create_filepath,
    save_plot,
)


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
        self.config = {
            "export": export,
            "output_dir": output_dir,
            "prefix": prefix,
        }
        if self.config["export"]:
            os.makedirs(self.config["output_dir"], exist_ok=True)
        self.format = format.lower()

    def _export_graph(self, output_name: str) -> None:
        validate_format(self.format)
        
        if self.config["export"]:
            filepath = create_filepath(
                self.config["output_dir"],
                self.config["prefix"],
                output_name,
                self.format
            )
            save_plot(filepath, self.format)
        plt.show()

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
            countplot_x_normalized(
                df=df, x=x, hue=hue, palette=palette, label_map=label_map,
                xlabel=xlabel, ylabel=ylabel, plot_legend=plot_legend,
                legend_offset=legend_offset, ncol=ncol, top_n=top_n,
                figsize_width=figsize_width, order_type=order_type,
                show_labels=show_labels
            )
        else:
            countplot_x(
                df=df, x=x, hue=hue, palette=palette, label_map=label_map,
                xlabel=xlabel, ylabel=ylabel, plot_legend=plot_legend,
                legend_offset=legend_offset, ncol=ncol, top_n=top_n,
                figsize_width=figsize_width, stacked=stacked,
                stacked_labels=stacked_labels, order_type=order_type
            )
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
            countplot_y_normalized(
                df=df, y=y, hue=hue, palette=palette, label_map=label_map,
                xlabel=xlabel, ylabel=ylabel, plot_legend=plot_legend,
                legend_offset=legend_offset, ncol=ncol, top_n=top_n,
                figsize_height=figsize_height, order_type=order_type,
                show_labels=show_labels
            )
        else:
            countplot_y(
                df=df, y=y, hue=hue, palette=palette, label_map=label_map,
                xlabel=xlabel, ylabel=ylabel, plot_legend=plot_legend,
                legend_offset=legend_offset, ncol=ncol, top_n=top_n,
                figsize_height=figsize_height, stacked=stacked,
                stacked_labels=stacked_labels, order_type=order_type
            )
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
        """Create a **histogram** showing the distribution of continuous data.
        
        Args:
            df: DataFrame containing the data to plot.
            x: Column name for the continuous variable to plot.
            xlabel: Label for the x-axis. *Default: `''`*.
            ylabel: Label for the y-axis. *Default: `'Count'`*.
            xlimit: Maximum value for the x-axis. Values beyond this will be excluded. *Optional*.
            bins: Number of bins for the histogram. *Default: `100`*.
            palette: Color scheme. Can be a seaborn palette name (`str`) or a `dict` mapping
                categories to hex colors. *Optional*.
            label_map: `Dict` mapping original category values to display labels. *Optional*.
            hue: Column name for grouping data by color. *Optional*.
            stacked: Whether to stack histograms when using `hue`. *Optional*.
            plot_legend: Whether to show the legend. *Default: `True`*.
            legend_offset: Vertical position offset for legend. *Default: `1.13`*.
            ncol: Number of columns in the legend. *Default: `2`*.
            output_name: Name for the exported file. *Default: `'histogram'`*.
        """
        histogram(
            df=df, x=x, xlabel=xlabel, ylabel=ylabel, xlimit=xlimit,
            bins=bins, palette=palette, label_map=label_map, hue=hue,
            stacked=stacked, plot_legend=plot_legend,
            legend_offset=legend_offset, ncol=ncol
        )
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
        """Create a **pie chart** showing the distribution of categories.
        
        The chart _automatically calculates value counts_ from the specified column.
        
        Args:
            df: DataFrame containing the data to plot.
            col: Column name to calculate value counts from.
            palette: `Dict` mapping category values to hex colors. **Required**.
            label_map: `Dict` mapping original category values to display labels. *Optional*.
            n_after_comma: Number of decimal places for percentage labels. *Default: `0`*.
            value_datalabel: Minimum percentage threshold to display labels. Segments below
                this percentage won't show labels. *Default: `5`*.
            donut: Whether to create a donut chart (pie with center hole). *Default: `False`*.
            output_name: Name for the exported file. *Default: `'pie_value_counts'`*.
        """
        df_value_counts = calculate_value_counts(df, col)
        pie_base(
            df=df_value_counts,
            value="count",
            label=col,
            palette=palette,
            label_map=label_map,
            n_after_comma=n_after_comma,
            value_datalabel=value_datalabel,
            donut=donut
        )
        self._export_graph(output_name)


    def lineplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        xlabel: str = '',
        ylabel: str = '',
        rotation: int = 0,
        dynamic_x_ticks: Optional[int] = None,
        fill_missing_values: FillMissingValuesInput = None,
        output_name: str = 'lineplot'
    ) -> None:
        """Create a **line plot** showing trends over time or across categories.
        
        Args:
            df: DataFrame containing the data to plot.
            x: Column name for the x-axis.
            y: Column name for the y-axis values.
            xlabel: Label for the x-axis. *Default: `''`*.
            ylabel: Label for the y-axis. *Default: `''`*.
            rotation: Rotation angle for x-axis labels in degrees. *Default: `0`*.
            dynamic_x_ticks: Show every Nth x-axis tick to reduce clutter. *Optional*.
            fill_missing_values: How to handle missing values. **Options:** `'shift'` (interpolate),
                `'zero'` (fill with 0), or `None`. *Default: `None`*.
            output_name: Name for the exported file. *Default: `'lineplot'`*.
        """
        lineplot(
            df=df, x=x, y=y, xlabel=xlabel, ylabel=ylabel,
            rotation=rotation, dynamic_x_ticks=dynamic_x_ticks,
            fill_missing_values=fill_missing_values
        )
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
        barplot_x(
            df=df, x=x, value=value, hue=hue, palette=palette,
            label_map=label_map, xlabel=xlabel, ylabel=ylabel,
            plot_legend=plot_legend, legend_offset=legend_offset,
            ncol=ncol, figsize_width=figsize_width, stacked=stacked,
            stacked_labels=stacked_labels, order_type=order_type,
            percentage_labels=percentage_labels
        )
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
        barplot_y(
            df=df, y=y, value=value, hue=hue, palette=palette,
            label_map=label_map, xlabel=xlabel, ylabel=ylabel,
            plot_legend=plot_legend, legend_offset=legend_offset,
            ncol=ncol, figsize_height=figsize_height, stacked=stacked,
            stacked_labels=stacked_labels, order_type=order_type,
            percentage_labels=percentage_labels
        )
        self._export_graph(output_name)