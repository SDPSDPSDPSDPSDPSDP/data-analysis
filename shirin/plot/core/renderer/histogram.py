"""Histogram bars: stacked or dodged per hue group."""

from typing import Any, Optional

import numpy as np
import pandas as pd

from ...config import Marks
from ...svg import Chart, Rect
from .bar_shapes import stacked_bars
from .hue import hue_groups


def render_histogram(
    chart: Chart,
    df: pd.DataFrame,
    x: str,
    bins: int,
    hue: Optional[str] = None,
    color: Optional[str] = None,
    palette: Optional[dict[Any, str]] = None,
    stacked: Optional[bool] = None,
) -> Chart:
    """With hue, groups stack unless stacked is False, then they are drawn side by side."""
    edges = np.histogram_bin_edges(df[x], bins=bins)
    chart.y.sticky = (0,)
    masks, colors = hue_groups(chart, df, hue, color, palette)
    groups = [df.loc[mask, x] for mask in masks]

    group_counts = [np.histogram(values, bins=edges)[0].astype(float) for values in groups]
    bin_width = edges[1] - edges[0]
    inset = bin_width * Marks.HISTOGRAM_GAP / 2
    if hue is not None and stacked is not False:
        centers = list((edges[:-1] + edges[1:]) / 2)
        bar_width = bin_width - 2 * inset
        stacked_bars(
            chart, centers, bar_width, np.column_stack(group_counts), [colors] * len(centers), horizontal=False
        )
        return chart
    for i, (counts, group_color) in enumerate(zip(group_counts, colors)):
        for left, right, count in zip(edges[:-1] + inset, edges[1:] - inset, counts):
            if hue is not None:
                step = (right - left) / len(groups)
                left, right = left + i * step, left + (i + 1) * step
            chart.rects.append(Rect(left, right, 0, count, group_color, rounded=True))
    return chart
