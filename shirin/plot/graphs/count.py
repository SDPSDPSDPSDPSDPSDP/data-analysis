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
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = 'Count',
        suffix: Optional[str] = None,
        legend: bool = False,
        data_labels: bool = True,
        order_type: OrderTypeInput = 'frequency',
        top_n: Optional[int] = None,
        stacked: bool = False,
        normalized: bool = False,
    ) -> None:
        """Create a **vertical count plot** showing category frequencies.

        Input:
            df: DataFrame containing the data to plot.
            x: Column name for the x-axis categories.
            hue: Column name for grouping data by color. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. *Optional*.
            y_axis_label: Label for the y-axis; `None` hides it. *Default: `'Count'`*.
            suffix: Text appended to each data label (e.g. `'%'` -> `'12 %'`). *Optional*.
            legend: Whether to show the legend. *Default: `False`*.
            data_labels: Whether to show the value on each bar (percentages on stacked bars).
                *Default: `True`*.

        Layout:
            order_type: How to order categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
            top_n: Show only the top N most frequent categories. *Optional*.
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            normalized: Show percentages. With `hue`: 100% stacked bars of hue shares (overrides `stacked`).
                Without `hue`: labels show each bar's share of the total. *Default: `False`*.
        """
        self._countplot(
            normalized=normalized,
            stacked=stacked,
            df=df,
            axis_column=x,
            orientation='vertical',
            hue=hue,
            **resolve_palette(self, hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            suffix=suffix,
            legend=legend,
            data_labels=data_labels,
            order_type=order_type,
            top_n=top_n,
        )

    def countplot_y(
        self,
        df: pd.DataFrame,
        y: str,
        hue: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[str] = 'Count',
        y_axis_label: Optional[str] = None,
        suffix: Optional[str] = None,
        legend: bool = False,
        data_labels: bool = True,
        order_type: OrderTypeInput = 'frequency',
        top_n: Optional[int] = None,
        stacked: bool = False,
        normalized: bool = False,
    ) -> None:
        """Create a **horizontal count plot** showing category frequencies.

        Input:
            df: DataFrame containing the data to plot.
            y: Column name for the y-axis categories.
            hue: Column name for grouping data by color. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis; `None` hides it. *Default: `'Count'`*.
            y_axis_label: Label for the y-axis. *Optional*.
            suffix: Text appended to each data label (e.g. `'%'` -> `'12 %'`). *Optional*.
            legend: Whether to show the legend. *Default: `False`*.
            data_labels: Whether to show the value on each bar (percentages on stacked bars).
                *Default: `True`*.

        Layout:
            order_type: How to order categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
            top_n: Show only the top N most frequent categories. *Optional*.
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            normalized: Show percentages. With `hue`: 100% stacked bars of hue shares (overrides `stacked`).
                Without `hue`: labels show each bar's share of the total. *Default: `False`*.
        """
        self._countplot(
            normalized=normalized,
            stacked=stacked,
            df=df,
            axis_column=y,
            orientation='horizontal',
            hue=hue,
            **resolve_palette(self, hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            suffix=suffix,
            legend=legend,
            data_labels=data_labels,
            order_type=order_type,
            top_n=top_n,
        )
