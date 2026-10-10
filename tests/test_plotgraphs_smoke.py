"""Smoke tests: every public PlotGraphs method renders without raising, plus regressions."""
import dataclasses
from typing import List

import pandas as pd
import pytest

from shirin.plot import PlotGraphs
from shirin.plot.common.data_conversion import fill_missing_values_in_data
from shirin.plot.core import (
    AccuracyPlotOptions,
    BarPlotOptions,
    CountPlotOptions,
    HistogramOptions,
    NormalizedCountPlotOptions,
    PiePlotOptions,
)
from shirin.plot.plots import BarPlot, CountPlot, Histogram, NormalizedCountPlot, PieChart


@pytest.fixture
def df() -> pd.DataFrame:
    return pd.DataFrame({
        'category': ['A', 'A', 'B', 'B', 'C', 'C'],
        'group': ['x', 'y', 'x', 'y', 'x', 'x'],
        'value': [1.5, 2.0, 3.0, 4.0, 5.0, 0.5],
        'date': pd.date_range('2023-01-01', periods=6, freq='35D'),
    })


@pytest.fixture
def plot() -> PlotGraphs:
    return PlotGraphs()


def test_every_method_renders(plot: PlotGraphs, df: pd.DataFrame, shown: List[str]) -> None:
    palette = {'x': '#111111', 'y': '#eeeeee'}
    plot.countplot_x(df, x='category')
    plot.countplot_y(df, y='category', hue='group', palette=palette, stacked=True, stacked_labels='standard')
    plot.countplot_x(df, x='category', hue='group', palette=palette, normalized=True)
    plot.barplot_x(df, x='category', value='value')
    plot.barplot_y(df, y='category', value='value', hue='group', palette=palette, stacked=True)
    plot.histogram(df, x='value')
    plot.lineplot(df, x='date', y='value', hue='group')
    plot.scatterplot(df, x='value', y='value')
    plot.pie(df, col='category')
    plot.timeplot(df, x='date', group_by='month')
    plot.timeplot(df, x='date', group_by='day', plot_type='line', rotation=45)
    plot.accuracy(pd.DataFrame({'run': ['a', 'b'], 'acc': [0.7, 0.9]}), experiment='run', accuracy='acc', reverse_order=True)
    assert len(shown) == 12
    assert all(svg.startswith('<svg') for svg in shown)


def test_countplot_show_labels_false_draws_no_labels(df: pd.DataFrame) -> None:
    rendered = CountPlot(CountPlotOptions(df=df, axis_column='category', show_labels=False))
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


def test_barplot_uses_mean_per_category() -> None:
    df = pd.DataFrame({'cat': ['A', 'A', 'B'], 'v': [1.0, 3.0, 5.0]})
    chart = BarPlot(BarPlotOptions(df=df, axis_column='cat', value='v', orientation='horizontal')).render()
    assert sorted(rect.width for rect in chart.rects) == [2.0, 5.0]
    assert chart.y.lim[0] > chart.y.lim[1]  # first category on top


def test_title_and_mapped_legend_render(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs(font='satoshi').countplot_x(df, x='category', hue='group', title='Totals', label_map={'x': 'Ex'})
    assert '>Totals</text>' in shown[0]
    assert '>Ex</text>' in shown[0]
    assert '@font-face' in shown[0]


def test_hidden_legend(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs().countplot_x(df, x='category', hue='group', plot_legend=False)
    assert '>x</text>' not in shown[0]


def test_unknown_font_raises() -> None:
    with pytest.raises(ValueError, match="Unknown font"):
        PlotGraphs(font='comic sans')


def test_unknown_column_raises_clear_error(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="hue='missing' is not a column"):
        CountPlot(CountPlotOptions(df=df, axis_column='category', hue='missing')).render()


def test_stacked_and_normalized_without_palette_use_default_colors(df: pd.DataFrame) -> None:
    CountPlot(CountPlotOptions(df=df, axis_column='category', hue='group', stacked=True)).render()
    NormalizedCountPlot(NormalizedCountPlotOptions(df=df, axis_column='category', hue='group')).render()


def test_missing_palette_key_raises_key_error(df: pd.DataFrame) -> None:
    counts = df['category'].value_counts().to_frame()
    with pytest.raises(KeyError, match="Palette missing keys"):
        PieChart(PiePlotOptions(df=counts, col='count', palette={'A': '#111111'})).render()


def test_accuracy_outside_unit_interval_raises() -> None:
    options = AccuracyPlotOptions(df=pd.DataFrame({'run': ['a'], 'acc': [78]}), axis_column='run', value_column='acc')
    with pytest.raises(ValueError, match=r"fractions in \[0, 1\]"):
        options.validate()


def test_pie_on_column_named_count(plot: PlotGraphs) -> None:
    plot.pie(pd.DataFrame({'count': ['a', 'b', 'b']}), col='count')


def test_shift_fill_interpolates_in_x_order() -> None:
    df = pd.DataFrame({'x': [3, 1, 2], 'y': [30.0, 10.0, None]})
    filled = fill_missing_values_in_data(df, 'x', 'y', hue=None, fill_method='shift')
    assert filled.set_index('x').loc[2, 'y'] == 20.0
