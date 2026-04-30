from typing import Any, Optional, Dict

import pandas as pd

from ..core.base_plot import AbstractPlot
from ..core.options import AccuracyPlotOptions
from ..common.strategies.figsize import get_figure_size_strategy
from ..common.formatting import (
    format_datalabels_stacked,
    format_optional_legend,
    format_ticks,
    format_xy_labels,
)
from ..common.data_conversion import ensure_column_is_string
from ..common.sorting import apply_label_mapping, create_colors_list
from ..common.stacked_plots import prepare_stacked_data

_CORRECT_KEY = 'Correct'
_INCORRECT_KEY = 'Incorrect'
_HUE_COL = '__is_correct__'
_VALUE_COL = '__value__'


class AccuracyPlot(AbstractPlot):
    """Stacked bar plot built from a per-run accuracy column.

    The DataFrame is expected to have one row per run with:
      - ``axis_column``: category / run name (x-axis)
      - ``value_column``: accuracy as a fraction in [0, 1]

    The plot expands each row into two segments -- *Correct* (= accuracy) and
    *Incorrect* (= 1 - accuracy) -- and renders them as a stacked bar chart
    that reuses the exact same draw/format machinery as ``BarPlot``.
    """

    def __init__(self, options: AccuracyPlotOptions, renderer=None):
        super().__init__(options, renderer)
        self.options: AccuracyPlotOptions = options
        self._df_unlabeled: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------------
    # AbstractPlot interface
    # ------------------------------------------------------------------

    def preprocess(self) -> pd.DataFrame:
        return ensure_column_is_string(self.options.df, self.options.axis_column)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Expand accuracy rows into long-format correct/incorrect rows."""
        axis = self.options.axis_column
        accuracy = df[self.options.value_column].astype(float)

        correct = pd.DataFrame({axis: df[axis], _HUE_COL: _CORRECT_KEY, _VALUE_COL: accuracy})
        incorrect = pd.DataFrame({axis: df[axis], _HUE_COL: _INCORRECT_KEY, _VALUE_COL: 1.0 - accuracy})

        return pd.concat([correct, incorrect], ignore_index=True)

    def draw(self, data: pd.DataFrame) -> Any:
        orientation = self.options.orientation
        size_strategy = get_figure_size_strategy(self.options.figsize, orientation)
        figsize = size_strategy.calculate_size(data, self.options.axis_column, orientation)
        self.renderer.create_figure(figsize)

        df_prepared = prepare_stacked_data(
            data,
            _HUE_COL,
            self.options.axis_column,
            self.options.order_type,
            value_col=_VALUE_COL,
            orientation=orientation,
        )

                # Correct drawn first (bottom); sort so highest accuracy is
        # leftmost (vertical) or topmost (horizontal).
        df_prepared = df_prepared[[_CORRECT_KEY, _INCORRECT_KEY]]
        ascending = orientation == 'horizontal'
        df_prepared = df_prepared.sort_values(_CORRECT_KEY, ascending=ascending)

        palette = self.options.palette  # type: ignore[assignment]
        df_labeled = apply_label_mapping(df_prepared, self.options.label_map)
        colors = create_colors_list(df_prepared, palette)

        kind = 'barh' if orientation == 'horizontal' else 'bar'
        plot = self.renderer.render_stacked_barplot(
            df=df_labeled, kind=kind, colors=colors, width=0.6,
        )

        self._df_unlabeled = df_prepared
        return plot

    def format_plot(self, plot: Any) -> None:
        orientation = self.options.orientation
        palette = self.options.palette  # type: ignore[assignment]

        if orientation == 'horizontal':
            format_xy_labels(plot, xlabel=self.options.ylabel, x_labelpad=0,
                             ylabel=self.options.xlabel)
        else:
            format_xy_labels(plot, xlabel=self.options.xlabel,
                             ylabel=self.options.ylabel, y_labelpad=0)
        format_optional_legend(
            plot,
            hue=_HUE_COL,
            plot_legend=self.options.plot_legend,
            label_map=None,
            ncol=self.options.ncol,
            legend_offset=self.options.legend_offset,
        )

        format_ticks(plot)
        if orientation == 'horizontal':
            plot.set_xticklabels([])
            plot.xaxis.set_ticks_position('none')
        else:
            plot.set_yticklabels([])
            plot.yaxis.set_ticks_position('none')

        if self._df_unlabeled is not None:
            format_datalabels_stacked(
                plot,
                self._df_unlabeled,
                palette,
                orientation=orientation,
            )
