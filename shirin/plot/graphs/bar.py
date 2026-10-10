import pandas as pd
from typing import Optional

from ..config import TitleInput, SortInput
from ..core import BarPlotOptions, NormalizedPlotOptions
from ..core.base_plot import default_palette
from ..common.data_conversion import REMAINDER_LABEL, REMAINDER_SHARE_COL, fill_remainder
from ..common.resolve_palette import resolve_palette
from ..plots import BarPlot, NormalizedPlot


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
        suffix: Optional[str] = None,
        legend: bool = False,
        data_labels: bool = True,
        stacked: bool = False,
        normalized: bool = False,
        sort: SortInput = 'frequency',
        remainder: bool = False,
    ) -> None:
        """Create a **bar plot** with pre-aggregated data.

        _Unlike countplot, this requires a column with pre-calculated values._
        Rows with the same category (and hue) are summed.
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
            suffix: Text appended to each data label (e.g. `'%'` -> `'12 %'`). *Optional*.
            legend: Whether to show the legend. *Default: `False`*.
            data_labels: Whether to show the value on each bar. *Default: `True`*.

        Layout:
            stacked: Whether to create a stacked bar chart (_requires `hue`_). *Default: `False`*.
            normalized: Show percentages. With `hue`: 100% stacked bars of hue shares (overrides `stacked`).
                Without `hue`: labels show each bar's share of the total. *Default: `False`*.
            remainder: Fill each bar up to 100% with a lighter segment when `value` holds fractions
                in [0, 1] (e.g. `value='accuracy'`). Needs `normalized=True`. The filled segment is
                labelled with the `value` column name, the rest with `'Remainder'`. Pass `hue` equal to `x`/`y`
                to color each bar by its category instead. *Optional*.
            sort: How to sort categories. **Options:** `'frequency'`, `'alphabetical'`.
                *Default: `'frequency'`*.
        """
        if (x is None) == (y is None):
            raise ValueError('barplot needs exactly one of x or y.')
        vertical = x is not None
        common = dict(
            df=df,
            axis_column=x if vertical else y,
            value=value,
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
        )
        if remainder:
            if not normalized:
                raise ValueError('remainder needs normalized=True.')
            if hue is not None and hue != common['axis_column']:
                raise ValueError(f"With remainder, hue must be the category column {common['axis_column']!r} or None.")
            if hue is not None:
                category_palette = common['palette']
                if not isinstance(category_palette, dict):
                    category_palette = default_palette(df[hue], category_palette)
                common['category_palette'] = category_palette
            common.update(
                df=fill_remainder(df, common['axis_column'], value, REMAINDER_LABEL),
                value=REMAINDER_SHARE_COL,
                hue=value,
                remainder=REMAINDER_LABEL,
                **resolve_palette(self, value),
            )
            if isinstance(common['palette'], str):
                common['palette'] = {value: common['palette']}
        if normalized and common['hue'] is not None and common['hue'] != common['axis_column']:
            self._render(NormalizedPlot(NormalizedPlotOptions(**common)))
        else:
            self._render(BarPlot(BarPlotOptions(**common, stacked=stacked, normalized=normalized)))
