import pandas as pd
from typing import Any, Dict, Optional, Union

from ..config import OrderTypeInput, StackedLabelTypeInput
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
        x_axis_label: str = '',
        y_axis_label: str = '',
        legend: bool = False,
        title: str = '',
        subtitle: str = '',
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
            x_axis_label: Label for the x-axis. *Default: `''`*.
            y_axis_label: Label for the y-axis. *Default: `''`*.
            legend: Whether to show the legend. *Default: `False`*.
            title: Chart title above the plot. *Default: `''`*.
            subtitle: Grey line under the title. *Default: `''`*.
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
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            legend=legend,
            title=title,
            subtitle=subtitle,
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
        x_axis_label: str = '',
        y_axis_label: str = '',
        legend: bool = False,
        title: str = '',
        subtitle: str = '',
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
            x_axis_label: Label for the x-axis. *Default: `''`*.
            y_axis_label: Label for the y-axis. *Default: `''`*.
            legend: Whether to show the legend. *Default: `False`*.
            title: Chart title above the plot. *Default: `''`*.
            subtitle: Grey line under the title. *Default: `''`*.
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
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            legend=legend,
            title=title,
            subtitle=subtitle,
            stacked=stacked,
            stacked_labels=stacked_labels,
            order_type=order_type,
            percentage_labels=percentage_labels,
            suffix=suffix,
        )

        self._render(BarPlot(options))
