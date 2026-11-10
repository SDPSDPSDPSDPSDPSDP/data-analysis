import re

import numpy as np
import pandas as pd
import pytest

from shirin.plot.config import FontSizes, Marks
from shirin.plot.config.theme import Theme
from shirin.plot.core import LinePlotOptions
from shirin.plot.plots import LinePlot
from shirin.plot.svg import to_svg
from shirin.plot.svg.frame import layout


def _curve() -> pd.DataFrame:
    return pd.DataFrame({
        'coverage': [1.0, 0.8, 0.6, 0.4],
        'accuracy': [0.86, 0.93, 0.98, 0.99],
        'marked': [True, False, True, False],
    })


def _render(df: pd.DataFrame, **options):
    return LinePlot(LinePlotOptions(df=df, x='coverage', y='accuracy', **options)).render()


def test_line_sorted_by_x() -> None:
    chart = _render(_curve())

    assert len(chart.lines) == 1
    assert chart.lines[0].xs == [0.4, 0.6, 0.8, 1.0]
    assert chart.x.grid and chart.y.grid


def test_marks_dot_only_true_rows_labelled_with_y() -> None:
    chart = _render(_curve(), marks='marked')

    assert [(t.x, t.y, t.text) for t in chart.texts] == [(1.0, 0.86, '0,86'), (0.6, 0.98, '0,98')]
    assert chart.dots[0].xs == [1.0, 0.6]
    assert chart.dots[0].color == chart.lines[0].color


def test_marks_keep_hue_colors() -> None:
    df = pd.concat([_curve().assign(model='a'), _curve().assign(model='b')])
    chart = _render(df, hue='model', marks='marked', legend=True)

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
    plot.line(_curve(), x='coverage', y='accuracy', marks='marked', x_limits=(1, 0), title='Curve')

    assert len(shown) == 1
    assert '0,98' in shown[0]


def test_flipped_x_axis_keeps_tick_labels() -> None:
    chart = _render(_curve(), x_limits=(1, 0), percentage_x=True)

    labels = [label for _, label in layout(chart, Theme(False).color).x_ticks if label]

    assert labels == ['0%', '20%', '40%', '60%', '80%', '100%']


@pytest.mark.parametrize('mark_labels, expected', [
    ('x', ['100%', '60%']),
    ('y', ['86%', '98%']),
    ('both', ['100%\n86%', '60%\n98%']),
    (None, ['', '']),
])
def test_mark_labels_follow_axis_format(mark_labels, expected) -> None:
    chart = _render(_curve(), marks='marked', mark_labels=mark_labels, percentage_x=True, percentage_y=True)

    assert [t.text for t in chart.texts] == expected


def test_both_mark_labels_use_axis_label_titles_and_plain_numbers() -> None:
    chart = _render(
        _curve(), marks='marked', mark_labels='both', x_axis_label=['Coverage', 'share'], y_axis_label='Accuracy',
    )

    assert [(t.line_titles, t.text) for t in chart.texts] == [
        (('Coverage', 'Accuracy'), '1\n0,86'), (('Coverage', 'Accuracy'), '0,6\n0,98'),
    ]


def test_single_mark_labels_have_no_titles() -> None:
    chart = _render(_curve(), marks='marked', mark_labels='y')

    assert all(t.line_titles == () for t in chart.texts)


def test_both_mark_labels_draw_faded_smaller_title_and_x_line_above_y_line() -> None:
    chart = _render(_curve().assign(marked=[False, False, True, False]), marks='marked', mark_labels='both')

    svg = to_svg(chart)
    title = f'<tspan font-size="{FontSizes.POINT_LABEL_TITLES}" fill-opacity="{Marks.POINT_LABEL_TITLE_ALPHA}">'
    x_line = re.search(r'y="([\d.]+)"[^>]*>' + re.escape(title) + r'coverage </tspan>0,6</text>', svg)
    y_line = re.search(r'y="([\d.]+)"[^>]*>' + re.escape(title) + r'accuracy </tspan>0,98</text>', svg)

    assert x_line and y_line
    assert float(x_line.group(1)) < float(y_line.group(1))
    assert FontSizes.POINT_LABEL_TITLES < FontSizes.POINT_LABELS


@pytest.mark.parametrize('marked', [[1.0, np.nan, 1.0, np.nan], ['yes', '', 'yes', ''], [True, None, True, False]])
def test_non_boolean_marks_raise(marked) -> None:
    with pytest.raises(ValueError, match="marks='marked' must be a boolean column"):
        _render(_curve().assign(marked=marked), marks='marked')


def test_unknown_mark_labels_raise() -> None:
    with pytest.raises(ValueError, match='mark_labels must be one of'):
        _render(_curve(), marks='marked', mark_labels='xy')


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
    chart = _render(_curve(), marks='marked')

    assert all(t.size == FontSizes.POINT_LABELS > FontSizes.DATALABELS for t in chart.texts)


def _placed_label_va(**options) -> str:
    chart = _render(_curve().assign(marked=[False, False, True, False]), marks='marked', **options)
    return layout(chart, Theme(False).color).texts[0].va


def test_point_label_above_falling_line() -> None:
    assert _placed_label_va() == 'bottom'


def test_point_label_below_line_rising_on_flipped_axis() -> None:
    assert _placed_label_va(x_limits=(1, 0)) == 'top'


def test_point_labels_keep_line_color_in_dark_mode() -> None:
    chart = _render(_curve(), marks='marked', palette='#ffffff')

    assert re.search(r'fill="#ffffff"[^>]*>0,98</text>', to_svg(chart, dark_mode=True))


def test_axis_sublabels_use_tighter_letter_spacing(plot, shown) -> None:
    plot.line(_curve(), x='coverage', y='accuracy', x_axis_label=['Coverage', 'x share'], y_axis_label=['Accuracy', 'y share'])

    assert re.search(r'class="s"[^>]*>x share</text>', shown[0])
    assert re.search(r'class="s"[^>]*>y share</text>', shown[0])
    assert f'.s{{letter-spacing:{FontSizes.SUBLABEL_LETTER_SPACING}em}}' in shown[0]
