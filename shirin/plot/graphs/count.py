import pandas as pd
from typing import Any, Optional

from ..config import TitleInput, OrderTypeInput
from ..core import CountPlotOptions, NormalizedCountPlotOptions
from ..common.resolve_palette import resolve_palette
from ..plots import CountPlot, NormalizedCountPlot


class CountPlotsMixin:
    def _countplot(
        self,
        normalized: bool,
        stacked: bool,
        **common: Any,
    ) -> None:
        if normalized and common['hue'] is not None:
            self._render(NormalizedCountPlot(NormalizedCountPlotOptions(**common)))
        else:
            self._render(CountPlot(CountPlotOptions(**common, stacked=stacked, normalized=normalized)))

    def countplot_x(
        self,
        df: pd.DataFrame,
        x: str,
        hue: Optional[str] = None,
        x_axis_label: str = '',
        y_axis_label: str = 'Count',
        legend: bool = False,
        title: Optional[TitleInput] = None,
        top_n: Optional[int] = None,
        stacked: bool = False,
        order_type: OrderTypeInput = 'frequency',
        normalized: bool = False,
        show_labels: bool = True,
        suffix: Optional[str] = None,
    ) -> None:
        """Create a **vertical count plot** showing category frequencies.

        Args:
            df: DataFrame containing the data to plot.
            x: Column name for the x-axis categories.
            hue: Column name for grouping data by color. *Optional*.
            x_axis_label: Label for the x-axis. *Default: `''`*.
            y_axis_label: Label for the y-axis. *Default: `'Count'`*.
            legend: Whether to show the legend. *Default: `False`*.
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            top_n: Show only the top N most frequent categories. *Optional*.
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            order_type: How to order categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
            normalized: Show percentages. With `hue`: 100% stacked bars of hue shares (overrides `stacked`).
                Without `hue`: labels show each bar's share of the total. *Default: `False`*.
            show_labels: Whether to show data labels on bars (percentages on stacked bars). *Default: `True`*.
            suffix: Optional suffix appended to each data label (e.g. `'%'` -> `'12 %'`).
                *Default: `None`*.
        """
        self._countplot(
            normalized=normalized,
            stacked=stacked,
            df=df,
            axis_column=x,
            orientation='vertical',
            hue=hue,
            **resolve_palette(self, hue),
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            legend=legend,
            title=title,
            top_n=top_n,
            order_type=order_type,
            show_labels=show_labels,
            suffix=suffix,
        )

    def countplot_y(
        self,
        df: pd.DataFrame,
        y: str,
        hue: Optional[str] = None,
        x_axis_label: str = 'Count',
        y_axis_label: str = '',
        legend: bool = False,
        title: Optional[TitleInput] = None,
        top_n: Optional[int] = None,
        stacked: bool = False,
        order_type: OrderTypeInput = 'frequency',
        normalized: bool = False,
        show_labels: bool = True,
        suffix: Optional[str] = None,
    ) -> None:
        """Create a **horizontal count plot** showing category frequencies.

        Args:
            df: DataFrame containing the data to plot.
            y: Column name for the y-axis categories.
            hue: Column name for grouping data by color. *Optional*.
            x_axis_label: Label for the x-axis. *Default: `'Count'`*.
            y_axis_label: Label for the y-axis. *Default: `''`*.
            legend: Whether to show the legend. *Default: `False`*.
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            top_n: Show only the top N most frequent categories. *Optional*.
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            order_type: How to order categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
            normalized: Show percentages. With `hue`: 100% stacked bars of hue shares (overrides `stacked`).
                Without `hue`: labels show each bar's share of the total. *Default: `False`*.
            show_labels: Whether to show data labels on bars (percentages on stacked bars). *Default: `True`*.
            suffix: Optional suffix appended to each data label (e.g. `'%'` -> `'12 %'`).
                *Default: `None`*.
        """
        self._countplot(
            normalized=normalized,
            stacked=stacked,
            df=df,
            axis_column=y,
            orientation='horizontal',
            hue=hue,
            **resolve_palette(self, hue),
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            legend=legend,
            title=title,
            top_n=top_n,
            order_type=order_type,
            show_labels=show_labels,
            suffix=suffix,
        )
