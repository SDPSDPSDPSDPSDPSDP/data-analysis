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
from ..common.sorting import (
    apply_label_mapping,
    create_colors_list,
    create_default_label_map,
)
from ..common.data_conversion import (
    fill_missing_values_in_data,
    prepare_legend_label_map,
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
        
        # Keep original types for palette keys to match data types
        # Label map for legend will be prepared in format_plot
        
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
        if (self.options.label_map is None and 
            self.options.plot_legend and 
            self.options.hue is not None):
            self.options.label_map = create_default_label_map(
                self._preprocessed_df,  # type: ignore
                self.options.hue
            )
        
        # Prepare legend version with string keys
        self._label_map_legend = prepare_legend_label_map(self.options.label_map)
        
        format_xy_labels(plot, xlabel=self.options.xlabel, ylabel=self.options.ylabel)
        format_optional_legend(
            plot,
            self.options.hue,
            self.options.plot_legend,
            self._label_map_legend,
            self.options.ncol,
            self.options.legend_offset
        )
        format_ticks(
            plot,
            y_grid=True,
            numeric_y=True,
            rotation=self.options.rotation
        )
