import pandas as pd
from typing import Optional

from ..config import TitleInput, OrderTypeInput
from ..core import BarPlotOptions
from ..common.resolve_palette import resolve_palette
from ..plots import BarPlot


class BarPlotsMixin:
    def barplot_x(
        self,
        df: pd.DataFrame,
        x: str,
        value: str,
        hue: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        percentage_labels: bool = False,
        suffix: Optional[str] = None,
        legend: bool = False,
        stacked: bool = False,
        order_type: OrderTypeInput = 'frequency',
    ) -> None:
        """Create a **vertical bar plot** with pre-aggregated data.

        _Unlike countplot, this requires a column with pre-calculated values._

        Input:
            df: DataFrame containing the pre-aggregated data.
            x: Column name for the x-axis categories.
            value: Column name containing the values to plot.
            hue: Column name for grouping data by color. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. *Optional*.
            y_axis_label: Label for the y-axis. *Optional*.
            percentage_labels: Whether to format data labels as percentages. *Default: `False`*.
            suffix: Text appended to each data label (e.g. `'%'` -> `'12 %'`). *Optional*.
            legend: Whether to show the legend. *Default: `False`*.

        Layout:
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            order_type: How to order categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
        """
        options = BarPlotOptions(
            df=df,
            axis_column=x,
            value=value,
            orientation='vertical',
            hue=hue,
            **resolve_palette(self, hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            percentage_labels=percentage_labels,
            suffix=suffix,
            legend=legend,
            stacked=stacked,
            order_type=order_type,
        )

        self._render(BarPlot(options))

    def barplot_y(
        self,
        df: pd.DataFrame,
        y: str,
        value: str,
        hue: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        percentage_labels: bool = False,
        suffix: Optional[str] = None,
        legend: bool = False,
        stacked: bool = False,
        order_type: OrderTypeInput = 'frequency',
    ) -> None:
        """Create a **horizontal bar plot** with pre-aggregated data.

        _Unlike countplot, this requires a column with pre-calculated values._

        Input:
            df: DataFrame containing the pre-aggregated data.
            y: Column name for the y-axis categories.
            value: Column name containing the values to plot.
            hue: Column name for grouping data by color. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. *Optional*.
            y_axis_label: Label for the y-axis. *Optional*.
            percentage_labels: Whether to format data labels as percentages. *Default: `False`*.
            suffix: Text appended to each data label (e.g. `'%'` -> `'12 %'`). *Optional*.
            legend: Whether to show the legend. *Default: `False`*.

        Layout:
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            order_type: How to order categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
        """
        options = BarPlotOptions(
            df=df,
            axis_column=y,
            value=value,
            orientation='horizontal',
            hue=hue,
            **resolve_palette(self, hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            percentage_labels=percentage_labels,
            suffix=suffix,
            legend=legend,
            stacked=stacked,
            order_type=order_type,
        )

        self._render(BarPlot(options))
