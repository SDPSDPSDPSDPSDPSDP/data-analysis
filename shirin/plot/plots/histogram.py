from typing import Any, Optional, cast

import pandas as pd

from ..core.base_plot import AbstractPlot
from ..core.options import HistogramOptions
from ..common.strategies.palette import get_palette_strategy
from ..common.formatting import (
    format_ticks,
)
from ..common.data_conversion import (
    ensure_column_is_int,
    ensure_column_is_string,
)


class Histogram(AbstractPlot):
    def __init__(self, options: HistogramOptions, renderer=None):
        super().__init__(options, renderer)
        self.options: HistogramOptions = options
        self._color: Optional[str] = None
        self._palette: Optional[Any] = None
        self._bins: int = 100
    
    def preprocess(self) -> pd.DataFrame:
        df = self.options.df.copy()
        
        if self.options.xlimit is not None:
            df = cast(pd.DataFrame, df[df[self.options.x] <= self.options.xlimit].copy())
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = ensure_column_is_int(df, self.options.x)
        # Convert hue to string if present, so it matches normalized palette keys
        if self.options.hue is not None:
            df = ensure_column_is_string(df, self.options.hue)
        
        self._bins = self._calculate_bins(df)
        
        palette_strategy = get_palette_strategy(self.options.palette)
        self._color, self._palette = palette_strategy.get_palette()
        
        
        return df
    
    def _calculate_bins(self, df: pd.DataFrame) -> int:
        max_value_x = int(df[self.options.x].max())
        if max_value_x == 0:
            return self.options.bins
        return min(self.options.bins, max_value_x)
    
    def draw(self, data: pd.DataFrame) -> Any:
        from ..config import FigureSize
        self.renderer.create_figure((FigureSize.WIDTH, FigureSize.HEIGHT * 0.7))
        

        plot = self.renderer.render_histogram(
            df=data,
            x=self.options.x,
            bins=self._bins,
            hue=self.options.hue,
            color=self._color,
            palette=self._palette,
            stacked=self.options.stacked
        )
        
        return plot
    
    def format_plot(self, plot: Any) -> None:
        self._format_labels_and_legend(plot)

        min_value = self._preprocessed_df[self.options.x].min()  # type: ignore
        max_value = self._preprocessed_df[self.options.x].max()  # type: ignore
        is_year_column = (
            1600 < min_value and max_value < 2300
            and len(str(min_value)) == 4 and len(str(max_value)) == 4
        )
        
        format_ticks(
            plot,
            y_grid=True,
            numeric_x=not is_year_column,
            numeric_y=True
        )
