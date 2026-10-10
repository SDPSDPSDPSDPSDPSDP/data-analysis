"""Regressions on single plot classes: what ends up in the rendered Chart."""
import dataclasses

import pandas as pd
import pytest

from shirin.plot.common.data_conversion import fill_missing_values_in_data
from shirin.plot.core import (
    BarPlotOptions,
    CountPlotOptions,
    HistogramOptions,
    NormalizedPlotOptions,
    PiePlotOptions,
)
from shirin.plot.plots import BarPlot, CountPlot, Histogram, NormalizedPlot, PieChart


def test_countplot_data_labels_false_draws_no_labels(df: pd.DataFrame) -> None:
    rendered = CountPlot(CountPlotOptions(df=df, axis_column='category', data_labels=False))
    chart = rendered.render()
    assert len(chart.texts) == 0


def test_pie_without_palette_uses_distinct_colors(df: pd.DataFrame) -> None:
    counts = df['category'].value_counts().to_frame()
    chart = PieChart(PiePlotOptions(df=counts, col='count')).render()
    assert len({wedge.color for wedge in chart.wedges}) == 3


def test_histogram_keeps_fractional_values() -> None:
    df = pd.DataFrame({'x': [0.1, 0.2, 0.5, 0.9, None]})
    chart = Histogram(HistogramOptions(df=df, x='x', bins=10)).render()
    assert len(chart.rects) == 10
    assert sum(rect.height for rect in chart.rects) == 4


def test_histogram_suffix_on_tick_labels() -> None:
    df = pd.DataFrame({'x': [0.5, 1.5, 2.5]})
    chart = Histogram(HistogramOptions(df=df, x='x', bins=3, suffix='%')).render()
    assert chart.x.formatter(10) == '10 %'


def test_histogram_bars_round_and_stacks_overlap_as_pills() -> None:
    df = pd.DataFrame({'x': [1, 1, 2, 3], 'hue': ['a', 'b', 'a', 'b']})
    plain = Histogram(HistogramOptions(df=df, x='x', bins=3)).render()
    assert all(rect.rounded and rect.clip is None for rect in plain.rects)
    palette = {'a': '#111111', 'b': '#eeeeee'}
    stacked = Histogram(HistogramOptions(df=df, x='x', bins=3, hue='hue', palette=palette)).render()
    assert all(rect.rounded and rect.clip is None and rect.fade_to is None for rect in stacked.rects)
    back, front = stacked.rects[:3], stacked.rects[3:]
    assert [r.color for r in back + front] == ['#eeeeee'] * 3 + ['#111111'] * 3
    assert [r.height for r in back] == [2, 1, 1] and [r.height for r in front] == [1, 1, 0]


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
