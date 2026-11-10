from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd

from ..common.colors import palette_colors
from ..common.data_conversion import aggregate
from ..common.formatting import (
    format_categorical_tick_labels,
    format_datalabels,
    format_datalabels_stacked,
    format_period_ticks,
    format_tick_descriptions,
    format_ticks,
)
from ..common.sorting import get_order
from ..common.stacked_plots import largest_hue_first, sort_stacked_pivot
from ..config import FigureSize, Layout, Marks
from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.categorical_options import CategoricalPlotOptions
from ..svg import Chart


def calculate_figsize(options: CategoricalPlotOptions, data: pd.DataFrame) -> tuple[float, float]:
    """(figure width, plot height) in inches; vertical width grows with the category count."""
    n_categories = data[options.axis_column].nunique()
    if options.orientation == 'vertical':
        width = n_categories * FigureSize.CATEGORY_SLOT + FigureSize.CATEGORY_MARGIN
        # Long time series get thinner bars instead of an ever wider figure.
        return (min(width, FigureSize.WIDTH) if options.group_by else width, FigureSize.PLOT_HEIGHT)
    return (FigureSize.HORIZONTAL_WIDTH, n_categories * FigureSize.BAR_ROW)


def create_sized_figure(plot: AbstractPlot, data: pd.DataFrame) -> Chart:
    return plot._new_chart(*calculate_figsize(plot.options, data))  # type: ignore[arg-type]


def format_period_axis(chart: Chart, options: CategoricalPlotOptions) -> None:
    """Date period categories: month ticks with a year row below, or every nth day."""
    if options.group_by == 'month':
        periods = pd.Series(pd.to_datetime(chart.x.tick_labels))
        format_period_ticks(chart, periods, pd.Series(chart.x.ticks), months=True)
    elif options.group_by == 'day':
        step = -(-len(chart.x.ticks) // Layout.MAX_DAY_TICKS)
        chart.x.ticks, chart.x.tick_labels = chart.x.ticks[::step], chart.x.tick_labels[::step]  # type: ignore[index]


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
        order = get_order(self.options.sort, df, self.options.axis_column, value_column=self._value_column())
        df = self._resolve_hue_palette(df)
        stacked = None
        if self.options.stacked:
            pivot = largest_hue_first(aggregate(df, self.options.axis_column, self._value_column(), self.options.hue).fillna(0))
            stacked = sort_stacked_pivot(pivot, self.options.sort, self.options.orientation)
        return CategoricalData(df, order, stacked)

    def _draw_unstacked(self, chart: Chart, data: CategoricalData) -> Any:
        return renderer.render_barplot(
            chart,
            df=data.df,
            column=self.options.axis_column,
            value=self._value_column(),
            horizontal=self.options.orientation == 'horizontal',
            hue=self.options.hue,
            order=data.order,
            color=self._color,
            palette=self._palette,
        )

    def _datalabel_formatting(self) -> str:
        return 'totals'

    def _value_column(self) -> Optional[str]:
        """Column holding pre-aggregated values; None means count rows."""
        return None

    def draw(self, data: CategoricalData) -> Any:
        chart = create_sized_figure(self, data.df)
        if data.stacked is not None:
            return self._draw_stacked(chart, data.stacked)
        return self._draw_unstacked(chart, data)

    def _draw_stacked(self, chart: Chart, stacked: pd.DataFrame) -> Any:
        horizontal = self.options.orientation == 'horizontal'
        return renderer.render_stacked_barplot(
            chart,
            df=stacked,
            horizontal=horizontal,
            colors=palette_colors(self._palette, stacked.columns),  # type: ignore[arg-type]
            width=Marks.HORIZONTAL_BAR_WIDTH if horizontal else Marks.BAR_WIDTH,
        )

    def format_plot(self, plot: Any, data: CategoricalData) -> None:
        self._format_labels_and_legend(plot)
        # label_map renames hue values when there is a hue, otherwise the category ticks.
        tick_label_map = self.options.label_map if self.options.hue is None else None
        category_axis = 'x' if self.options.orientation == 'vertical' else 'y'
        format_tick_descriptions(plot, self.options.descriptions, category_axis)
        if self.options.orientation == 'vertical':
            format_ticks(plot, numeric_y=True)
            format_categorical_tick_labels(plot, tick_label_map, axis='x')
            format_period_axis(plot, self.options)
        else:
            format_ticks(plot, numeric_x=True)
            format_categorical_tick_labels(plot, tick_label_map, axis='y')

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
