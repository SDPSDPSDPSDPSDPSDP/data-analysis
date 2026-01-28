from typing import Any, Optional, List, cast

import pandas as pd
import matplotlib.pyplot as plt

from ..core.base_plot import AbstractPlot
from ..core.options import PiePlotOptions
from ..common.label_mapping import create_label_map
from ..common.formatting.text_contrast import get_text_color_for_background
from ..common.data_conversion import convert_dict_keys_to_string


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
        
        label_map_to_use = self.options.label_map
        # Keep original types for label_map keys
        # if label_map_to_use:
        #     label_map_to_use = convert_dict_keys_to_string(label_map_to_use)
        
        label_map = create_label_map(
            label_map_to_use,
            self._original_labels
        )
        
        original_labels = cast(list, self._original_labels)
        self._labels = [label_map.get(str(val), str(val)) for val in original_labels]
        
        palette_dict = cast(dict, self.options.palette)
        if palette_dict:
            self._colors = [palette_dict.get(str(val), '#000000') for val in original_labels]
        else:
            self._colors = ['#000000'] * len(original_labels)
        
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
        
        self._autotexts = result[2] if len(result) == 3 else []
        
        ax = plt.gca()
        return ax
    
    def format_plot(self, plot: Any) -> None:
        from ..config import FontSizes, TextColors
        
        # Create legend labels
        legend_labels = [
            f'{label}: {val:,.0f}'.replace(",", ".")
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
        
        # Apply automatic text colors
        palette_dict = cast(dict, self.options.palette)
        for label, autotext in zip(self._original_labels, self._autotexts):  # type: ignore
            bg_color = palette_dict.get(label, '#000000')
            text_color = get_text_color_for_background(bg_color)
            autotext.set_color(text_color)
