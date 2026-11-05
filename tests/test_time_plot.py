"""TimePlot regressions: what ends up in the rendered Chart."""

import pandas as pd

from shirin.plot.common.data_conversion import COUNT_COL, fill_missing_values_in_data
from shirin.plot.core import (
    TimePlotOptions,
)
from shirin.plot.plots import TimePlot
from shirin.plot.svg import to_svg


def test_shift_fill_interpolates_in_x_order() -> None:
    df = pd.DataFrame({'x': [3, 1, 2], 'y': [30.0, 10.0, None]})
    filled = fill_missing_values_in_data(df, 'x', 'y', hue=None, fill_method='shift')
    assert filled.set_index('x').loc[2, 'y'] == 20.0


def test_time_counts_per_period_with_zero_gaps_and_cumulative() -> None:
    df = pd.DataFrame({
        'date': pd.to_datetime(['2024-01-05', '2024-01-20', '2024-03-02', '2024-03-09']),
        'shop': ['a', 'b', 'a', 'a'],
    })
    plot = TimePlot(TimePlotOptions(df=df, x='date', hue='shop', group_by='month', cumulative=True))
    plot.options.validate()
    data = plot.transform(plot.preprocess()).set_index(['date', 'shop'])[COUNT_COL]
    assert data['2024-01-01', 'a'] == 1
    assert data['2024-02-01', 'a'] == 1  # empty February counts as zero
    assert data['2024-03-01', 'a'] == 3
    assert data['2024-03-01', 'b'] == 1


def test_time_long_monthly_axis_thins_month_ticks() -> None:
    df = pd.DataFrame({'date': pd.date_range('2018-01-01', '2023-12-01', freq='MS')})
    chart = TimePlot(TimePlotOptions(df=df, x='date', group_by='month')).render()
    assert chart.x.tick_labels[:3] == ['Jan', 'Apr', 'Jul']
    assert len(chart.x.sub_labels) == 6


def test_time_lines_have_no_point_markers() -> None:
    df = pd.DataFrame({'year': [2000, 2001, 2002], 'n': [1, 2, 3]})
    chart = TimePlot(TimePlotOptions(df=df, x='year', y='n')).render()
    assert chart.lines and not chart.dots
    assert '<circle' not in to_svg(chart)
