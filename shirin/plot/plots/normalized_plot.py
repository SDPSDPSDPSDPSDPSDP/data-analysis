from typing import Any, List, Optional

import pandas as pd

from ..core import renderer
from ..core.categorical_options import NormalizedPlotOptions
from ..core.base_plot import AbstractPlot
from ..common.formatting import format_ticks, format_datalabels_stacked_normalized
from ..common.data_conversion import ensure_column_is_string, filter_top_n_categories
from ..common.sorting import palette_colors
from ..common.stacked_plots import sort_stacked_pivot
from ..common.colors import blend
from ..config import Marks, TextColors
from ..config.colors import REMAINDER_TINT
from .categorical import create_sized_figure


class NormalizedPlot(AbstractPlot):
    options: NormalizedPlotOptions

    def __init__(self, options: NormalizedPlotOptions):
        super().__init__(options)
        self._normalized_pivot: Optional[pd.DataFrame] = None
        self._row_colors: Optional[List[str]] = None

    def preprocess(self) -> pd.DataFrame:
        # crosstab aligns columns on the index, which fails on duplicate labels (e.g. after pd.concat).
        df = ensure_column_is_string(self.options.df, self.options.axis_column).reset_index(drop=True)
        df = self._resolve_hue_palette(df)
        remainder = self.options.remainder
        if remainder is not None and not (isinstance(self.options.palette, dict) and remainder in self.options.palette):
            filled = next(level for level in df[self.options.hue].unique() if level != remainder)
            self._palette = {**self._palette, remainder: blend(self._palette[filled], TextColors.WHITE, REMAINDER_TINT)}  # type: ignore[dict-item]
        if self.options.top_n is not None:
            df = filter_top_n_categories(df, self.options.axis_column, self.options.top_n)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        values = df[self.options.value] if self.options.value else None
        shares = pd.crosstab(
            df[self.options.axis_column], df[self.options.hue],
            values=values, aggfunc='sum' if values is not None else None, normalize='index',
        )
        if self.options.remainder is not None:
            shares = shares[[level for level in shares.columns if level != self.options.remainder] + [self.options.remainder]]
        if self.options.sort == 'frequency':
            # Every row sums to 1, so rank by the first segment's share instead.
            self._normalized_pivot = shares.sort_values(
                shares.columns[0], ascending=self.options.orientation == 'horizontal',
            )
        else:
            self._normalized_pivot = sort_stacked_pivot(shares, self.options.sort, self.options.orientation)
        return df

    def _category_colors(self) -> Optional[List[str]]:
        """Fill color per bar when bars are colored by category, else None."""
        if self.options.category_palette is None:
            return None
        palette = {str(key): color for key, color in self.options.category_palette.items()}
        return palette_colors(palette, self._normalized_pivot.index)  # type: ignore[union-attr]

    def draw(self, data: pd.DataFrame) -> Any:
        vertical = self.options.orientation == 'vertical'
        category_colors = self._row_colors = self._category_colors()
        return renderer.render_stacked_barplot(
            create_sized_figure(self, data),
            df=self._normalized_pivot,  # type: ignore[arg-type]
            horizontal=not vertical,
            colors=palette_colors(self._palette, self._normalized_pivot.columns),  # type: ignore[arg-type, union-attr]
            width=Marks.BAR_WIDTH if vertical else Marks.HORIZONTAL_BAR_WIDTH,
            overlap=len(self._normalized_pivot.columns) == 2,  # type: ignore[union-attr]
            row_colors=None if category_colors is None else [
                (color, blend(color, TextColors.WHITE, REMAINDER_TINT)) for color in category_colors
            ],
        )

    def format_plot(self, plot: Any) -> None:
        if self.options.remainder is not None:
            # Legend entries follow the pivot columns; match on level, not on the shown text.
            plot.legend = [
                item for item, level in zip(plot.legend, self._normalized_pivot.columns)  # type: ignore[union-attr]
                if level != self.options.remainder
            ]
        self._format_labels_and_legend(plot)

        if self.options.orientation == 'vertical':
            format_ticks(plot, y_grid=True, percentage_y=True)
        else:
            format_ticks(plot, x_grid=True, percentage_x=True)

        if self.options.data_labels:
            labelled = self._normalized_pivot
            if self.options.remainder is not None:
                # The remainder is stacked last, so dropping it leaves the other labels in place.
                labelled = labelled.drop(columns=self.options.remainder)  # type: ignore[union-attr]
            format_datalabels_stacked_normalized(
                plot,
                labelled,  # type: ignore[arg-type]
                self._palette,  # type: ignore[arg-type]
                orientation=self.options.orientation,
                suffix=self.options.suffix,
                row_colors=self._row_colors,
            )
