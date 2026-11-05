from dataclasses import dataclass
from typing import Any

import pandas as pd

from ..common.data_conversion import COUNT_COL, fill_missing_values_in_data, to_period_start, totals_per_x
from ..common.formatting import format_period_ticks, format_ticks
from ..config.colors import Colors
from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import TimePlotOptions
from ..svg import Chart
from ..svg.ticks import to_days


@dataclass
class TimeData:
    df: pd.DataFrame
    # Column plotted on y: the given y, or the row count per x.
    y: str
    # Distinct x values, sorted.
    periods: pd.Series


class TimePlot(AbstractPlot[TimeData]):
    options: TimePlotOptions

    def preprocess(self) -> pd.DataFrame:
        options = self.options
        df = options.df.copy()
        if options.group_by is not None:
            df[options.x] = to_period_start(df[options.x], options.group_by)  # type: ignore[arg-type]
        if options.fill_missing_values is not None:
            df = fill_missing_values_in_data(df, options.x, options.y, options.hue, options.fill_missing_values)  # type: ignore[arg-type]
        return df

    def transform(self, df: pd.DataFrame) -> TimeData:
        options = self.options
        df = self._resolve_hue_palette(df, no_hue_color=Colors.BLACK)
        y = options.y or COUNT_COL
        if options.y is None or options.group_by is not None or options.cumulative:
            values = totals_per_x(df, options.x, options.y, options.hue, options.group_by)  # type: ignore[arg-type]
            if options.cumulative:
                values = values.groupby(level=options.hue).cumsum() if options.hue else values.cumsum()
            df = values.rename(y).reset_index()
        return TimeData(df, y, df[options.x].drop_duplicates().sort_values())

    def draw(self, data: TimeData) -> Any:
        options = self.options
        return renderer.render_lineplot(
            self._standard_chart(), df=data.df, x=options.x, y=data.y, hue=options.hue,
            color=self._color, palette=self._palette, fill=options.fill,
        )

    def format_plot(self, plot: Any, data: TimeData) -> None:
        self._format_labels_and_legend(plot)
        format_ticks(plot, y_grid=True, numeric_y=True, rotation=self.options.rotation)
        if self.options.group_by is not None:
            self._format_date_axis(plot, data.periods)

    def _format_date_axis(self, chart: Chart, periods: pd.Series) -> None:
        """Year ticks, month ticks with a year row below, or automatic day ticks."""
        if self.options.group_by == 'day':
            chart.x.date_format = '%Y-%m-%d'
            return
        months = self.options.group_by == 'month' and self.options.display_month
        format_period_ticks(chart, periods, to_days(periods), months)
