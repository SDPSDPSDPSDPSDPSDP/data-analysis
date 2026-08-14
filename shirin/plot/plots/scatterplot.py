from typing import Any, Optional

import pandas as pd

from ..core.base_plot import AbstractPlot
from ..core.options import ScatterPlotOptions
from ..common.strategies.palette import get_palette_strategy
from ..common.formatting import (
    format_optional_legend,
    format_ticks,
    format_xy_labels,
)
from ..common.sorting import create_default_label_map
from ..common.data_conversion import (
    prepare_legend_label_map,
    ensure_column_is_string,
)


class ScatterPlot(AbstractPlot):
    def __init__(self, options: ScatterPlotOptions, renderer=None):
        super().__init__(options, renderer)
        self.options: ScatterPlotOptions = options
        self._color: Optional[str] = None
        self._palette: Optional[Any] = None

    def preprocess(self) -> pd.DataFrame:
        df = self.options.df.copy()
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.options.hue is not None:
            df = ensure_column_is_string(df, self.options.hue)

        palette_strategy = get_palette_strategy(self.options.palette)
        self._color, self._palette = palette_strategy.get_palette()
        self._color = self._resolve_color(self._color)

        return df

    def draw(self, data: pd.DataFrame) -> Any:
        self._create_standard_figure()

        plot = self.renderer.render_scatterplot(
            df=data,
            x=self.options.x,
            y=self.options.y,
            hue=self.options.hue,
            size=self.options.size,
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
            numeric_x=True
        )
