import pandas as pd
from typing import Optional

from ..config import TitleInput, SortInput
from ..core import CountPlotOptions, NormalizedPlotOptions
from ..common.resolve_palette import resolve_palette
from ..plots import CountPlot, NormalizedPlot


class CountPlotsMixin:
    def countplot(
        self,
        df: pd.DataFrame,
        x: Optional[str] = None,
        y: Optional[str] = None,
        hue: Optional[str] = None,
        title: Optional[TitleInput] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        suffix: Optional[str] = None,
        legend: bool = False,
        data_labels: bool = True,
        sort: SortInput = 'frequency',
        top_n: Optional[int] = None,
        stacked: bool = False,
        normalized: bool = False,
    ) -> None:
        """Create a **count plot** showing category frequencies.

        Pass `x` for vertical bars or `y` for horizontal bars, not both.

        Input:
            df: DataFrame containing the data to plot.
            x: Column name for categories on the x-axis (vertical bars).
            y: Column name for categories on the y-axis (horizontal bars).
            hue: Column name for grouping data by color. *Optional*.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            x_axis_label: Label for the x-axis. On the count axis it defaults to `'Count'`;
                pass `''` to hide it. *Optional*.
            y_axis_label: Label for the y-axis. On the count axis it defaults to `'Count'`;
                pass `''` to hide it. *Optional*.
            suffix: Text appended to each data label (e.g. `'%'` -> `'12 %'`). *Optional*.
            legend: Whether to show the legend. *Default: `False`*.
            data_labels: Whether to show the value on each bar (percentages on stacked bars).
                *Default: `True`*.

        Layout:
            sort: How to sort categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
            top_n: Show only the top N most frequent categories. *Optional*.
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            normalized: Show percentages. With `hue`: 100% stacked bars of hue shares (overrides `stacked`).
                Without `hue`: labels show each bar's share of the total. *Default: `False`*.
        """
        if (x is None) == (y is None):
            raise ValueError('countplot needs exactly one of x or y.')
        vertical = x is not None
        if vertical and y_axis_label is None:
            y_axis_label = 'Count'
        if not vertical and x_axis_label is None:
            x_axis_label = 'Count'
        common = dict(
            df=df,
            axis_column=x if vertical else y,
            orientation='vertical' if vertical else 'horizontal',
            hue=hue,
            **resolve_palette(self, hue),
            title=title,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            suffix=suffix,
            legend=legend,
            data_labels=data_labels,
            sort=sort,
            top_n=top_n,
        )
        if normalized and hue is not None:
            self._render(NormalizedPlot(NormalizedPlotOptions(**common)))
        else:
            self._render(CountPlot(CountPlotOptions(**common, stacked=stacked, normalized=normalized)))
