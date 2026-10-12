from typing import Any

import pandas as pd

from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import TimePlotOptions
from ..common.data_conversion import COUNT_COL, fill_missing_values_in_data, to_period_start, totals_per_x
from ..common.formatting import format_period_ticks, format_ticks
from ..config.colors import Colors
from ..svg import Chart
from ..svg.ticks import to_days


class TimePlot(AbstractPlot):
    options: TimePlotOptions

    def preprocess(self) -> pd.DataFrame:
        options = self.options
        df = options.df.copy()
        if options.group_by is not None:
            df[options.x] = to_period_start(df[options.x], options.group_by)  # type: ignore[arg-type]
        if options.fill_missing_values is not None:
            df = fill_missing_values_in_data(df, options.x, options.y, options.hue, options.fill_missing_values)  # type: ignore[arg-type]
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        options = self.options
        df = self._resolve_hue_palette(df, no_hue_color=Colors.BLACK)
        self._y = options.y or COUNT_COL
        if options.y is not None and options.group_by is None and not options.cumulative:
            return df

        values = totals_per_x(df, options.x, options.y, options.hue, options.group_by)  # type: ignore[arg-type]
        if options.cumulative:
            values = values.groupby(level=options.hue).cumsum() if options.hue else values.cumsum()
        return values.rename(self._y).reset_index()

    def draw(self, data: pd.DataFrame) -> Any:
        options = self.options
        chart = self._standard_chart()
        self._periods = data[options.x].drop_duplicates().sort_values()
        return renderer.render_lineplot(chart, df=data, x=options.x, y=self._y, hue=options.hue, color=self._color, palette=self._palette, fill=options.fill)

    def format_plot(self, plot: Any) -> None:
        self._format_labels_and_legend(plot)
        format_ticks(plot, y_grid=True, numeric_y=True, rotation=self.options.rotation)
        if self.options.group_by is not None:
            self._format_date_axis(plot)

    def _format_date_axis(self, chart: Chart) -> None:
        """Year ticks, month ticks with a year row below, or automatic day ticks."""
        if self.options.group_by == 'day':
            chart.x.date_format = '%Y-%m-%d'
            return
        months = self.options.group_by == 'month' and self.options.display_month
        format_period_ticks(chart, self._periods, to_days(self._periods), months)
