from typing import Any, List

import pandas as pd

from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import PiePlotOptions
from ..common.formatting.text_contrast import get_text_color_for_background
from ..common.colors import default_colors, default_palette, palette_colors
from ..config import FigureSize, Marks
from ..svg import Text
from ...number_format import format_percentage, format_thousands


class PieChart(AbstractPlot):
    options: PiePlotOptions

    def __init__(self, options: PiePlotOptions):
        super().__init__(options)
        self._labels: List[str] = []
        self._colors: List[str] = []
        self._values: List[float] = []
        self._autotexts: List[Text] = []

    def preprocess(self) -> pd.DataFrame:
        return self.options.df.copy()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.options.col] = df[self.options.col].fillna(0).astype(float)
        self._values = df[self.options.col].tolist()
        keys = [str(val) for val in df.index]

        label_map = self.options.label_map
        self._labels = [label_map.get(key, key) for key in keys] if label_map else keys

        palette = self.options.palette
        if isinstance(palette, str):
            palette = default_palette(pd.Series(keys), palette)
        self._colors = default_colors(len(keys)) if palette is None else palette_colors(palette, keys)
        return df

    def draw(self, data: pd.DataFrame) -> Any:
        chart = self._new_chart(None, FigureSize.PIE)
        self._autotexts = renderer.render_piechart(
            chart,
            values=self._values,
            colors=self._colors,
            donut=self.options.donut,
            n_after_comma=self.options.n_after_comma,
            value_datalabel=self.options.value_datalabel,
            pctdistance=Marks.DONUT_LABEL_RADIUS if self.options.donut else Marks.PIE_LABEL_RADIUS,
            datalabels=not self.options.legend_percentages,
        )
        return chart

    def format_plot(self, plot: Any) -> None:
        total = sum(self._values)
        plot.legend = [
            (color, label, format_percentage(val / total * 100, self.options.n_after_comma)
             if self.options.legend_percentages else format_thousands(val))
            for color, label, val in zip(self._colors, self._labels, self._values)
        ]
        for bg_color, autotext in zip(self._colors, self._autotexts):
            autotext.color = get_text_color_for_background(bg_color)
