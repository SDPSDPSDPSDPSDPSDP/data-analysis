"""Smoke tests: every public PlotGraphs method renders without raising, plus argument validation."""
import re
from typing import List

import pandas as pd
import pytest

from shirin.plot import PlotGraphs

GROUP_PALETTE = {'group': {'x': '#111111', 'y': '#eeeeee'}}
GROUP_LABELS = {'group': {'x': 'Ex'}}


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


def test_bar_group_by_fills_empty_periods_in_time_order(shown: List[str]) -> None:
    df = pd.DataFrame({'date': pd.to_datetime(['2024-03-02', '2024-01-05', '2024-03-09'])})
    PlotGraphs().bar(df, x='date', group_by='month')
    PlotGraphs().bar(df, x='date', group_by='day')
    month_svg, day_svg = shown
    assert month_svg.index('>Jan</text>') < month_svg.index('>Feb</text>') < month_svg.index('>Mar</text>')
    assert '>2024</text>' in month_svg
    assert day_svg.count('>2024-') <= 12


def test_bar_group_by_rejects_incompatible_options(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match='group_by needs x'):
        PlotGraphs().bar(df, y='date', group_by='month')
    with pytest.raises(ValueError, match='does not work with sort'):
        PlotGraphs().bar(df, x='date', group_by='month', sort='frequency')
    with pytest.raises(ValueError, match='Valid options'):
        PlotGraphs().bar(df, x='date', group_by='week')


def test_bar_compact_labels(shown: List[str]) -> None:
    df = pd.DataFrame({'category': ['a', 'b'], 'value': [1_228_787, 457_435]})
    PlotGraphs().bar(df, y='category', value='value')
    PlotGraphs().bar(df, y='category', value='value', compact_labels=False)
    assert '1,2M' in shown[0] and '457k' in shown[0]
    assert '1.228.787' in shown[1] and '457.435' in shown[1]


DESCRIBED = pd.DataFrame({
    'name': ['v1', 'v2', 'v3'],
    'accuracy': [0.8, 0.86, 0.7],
    'description': ['Baseline', 'Route features', None],
})


def _text_y(svg: str, text: str) -> float:
    match = re.search(rf'<text x="[\d.]+" y="([\d.]+)"[^>]*>{re.escape(text)}</text>', svg)
    assert match, f'{text!r} not in SVG'
    return float(match.group(1))


def test_bar_description_line_under_each_category_label(shown: List[str]) -> None:
    PlotGraphs().bar(DESCRIBED, y='name', value='accuracy', description='description')
    PlotGraphs().bar(DESCRIBED, x='name', value='accuracy', description='description')
    PlotGraphs().bar(DESCRIBED, y='name', value='accuracy', normalized=True, remainder=True, description='description')
    for svg in shown:
        assert _text_y(svg, 'v1') < _text_y(svg, 'Baseline')
        assert _text_y(svg, 'v2') < _text_y(svg, 'Route features')
        assert '>None</text>' not in svg and '>nan</text>' not in svg


def test_bar_description_rejects_bad_input() -> None:
    with pytest.raises(ValueError, match="description='notes' is not a column"):
        PlotGraphs().bar(DESCRIBED, y='name', description='notes')
    conflicting = pd.DataFrame({'name': ['a', 'a'], 'description': ['one', 'two']})
    with pytest.raises(ValueError, match=r"differs for \['a'\]"):
        PlotGraphs().bar(conflicting, y='name', description='description')
    dates = pd.DataFrame({'date': pd.to_datetime(['2024-01-01']), 'description': ['x']})
    with pytest.raises(ValueError, match='descriptions do not work with group_by'):
        PlotGraphs().bar(dates, x='date', group_by='month', description='description')
