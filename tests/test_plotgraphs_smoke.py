"""Smoke tests: every public PlotGraphs method renders without raising, plus regressions."""
import dataclasses

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from shirin.plot import PlotGraphs
from shirin.plot.core import BarPlotOptions, CountPlotOptions, HistogramOptions, PiePlotOptions
from shirin.plot.plots import create_plot


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


@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive")
def test_every_method_renders(plot: PlotGraphs, df: pd.DataFrame) -> None:
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
    assert plt.get_fignums() == []  # exporter closes every figure


def test_countplot_show_labels_false_draws_no_labels(df: pd.DataFrame) -> None:
    rendered = create_plot('count', CountPlotOptions(df=df, axis_column='category', show_labels=False))
    ax = rendered.render()
    assert len(ax.texts) == 0


def test_pie_without_palette_uses_distinct_colors(df: pd.DataFrame) -> None:
    counts = df['category'].value_counts().to_frame()
    rendered = create_plot('pie', PiePlotOptions(df=counts, col='count'))
    rendered.render()
    assert len(set(rendered._colors)) == 3


def test_histogram_keeps_fractional_values() -> None:
    df = pd.DataFrame({'x': [0.1, 0.2, 0.5, 0.9, None]})
    rendered = create_plot('histogram', HistogramOptions(df=df, x='x', bins=10))
    rendered.render()
    assert rendered._bins == 10
    assert rendered._preprocessed_df['x'].tolist() == [0.1, 0.2, 0.5, 0.9]


def test_stacked_barplot_sums_duplicate_rows() -> None:
    df = pd.DataFrame({'cat': ['A', 'A', 'B'], 'hue': ['x', 'x', 'y'], 'v': [1, 2, 3]})
    options = BarPlotOptions(
        df=df, axis_column='cat', value='v', hue='hue', stacked=True,
        palette={'x': '#111111', 'y': '#eeeeee'},
    )
    rendered = create_plot('bar', options)
    rendered.render()
    assert rendered._df_unlabeled.loc['A', 'x'] == 3


def test_stacked_without_dict_palette_raises(df: pd.DataFrame) -> None:
    options = CountPlotOptions(df=df, axis_column='category', hue='group', stacked=True, palette='#123456')
    with pytest.raises(ValueError, match="palette must be a dictionary"):
        create_plot('count', options).render()


def test_render_does_not_mutate_caller_options(df: pd.DataFrame) -> None:
    options = CountPlotOptions(df=df, axis_column='category', hue='group', palette={'x': '#111111', 'y': '#eeeeee'})
    before = dataclasses.replace(options)
    create_plot('count', options).render()
    assert options.palette == before.palette
    assert options.label_map is None
