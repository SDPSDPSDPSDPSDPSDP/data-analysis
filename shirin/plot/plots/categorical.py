from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd

from ..common.colors import palette_colors
from ..common.data_conversion import aggregate
from ..common.formatting import (
    format_categorical_tick_labels,
    format_datalabels,
    format_datalabels_stacked,
    format_tick_descriptions,
    format_ticks,
)
from ..common.sorting import get_order
from ..common.stacked_plots import largest_hue_first, sort_stacked_pivot
from ..config import Marks
from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.categorical_options import CategoricalPlotOptions
from ..svg import Chart
from .categorical_layout import create_sized_figure, format_period_axis


@dataclass
class CategoricalData:
    df: pd.DataFrame
    # Category order on the axis, None keeps data order.
    order: Optional[list]
    # Totals pivot (categories x hue levels) for stacked plots, else None.
    stacked: Optional[pd.DataFrame]


class StackableCategoricalPlot(AbstractPlot[CategoricalData]):
    """Shared draw/format logic for count and bar plots (plain or stacked by hue)."""

    options: CategoricalPlotOptions

    def transform(self, df: pd.DataFrame) -> CategoricalData:
        order = get_order(self.options.resolved_sort(), df, self.options.axis_column, value_column=self._value_column())
        df = self._resolve_hue_palette(df)
        stacked = None
        if self.options.stacked:
            totals = aggregate(df, self.options.axis_column, self._value_column(), self.options.hue).fillna(0)
            pivot = largest_hue_first(totals)
            stacked = sort_stacked_pivot(pivot, self.options.resolved_sort(), self.options.orientation)
        return CategoricalData(df, order, stacked)

    def _draw_unstacked(self, chart: Chart, data: CategoricalData) -> Any:
        return renderer.render_barplot(
            chart,
            df=data.df,
            column=self.options.axis_column,
            value=self._value_column(),
            horizontal=self.options.orientation == "horizontal",
            hue=self.options.hue,
            order=data.order,
            color=self._color,
            palette=self._palette,
        )

    def _datalabel_formatting(self) -> str:
        return "totals"

    def _value_column(self) -> Optional[str]:
        """Column holding pre-aggregated values; None means count rows."""
        return None

    def draw(self, data: CategoricalData) -> Any:
        chart = create_sized_figure(self, data.df)
        if data.stacked is not None:
            return self._draw_stacked(chart, data.stacked)
        return self._draw_unstacked(chart, data)

    def _draw_stacked(self, chart: Chart, stacked: pd.DataFrame) -> Any:
        horizontal = self.options.orientation == "horizontal"
        return renderer.render_stacked_barplot(
            chart,
            df=stacked,
            horizontal=horizontal,
            colors=palette_colors(self._palette, stacked.columns),  # type: ignore[arg-type]
            width=Marks.HORIZONTAL_BAR_WIDTH if horizontal else Marks.BAR_WIDTH,
            split=self.options.split,
        )

    def format_plot(self, plot: Any, data: CategoricalData) -> None:
        self._format_labels_and_legend(plot)
        # label_map renames hue values when there is a hue, otherwise the category ticks.
        tick_label_map = self.options.label_map if self.options.hue is None else None
        category_axis = "x" if self.options.orientation == "vertical" else "y"
        format_tick_descriptions(plot, self.options.descriptions, category_axis)
        if self.options.orientation == "vertical":
            format_ticks(plot, numeric_y=True)
            format_categorical_tick_labels(plot, tick_label_map, axis="x")
            format_period_axis(plot, self.options)
        else:
            format_ticks(plot, numeric_x=True)
            format_categorical_tick_labels(plot, tick_label_map, axis="y")

        if self.options.data_labels:
            self._format_data_labels(plot, data.stacked)

    def _format_data_labels(self, plot: Any, stacked: Optional[pd.DataFrame]) -> None:
        if stacked is not None:
            format_datalabels_stacked(
                plot,
                stacked,
                self._palette,  # type: ignore[arg-type]
                orientation=self.options.orientation,
                suffix=self.options.suffix,
            )
            return
        format_datalabels(
            plot,
            formatting=self._datalabel_formatting(),
            orientation=self.options.orientation,
            suffix=self.options.suffix,
            compact=self.options.compact_labels,
        )
