from typing import Any, Optional, Dict

import pandas as pd

from ..core.base_plot import AbstractPlot
from ..core.options import CountPlotOptions
from ..common.strategies.ordering import get_ordering_strategy
from ..common.strategies.figsize import get_figure_size_strategy
from ..common.strategies.palette import get_palette_strategy
from ..common.formatting import (
    format_datalabels,
    format_datalabels_stacked,
    format_optional_legend,
    format_ticks,
    format_xy_labels,
)
from ..common.data_conversion import (
    ensure_column_is_string,
    convert_dict_keys_to_string,
    prepare_legend_label_map,
)
from ..common.data_filtering import filter_top_n_categories
from ..common.sorting import (
    apply_label_mapping,
    create_colors_list,
    create_default_label_map,
)
from ..common.stacked_plots import prepare_stacked_data


class CountPlot(AbstractPlot):
    def __init__(self, options: CountPlotOptions, renderer=None):
        super().__init__(options, renderer)
        self.options: CountPlotOptions = options
        self._order: Optional[Any] = None
        self._color: Optional[str] = None
        self._palette: Optional[Any] = None
        self._original_palette: Optional[Dict[Any, str]] = None
        self._df_unlabeled: Optional[pd.DataFrame] = None
    
    def preprocess(self) -> pd.DataFrame:
        df = self.options.df.copy()
        df = ensure_column_is_string(df, self.options.axis_column)
        
        if self.options.top_n is not None:
            df = filter_top_n_categories(df, self.options.axis_column, self.options.top_n)
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        ordering_strategy = get_ordering_strategy(self.options.order_type)
        self._order = ordering_strategy.get_order(df, self.options.axis_column)
        
        palette_strategy = get_palette_strategy(self.options.palette)
        self._color, self._palette = palette_strategy.get_palette()
        self._original_palette = self._palette if isinstance(self._palette, dict) else None
        
        # Keep original types for palette keys to match data types
        # Label map for legend will be prepared in format_plot
        
        return df
    
    def draw(self, data: pd.DataFrame) -> Any:
        size_strategy = get_figure_size_strategy(
            self.options.figsize,
            self.options.orientation
        )
        figsize = size_strategy.calculate_size(
            data,
            self.options.axis_column,
            self.options.orientation
        )
        self.renderer.create_figure(figsize)
        
        if (self.options.stacked and 
            self.options.hue is not None and 
            isinstance(self._palette, dict)):
            return self._draw_stacked(data)
        
        if self.options.orientation == 'vertical':
            plot = self.renderer.render_countplot(
                df=data,
                x=self.options.axis_column,
                hue=self.options.hue,
                order=self._order,
                color=self._color,
                palette=self._palette
            )
        else:
            plot = self.renderer.render_countplot(
                df=data,
                y=self.options.axis_column,
                hue=self.options.hue,
                order=self._order,
                color=self._color,
                palette=self._palette
            )
        
        return plot
    
    def _draw_stacked(self, data: pd.DataFrame) -> Any:
        df_prepared = prepare_stacked_data(
            data,
            self.options.hue,  # type: ignore
            self.options.axis_column,
            self.options.order_type,
            orientation='horizontal' if self.options.orientation == 'horizontal' else 'vertical'
        )
        
        df_labeled = apply_label_mapping(df_prepared, self.options.label_map)
        colors = create_colors_list(df_prepared, self._palette)  # type: ignore
        
        kind = 'barh' if self.options.orientation == 'horizontal' else 'bar'
        width = 0.8 if self.options.orientation == 'horizontal' else 0.6
        
        plot = self.renderer.render_stacked_barplot(
            df=df_labeled,
            kind=kind,
            colors=colors,
            width=width
        )
        
        self._df_unlabeled = df_prepared
        return plot
    
    def format_plot(self, plot: Any) -> None:
        if (self.options.label_map is None and 
            self.options.plot_legend and 
            self.options.hue is not None):
            self.options.label_map = create_default_label_map(
                self._preprocessed_df,  # type: ignore
                self.options.hue
            )
        
        # Create legend version with string keys
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
        
        if self.options.orientation == 'vertical':
            format_ticks(plot, y_grid=True, numeric_y=True)
        else:
            format_ticks(plot, x_grid=True, numeric_x=True)
        
        self._format_data_labels(plot)
    
    def _format_data_labels(self, plot: Any) -> None:
        if (self.options.stacked and 
            self.options.stacked_labels is not None and 
            self._df_unlabeled is not None and 
            self._original_palette is not None):
            orientation = 'vertical' if self.options.orientation == 'vertical' else 'horizontal'
            format_datalabels_stacked(
                plot,
                self._df_unlabeled,
                self._original_palette,
                orientation=orientation  # type: ignore
            )
        elif not self.options.stacked:
            format_datalabels(
                plot,
                label_offset=0.007,
                orientation='vertical' if self.options.orientation == 'vertical' else 'horizontal'  # type: ignore
            )
