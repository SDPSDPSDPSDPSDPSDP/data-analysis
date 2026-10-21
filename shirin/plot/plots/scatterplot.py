from typing import Any

import pandas as pd

from ..common.formatting import format_ticks
from ..config import Colors
from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import ScatterPlotOptions


class ScatterPlot(AbstractPlot):
    options: ScatterPlotOptions

    def preprocess(self) -> pd.DataFrame:
        return self.options.df.copy()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._resolve_hue_palette(df, no_hue_color=Colors.BLACK)

    def draw(self, data: pd.DataFrame) -> Any:
        return renderer.render_scatterplot(
            self._standard_chart(),
            df=data,
            x=self.options.x,
            y=self.options.y,
            hue=self.options.hue,
            size=self.options.size,
            color=self._color,
            palette=self._palette
        )

    def format_plot(self, plot: Any) -> None:
        self._format_labels_and_legend(plot)
        format_ticks(
            plot,
            y_grid=True,
            numeric_y=True,
            numeric_x=True
        )
