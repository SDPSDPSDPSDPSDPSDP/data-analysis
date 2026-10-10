"""Smoke tests: every public PlotGraphs method renders without raising, plus argument validation."""
from typing import List

import pandas as pd
import pytest

from shirin.plot import PlotGraphs

GROUP_PALETTE = {'group': {'x': '#111111', 'y': '#eeeeee'}}
GROUP_LABELS = {'group': {'x': 'Ex'}}


def test_every_method_renders(df: pd.DataFrame, shown: List[str]) -> None:
    plot = PlotGraphs(palette=GROUP_PALETTE)
    plot.bar(df, x='category')
    plot.bar(df, y='category', hue='group', stacked=True)
    plot.bar(df, x='category', hue='group', normalized=True)
    plot.bar(df, x='category', value='value')
    plot.bar(df, y='category', value='value', hue='group', stacked=True)
    plot.histogram(df, x='value')
    plot.lineplot(df, x='date', y='value', hue='group')
    plot.scatterplot(df, x='value', y='value')
    plot.pie(df, col='category')
    plot.timeplot(df, x='date', group_by='month')
    plot.timeplot(df, x='date', group_by='day', plot_type='line', rotation=45)
    assert len(shown) == 11
    assert all(svg.startswith('<svg') for svg in shown)


def test_title_and_mapped_legend_render(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs(font='satoshi', label_mapping=GROUP_LABELS).bar(
        df, x='category', hue='group', title='Totals', legend=True
    )
    assert '>Totals</text>' in shown[0]
    assert '>Ex</text>' in shown[0]
    assert '@font-face' in shown[0]


def test_hidden_legend(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs().bar(df, x='category', hue='group')
    assert '>x</text>' not in shown[0]


def test_bad_palette_config_raises() -> None:
    with pytest.raises(TypeError, match="palette must be a dict"):
        PlotGraphs(palette=['#111111'])
    with pytest.raises(TypeError, match=r"label_mapping\['group'\] must be a dict"):
        PlotGraphs(label_mapping={'group': 'Ex'})


def test_unknown_font_raises() -> None:
    with pytest.raises(ValueError, match="Unknown font"):
        PlotGraphs(font='comic sans')


def test_pie_on_column_named_count(plot: PlotGraphs) -> None:
    plot.pie(pd.DataFrame({'count': ['a', 'b', 'b']}), col='count')


def test_title_list_adds_subtitle(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs().bar(df, x='category', title=['Totals', 'Per category'])
    assert '>Totals</text>' in shown[0]
    assert '>Per category</text>' in shown[0]
    with pytest.raises(ValueError, match='title must be'):
        PlotGraphs().bar(df, x='category', title=['a', 'b', 'c'])


def test_countplot_direction_from_x_or_y(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs().bar(df, y='category')
    PlotGraphs().bar(df, y='category', x_axis_label='')
    assert '>Count</text>' in shown[0]
    assert '>Count</text>' not in shown[1]
    with pytest.raises(ValueError, match='exactly one of x or y'):
        PlotGraphs().bar(df, x='category', y='category')
    with pytest.raises(ValueError, match='exactly one of x or y'):
        PlotGraphs().bar(df)


def test_barplot_needs_exactly_one_of_x_or_y(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match='exactly one of x or y'):
        PlotGraphs().bar(df, x='category', y='category', value='value')
    with pytest.raises(ValueError, match='exactly one of x or y'):
        PlotGraphs().bar(df, value='value')


def test_bar_rejects_options_of_the_other_mode(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match='remainder needs value'):
        PlotGraphs().bar(df, x='category', normalized=True, remainder=True)
    with pytest.raises(ValueError, match='top_n only works without value'):
        PlotGraphs().bar(df, x='category', value='value', top_n=2)
