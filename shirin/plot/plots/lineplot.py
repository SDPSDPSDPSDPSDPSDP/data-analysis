from typing import Any, Optional

import pandas as pd

from ..core.base_plot import AbstractPlot
from ..core.options import LinePlotOptions
from ..common.formatting import (
    format_ticks,
)
from ..common.data_conversion import (
    fill_missing_values_in_data,
)


class LinePlot(AbstractPlot):
    def __init__(self, options: LinePlotOptions, renderer=None):
        super().__init__(options, renderer)
        self.options: LinePlotOptions = options
        self._color: Optional[str] = None
        self._palette: Optional[Any] = None
    
    def preprocess(self) -> pd.DataFrame:
        df = self.options.df.copy()
        
        if self.options.fill_missing_values is not None:
            df = fill_missing_values_in_data(
                df,
                self.options.x,
                self.options.y,
                                self.options.hue,
                self.options.fill_missing_values
            )
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._resolve_hue_palette(df)

    def draw(self, data: pd.DataFrame) -> Any:
        self._create_standard_figure()
        
        plot = self.renderer.render_lineplot(
            df=data,
            x=self.options.x,
            y=self.options.y,
            hue=self.options.hue,
            color=self._color,
            palette=self._palette
        )
        
        return plot
    
    def format_plot(self, plot: Any) -> None:
        self._format_labels_and_legend(plot)
        format_ticks(
            plot,
            y_grid=True,
            numeric_y=True,
            rotation=self.options.rotation
        )
