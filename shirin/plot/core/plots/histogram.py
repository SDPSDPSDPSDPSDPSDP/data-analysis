from typing import Any, Optional, Dict

import pandas as pd

from ..base_plot import AbstractPlot
from ..options import HistogramOptions
from ..strategies import get_palette_strategy
from ...formatting import (
    format_optional_legend,
    format_ticks,
    format_xy_labels,
)
from ...utils.label_mapping import create_label_map
from ...utils.data_conversion import (
    convert_dict_keys_to_string,
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
            df = df[df[self.options.x] <= self.options.xlimit].copy()  # type: ignore
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = ensure_column_is_int(df, self.options.x)
        if self.options.hue is not None:
            df = ensure_column_is_string(df, self.options.hue)
        
        self._bins = self._calculate_bins(df)
        
        palette_strategy = get_palette_strategy(self.options.palette)
        self._color, self._palette = palette_strategy.get_palette()
        
        if self.options.label_map:
            self.options.label_map = convert_dict_keys_to_string(self.options.label_map)
        if isinstance(self._palette, dict):
            self._palette = convert_dict_keys_to_string(self._palette)
        
        return df
    
    def _calculate_bins(self, df: pd.DataFrame) -> int:
        max_value_x = int(df[self.options.x].max())
        if max_value_x == 0:
            return self.options.bins
        return min(self.options.bins, max_value_x)
    
    def draw(self, data: pd.DataFrame) -> Any:
        from ...config import FigureSize
        self.renderer.create_figure((FigureSize.WIDTH, FigureSize.HEIGHT * 0.7))
        
        # Determine multiple strategy
        if self.options.hue is None:
            multiple = 'stack'
        elif self.options.stacked is True:
            multiple = 'stack'
        elif self.options.stacked is False:
            multiple = 'dodge'
        else:
            multiple = 'stack'
        
        import seaborn as sns
        plot = sns.histplot(
            data=data,
            x=self.options.x,
            hue=self.options.hue,
            color=self._color,
            palette=self._palette,
            bins=self._bins,
            multiple=multiple,  # type: ignore
            alpha=1,
            edgecolor='white'
        )
        
        return plot
    
    def format_plot(self, plot: Any) -> None:
        label_map = None
        if self.options.hue is not None and self.options.label_map is None:
            label_map = create_label_map(
                self.options.label_map,
                self._preprocessed_df[self.options.hue].unique()  # type: ignore
            )
        else:
            label_map = self.options.label_map
        
        # Check if it's a year column
        min_value = self._preprocessed_df[self.options.x].min()  # type: ignore
        max_value = self._preprocessed_df[self.options.x].max()  # type: ignore
        is_year_column = True
        if 1600 < min_value and max_value < 2300:
            if len(str(min_value)) == 4 and len(str(max_value)) == 4:
                is_year_column = False
        
        format_xy_labels(plot, xlabel=self.options.xlabel, ylabel=self.options.ylabel)
        format_ticks(
            plot,
            y_grid=True,
            numeric_x=is_year_column,
            numeric_y=True
        )
        format_optional_legend(
            plot,
            self.options.hue,
            self.options.plot_legend,
            label_map,
            self.options.ncol,
            self.options.legend_offset
        )
