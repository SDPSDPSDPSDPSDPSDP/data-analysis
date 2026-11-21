"""Figure size and period axis shared by the categorical bar plots."""

import math

import pandas as pd

from ..common.formatting import format_period_ticks
from ..config import FigureSize, Layout
from ..core.base_plot import AbstractPlot
from ..core.categorical_options import CategoricalPlotOptions
from ..svg import Chart


def calculate_figsize(options: CategoricalPlotOptions, data: pd.DataFrame) -> tuple[float, float]:
    """(figure width, plot height) in inches; vertical width grows with the category count."""
    n_categories = data[options.axis_column].nunique()
    if options.orientation == "vertical":
        width = n_categories * FigureSize.CATEGORY_SLOT + FigureSize.CATEGORY_MARGIN
        # Long time series get thinner bars instead of an ever wider figure.
        return (min(width, FigureSize.WIDTH) if options.group_by else width, FigureSize.PLOT_HEIGHT)
    return (FigureSize.HORIZONTAL_WIDTH, n_categories * FigureSize.BAR_ROW)


def create_sized_figure(plot: AbstractPlot, data: pd.DataFrame) -> Chart:
    return plot._new_chart(*calculate_figsize(plot.options, data))  # type: ignore[arg-type]


def format_period_axis(chart: Chart, options: CategoricalPlotOptions) -> None:
    """Date period categories: month ticks with a year row below, or every nth day."""
    if options.group_by == "month":
        periods = pd.Series(pd.to_datetime(chart.x.tick_labels))
        format_period_ticks(chart, periods, pd.Series(chart.x.ticks), months=True)
    elif options.group_by == "day":
        ticks, labels = chart.x.ticks, chart.x.tick_labels
        assert ticks is not None and labels is not None, "category axis sets ticks before period formatting"
        step = math.ceil(len(ticks) / Layout.MAX_DAY_TICKS)
        chart.x.ticks, chart.x.tick_labels = ticks[::step], labels[::step]
