from typing import Any, List

import pandas as pd

from ...number_format import format_percentage, format_thousands
from ..common.colors import default_colors, palette_colors, resolve_palette
from ..common.formatting.text_contrast import get_text_color_for_background
from ..config import FigureSize, Marks
from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import PiePlotOptions
from ..svg import Text


class PieChart(AbstractPlot[pd.DataFrame]):
    options: PiePlotOptions

    def __init__(self, options: PiePlotOptions):
        super().__init__(options)
        self._labels: List[str] = []
        self._colors: List[str] = []
        self._values: List[float] = []
        self._autotexts: List[Text] = []
        self._headlines: List[str] = []
        self._headline_texts: List[Text] = []

    def preprocess(self) -> pd.DataFrame:
        return self.options.df.copy()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.options.col] = df[self.options.col].fillna(0).astype(float)
        self._values = df[self.options.col].tolist()
        keys = [str(val) for val in df.index]

        label_map = self.options.label_map
        self._labels = [label_map.get(key, key) for key in keys] if label_map else keys

        slice_labels = {str(key): text for key, text in (self.options.slice_labels or {}).items()}
        unknown = sorted(set(slice_labels) - set(keys))
        if unknown:
            raise ValueError(f"slice_labels keys {unknown} are not values of the column. Available values: {keys}")
        self._headlines = [slice_labels.get(key, '') for key in keys]

        palette = self.options.palette
        if palette is None:
            # Slices keep data order, so the default cycle follows it instead of sorted keys.
            self._colors = default_colors(len(keys))
        else:
            self._colors = palette_colors(resolve_palette(palette, pd.Series(keys)), keys)
        return df

    def draw(self, data: pd.DataFrame) -> Any:
        chart = self._new_chart(None, FigureSize.PIE)
        self._autotexts, self._headline_texts = renderer.render_piechart(
            chart,
            values=self._values,
            colors=self._colors,
            donut=self.options.donut,
            n_after_comma=self.options.n_after_comma,
            value_datalabel=self.options.value_datalabel,
            pctdistance=Marks.DONUT_LABEL_RADIUS if self.options.donut else Marks.PIE_LABEL_RADIUS,
            headlines=self._headlines,
            datalabels=not self.options.legend_percentages,
        )
        return chart

    def format_plot(self, plot: Any, data: pd.DataFrame) -> None:
        total = sum(self._values)
        plot.legend = [
            (color, label, format_percentage(val / total * 100, self.options.n_after_comma)
             if self.options.legend_percentages else format_thousands(val))
            for color, label, val in zip(self._colors, self._labels, self._values)
        ]
        for bg_color, autotext in zip(self._colors, self._autotexts):
            autotext.color = get_text_color_for_background(bg_color)
        headline_colors = [color for color, headline in zip(self._colors, self._headlines) if headline]
        for bg_color, headline_text in zip(headline_colors, self._headline_texts):
            headline_text.color = get_text_color_for_background(bg_color)
