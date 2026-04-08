from typing import Any, Optional, Dict

import pandas as pd


from ..core.base_plot import AbstractPlot
from ..core.options import NormalizedCountPlotOptions
from ..common.strategies.figsize import get_figure_size_strategy
from ..common.formatting import (
    format_optional_legend,
    format_ticks,
    format_xy_labels,
    format_datalabels_stacked_normalized,
)
from ..common.data_conversion import (
    convert_palette_to_strings,
    ensure_column_is_string,
    convert_dict_keys_to_string,
)
from ..common.data_filtering import filter_top_n_categories
from ..common.label_mapping import create_label_map
from ..common.sorting import sort_pivot_table


class NormalizedCountPlot(AbstractPlot):
    def __init__(self, options: NormalizedCountPlotOptions, renderer=None):
        super().__init__(options, renderer)
        self.options: NormalizedCountPlotOptions = options
        self._palette: Dict[Any, str] = {}
        self._normalized_pivot: Optional[pd.DataFrame] = None
    
    def preprocess(self) -> pd.DataFrame:
        df = self.options.df.copy()
        
        unique_hue_values = df[self.options.hue].unique()
        missing_keys = [val for val in unique_hue_values if val not in self.options.palette]
        if missing_keys:
            raise ValueError(f"Palette missing keys for hue values: {missing_keys}")
        
        df = ensure_column_is_string(df, self.options.axis_column)
        df = ensure_column_is_string(df, self.options.hue)
        
        if self.options.top_n is not None:
            df = filter_top_n_categories(df, self.options.axis_column, self.options.top_n)
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self._palette = convert_palette_to_strings(self.options.palette)
        
        if self.options.label_map:
            self.options.label_map = convert_dict_keys_to_string(self.options.label_map)
        
        counts = df.groupby([self.options.axis_column, self.options.hue]).size()
        normalized_counts = counts / counts.groupby(level=0).sum()
        normalized_df = normalized_counts.rename("percentage").reset_index()
        
        normalized_pivot = normalized_df.pivot(
            index=self.options.axis_column,
            columns=self.options.hue,
            values="percentage"
        )
        self._normalized_pivot = normalized_pivot.fillna(0)
        
        ascending = False if self.options.order_type == 'frequency' else True
        if self.options.orientation == 'horizontal':
            ascending = not ascending
        
        self._normalized_pivot = sort_pivot_table(
            self._normalized_pivot,
            self.options.order_type,
            ascending=ascending
        )
        
        return df
    
    def draw(self, data: pd.DataFrame) -> Any:

        
        size_strategy = get_figure_size_strategy(self.options.figsize, self.options.orientation)
        figsize = size_strategy.calculate_size(
            data,
            self.options.axis_column,
            self.options.orientation
        )
        
        self.renderer.create_figure(figsize)
        colors = []
        for col in self._normalized_pivot.columns:
            str_col = str(col)
            if str_col in self._palette:
                colors.append(self._palette[str_col])
            else:
                raise KeyError(f"Column '{col}' not found in palette. Available keys: {list(self._palette.keys())}")
        
        plot_kind = 'bar' if self.options.orientation == 'vertical' else 'barh'
        width = 0.6 if self.options.orientation == 'vertical' else 0.8
        
        plot = self.renderer.render_stacked_barplot(
            df=self._normalized_pivot,  # type: ignore
            kind=plot_kind,
            colors=colors,
            width=width
        )
        
        return plot
    
    def format_plot(self, plot: Any) -> None:
        label_map = create_label_map(
            self.options.label_map,
            self._preprocessed_df[self.options.hue].unique()  # type: ignore
        )
        
        format_xy_labels(plot, xlabel=self.options.xlabel, ylabel=self.options.ylabel)
        format_optional_legend(
            plot,
            self.options.hue,
            self.options.plot_legend,
            label_map,
            self.options.ncol,
            self.options.legend_offset
        )
        
        if self.options.orientation == 'vertical':
            format_ticks(plot=plot, y_grid=True, percentage_y=True)
        else:
            format_ticks(plot=plot, x_grid=True, percentage_x=True)
        
        if self.options.show_labels:
            format_datalabels_stacked_normalized(
                plot,
                self._normalized_pivot,  # type: ignore
                self._palette,
                orientation=self.options.orientation
            )
