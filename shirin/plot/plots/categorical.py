from abc import abstractmethod
from typing import Any, Dict, Optional

import pandas as pd

from ..core.base_plot import AbstractPlot
from ..core.options import CategoricalPlotOptions
from ..common.strategies.figsize import get_figure_size_strategy
from ..common.strategies.palette import get_palette_strategy
from ..common.formatting import (
    format_categorical_tick_labels,
    format_datalabels,
    format_datalabels_stacked,
    format_ticks,
)
from ..common.data_conversion import convert_palette_to_strings
from ..common.sorting import apply_label_mapping, create_colors_list
from ..common.stacked_plots import prepare_stacked_data


def create_sized_figure(plot: AbstractPlot, data: pd.DataFrame) -> None:
    """Create a figure sized by the plot's figsize strategy (categorical options only)."""
    options = plot.options
    size_strategy = get_figure_size_strategy(options.figsize, options.orientation)
    plot.renderer.create_figure(
        size_strategy.calculate_size(data, options.axis_column, options.orientation)
    )


class StackableCategoricalPlot(AbstractPlot):
    """Shared draw/format logic for count and bar plots (plain or stacked by hue)."""

    options: CategoricalPlotOptions
    value_column: Optional[str] = None

    def __init__(self, options: CategoricalPlotOptions, renderer=None):
        super().__init__(options, renderer)
        self._order: Optional[Any] = None
        self._color: Optional[str] = None
        self._palette: Optional[Any] = None
        self._original_palette: Optional[Dict[Any, str]] = None
        self._df_unlabeled: Optional[pd.DataFrame] = None

    def _resolve_palette(self) -> None:
        self._color, self._palette = get_palette_strategy(self.options.palette).get_palette()
        self._original_palette = self._palette if isinstance(self._palette, dict) else None

    @abstractmethod
    def _draw_unstacked(self, data: pd.DataFrame) -> Any:
        pass

    @abstractmethod
    def _datalabel_formatting(self) -> str:
        pass

    def draw(self, data: pd.DataFrame) -> Any:
        create_sized_figure(self, data)
        if self.options.stacked and self.options.hue is not None and isinstance(self._palette, dict):
            return self._draw_stacked(data)
        return self._draw_unstacked(data)

    def _draw_stacked(self, data: pd.DataFrame) -> Any:
        horizontal = self.options.orientation == 'horizontal'
        df_prepared = prepare_stacked_data(
            data,
            self.options.hue,  # type: ignore[arg-type]
            self.options.axis_column,
            self.options.order_type,
            value_col=self.value_column,
            orientation=self.options.orientation,
        )
        plot = self.renderer.render_stacked_barplot(
            df=apply_label_mapping(df_prepared, self.options.label_map),
            kind='barh' if horizontal else 'bar',
            colors=create_colors_list(df_prepared, self._palette),  # type: ignore[arg-type]
            width=0.8 if horizontal else 0.6,
        )
        self._df_unlabeled = df_prepared
        return plot

    def format_plot(self, plot: Any) -> None:
        self._format_labels_and_legend(plot)
        if self.options.orientation == 'vertical':
            format_ticks(plot, y_grid=True, numeric_y=True)
            format_categorical_tick_labels(plot, self._label_map_legend, axis='x')
        else:
            format_ticks(plot, x_grid=True, numeric_x=True)
            format_categorical_tick_labels(plot, self._label_map_legend, axis='y')

        self._format_data_labels(plot)

    def _format_data_labels(self, plot: Any) -> None:
        if (
            self.options.stacked
            and self.options.stacked_labels is not None
            and self._df_unlabeled is not None
            and self._original_palette is not None
        ):
            # Palette keys as strings to match pivot table column names
            format_datalabels_stacked(
                plot,
                self._df_unlabeled,
                convert_palette_to_strings(self._original_palette),
                orientation=self.options.orientation,  # type: ignore[arg-type]
                suffix=self.options.suffix,  # type: ignore[attr-defined]
            )
        elif not self.options.stacked:
            format_datalabels(
                plot,
                label_offset=0.007,
                formatting=self._datalabel_formatting(),  # type: ignore[arg-type]
                orientation=self.options.orientation,  # type: ignore[arg-type]
                suffix=self.options.suffix,  # type: ignore[attr-defined]
            )
