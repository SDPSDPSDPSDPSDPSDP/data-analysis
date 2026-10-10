from typing import Any

import pandas as pd

from ..core.categorical_options import AccuracyPlotOptions
from ..common.formatting import (
    format_datalabels_stacked,
    format_optional_legend,
    format_ticks,
    format_xy_labels,
)
from ..common.data_conversion import ensure_column_is_string
from ..common.stacked_plots import prepare_stacked_data
from .categorical import StackableCategoricalPlot

_CORRECT_KEY = 'Correct'
_INCORRECT_KEY = 'Incorrect'
_VALUE_COL = '__value__'


class AccuracyPlot(StackableCategoricalPlot):
    """Stacked bar plot built from a per-run accuracy column.

    The DataFrame is expected to have one row per run with:
      - ``axis_column``: category / run name (x-axis)
      - ``value_column``: accuracy as a fraction in [0, 1]

    The plot expands each row into two segments -- *Correct* (= accuracy) and
    *Incorrect* (= 1 - accuracy) -- and renders them as a stacked bar chart,
    sorted by accuracy, with the value axis hidden and percentage labels inside the bars.
    """

    options: AccuracyPlotOptions
    _horizontal_width = 0.6

    def preprocess(self) -> pd.DataFrame:
        return ensure_column_is_string(self.options.df, self.options.axis_column)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Expand accuracy rows into long-format correct/incorrect rows."""
        self._palette = self.options.palette  # type: ignore[assignment]
        axis, hue = self.options.axis_column, self.options.hue
        accuracy = df[self.options.value_column].astype(float)

        correct = pd.DataFrame({axis: df[axis], hue: _CORRECT_KEY, _VALUE_COL: accuracy})
        incorrect = pd.DataFrame({axis: df[axis], hue: _INCORRECT_KEY, _VALUE_COL: 1.0 - accuracy})
        return pd.concat([correct, incorrect], ignore_index=True)

    def _prepare_stacked(self, data: pd.DataFrame) -> pd.DataFrame:
        # Correct drawn first (bottom). Default sorting is highest-first for
        # vertical plots and top-to-bottom for horizontal plots. reverse_order
        # flips that behavior.
        df_prepared = prepare_stacked_data(
            data,
            self.options.hue,  # type: ignore[arg-type]
            self.options.axis_column,
            sort=None,
            value_col=_VALUE_COL,
            orientation=self.options.orientation,
        )[[_CORRECT_KEY, _INCORRECT_KEY]]
        ascending = (self.options.orientation == 'horizontal') != self.options.reverse_order
        return df_prepared.sort_values(_CORRECT_KEY, ascending=ascending)

    def format_plot(self, plot: Any) -> None:
        if self.options.orientation == 'horizontal':
            format_xy_labels(plot, x_axis_label=self.options.y_axis_label, y_axis_label=self.options.x_axis_label)
            value_axis = plot.x
        else:
            format_xy_labels(plot, x_axis_label=self.options.x_axis_label, y_axis_label=self.options.y_axis_label)
            value_axis = plot.y
        format_optional_legend(
            plot,
            hue=self.options.hue,
            legend=self.options.legend,
            label_map=self.options.label_map,
        )

        format_ticks(plot)
        value_axis.show_tick_labels = False

        if self._df_unlabeled is not None:
            format_datalabels_stacked(
                plot,
                self._df_unlabeled,
                self._palette,  # type: ignore[arg-type]
                orientation=self.options.orientation,
                suffix=self.options.suffix,
            )
