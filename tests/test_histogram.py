"""Histogram regressions: what ends up in the rendered Chart."""

import pandas as pd

from shirin.plot.core import (
    HistogramOptions,
)
from shirin.plot.plots import Histogram


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
