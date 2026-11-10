from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import pandas as pd

from ..common.colors import palette_colors
from ..common.data_conversion import ensure_column_is_string, filter_top_n_categories
from ..common.formatting import format_datalabels_stacked_normalized, format_tick_descriptions, format_ticks
from ..common.stacked_plots import sort_stacked_pivot
from ..config import Marks
from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.categorical_options import NormalizedPlotOptions
from .categorical import create_sized_figure, format_period_axis


@dataclass
class NormalizedData:
    df: pd.DataFrame
    # Share per hue level (columns) for each category (rows); every row sums to 1.
    shares: pd.DataFrame
    # (front, back) fill per bar when bars are colored by category, else None.
    row_colors: Optional[List[Tuple[str, str]]] = None


class NormalizedPlot(AbstractPlot[NormalizedData]):
    options: NormalizedPlotOptions

    def preprocess(self) -> pd.DataFrame:
        # crosstab aligns columns on the index, which fails on duplicate labels (e.g. after pd.concat).
        df = ensure_column_is_string(self.options.df, self.options.axis_column).reset_index(drop=True)
        df = self._resolve_hue_palette(df)
        if self.options.top_n is not None:
            df = filter_top_n_categories(df, self.options.axis_column, self.options.top_n)
        return df

    def _shares(self, df: pd.DataFrame) -> pd.DataFrame:
        values = df[self.options.value] if self.options.value else None
        return pd.crosstab(
            df[self.options.axis_column], df[self.options.hue],
            values=values, aggfunc='sum' if values is not None else None, normalize='index',
        )

    def transform(self, df: pd.DataFrame) -> NormalizedData:
        shares = self._shares(df)
        if self.options.sort == 'frequency':
            # Every row sums to 1, so rank by the first segment's share instead.
            shares = shares.sort_values(shares.columns[0], ascending=self.options.orientation == 'horizontal')
        else:
            shares = sort_stacked_pivot(shares, self.options.sort, self.options.orientation)
        return NormalizedData(df, shares)

    def draw(self, data: NormalizedData) -> Any:
        vertical = self.options.orientation == 'vertical'
        return renderer.render_stacked_barplot(
            create_sized_figure(self, data.df),
            df=data.shares,
            horizontal=not vertical,
            colors=palette_colors(self._palette, data.shares.columns),  # type: ignore[arg-type]
            width=Marks.BAR_WIDTH if vertical else Marks.HORIZONTAL_BAR_WIDTH,
            overlap=len(data.shares.columns) == 2,
            row_colors=data.row_colors,
        )

    def format_plot(self, plot: Any, data: NormalizedData) -> None:
        self._format_labels_and_legend(plot)
        vertical = self.options.orientation == 'vertical'
        format_tick_descriptions(plot, self.options.descriptions, 'x' if vertical else 'y')

        if vertical:
            format_ticks(plot, percentage_y=True)
            format_period_axis(plot, self.options)
        else:
            format_ticks(plot, percentage_x=True)

        if self.options.data_labels:
            format_datalabels_stacked_normalized(
                plot,
                data.shares,
                self._palette,  # type: ignore[arg-type]
                orientation=self.options.orientation,
                suffix=self.options.suffix,
                row_colors=None if data.row_colors is None else [front for front, _ in data.row_colors],
            )
