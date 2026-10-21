from typing import Any

import pandas as pd

from ..common.formatting import format_ticks
from ..common.formatting.datalabels import with_suffix
from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import HistogramOptions

# Whole numbers in this range are treated as years: their ticks get no thousands separator.
_YEAR_RANGE = (1600, 2300)


def _is_whole_numbers(values: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(values) and bool((values % 1 == 0).all())


class Histogram(AbstractPlot):
    options: HistogramOptions

    def __init__(self, options: HistogramOptions):
        super().__init__(options)
        self._bins: int = options.bins
        self._is_year = False

    def preprocess(self) -> pd.DataFrame:
        df = self.options.df.dropna(subset=[self.options.x])
        if self.options.xlimit is not None:
            df = df[df[self.options.x] <= self.options.xlimit]
            if df.empty:
                raise ValueError(f"xlimit={self.options.xlimit} leaves no {self.options.x!r} values to plot")
        return df.copy()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        values = df[self.options.x]
        self._bins = self._calculate_bins(values)
        self._is_year = not values.empty and _is_whole_numbers(values) and bool(values.between(*_YEAR_RANGE).all())
        return self._resolve_hue_palette(df)

    def _calculate_bins(self, values: pd.Series) -> int:
        """Integer data gets at most one bin per distinct integer value."""
        if values.empty or not _is_whole_numbers(values):
            return self.options.bins
        return max(1, min(self.options.bins, int(values.max() - values.min()) + 1))

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
            numeric_x=not self._is_year,
            numeric_y=True
        )
        if self.options.suffix:
            plain = plot.x.formatter
            plot.x.formatter = lambda val: with_suffix(plain(val), self.options.suffix)
