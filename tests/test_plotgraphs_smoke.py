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
    plot.time(df, x='date', y='value', hue='group')
    plot.scatter(df, x='value', y='value')
    plot.pie(df, col='category')
    plot.time(df, x='date', group_by='month')
    plot.time(df, x='date', group_by='day', rotation=45)
    plot.time(df, x='date', y='value', hue='group', group_by='year', cumulative=True)
    assert len(shown) == 12
    assert all(svg.startswith('<svg') for svg in shown)


def test_dark_mode_draws_charts_without_hue_white(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs().bar(df, x='category')
    PlotGraphs(dark_mode=True).bar(df, x='category')
    light, dark = shown
    assert 'fill="#d6dde6"' in light and 'fill="#d6dde6"' not in dark
    assert 'fill="#ffffff"' in dark


def test_dark_mode_draws_scatter_and_time_without_hue_white(df: pd.DataFrame, shown: List[str]) -> None:
    PlotGraphs(dark_mode=True).scatter(df, x='value', y='value')
    PlotGraphs(dark_mode=True).time(df, x='date', y='value')
    for svg in shown:
        assert '"#000000"' not in svg
        assert '"#ffffff"' in svg


def test_dark_mode_draws_grey_palette_entries_white(df: pd.DataFrame, shown: List[str]) -> None:
    palette = {'group': {'x': '#D6DDE6', 'y': '#111111'}}
    PlotGraphs(palette=palette).bar(df, x='category', hue='group')
    PlotGraphs(palette=palette, dark_mode=True).bar(df, x='category', hue='group')
    light, dark = (svg.lower() for svg in shown)
    assert '"#d6dde6"' in light and '"#d6dde6"' not in dark
    assert '"#111111"' in dark


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


def test_empty_filters_raise_named_errors(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match='top_n must be at least 1'):
        PlotGraphs().bar(df, x='category', top_n=0)
    with pytest.raises(ValueError, match='xlimit=-1000 leaves no'):
        PlotGraphs().histogram(df, x='value', xlimit=-1000)


def test_named_palette_color_raises_up_front() -> None:
    with pytest.raises(ValueError, match=r"palette\['fruit'\]"):
        PlotGraphs(palette={'fruit': {'Apple': 'red'}})


def test_pie_unknown_column_raises_clear_error(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="col='nope' is not a column"):
        PlotGraphs().pie(df, col='nope')
