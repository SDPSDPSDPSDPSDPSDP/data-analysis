import numpy as np
import pandas as pd
import pytest

from shirin.plot.core import LinePlotOptions
from shirin.plot.plots import LinePlot


def _curve() -> pd.DataFrame:
    return pd.DataFrame({
        'coverage': [1.0, 0.8, 0.6, 0.4],
        'accuracy': [0.86, 0.93, 0.98, 0.99],
        'threshold': [0.0, np.nan, 0.9, np.nan],
    })


def _render(df: pd.DataFrame, **options):
    return LinePlot(LinePlotOptions(df=df, x='coverage', y='accuracy', **options)).render()


def test_line_sorted_by_x() -> None:
    chart = _render(_curve())

    assert len(chart.lines) == 1
    assert chart.lines[0].xs == [0.4, 0.6, 0.8, 1.0]
    assert chart.x.grid and chart.y.grid


def test_labels_mark_only_labelled_points() -> None:
    chart = _render(_curve(), labels='threshold')

    assert [(t.x, t.y, t.text) for t in chart.texts] == [(1.0, 0.86, '0'), (0.6, 0.98, '0,9')]
    assert chart.dots[0].xs == [1.0, 0.6]
    assert chart.dots[0].color == chart.lines[0].color


def test_labels_keep_hue_colors() -> None:
    df = pd.concat([_curve().assign(model='a'), _curve().assign(model='b')])
    chart = _render(df, hue='model', labels='threshold', legend=True)

    assert [dots.color for dots in chart.dots] == [line.color for line in chart.lines]
    assert [label for _, label, _ in chart.legend] == ['a', 'b']


def test_limits_and_percentage_ticks() -> None:
    chart = _render(_curve(), x_limits=(1, 0), y_limits=(0.84, 1), percentage_x=True, percentage_y=True)

    assert chart.x.lim == (1, 0)
    assert chart.y.lim == (0.84, 1)
    assert chart.x.formatter(0.25) == '25%'
    assert chart.y.formatter(0.9) == '90%'


def test_non_numeric_x_raises() -> None:
    df = pd.DataFrame({'coverage': ['a', 'b'], 'accuracy': [1, 2]})

    with pytest.raises(ValueError, match='must be numeric'):
        _render(df)


def test_equal_limits_raise() -> None:
    with pytest.raises(ValueError, match='x_limits must be two different numbers'):
        _render(_curve(), x_limits=(1, 1))


def test_plotgraphs_line_renders_svg(plot, shown) -> None:
    plot.line(_curve(), x='coverage', y='accuracy', labels='threshold', x_limits=(1, 0), title='Curve')

    assert len(shown) == 1
    assert '0,9' in shown[0]
