"""Regressions on single plot classes: what ends up in the rendered Chart."""
import dataclasses

import pandas as pd
import pytest

from shirin.plot.common.data_conversion import COUNT_COL, fill_missing_values_in_data
from shirin.plot.core import (
    BarPlotOptions,
    CountPlotOptions,
    HistogramOptions,
    NormalizedPlotOptions,
    PiePlotOptions,
    TimePlotOptions,
)
from shirin.plot.plots import BarPlot, CountPlot, Histogram, NormalizedPlot, PieChart, TimePlot
from shirin.plot.svg import to_svg


def test_countplot_data_labels_false_draws_no_labels(df: pd.DataFrame) -> None:
    rendered = CountPlot(CountPlotOptions(df=df, axis_column='category', data_labels=False))
    chart = rendered.render()
    assert len(chart.texts) == 0


def test_pie_without_palette_uses_distinct_colors(df: pd.DataFrame) -> None:
    counts = df['category'].value_counts().to_frame()
    chart = PieChart(PiePlotOptions(df=counts, col='count')).render()
    assert len({wedge.color for wedge in chart.wedges}) == 3


def test_pie_leaves_whitespace_around_wedges(df: pd.DataFrame) -> None:
    counts = df['category'].value_counts().to_frame()
    chart = PieChart(PiePlotOptions(df=counts, col='count')).render()
    assert chart.x.lim[1] > max(wedge.radius for wedge in chart.wedges)


def test_histogram_keeps_fractional_values() -> None:
    df = pd.DataFrame({'x': [0.1, 0.2, 0.5, 0.9, None]})
    chart = Histogram(HistogramOptions(df=df, x='x', bins=10)).render()
    assert len(chart.rects) == 10
    assert sum(rect.height for rect in chart.rects) == 4


def test_histogram_suffix_on_tick_labels() -> None:
    df = pd.DataFrame({'x': [0.5, 1.5, 2.5]})
    chart = Histogram(HistogramOptions(df=df, x='x', bins=3, suffix='%')).render()
    assert chart.x.formatter(10) == '10 %'


def test_histogram_bars_round_and_stacks_are_clipped_segments() -> None:
    df = pd.DataFrame({'x': [1, 1, 2, 3], 'hue': ['a', 'b', 'a', 'b']})
    plain = Histogram(HistogramOptions(df=df, x='x', bins=3)).render()
    assert all(rect.rounded and rect.clip is None for rect in plain.rects)
    palette = {'a': '#111111', 'b': '#eeeeee'}
    stacked = Histogram(HistogramOptions(df=df, x='x', bins=3, hue='hue', palette=palette)).render()
    # Segments must not overlap: a full back pill bleeds through the front pill's anti-aliased edges.
    assert all(rect.clip is not None and rect.clip.rounded for rect in stacked.rects)
    bottom, top = stacked.rects[:3], stacked.rects[3:]
    assert [r.color for r in bottom + top] == ['#111111'] * 3 + ['#eeeeee'] * 3
    assert [r.height for r in bottom] == [1, 1, 0] and [r.height for r in top] == [1, 0, 1]
    assert [r.y0 for r in top] == [1, 1, 0]


def test_stacked_barplot_sums_duplicate_rows() -> None:
    df = pd.DataFrame({'cat': ['A', 'A', 'B'], 'hue': ['x', 'x', 'y'], 'v': [1, 2, 3]})
    options = BarPlotOptions(
        df=df, axis_column='cat', value='v', hue='hue', stacked=True,
        palette={'x': '#111111', 'y': '#eeeeee'},
    )
    chart = BarPlot(options).render()
    assert max(rect.height for rect in chart.rects) == 3


def test_stacked_without_dict_palette_raises(df: pd.DataFrame) -> None:
    options = CountPlotOptions(df=df, axis_column='category', hue='group', stacked=True, palette='#123456')
    with pytest.raises(ValueError, match="palette must be a dictionary"):
        CountPlot(options).render()


def test_render_does_not_mutate_caller_options(df: pd.DataFrame) -> None:
    options = CountPlotOptions(df=df, axis_column='category', hue='group', palette={'x': '#111111', 'y': '#eeeeee'})
    before = dataclasses.replace(options)
    CountPlot(options).render()
    assert options.palette == before.palette
    assert options.label_map is None


@pytest.mark.parametrize("palette", [None, '#123456'])
def test_hue_without_dict_palette_gets_one_color_per_hue_value(df: pd.DataFrame, palette) -> None:
    options = CountPlotOptions(df=df, axis_column='category', hue='group', palette=palette)
    rendered = CountPlot(options)
    chart = rendered.render()
    assert rendered._color is None
    assert len(set(rendered._palette.values())) == 2
    assert len({rect.color for rect in chart.rects}) == 2


def test_countplot_counts_per_category_and_hue() -> None:
    df = pd.DataFrame({'cat': ['A', 'A', 'A', 'B'], 'hue': ['x', 'x', 'y', 'y']})
    chart = CountPlot(CountPlotOptions(df=df, axis_column='cat', hue='hue', palette={'x': '#111111', 'y': '#eeeeee'})).render()
    heights = sorted(rect.height for rect in chart.rects if rect.height > 0)
    assert heights == [1, 1, 2]
    assert chart.x.tick_labels == ['A', 'B']


def test_barplot_sums_per_category() -> None:
    df = pd.DataFrame({'cat': ['A', 'A', 'B'], 'v': [1.0, 3.0, 5.0]})
    chart = BarPlot(BarPlotOptions(df=df, axis_column='cat', value='v', orientation='horizontal')).render()
    assert sorted(rect.width for rect in chart.rects) == [4.0, 5.0]
    assert chart.y.lim[0] > chart.y.lim[1]  # first category on top


def test_unknown_column_raises_clear_error(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="hue='missing' is not a column"):
        CountPlot(CountPlotOptions(df=df, axis_column='category', hue='missing')).render()


def test_stacked_and_normalized_without_palette_use_default_colors(df: pd.DataFrame) -> None:
    CountPlot(CountPlotOptions(df=df, axis_column='category', hue='group', stacked=True)).render()
    NormalizedPlot(NormalizedPlotOptions(df=df, axis_column='category', hue='group')).render()


def test_missing_palette_key_raises_key_error(df: pd.DataFrame) -> None:
    counts = df['category'].value_counts().to_frame()
    with pytest.raises(KeyError, match="Palette missing keys"):
        PieChart(PiePlotOptions(df=counts, col='count', palette={'A': '#111111'})).render()


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
