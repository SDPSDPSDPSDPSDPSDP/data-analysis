from typing import Any, Optional, Dict

import pandas as pd

from ..core.base_plot import AbstractPlot
from ..core.options import AccuracyPlotOptions
from ..common.strategies.ordering import get_ordering_strategy
from ..common.strategies.figsize import get_figure_size_strategy
from ..common.strategies.palette import get_palette_strategy
from ..common.formatting import (
    format_datalabels_stacked,
    format_optional_legend,
    format_ticks,
    format_xy_labels,
)
from ..common.data_conversion import convert_palette_to_strings
from ..common.sorting import apply_label_mapping, create_colors_list
from ..common.stacked_plots import prepare_stacked_data

_CORRECT_KEY = 'Correct'
_INCORRECT_KEY = 'Incorrect'
_HUE_COL = '__is_correct__'


class AccuracyPlot(AbstractPlot):
    """Stacked bar plot built from a per-run accuracy column.

    The DataFrame is expected to have one row per run with:
      - ``axis_column``: category / run name (x-axis)
      - ``value_column``: accuracy as a fraction in [0, 1]

    The plot expands each row into two segments – *Correct* (= accuracy) and
    *Incorrect* (= 1 − accuracy) – and renders them as a stacked bar chart
    that reuses the exact same draw/format machinery as ``BarPlot``.
    """

    def __init__(self, options: AccuracyPlotOptions, renderer=None):
        super().__init__(options, renderer)
        self.options: AccuracyPlotOptions = options
        self._palette: Optional[Dict[str, str]] = None
        self._df_unlabeled: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------------
    # AbstractPlot interface
    # ------------------------------------------------------------------

    def preprocess(self) -> pd.DataFrame:
        df = self.options.df.copy()
        df[self.options.axis_column] = df[self.options.axis_column].astype(str)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Expand accuracy rows into long-format correct/incorrect rows."""
        rows = []
        for _, row in df.iterrows():
            accuracy = float(row[self.options.value_column])
            run = row[self.options.axis_column]
            rows.append({self.options.axis_column: run, _HUE_COL: _CORRECT_KEY, '__value__': accuracy})
            rows.append({self.options.axis_column: run, _HUE_COL: _INCORRECT_KEY, '__value__': 1.0 - accuracy})

        df_long = pd.DataFrame(rows)

        # Resolve palette: user-supplied or default correct/incorrect colours
        palette_strategy = get_palette_strategy(self.options.palette)
        _, raw_palette = palette_strategy.get_palette()

        if isinstance(raw_palette, dict):
            self._palette = {str(k): str(v) for k, v in raw_palette.items()}
        else:
            # Fall back to defaults when no dict palette provided
            from ..config.colors import Colors
            self._palette = {
                _CORRECT_KEY: Colors.GOOD_GREEN,
                _INCORRECT_KEY: Colors.BAD_RED,
            }

        return df_long

    def draw(self, data: pd.DataFrame) -> Any:
        orientation = self.options.orientation
        size_strategy = get_figure_size_strategy(
            self.options.figsize,
            orientation,
        )
        figsize = size_strategy.calculate_size(data, self.options.axis_column, orientation)
        self.renderer.create_figure(figsize)

        df_prepared = prepare_stacked_data(
            data,
            _HUE_COL,
            self.options.axis_column,
            self.options.order_type,
            value_col='__value__',
            orientation=orientation,
        )

        # Sort by accuracy (Correct column) descending — highest accuracy first
        if _CORRECT_KEY in df_prepared.columns:
            df_prepared = df_prepared.sort_values(_CORRECT_KEY, ascending=False)

        # Correct is drawn first (bottom), Incorrect stacked on top
        cols_ordered = []
        for key in (_CORRECT_KEY, _INCORRECT_KEY):
            if key in df_prepared.columns:
                cols_ordered.append(key)
        # Append any remaining columns that aren't in the expected pair
        for col in df_prepared.columns:
            if col not in cols_ordered:
                cols_ordered.append(col)
        df_prepared = df_prepared[cols_ordered]

        df_labeled = apply_label_mapping(df_prepared, self.options.label_map)
        colors = create_colors_list(df_prepared, self._palette)  # type: ignore

        kind = 'barh' if self.options.orientation == 'horizontal' else 'bar'
        plot = self.renderer.render_stacked_barplot(
            df=df_labeled,
            kind=kind,
            colors=colors,
            width=0.6,
        )

        self._df_unlabeled = df_prepared
        return plot

    def format_plot(self, plot: Any) -> None:
        orientation = self.options.orientation
        format_xy_labels(plot, xlabel=self.options.xlabel, ylabel=self.options.ylabel)

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
            plot.xaxis.set_visible(False)
        else:
            plot.yaxis.set_visible(False)

        if self._df_unlabeled is not None and self._palette is not None:
            format_datalabels_stacked(
                plot,
                self._df_unlabeled,
                self._palette,
                orientation=orientation,
            )
