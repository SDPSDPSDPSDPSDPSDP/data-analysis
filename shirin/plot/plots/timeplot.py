from typing import Any

import pandas as pd

from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import TimePlotOptions
from ..common.formatting import (
    format_ticks,
    format_xy_labels,
)
from ..config import Marks
from ..config.colors import Colors
from ..svg import Chart
from ..svg.ticks import to_days


class TimePlot(AbstractPlot):
    options: TimePlotOptions

    def __init__(self, options: TimePlotOptions):
        super().__init__(options)
        self._aggregated_df: pd.DataFrame = pd.DataFrame()

    def preprocess(self) -> pd.DataFrame:
        df = self.options.df.copy()
        date_col = self.options.x

        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col])
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Bars default to grey, the line to black; a palette string overrides both.
        self._color = self.options.palette or (Colors.BLACK if self.options.plot_type == 'line' else Colors.GREY)  # type: ignore[assignment]

        group_by = self.options.group_by
        date_col = self.options.x

        period = {'year': 'Y', 'month': 'M', 'day': 'D'}[group_by]
        df['_time_group'] = df[date_col].dt.to_period(period).dt.to_timestamp()

        self._aggregated_df = (
            df.groupby('_time_group')
            .size()
            .reset_index(name='count')
            .sort_values('_time_group')
        )

        # Include empty periods with zero counts so the x-axis stays continuous.
        if not self._aggregated_df.empty:
            groups = self._aggregated_df['_time_group']
            full_range = pd.date_range(
                start=groups.min(),
                end=groups.max(),
                freq={'year': 'YS', 'month': 'MS', 'day': 'D'}[group_by],
            )

            full_df = pd.DataFrame({'_time_group': full_range})
            self._aggregated_df = (
                full_df.merge(self._aggregated_df, on='_time_group', how='left')
                .fillna({'count': 0})
            )
            self._aggregated_df['count'] = self._aggregated_df['count'].astype(int)

        if self.options.cumulative:
            self._aggregated_df['count'] = self._aggregated_df['count'].cumsum()

        return self._aggregated_df

    def draw(self, data: pd.DataFrame) -> Any:
        chart = self._standard_chart()
        days = to_days(data['_time_group'])
        if self.options.plot_type == 'bar':
            return renderer.render_time_bars(chart, days, data['count'], color=self._color, width=Marks.TIME_BAR_DAYS[self.options.group_by])  # type: ignore[arg-type]
        return renderer.render_time_line(
            chart,
            days,
            data['count'],
            color=self._color,  # type: ignore[arg-type]
            show_markers=not (self.options.group_by == 'day' and len(data) > Marks.TIME_LINE_MAX_MARKED_DAYS),
        )

    def format_plot(self, plot: Any) -> None:
        format_xy_labels(plot, x_axis_label=self.options.x_axis_label, y_axis_label=self.options.y_axis_label)
        format_ticks(plot, y_grid=True, numeric_y=True)
        self._format_date_axis(plot)

    def _format_date_axis(self, chart: Chart) -> None:
        """Year ticks, month ticks with a year row below, or automatic day ticks."""
        groups = self._aggregated_df['_time_group']
        if self.options.group_by == 'day':
            chart.x.dates, chart.x.date_format = True, '%Y-%m-%d'
            chart.x.rotation = self.options.rotation
            return
        if self.options.group_by == 'month' and self.options.display_month:
            ticks, fmt = groups, '%b'
            chart.x.rotation = 90
            first_of_year = groups.groupby(groups.dt.year).min()
            chart.x.sub_labels = list(zip(to_days(first_of_year), (str(d.year) for d in first_of_year)))
        else:
            ticks, fmt = groups[groups.dt.month == 1], '%Y'
        chart.x.ticks = list(to_days(ticks))
        chart.x.tick_labels = [d.strftime(fmt) for d in ticks]
