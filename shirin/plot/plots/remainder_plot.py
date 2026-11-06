import dataclasses
from typing import Any

import pandas as pd

from ..common.colors import blend, palette_colors, resolve_palette
from ..common.data_conversion import REMAINDER_LABEL, REMAINDER_SHARE_COL, fill_remainder
from ..config.colors import REMAINDER_TINT
from ..core.categorical_options import RemainderPlotOptions
from .normalized_plot import NormalizedData, NormalizedPlot


class RemainderPlot(NormalizedPlot):
    """Normalized bars of two levels per bar: the `value` fraction, then REMAINDER_LABEL up to 100%.

    The remainder is tinted from the filled color toward the background, stacked last, and has
    no legend entry or data label.
    """

    options: RemainderPlotOptions  # type: ignore[assignment]

    def preprocess(self) -> pd.DataFrame:
        options = self.options
        by_category = options.hue is not None
        self._category_palette = (
            resolve_palette(options.category_palette, options.df[options.hue]) if by_category else None
        )
        palette = {options.value: options.palette} if isinstance(options.palette, str) else options.palette
        # From here on hue is the split of each bar into the filled level (named after value) and the remainder.
        self.options = dataclasses.replace(
            options,
            df=fill_remainder(options.df, options.axis_column, options.value, REMAINDER_LABEL),
            hue=options.value,
            value=REMAINDER_SHARE_COL,
            palette=palette,
        )
        df = super().preprocess()
        if not (isinstance(palette, dict) and REMAINDER_LABEL in palette):
            filled = next(level for level in df[self.options.hue].unique() if level != REMAINDER_LABEL)
            self._palette = {**self._palette, REMAINDER_LABEL: self._tint(self._palette[filled])}  # type: ignore[index]
        return df

    def _tint(self, color: str) -> str:
        return blend(color, self.options.background, REMAINDER_TINT)

    def _shares(self, df: pd.DataFrame) -> pd.DataFrame:
        shares = super()._shares(df)
        filled_levels = [level for level in shares.columns if level != REMAINDER_LABEL]
        return shares[filled_levels + [REMAINDER_LABEL]]

    def transform(self, df: pd.DataFrame) -> NormalizedData:
        data = super().transform(df)
        if self._category_palette is not None:
            palette = {str(key): color for key, color in self._category_palette.items()}
            data.row_colors = [(color, self._tint(color)) for color in palette_colors(palette, data.shares.index)]
        return data

    def format_plot(self, plot: Any, data: NormalizedData) -> None:
        # Legend entries follow the pivot columns; match on level, not on the shown text.
        plot.legend = [item for item, level in zip(plot.legend, data.shares.columns) if level != REMAINDER_LABEL]
        # The remainder is stacked last, so dropping it leaves the other labels in place.
        super().format_plot(plot, dataclasses.replace(data, shares=data.shares.drop(columns=REMAINDER_LABEL)))
