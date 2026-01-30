from typing import Any

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

from ..core.base_plot import AbstractPlot
from ..core.options import TimePlotOptions
from ..common.formatting import (
    format_ticks,
    format_xy_labels,
)


class TimePlot(AbstractPlot):
    def __init__(self, options: TimePlotOptions, renderer=None):
        super().__init__(options, renderer)
        self.options: TimePlotOptions = options
        self._aggregated_df: pd.DataFrame = pd.DataFrame()
    
    def preprocess(self) -> pd.DataFrame:
        df = self.options.df.copy()
        date_col = self.options.x
        
        # Ensure the column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col])
        
        # Validate that conversion was successful
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            raise ValueError(f"Column '{date_col}' could not be converted to datetime")
        
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        group_by = self.options.group_by
        date_col = self.options.x
        
        # Get datetime series with proper type for accessor
        datetime_series = pd.to_datetime(df[date_col])
        
        if group_by == 'year':
            df['_time_group'] = datetime_series.dt.to_period('Y').dt.to_timestamp()
        elif group_by == 'month':
            df['_time_group'] = datetime_series.dt.to_period('M').dt.to_timestamp()
        else:  # day
            df['_time_group'] = datetime_series.dt.to_period('D').dt.to_timestamp()
        
        # Count occurrences per time group
        self._aggregated_df = (
            df.groupby('_time_group')
            .size()
            .reset_index(name='count')
            .sort_values('_time_group')
        )
        
        return self._aggregated_df
    
    def draw(self, data: pd.DataFrame) -> Any:
        from ..config import FigureSize
        self.renderer.create_figure((FigureSize.WIDTH, FigureSize.STANDARD_HEIGHT))
        
        ax = plt.gca()
        
        ax.bar(
            data['_time_group'],
            data['count'],
            color='steelblue',
            edgecolor='none',
            alpha=1,
            width=self._get_bar_width()
        )
        
        return ax
    
    def _get_bar_width(self) -> float:
        """Get appropriate bar width based on grouping."""
        group_by = self.options.group_by
        if group_by == 'year':
            return 300  # ~300 days width for yearly bars
        elif group_by == 'month':
            return 25   # ~25 days width for monthly bars
        else:  # day
            return 0.8  # ~0.8 days width for daily bars
    
    def format_plot(self, plot: Any) -> None:
        format_xy_labels(plot, xlabel=self.options.xlabel, ylabel=self.options.ylabel)
        format_ticks(plot, y_grid=True, numeric_y=True)
        
        # Format x-axis based on grouping
        self._format_date_axis(plot)
    
    def _format_date_axis(self, ax: Any) -> None:
        """Format x-axis with appropriate date labels based on grouping."""
        group_by = self.options.group_by
        
        if group_by == 'year':
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        elif group_by == 'month':
            # Show month names for each tick, but include the year only on January
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            def month_fmt(x, pos=None):
                dt = mdates.num2date(x)
                if dt.month == 1:
                    return dt.strftime('%b\n%Y')
                return dt.strftime('%b')
            ax.xaxis.set_major_formatter(FuncFormatter(month_fmt))
            plt.xticks(rotation=90, ha='right')
        else:  # day
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
