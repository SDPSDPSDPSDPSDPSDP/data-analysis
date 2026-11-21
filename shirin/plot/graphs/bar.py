from typing import Optional

import pandas as pd

from ..common.data_conversion import category_descriptions
from ..config import SortInput, StackSplitInput, TimeGroupByInput, TitleInput
from .bar_dispatch import BarDispatchMixin, BarModes, count_axis_labels


class BarPlotsMixin(BarDispatchMixin):
    def bar(
        self,
        df: pd.DataFrame,
        x: Optional[str] = None,
        y: Optional[str] = None,
        value: Optional[str] = None,
        hue: Optional[str] = None,
        description: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[TitleInput] = None,
        y_axis_label: Optional[TitleInput] = None,
        suffix: Optional[str] = None,
        legend: bool = False,
        data_labels: bool = True,
        compact_labels: bool = True,
        stacked: bool = False,
        normalized: bool = False,
        split: StackSplitInput = "rounded",
        sort: Optional[SortInput] = None,
        top_n: Optional[int] = None,
        remainder: bool = False,
        group_by: Optional[TimeGroupByInput] = None,
    ) -> None:
        """Create a **bar plot**.

        Without `value`, bars count the rows per category (one row per observation).
        With `value`, bars sum that column per category (and hue) (pre-aggregated data).
        Pass `x` for vertical bars or `y` for horizontal bars, not both.

        Input:
            df: DataFrame containing the data to plot.
            x: Column name for categories on the x-axis (vertical bars).
            y: Column name for categories on the y-axis (horizontal bars).
            value: Column name containing pre-calculated values. Without it, rows are counted. *Optional*.
            hue: Column name for grouping data by color. *Optional*.
            description: Column with a short text per category, shown as a grey line under its axis
                label (e.g. `'description'`). Must be the same on every row of a category; empty cells
                show no line. Not with `group_by`. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. Pass `['label', 'sublabel']` to add a grey second line.
                When counting, the count axis defaults to `'Count'`; pass `''` to hide it. *Optional*.
            y_axis_label: Label for the y-axis. Pass `['label', 'sublabel']` to add a grey second line.
                When counting, the count axis defaults to `'Count'`; pass `''` to hide it. *Optional*.
            suffix: Text appended to each data label (e.g. `'%'` -> `'12 %'`). *Optional*.
            legend: Whether to show the legend. *Default: `False`*.
            data_labels: Whether to show the value on each bar. *Default: `True`*.
            compact_labels: Shorten data labels to k/M (e.g. `1.228.787` -> `'1,2M'`). Pass `False` for
                full numbers. *Default: `True`*.

        Layout:
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            normalized: Show percentages. With `hue`: 100% stacked bars of hue shares (overrides `stacked`).
                Without `hue`: labels show each bar's share of the total. *Default: `False`*.
            split: How segments of stacked and normalized bars meet. **Options:** `'rounded'` (each
                segment ends in a rounded cap over the next), `'flat'` (hard straight edge). *Default: `'rounded'`*.
            sort: How to sort categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*, or time order with `group_by`.
            top_n: Show only the top N most frequent categories. Only without `value`. *Optional*.
            remainder: Fill each bar up to 100% with a lighter segment when `value` holds fractions
                in [0, 1] (e.g. `value='accuracy'`). Needs `value` and `normalized=True`. The filled segment is
                labelled with the `value` column name, the rest with `'Remainder'`. Pass `hue` equal to `x`/`y`
                to color each bar by its category instead. *Optional*.
            group_by: Treat `x` as dates and draw one bar per period, in time order. Empty periods
                count as zero. `'month'` shows month ticks with a year row below. Needs `x`; not with
                `sort`, `top_n` or `remainder`. **Options:** `'year'`, `'month'`, `'day'`. *Optional*.
        """
        if (x is None) == (y is None):
            raise ValueError("bar needs exactly one of x or y.")
        vertical = x is not None
        x_axis_label, y_axis_label = count_axis_labels(value, vertical, x_axis_label, y_axis_label)
        axis_column = x if vertical else y
        descriptions = category_descriptions(df, axis_column, description) if description is not None else None  # type: ignore[arg-type]
        common = dict(
            df=df,
            axis_column=axis_column,
            orientation="vertical" if vertical else "horizontal",
            hue=hue,
            **self._column_config(hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            suffix=suffix,
            legend=legend,
            data_labels=data_labels,
            compact_labels=compact_labels,
            sort=sort,
            split=split,
            group_by=group_by,
            descriptions=descriptions,
        )
        modes = BarModes(top_n=top_n, remainder=remainder, normalized=normalized, stacked=stacked)
        if value is None:
            self._render_counted_bar(common, modes)
        else:
            self._render_summed_bar(common, value, modes)
