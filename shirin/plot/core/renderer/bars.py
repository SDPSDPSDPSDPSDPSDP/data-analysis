"""Bar marks: categorical, stacked, histogram and time bars."""
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from ...common.sorting import palette_colors
from ...config import FigureSize, Marks, TextColors
from ...svg import Chart, Rect
from .hue import hue_groups, hue_levels, set_legend


def _bar_rect(center: float, width: float, base: float, value: float, color: str, horizontal: bool, **kwargs: Any) -> Rect:
    lo, hi = center - width / 2, center + width / 2
    if horizontal:
        return Rect(base, base + value, lo, hi, color, horizontal=True, **kwargs)
    return Rect(lo, hi, base, base + value, color, **kwargs)


def _bar(
    chart: Chart, center: float, width: float, base: float, value: float, color: str, horizontal: bool, rounded: bool = False
) -> None:
    chart.rects.append(_bar_rect(center, width, base, value, color, horizontal, rounded=rounded))


def _category_axis(chart: Chart, labels: List[str], horizontal: bool, top_down: bool) -> None:
    """Categories at 0..n-1; horizontal bars put the first category on top when top_down."""
    n = len(labels)
    axis, value_axis = (chart.y, chart.x) if horizontal else (chart.x, chart.y)
    axis.ticks, axis.tick_labels = list(range(n)), labels
    axis.lim = (n - 0.5, -0.5) if horizontal and top_down else (-0.5, n - 0.5)
    value_axis.sticky = (0,)


def _draw_categorical_bars(
    chart: Chart, table: pd.DataFrame, colors: List[str], horizontal: bool, hue: Optional[str]
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
                _bar(chart, position + offset, bar_width, 0, float(value), color, horizontal, rounded=True)
    _category_axis(chart, [str(category) for category in table.index], horizontal, top_down=True)
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
    order: Optional[List[Any]] = None,
    color: Optional[str] = None,
    palette: Optional[Dict[Any, str]] = None,
) -> Chart:
    """Bar length is the sum of value per category (and hue), or the row count when value is None."""
    order = order if order is not None else list(df[column].dropna().unique())
    if hue is None:
        totals = df.groupby(column)[value].sum() if value else df[column].value_counts()
        return _draw_categorical_bars(chart, totals.reindex(order).to_frame(), [color], horizontal, hue)  # type: ignore[list-item]
    levels = hue_levels(df, hue)
    table = df.groupby([column, hue])[value].sum().unstack() if value else pd.crosstab(df[column], df[hue])
    table = table.reindex(index=order, columns=levels)
    return _draw_categorical_bars(chart, table, palette_colors(palette, levels), horizontal, hue)  # type: ignore[arg-type]


def render_stacked_barplot(
    chart: Chart,
    df: pd.DataFrame,
    horizontal: bool,
    colors: List[str],
    width: float = Marks.BAR_WIDTH,
    overlap: bool = False,
    row_colors: Optional[List[Tuple[str, str]]] = None,
) -> Chart:
    """One stacked bar per row of df, columns stacked in order; horizontal draws row 0 at the bottom.

    overlap (two columns only): the first column is its own pill in front of a full-length pill of the second.
    row_colors (with overlap): (front, back) color per row instead of colors.
    """
    values = df.to_numpy(dtype=float)
    totals = values.sum(axis=1)
    if overlap:
        if len(df.columns) != 2:
            raise ValueError(f"overlap needs exactly 2 columns, got {len(df.columns)}")
        pairs = row_colors if row_colors is not None else [(colors[0], colors[1])] * len(df)
        for position, (total, first, (front, back)) in enumerate(zip(totals, values[:, 0], pairs)):
            _bar(chart, position, width, 0, total, back, horizontal, rounded=True)
            _bar(chart, position, width, 0, first, front, horizontal, rounded=True)
    else:
        outlines = [_bar_rect(position, width, 0, total, '', horizontal, rounded=True) for position, total in enumerate(totals)]
        base = np.zeros(len(df))
        for column, color in enumerate(colors[:len(df.columns)]):
            for position, (start, value) in enumerate(zip(base, values[:, column])):
                fade_to = next((colors[later] for later in range(column + 1, len(df.columns)) if values[position, later]), None)
                chart.rects.append(_bar_rect(position, width, start, value, color, horizontal, clip=outlines[position], fade_to=fade_to))
            base += values[:, column]
    _category_axis(chart, [str(category) for category in df.index], horizontal, top_down=False)
    set_legend(chart, colors, list(df.columns))
    return chart


def render_histogram(
    chart: Chart,
    df: pd.DataFrame,
    x: str,
    bins: int,
    hue: Optional[str] = None,
    color: Optional[str] = None,
    palette: Optional[Dict[Any, str]] = None,
    stacked: Optional[bool] = None,
) -> Chart:
    """With hue, groups stack unless stacked is False, then they are drawn side by side."""
    edges = np.histogram_bin_edges(df[x], bins=bins)
    chart.y.sticky = (0,)
    masks, colors = hue_groups(chart, df, hue, color, palette)
    groups = [df.loc[mask, x] for mask in masks]

    group_counts = [np.histogram(values, bins=edges)[0].astype(float) for values in groups]
    if hue is not None and stacked is not False:
        # Each group is a pill from 0 to its cumulative count, drawn back to front, like the barplot remainder.
        for top, group_color in reversed(list(zip(np.cumsum(group_counts, axis=0), colors))):
            for left, right, count in zip(edges[:-1], edges[1:], top):
                chart.rects.append(Rect(left, right, 0, count, group_color, rounded=True))  # type: ignore[arg-type]
        return chart
    for i, (counts, group_color) in enumerate(zip(group_counts, colors)):
        for left, right, count in zip(edges[:-1], edges[1:], counts):
            if hue is not None:
                step = (right - left) / len(groups)
                left, right = left + i * step, left + (i + 1) * step
            chart.rects.append(Rect(left, right, 0, count, group_color, stroke=TextColors.WHITE, rounded=True))  # type: ignore[arg-type]
    return chart


def render_time_bars(chart: Chart, days: pd.Series, counts: pd.Series, color: str, width: float) -> Chart:
    chart.y.sticky = (0,)
    for day, count in zip(days, counts):
        _bar(chart, day, width, 0, float(count), color, horizontal=False)
    return chart
