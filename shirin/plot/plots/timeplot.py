from typing import Any

import pandas as pd
import matplotlib.dates as mdates

from ..core import renderer
from ..core.base_plot import AbstractPlot
from ..core.options import TimePlotOptions
from ..common.formatting import (
    format_ticks,
    format_xy_labels,
)
from ..config.colors import Colors, TextColors


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

        period = {'year': 'Y', 'month': 'M'}.get(group_by, 'D')
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
                freq={'year': 'YS', 'month': 'MS'}.get(group_by, 'D'),
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
        ax = self._standard_axes()
        if self.options.plot_type == 'bar':
            return renderer.render_time_bars(
                ax, data['_time_group'], data['count'], color=self._color, width=self._get_bar_width()
            )
        return renderer.render_time_line(
            ax,
            data['_time_group'],
            data['count'],
            color=self._color,
            show_markers=not (self.options.group_by == 'day' and len(data) > 25),
        )

    def _get_bar_width(self) -> float:
        """Bar width in days for the grouping."""
        return {'year': 300, 'month': 25}.get(self.options.group_by, 0.8)

    def format_plot(self, plot: Any) -> None:
        format_xy_labels(plot, xlabel=self.options.xlabel, ylabel=self.options.ylabel)
        format_ticks(plot, y_grid=True, numeric_y=True)

        self._format_date_axis(plot)

    def _format_date_axis(self, ax: Any) -> None:
        """Format x-axis with appropriate date labels based on grouping."""
        group_by = self.options.group_by

        if group_by == 'year':
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        elif group_by == 'month':
            if not self.options.display_month:
                ax.xaxis.set_major_locator(mdates.YearLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                ax.tick_params(axis='x', which='major', rotation=0, pad=6)
            else:
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
                ax.tick_params(axis='x', which='major', rotation=90, pad=6)
                self._draw_year_labels(ax)
        else:  # day
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.tick_params(axis='x', labelrotation=self.options.rotation)
            for label in ax.get_xticklabels():
                label.set_horizontalalignment('right')

        ax.figure.tight_layout()

    def _draw_year_labels(self, ax: Any) -> None:
        """Year labels below the month ticks, so multi-year month axes stay readable."""
        years = pd.date_range(
            start=self._aggregated_df['_time_group'].min(),
            end=self._aggregated_df['_time_group'].max(),
            freq='YS',
        )
        # Extra bottom margin to avoid clipping the year row.
        ax.figure.subplots_adjust(bottom=0.30)
        major_lbls = ax.xaxis.get_majorticklabels()
        if major_lbls:
            label_color = major_lbls[0].get_color()
            label_size = major_lbls[0].get_fontsize()
            label_family = major_lbls[0].get_fontfamily()
        else:
            label_color = TextColors.DARK_GREY
            label_size = 9
            label_family = None
        for year in years:
            ax.text(
                year,
                -0.18,
                str(year.year),
                transform=ax.get_xaxis_transform(),
                ha='center',
                va='top',
                fontsize=label_size,
                fontfamily=label_family,
                color=label_color,
            )
