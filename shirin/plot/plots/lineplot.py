from typing import Any

import pandas as pd

from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import LinePlotOptions
from ..common.formatting import format_ticks
from ..common.data_conversion import fill_missing_values_in_data
from ..config import Colors


class LinePlot(AbstractPlot):
    options: LinePlotOptions

    def preprocess(self) -> pd.DataFrame:
        if self.options.fill_missing_values is None:
            return self.options.df.copy()
        return fill_missing_values_in_data(
            self.options.df,
            self.options.x,
            self.options.y,
            self.options.hue,
            self.options.fill_missing_values
        )

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._resolve_hue_palette(df, no_hue_color=Colors.BLACK)

    def draw(self, data: pd.DataFrame) -> Any:
        return renderer.render_lineplot(
            self._standard_chart(),
            df=data,
            x=self.options.x,
            y=self.options.y,
            hue=self.options.hue,
            color=self._color,
            palette=self._palette
        )

    def format_plot(self, plot: Any) -> None:
        self._format_labels_and_legend(plot)
        format_ticks(
            plot,
            y_grid=True,
            numeric_y=True,
            rotation=self.options.rotation
        )
