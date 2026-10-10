from typing import Any, Optional, Dict

import pandas as pd

from ..core.base_plot import AbstractPlot
from ..core.options import NormalizedCountPlotOptions
from ..common.formatting import (
    format_ticks,
    format_datalabels_stacked_normalized,
)
from ..common.data_conversion import (
    convert_palette_to_strings,
    ensure_column_is_string,
)
from ..common.data_filtering import filter_top_n_categories
from ..common.sorting import create_colors_list, sort_pivot_table
from .categorical import create_sized_figure


class NormalizedCountPlot(AbstractPlot):
    def __init__(self, options: NormalizedCountPlotOptions, renderer=None):
        super().__init__(options, renderer)
        self.options: NormalizedCountPlotOptions = options
        self._palette: Dict[Any, str] = {}
        self._normalized_pivot: Optional[pd.DataFrame] = None

    def preprocess(self) -> pd.DataFrame:
        df = self.options.df.copy()

        df = ensure_column_is_string(df, self.options.axis_column)
        df = ensure_column_is_string(df, self.options.hue)

        palette = self.options.palette or {}  # keys already stringified by options.validate()
        unique_hue_values = df[self.options.hue].unique()
        missing_keys = [val for val in unique_hue_values if val not in palette]
        if missing_keys:
            raise ValueError(f"Palette missing keys for hue values: {missing_keys}")

        if self.options.top_n is not None:
            df = filter_top_n_categories(df, self.options.axis_column, self.options.top_n)

        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:

        self._palette = convert_palette_to_strings(self.options.palette)

        counts = df.groupby([self.options.axis_column, self.options.hue]).size()
        normalized_counts = counts / counts.groupby(level=0).sum()
        normalized_df = normalized_counts.rename("percentage").reset_index()
        
        normalized_pivot = normalized_df.pivot(
            index=self.options.axis_column,
            columns=self.options.hue,
            values="percentage"
        )
        self._normalized_pivot = normalized_pivot.fillna(0)
        
        ascending = self.options.order_type != 'frequency'
        if self.options.orientation == 'horizontal':
            ascending = not ascending
        
        self._normalized_pivot = sort_pivot_table(
            self._normalized_pivot,
            self.options.order_type,
            ascending=ascending
        )
        
        return df
    
    def draw(self, data: pd.DataFrame) -> Any:
        create_sized_figure(self, data)
        colors = create_colors_list(self._normalized_pivot, self._palette)  # type: ignore[arg-type]

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
        self._format_labels_and_legend(plot)

        if self.options.orientation == 'vertical':
            format_ticks(plot=plot, y_grid=True, percentage_y=True)
        else:
            format_ticks(plot=plot, x_grid=True, percentage_x=True)
        
        if self.options.show_labels:
            format_datalabels_stacked_normalized(
                plot,
                self._normalized_pivot,  # type: ignore
                self._palette,
                orientation=self.options.orientation,
                suffix=self.options.suffix,
            )

