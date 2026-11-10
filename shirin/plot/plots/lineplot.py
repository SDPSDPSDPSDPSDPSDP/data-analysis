from typing import Any

import pandas as pd

from ..common.formatting import format_ticks
from ..config import Colors
from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import LinePlotOptions


class LinePlot(AbstractPlot[pd.DataFrame]):
    options: LinePlotOptions

    def preprocess(self) -> pd.DataFrame:
        return self.options.df.copy()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._resolve_hue_palette(df, no_hue_color=Colors.BLACK)

    def draw(self, data: pd.DataFrame) -> Any:
        options = self.options
        return renderer.render_lineplot(
            self._standard_chart(), df=data, x=options.x, y=options.y, hue=options.hue,
            color=self._color, palette=self._palette, marks=options.marks, mark_labels=options.mark_labels,
            percentage_x=options.percentage_x, percentage_y=options.percentage_y,
        )

    def format_plot(self, plot: Any, data: pd.DataFrame) -> None:
        options = self.options
        self._format_labels_and_legend(plot)
        format_ticks(
            plot,
            x_grid=True,
            y_grid=True,
            numeric_x=not options.percentage_x,
            numeric_y=not options.percentage_y,
            percentage_x=options.percentage_x,
            percentage_y=options.percentage_y,
        )
        plot.x.lim, plot.y.lim = options.x_limits, options.y_limits
