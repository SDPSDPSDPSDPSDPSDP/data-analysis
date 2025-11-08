from typing import Any, Optional, List

import pandas as pd
import matplotlib.pyplot as plt

from ..core.base_plot import AbstractPlot
from ..core.options import PiePlotOptions
from ..common.label_mapping import create_label_map
from ..common.formatting.text_contrast import get_text_color_for_background


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
        
        label_map = create_label_map(
            self.options.label_map,
            self._original_labels
        )
        
        self._labels = [label_map.get(val, str(val)) for val in self._original_labels]
        self._colors = [self.options.palette[val] for val in self._original_labels]
        
        return df
    
    def draw(self, data: pd.DataFrame) -> Any:
        from ..config import FigureSize
        fig, ax = plt.subplots(figsize=(FigureSize.PIE, FigureSize.PIE))
        
        wedgeprops = dict(edgecolor='none', width=0.6 if self.options.donut else 1.0)
        
        result = ax.pie(
            self._values,
            colors=self._colors,
            autopct=lambda p: f'{p:.{self.options.n_after_comma}f}%' if p >= self.options.value_datalabel else '',
            wedgeprops=wedgeprops,
            textprops={'fontsize': 10},
            pctdistance=0.775 if self.options.donut else 0.6,
        )
        
        self._autotexts = result[2] if len(result) == 3 else []
        
        if self.options.donut:
            from matplotlib.patches import Circle
            center_circle = Circle((0, 0), 0.6, color='white', fc='white', linewidth=0)
            ax.add_artist(center_circle)
        
        ax.axis('equal')
        
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
        for label, autotext in zip(self._original_labels, self._autotexts):  # type: ignore
            bg_color = self.options.palette.get(label, '#000000')
            text_color = get_text_color_for_background(bg_color)
            autotext.set_color(text_color)
