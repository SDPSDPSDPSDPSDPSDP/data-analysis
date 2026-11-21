"""Bar shapes shared by the bar renderers: rects, category axis, stacked segments."""

from collections.abc import Sequence
from typing import Any

import numpy as np

from ...svg import Chart, Rect


def bar_rect(
    center: float, width: float, base: float, value: float, color: str, horizontal: bool, **kwargs: Any
) -> Rect:
    lo, hi = center - width / 2, center + width / 2
    if horizontal:
        return Rect(base, base + value, lo, hi, color, horizontal=True, **kwargs)
    return Rect(lo, hi, base, base + value, color, **kwargs)


def category_axis(chart: Chart, labels: list[str], horizontal: bool, top_down: bool) -> None:
    """Categories at 0..n-1; horizontal bars put the first category on top when top_down."""
    n = len(labels)
    axis, value_axis = (chart.y, chart.x) if horizontal else (chart.x, chart.y)
    axis.ticks, axis.tick_labels = list(range(n)), labels
    axis.lim = (n - 0.5, -0.5) if horizontal and top_down else (-0.5, n - 0.5)
    value_axis.sticky = (0,)


def stacked_bars(
    chart: Chart,
    centers: list[float],
    width: float,
    values: np.ndarray,
    colors: list[Sequence[str]],
    horizontal: bool,
) -> None:
    """One bar per row of values, columns stacked in order as segments cut to one rounded outline.

    colors: segment colors per row.
    """
    n_columns = values.shape[1]
    totals = values.sum(axis=1)
    outlines = [
        bar_rect(center, width, 0, total, "", horizontal, rounded=True) for center, total in zip(centers, totals)
    ]
    base = np.zeros(len(values))
    for column in range(n_columns):
        for row, (center, start, value) in enumerate(zip(centers, base, values[:, column])):
            chart.rects.append(
                bar_rect(center, width, start, value, colors[row][column], horizontal, clip=outlines[row])
            )
        base += values[:, column]


def rounded_split_bars(
    chart: Chart, centers: list[float], width: float, values: np.ndarray, colors: list[Sequence[str]], horizontal: bool
) -> None:
    """Each segment a pill to its stack end, drawn back to front: segments meet in rounded caps.

    A segment starts under the cap of the one before it, not at 0: pills sharing an edge bleed through anti-aliasing.
    """
    ends = values.cumsum(axis=1)
    for center, row_values, row_ends, row_colors in zip(centers, values, ends, colors):
        for column in reversed(range(len(row_values))):
            if row_values[column]:
                before = row_ends[column] - row_values[column]
                chart.rects.append(
                    bar_rect(
                        center,
                        width,
                        0,
                        row_ends[column],
                        row_colors[column],
                        horizontal,
                        rounded=True,
                        tuck=float(before) if before else None,
                    )
                )
