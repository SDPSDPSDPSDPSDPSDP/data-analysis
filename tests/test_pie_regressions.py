"""PieChart regressions: what ends up in the rendered Chart."""

import pandas as pd

from shirin.plot.core import (
    PiePlotOptions,
)
from shirin.plot.plots import PieChart


def test_pie_without_palette_uses_distinct_colors(df: pd.DataFrame) -> None:
    counts = df['category'].value_counts().to_frame()
    chart = PieChart(PiePlotOptions(df=counts, col='count')).render()
    assert len({wedge.color for wedge in chart.wedges}) == 3


def test_pie_leaves_whitespace_around_wedges(df: pd.DataFrame) -> None:
    counts = df['category'].value_counts().to_frame()
    chart = PieChart(PiePlotOptions(df=counts, col='count')).render()
    assert chart.x.lim[1] > max(wedge.radius for wedge in chart.wedges)
