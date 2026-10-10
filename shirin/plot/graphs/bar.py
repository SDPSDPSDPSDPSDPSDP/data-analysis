import pandas as pd
from typing import Optional

from ..config import TitleInput, OrderTypeInput
from ..core import BarPlotOptions
from ..common.resolve_palette import resolve_palette
from ..plots import BarPlot


class BarPlotsMixin:
    def barplot(
        self,
        df: pd.DataFrame,
        value: str,
        x: Optional[str] = None,
        y: Optional[str] = None,
        hue: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        percentage_labels: bool = False,
        suffix: Optional[str] = None,
        legend: bool = False,
        data_labels: bool = True,
        stacked: bool = False,
        order_type: OrderTypeInput = 'frequency',
    ) -> None:
        """Create a **bar plot** with pre-aggregated data.

        _Unlike countplot, this requires a column with pre-calculated values._
        Pass `x` for vertical bars or `y` for horizontal bars, not both.

        Input:
            df: DataFrame containing the pre-aggregated data.
            value: Column name containing the values to plot.
            x: Column name for categories on the x-axis (vertical bars).
            y: Column name for categories on the y-axis (horizontal bars).
            hue: Column name for grouping data by color. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. *Optional*.
            y_axis_label: Label for the y-axis. *Optional*.
            percentage_labels: Whether to format data labels as percentages. *Default: `False`*.
            suffix: Text appended to each data label (e.g. `'%'` -> `'12 %'`). *Optional*.
            legend: Whether to show the legend. *Default: `False`*.
            data_labels: Whether to show the value on each bar. *Default: `True`*.

        Layout:
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            order_type: How to order categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
        """
        if (x is None) == (y is None):
            raise ValueError('barplot needs exactly one of x or y.')
        vertical = x is not None
        options = BarPlotOptions(
            df=df,
            axis_column=x if vertical else y,
            value=value,
            orientation='vertical' if vertical else 'horizontal',
            hue=hue,
            **resolve_palette(self, hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            percentage_labels=percentage_labels,
            suffix=suffix,
            legend=legend,
            data_labels=data_labels,
            stacked=stacked,
            order_type=order_type,
        )

        self._render(BarPlot(options))
