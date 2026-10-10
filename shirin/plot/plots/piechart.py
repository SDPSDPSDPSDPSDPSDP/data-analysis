from typing import Any, List

import pandas as pd
import seaborn as sns

from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import PiePlotOptions
from ..common.formatting.text_contrast import get_text_color_for_background
from ..common.sorting import palette_colors
from ..config import FigureSize, FontSizes, TextColors
from ...number_format import format_thousands


class PieChart(AbstractPlot):
    options: PiePlotOptions

    def __init__(self, options: PiePlotOptions):
        super().__init__(options)
        self._labels: List[str] = []
        self._colors: List[str] = []
        self._values: List[float] = []
        self._autotexts: List[Any] = []

    def preprocess(self) -> pd.DataFrame:
        return self.options.df.copy()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.options.col] = df[self.options.col].fillna(0).astype(float)
        self._values = df[self.options.col].tolist()
        keys = [str(val) for val in df.index]

        label_map = self.options.label_map or {}
        self._labels = [label_map.get(key, key) for key in keys]

        palette = self.options.palette
        if isinstance(palette, dict):
            self._colors = palette_colors(palette, keys)
        else:
            # No palette or a named seaborn palette: one distinct color per slice.
            self._colors = sns.color_palette(palette, n_colors=len(keys)).as_hex()
        return df

    def draw(self, data: pd.DataFrame) -> Any:
        ax = self._new_axes((FigureSize.PIE, FigureSize.PIE))
        self._autotexts = renderer.render_piechart(
            ax,
            values=self._values,
            colors=self._colors,
            donut=self.options.donut,
            n_after_comma=self.options.n_after_comma,
            value_datalabel=self.options.value_datalabel,
            pctdistance=0.775 if self.options.donut else 0.6
        )
        return ax

    def format_plot(self, plot: Any) -> None:
        legend_labels = [
            f'{label}: {format_thousands(val)}'
            for label, val in zip(self._labels, self._values)
        ]
        legend = plot.legend(
            legend_labels,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.98),
            fontsize=FontSizes.LEGEND,
            framealpha=0.0,
            ncol=1,
        )
        for text in legend.get_texts():
            text.set_color(TextColors.DARK_GREY)

        for bg_color, autotext in zip(self._colors, self._autotexts):
            autotext.set_color(get_text_color_for_background(bg_color))
