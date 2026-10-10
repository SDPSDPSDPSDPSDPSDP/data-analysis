import pandas as pd
from typing import Any, Dict, Optional, Union

from ..config import OrderTypeInput, StackedLabelTypeInput, FigureSizeInput
from ..core import CountPlotOptions, NormalizedCountPlotOptions
from ..common.resolve_palette import resolve_palette


class CountPlotsMixin:
    def _countplot(
        self,
        output_name: str,
        normalized: bool,
        stacked: bool,
        stacked_labels: StackedLabelTypeInput,
        **common: Any,
    ) -> None:
        if normalized and common['hue'] is not None:
            self._render('normalized_count', NormalizedCountPlotOptions(**common), output_name)
        else:
            options = CountPlotOptions(
                **common, stacked=stacked, stacked_labels=stacked_labels, normalized=normalized
            )
            self._render('count', options, output_name)


    @resolve_palette
    def countplot_x(
        self,
        df: pd.DataFrame,
        x: str,
        hue: Optional[str] = None,
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
        suffix: Optional[str] = None,
        output_name: str = 'countplot_x',
        # injected by @resolve_palette
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
    ) -> None:
        """Create a **vertical count plot** showing category frequencies.

        Args:
            df: DataFrame containing the data to plot.
            x: Column name for the x-axis categories.
            hue: Column name for grouping data by color. *Optional*.
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
            suffix: Optional suffix appended to each data label (e.g. `'%'` -> `'12 %'`).
                *Default: `None`*.
            output_name: Name for the exported file. *Default: `'countplot_x'`*.
        """
        self._countplot(
            output_name=output_name,
            normalized=normalized,
            stacked=stacked,
            stacked_labels=stacked_labels,
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
            show_labels=show_labels,
            suffix=suffix,
        )


    @resolve_palette
    def countplot_y(
        self,
        df: pd.DataFrame,
        y: str,
        hue: Optional[str] = None,
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
        suffix: Optional[str] = None,
        output_name: str = 'countplot_y',
        # injected by @resolve_palette
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
    ) -> None:
        """Create a **horizontal count plot** showing category frequencies.

        Args:
            df: DataFrame containing the data to plot.
            y: Column name for the y-axis categories.
            hue: Column name for grouping data by color. *Optional*.
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
            suffix: Optional suffix appended to each data label (e.g. `'%'` -> `'12 %'`).
                *Default: `None`*.
            output_name: Name for the exported file. *Default: `'countplot_y'`*.
        """
        self._countplot(
            output_name=output_name,
            normalized=normalized,
            stacked=stacked,
            stacked_labels=stacked_labels,
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
            show_labels=show_labels,
            suffix=suffix,
        )
