import numpy as np
import pandas as pd
import pytest

from shirin.plot.config import FontSizes
from shirin.plot.config.theme import Theme
from shirin.plot.core import LinePlotOptions
from shirin.plot.plots import LinePlot
from shirin.plot.svg.frame import layout


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


def test_flipped_x_axis_keeps_tick_labels() -> None:
    chart = _render(_curve(), x_limits=(1, 0), percentage_x=True)

    labels = [label for _, label in layout(chart, Theme(False).color).x_ticks if label]

    assert labels == ['0%', '20%', '40%', '60%', '80%', '100%']


def test_label_values_keep_only_listed_labels() -> None:
    df = pd.DataFrame({
        'coverage': [1.0, 0.8, 0.6, 0.4],
        'accuracy': [0.86, 0.93, 0.98, 0.99],
        'threshold': [0.5, 0.8, 0.9, 0.95],
    })

    chart = _render(df, labels='threshold', label_values=[0.5, 0.9])

    assert [t.text for t in chart.texts] == ['0,5', '0,9']
    assert chart.dots[0].xs == [1.0, 0.6]


def test_label_values_not_in_labels_raise() -> None:
    with pytest.raises(ValueError, match=r'label_values \[0.42\] not found'):
        _render(_curve(), labels='threshold', label_values=[0.9, 0.42])


def test_label_values_without_labels_raise() -> None:
    with pytest.raises(ValueError, match='label_values needs labels'):
        _render(_curve(), label_values=[0.9])


def test_axis_label_list_adds_sublabel(plot, shown) -> None:
    plot.line(
        _curve(), x='coverage', y='accuracy',
        x_axis_label=['Coverage', 'share of docs at or above the threshold'], y_axis_label=['Accuracy', 'above it'],
    )

    assert 'Coverage' in shown[0]
    assert 'share of docs at or above the threshold' in shown[0]
    assert 'above it' in shown[0]


def test_axis_label_list_of_three_raises() -> None:
    with pytest.raises(ValueError, match='x_axis_label must be a str'):
        _render(_curve(), x_axis_label=['a', 'b', 'c'])


def test_point_labels_larger_than_bar_data_labels() -> None:
    chart = _render(_curve(), labels='threshold')

    assert all(t.size == FontSizes.POINT_LABELS > FontSizes.DATALABELS for t in chart.texts)


def _placed_label_va(**options) -> str:
    chart = _render(_curve(), labels='threshold', label_values=[0.9], **options)
    return layout(chart, Theme(False).color).texts[0].va


def test_point_label_above_falling_line() -> None:
    assert _placed_label_va() == 'bottom'


def test_point_label_below_line_rising_on_flipped_axis() -> None:
    assert _placed_label_va(x_limits=(1, 0)) == 'top'
