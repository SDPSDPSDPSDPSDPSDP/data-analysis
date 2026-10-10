from typing import Any, Optional

import pandas as pd
from matplotlib.axes import Axes

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


def calculate_figsize(options: CategoricalPlotOptions, data: pd.DataFrame) -> tuple[float, float]:
    """'dynamic' grows with the category count, 'standard' is fixed, a number sets the length axis."""
    vertical = options.orientation == 'vertical'
    if options.figsize == 'dynamic':
        n_categories = data[options.axis_column].nunique()
        return (n_categories + 1, FigureSize.STANDARD_HEIGHT) if vertical else (FigureSize.WIDTH, n_categories / 2 + 1)
    if options.figsize == 'standard':
        return (FigureSize.WIDTH, FigureSize.STANDARD_HEIGHT if vertical else FigureSize.HEIGHT)
    size = float(options.figsize)
    return (size, FigureSize.STANDARD_HEIGHT) if vertical else (FigureSize.WIDTH, size)


def create_sized_figure(plot: AbstractPlot, data: pd.DataFrame) -> Axes:
    return plot._new_axes(calculate_figsize(plot.options, data))  # type: ignore[arg-type]


class StackableCategoricalPlot(AbstractPlot):
    """Shared draw/format logic for count, bar and accuracy plots (plain or stacked by hue)."""

    options: CategoricalPlotOptions
    _horizontal_width = 0.8

    def __init__(self, options: CategoricalPlotOptions):
        super().__init__(options)
        self._order: Optional[list] = None
        self._df_unlabeled: Optional[pd.DataFrame] = None

    def _draw_unstacked(self, ax: Axes, data: pd.DataFrame) -> Any:
        raise NotImplementedError

    def _datalabel_formatting(self) -> str:
        return 'totals'

    def _value_column(self) -> Optional[str]:
        """Column holding pre-aggregated values; None means count rows."""
        return None

    def draw(self, data: pd.DataFrame) -> Any:
        ax = create_sized_figure(self, data)
        if self.options.stacked:
            return self._draw_stacked(ax, data)
        return self._draw_unstacked(ax, data)

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

    def _draw_stacked(self, ax: Axes, data: pd.DataFrame) -> Any:
        horizontal = self.options.orientation == 'horizontal'
        df_prepared = self._prepare_stacked(data)
        plot = renderer.render_stacked_barplot(
            ax,
            df=df_prepared,
            kind='barh' if horizontal else 'bar',
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
            label_offset=0.007,
            formatting=self._datalabel_formatting(),
            orientation=self.options.orientation,
            suffix=self.options.suffix,
        )
