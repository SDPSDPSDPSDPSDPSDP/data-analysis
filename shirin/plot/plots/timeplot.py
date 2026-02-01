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
from ..config.colors import Colors, TextColors


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

        # Ensure continuity on the x-axis by including empty periods with zero counts
        if not self._aggregated_df.empty:
            start = self._aggregated_df['_time_group'].min()
            end = self._aggregated_df['_time_group'].max()
            if group_by == 'year':
                full_range = pd.date_range(start=start, end=end, freq='YS')
            elif group_by == 'month':
                full_range = pd.date_range(start=start, end=end, freq='MS')
            else:  # day
                full_range = pd.date_range(start=start, end=end, freq='D')

            full_df = pd.DataFrame({'_time_group': full_range})
            self._aggregated_df = (
                full_df.merge(self._aggregated_df, on='_time_group', how='left')
                .fillna({'count': 0})
            )
            # ensure integer counts
            self._aggregated_df['count'] = self._aggregated_df['count'].astype(int)
        
        # Calculate cumulative values if requested
        if self.options.cumulative:
            self._aggregated_df['count'] = self._aggregated_df['count'].cumsum()
        
        return self._aggregated_df
    
    def draw(self, data: pd.DataFrame) -> Any:
        from ..config import FigureSize
        self.renderer.create_figure((FigureSize.WIDTH, FigureSize.STANDARD_HEIGHT))
        
        ax = plt.gca()
        plot_type = getattr(self.options, 'plot_type', 'bar')

        if plot_type == 'bar':
            ax.bar(
                data['_time_group'],
                data['count'],
                color=Colors.GREY,
                edgecolor='none',
                alpha=1,
                width=self._get_bar_width()
            )
        else:  # line
            # Determine if we should show markers based on number of data points
            show_markers = True
            if self.options.group_by == 'day' and len(data) > 25:
                show_markers = False
            
            marker = 'o' if show_markers else None
            markersize = 3 if show_markers else 0
            
            ax.plot(
                data['_time_group'],
                data['count'],
                color=Colors.BLACK,
                linewidth=2,
                marker=marker,
                markersize=markersize,
                markerfacecolor=Colors.BLACK,
                markeredgecolor=Colors.BLACK,
                markeredgewidth=0,
                alpha=0.9,
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
            if not getattr(self.options, 'display_month', True):
                # Hide months: show only year labels as major ticks
                ax.xaxis.set_major_locator(mdates.YearLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                ax.tick_params(axis='x', which='major', rotation=0, pad=6)
            else:
                # Major ticks: months (short month names)
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
                # Rotate month labels 90° and add padding
                ax.tick_params(axis='x', which='major', rotation=90, pad=6)

                # Manually draw year labels below the months to ensure visibility
                try:
                    start = self._aggregated_df['_time_group'].min()
                    end = self._aggregated_df['_time_group'].max()
                    years = pd.date_range(start=start, end=end, freq='YS')
                    # Add a bit more bottom margin to avoid clipping
                    ax.figure.subplots_adjust(bottom=0.30)
                    for y in years:
                        # Match year label style to major tick labels
                        try:
                            major_lbls = ax.xaxis.get_majorticklabels()
                            if major_lbls:
                                label_color = major_lbls[0].get_color()
                                label_size = major_lbls[0].get_fontsize()
                                label_family = major_lbls[0].get_fontfamily()
                            else:
                                label_color = TextColors.DARK_GREY
                                label_size = 9
                                label_family = None
                        except Exception:
                            label_color = TextColors.DARK_GREY
                            label_size = 9
                            label_family = None

                        ax.text(
                            y,
                            -0.18,
                            str(y.year),
                            transform=ax.get_xaxis_transform(),
                            ha='center',
                            va='top',
                            fontsize=label_size,
                            fontfamily=label_family,
                            color=label_color,
                        )
                except Exception:
                    pass
        else:  # day
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.xticks(rotation=self.options.rotation, ha='right')
        
        plt.tight_layout()
