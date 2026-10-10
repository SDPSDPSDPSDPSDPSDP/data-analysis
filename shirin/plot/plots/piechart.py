from typing import Any, Optional, List, cast

import pandas as pd
import matplotlib.pyplot as plt

from ..core.base_plot import AbstractPlot
from ..core.options import PiePlotOptions
from ..common.formatting.text_contrast import get_text_color_for_background
from ...stats.number_format import format_thousands



class PieChart(AbstractPlot):
    def __init__(self, options: PiePlotOptions, renderer=None):
        super().__init__(options, renderer)
        self.options: PiePlotOptions = options
        self._labels: Optional[List] = None
        self._colors: Optional[List] = None
        self._original_labels: Optional[List] = None
        self._values: Optional[List] = None
    
    def preprocess(self) -> pd.DataFrame:
        return self.options.df.copy()
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df[self.options.col] = df[self.options.col].fillna(0).astype(float)
        self._values = df[self.options.col].tolist()
        self._original_labels = df.index.tolist()
        
        label_map = self.options.label_map or {}
        self._labels = [label_map.get(str(val), str(val)) for val in self._original_labels]

        palette = cast(dict, self.options.palette) or {}
        self._colors = [palette.get(str(val), '#000000') for val in self._original_labels]
        
        return df
    
    def draw(self, data: pd.DataFrame) -> Any:
        from ..config import FigureSize
        self.renderer.create_figure((FigureSize.PIE, FigureSize.PIE))
        
        result = self.renderer.render_piechart(
            values=self._values,  # type: ignore
            colors=self._colors,  # type: ignore
            donut=self.options.donut,
            n_after_comma=self.options.n_after_comma,
            value_datalabel=self.options.value_datalabel,
            pctdistance=0.775 if self.options.donut else 0.6
        )
        
        try:
            self._autotexts = result[2]
        except IndexError:
            self._autotexts = []
        
        ax = plt.gca()
        return ax
    
    def format_plot(self, plot: Any) -> None:
        from ..config import FontSizes, TextColors
        
        legend_labels = [
            f'{label}: {format_thousands(val)}'
            for label, val in zip(self._labels, self._values)  # type: ignore
        ]

        
        legend = plt.legend(
            legend_labels,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.98),
            fontsize=FontSizes.LEGEND,
            framealpha=0.0,
            ncol=1,
        )
        for text in legend.get_texts():
            text.set_color(TextColors.DARK_GREY)
        
        for bg_color, autotext in zip(self._colors, self._autotexts):  # type: ignore
            text_color = get_text_color_for_background(bg_color)
            autotext.set_color(text_color)
