from typing import Any, Optional

import pandas as pd

from ..core import renderer
from ..core.categorical_options import NormalizedCountPlotOptions
from ..core.base_plot import AbstractPlot
from ..common.formatting import format_ticks, format_datalabels_stacked_normalized
from ..common.data_conversion import ensure_column_is_string, filter_top_n_categories
from ..common.sorting import create_colors_list
from ..common.stacked_plots import sort_stacked_pivot
from .categorical import create_sized_figure


class NormalizedCountPlot(AbstractPlot):
    options: NormalizedCountPlotOptions

    def __init__(self, options: NormalizedCountPlotOptions):
        super().__init__(options)
        self._normalized_pivot: Optional[pd.DataFrame] = None

    def preprocess(self) -> pd.DataFrame:
        df = ensure_column_is_string(self.options.df, self.options.axis_column)
        df = self._resolve_hue_palette(df)
        if self.options.top_n is not None:
            df = filter_top_n_categories(df, self.options.axis_column, self.options.top_n)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        shares = pd.crosstab(df[self.options.axis_column], df[self.options.hue], normalize='index')
        self._normalized_pivot = sort_stacked_pivot(shares, self.options.order_type, self.options.orientation)
        return df

    def draw(self, data: pd.DataFrame) -> Any:
        vertical = self.options.orientation == 'vertical'
        return renderer.render_stacked_barplot(
            create_sized_figure(self, data),
            df=self._normalized_pivot,  # type: ignore[arg-type]
            horizontal=not vertical,
            colors=create_colors_list(self._normalized_pivot, self._palette),  # type: ignore[arg-type]
            width=0.6 if vertical else 0.8,
        )

    def format_plot(self, plot: Any) -> None:
        self._format_labels_and_legend(plot)

        if self.options.orientation == 'vertical':
            format_ticks(plot, y_grid=True, percentage_y=True)
        else:
            format_ticks(plot, x_grid=True, percentage_x=True)

        if self.options.show_labels:
            format_datalabels_stacked_normalized(
                plot,
                self._normalized_pivot,  # type: ignore[arg-type]
                self._palette,  # type: ignore[arg-type]
                orientation=self.options.orientation,
                suffix=self.options.suffix,
            )
