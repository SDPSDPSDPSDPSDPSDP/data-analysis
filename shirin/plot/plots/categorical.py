from typing import Any, Optional

import pandas as pd

from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.categorical_options import CategoricalPlotOptions
from ..config import FigureSize
from ..common.formatting import (
    format_categorical_tick_labels,
    format_datalabels,
    format_datalabels_stacked,
    format_ticks,
)
from ..common.sorting import create_colors_list
from ..common.stacked_plots import prepare_stacked_data
from ..svg import Chart


def calculate_figsize(options: CategoricalPlotOptions, data: pd.DataFrame) -> tuple[float, float]:
    """(figure width, plot height) in inches; grows with the category count, default width as minimum."""
    n_categories = data[options.axis_column].nunique()
    if options.orientation == 'vertical':
        # ponytail: +1 inch approximates the margins; measure them if wide charts look off.
        return (max(FigureSize.WIDTH, n_categories * FigureSize.CATEGORY_SLOT + 1), FigureSize.PLOT_HEIGHT)
    return (FigureSize.WIDTH, n_categories * FigureSize.BAR_ROW)


def create_sized_figure(plot: AbstractPlot, data: pd.DataFrame) -> Chart:
    return plot._new_chart(*calculate_figsize(plot.options, data))  # type: ignore[arg-type]


class StackableCategoricalPlot(AbstractPlot):
    """Shared draw/format logic for count, bar and accuracy plots (plain or stacked by hue)."""

    options: CategoricalPlotOptions
    _horizontal_width = 0.8

    def __init__(self, options: CategoricalPlotOptions):
        super().__init__(options)
        self._order: Optional[list] = None
        self._df_unlabeled: Optional[pd.DataFrame] = None

    def _draw_unstacked(self, chart: Chart, data: pd.DataFrame) -> Any:
        raise NotImplementedError

    def _datalabel_formatting(self) -> str:
        return 'totals'

    def _value_column(self) -> Optional[str]:
        """Column holding pre-aggregated values; None means count rows."""
        return None

    def draw(self, data: pd.DataFrame) -> Any:
        chart = create_sized_figure(self, data)
        if self.options.stacked:
            return self._draw_stacked(chart, data)
        return self._draw_unstacked(chart, data)

    def _prepare_stacked(self, data: pd.DataFrame) -> pd.DataFrame:
        """Pivot to one column per hue value and one row per category, in drawing order."""
        return prepare_stacked_data(
            data,
            self.options.hue,  # type: ignore[arg-type]
            self.options.axis_column,
            self.options.order_type,
            value_col=self._value_column(),
            orientation=self.options.orientation,
        )

    def _draw_stacked(self, chart: Chart, data: pd.DataFrame) -> Any:
        horizontal = self.options.orientation == 'horizontal'
        df_prepared = self._prepare_stacked(data)
        plot = renderer.render_stacked_barplot(
            chart,
            df=df_prepared,
            horizontal=horizontal,
            colors=create_colors_list(df_prepared, self._palette),  # type: ignore[arg-type]
            width=self._horizontal_width if horizontal else 0.6,
        )
        self._df_unlabeled = df_prepared
        return plot

    def format_plot(self, plot: Any) -> None:
        self._format_labels_and_legend(plot)
        # label_map renames hue values when there is a hue, otherwise the category ticks.
        tick_label_map = self.options.label_map if self.options.hue is None else None
        if self.options.orientation == 'vertical':
            format_ticks(plot, y_grid=True, numeric_y=True)
            format_categorical_tick_labels(plot, tick_label_map, axis='x')
        else:
            format_ticks(plot, x_grid=True, numeric_x=True)
            format_categorical_tick_labels(plot, tick_label_map, axis='y')

        if self.options.show_labels:
            self._format_data_labels(plot)

    def _format_data_labels(self, plot: Any) -> None:
        if self.options.stacked:
            if self.options.stacked_labels is not None and self._df_unlabeled is not None:
                format_datalabels_stacked(
                    plot,
                    self._df_unlabeled,
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
        )
