from typing import Any

import pandas as pd

from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import HistogramOptions
from ..common.formatting import format_ticks


# Whole numbers in this range are treated as years: their ticks get no thousands separator.
_YEAR_RANGE = (1600, 2300)


def _is_whole_numbers(values: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(values) and bool((values % 1 == 0).all())


class Histogram(AbstractPlot):
    options: HistogramOptions

    def __init__(self, options: HistogramOptions):
        super().__init__(options)
        self._bins: int = options.bins

    def preprocess(self) -> pd.DataFrame:
        df = self.options.df.dropna(subset=[self.options.x])
        if self.options.xlimit is not None:
            df = df[df[self.options.x] <= self.options.xlimit]
        return df.copy()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self._bins = self._calculate_bins(df[self.options.x])
        return self._resolve_hue_palette(df)

    def _calculate_bins(self, values: pd.Series) -> int:
        """Integer data gets at most one bin per distinct integer value."""
        if values.empty or not _is_whole_numbers(values):
            return self.options.bins
        return max(1, min(self.options.bins, int(values.max() - values.min()) + 1))

    def _is_year_column(self) -> bool:
        values = self._preprocessed_df[self.options.x]  # type: ignore[index]
        return not values.empty and _is_whole_numbers(values) and bool(values.between(*_YEAR_RANGE).all())

    def draw(self, data: pd.DataFrame) -> Any:
        return renderer.render_histogram(
            self._standard_chart(),
            df=data,
            x=self.options.x,
            bins=self._bins,
            hue=self.options.hue,
            color=self._color,
            palette=self._palette,
            stacked=self.options.stacked
        )

    def format_plot(self, plot: Any) -> None:
        self._format_labels_and_legend(plot)
        format_ticks(
            plot,
            y_grid=True,
            numeric_x=not self._is_year_column(),
            numeric_y=True
        )
        if self.options.suffix:
            plain = plot.x.formatter
            plot.x.formatter = lambda val: f"{plain(val)} {self.options.suffix.strip()}"
