from typing import Any, Optional

import pandas as pd

from ..core.base_plot import AbstractPlot
from ..core.options import LinePlotOptions
from ..common.strategies.palette import get_palette_strategy
from ..common.formatting import (
    format_optional_legend,
    format_ticks,
    format_xy_labels,
)
from ..common.label_mapping import create_label_map
from ..common.data_conversion import (
    fill_missing_values_in_data,
    convert_dict_keys_to_string,
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
        palette_strategy = get_palette_strategy(self.options.palette)
        self._color, self._palette = palette_strategy.get_palette()
        
        # Default to black when no hue is specified
        if self.options.hue is None:
            self._color = 'black'
        
        # Convert label_map and palette keys to strings to match converted data columns
        if self.options.label_map:
            self.options.label_map = convert_dict_keys_to_string(self.options.label_map)
        if isinstance(self._palette, dict):
            self._palette = convert_dict_keys_to_string(self._palette)
        
        return df
    
    def draw(self, data: pd.DataFrame) -> Any:
        from ..config import FigureSize
        self.renderer.create_figure((FigureSize.WIDTH, FigureSize.STANDARD_HEIGHT))
        
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
        label_map = None
        if self.options.hue is not None and self.options.label_map is None:
            label_map = create_label_map(
                self.options.label_map,
                self._preprocessed_df[self.options.hue].unique()  # type: ignore
            )
        else:
            label_map = self.options.label_map
        
        format_xy_labels(plot, xlabel=self.options.xlabel, ylabel=self.options.ylabel)
        format_optional_legend(
            plot,
            self.options.hue,
            self.options.plot_legend,
            label_map,
            self.options.ncol,
            self.options.legend_offset
        )
        format_ticks(
            plot,
            y_grid=True,
            numeric_y=True,
            rotation=self.options.rotation
        )
