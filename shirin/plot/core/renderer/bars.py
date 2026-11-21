"""Bar marks: categorical, stacked and histogram."""

from collections.abc import Sequence
from typing import Any, Optional

import numpy as np
import pandas as pd

from ...common.colors import palette_colors
from ...common.data_conversion import aggregate
from ...config import FigureSize, Marks
from ...svg import Chart, Rect
from .bar_shapes import bar_rect, category_axis, rounded_split_bars, stacked_bars
from .hue import hue_groups, hue_levels, set_legend


def _draw_categorical_bars(
    chart: Chart, table: pd.DataFrame, colors: list[str], horizontal: bool, hue: Optional[str]
) -> Chart:
    """One bar group per row of table, one dodged bar per column; NaN cells are not drawn."""
    # hue equal to the category column fills one cell per row: draw full-width bars, no dodge.
    n_slots = len(table.columns) if (table.notna().sum(axis=1) > 1).any() else 1
    width = FigureSize.BAR_GROUP_WIDTH / n_slots
    bar_width = width - FigureSize.DODGE_GAP if n_slots > 1 else width
    for i, (level, color) in enumerate(zip(table.columns, colors)):
        offset = (i - (n_slots - 1) / 2) * width if n_slots > 1 else 0
        for position, value in enumerate(table[level]):
            if pd.notna(value):
                bar = bar_rect(position + offset, bar_width, 0, float(value), color, horizontal, rounded=True)
                chart.rects.append(bar)
    category_axis(chart, [str(category) for category in table.index], horizontal, top_down=True)
    if hue is not None:
        set_legend(chart, colors, list(table.columns))
    return chart


def render_barplot(
    chart: Chart,
    df: pd.DataFrame,
    column: str,
    value: Optional[str],
    horizontal: bool,
    hue: Optional[str] = None,
    order: Optional[list[Any]] = None,
    color: Optional[str] = None,
    palette: Optional[dict[Any, str]] = None,
) -> Chart:
    """Bar length is the sum of value per category (and hue), or the row count when value is None."""
    order = order if order is not None else list(df[column].dropna().unique())
    if hue is None:
        totals = aggregate(df, column, value)
        return _draw_categorical_bars(chart, totals.reindex(order).to_frame(), [color], horizontal, hue)  # type: ignore[list-item]
    levels = hue_levels(df, hue)
    table = aggregate(df, column, value, hue)
    table = table.reindex(index=order, columns=levels)
    return _draw_categorical_bars(chart, table, palette_colors(palette, levels), horizontal, hue)  # type: ignore[arg-type]


def render_stacked_barplot(
    chart: Chart,
    df: pd.DataFrame,
    horizontal: bool,
    colors: list[str],
    width: float = Marks.BAR_WIDTH,
    split: str = "rounded",
    row_colors: Optional[Sequence[Sequence[str]]] = None,
) -> Chart:
    """One stacked bar per row of df, columns stacked in order; horizontal draws row 0 at the bottom.

    split: how segments meet, 'rounded' (rounded caps) or 'flat' (hard edge).
    row_colors: segment colors per row instead of colors.
    """
    values = df.to_numpy(dtype=float)
    centers: list[float] = list(range(len(df)))
    segment_colors: list[Sequence[str]] = list(row_colors) if row_colors is not None else [colors] * len(df)
    if split == "rounded":
        rounded_split_bars(chart, centers, width, values, segment_colors, horizontal)
    else:
        stacked_bars(chart, centers, width, values, segment_colors, horizontal)
    category_axis(chart, [str(category) for category in df.index], horizontal, top_down=False)
    set_legend(chart, colors, list(df.columns))
    return chart


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
