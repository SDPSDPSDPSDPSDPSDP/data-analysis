import math
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from ..common.sorting import palette_colors
from ..config import FigureSize, FontSizes, TextColors
from ..svg import Chart, Dots, Line, Rect, Text, Wedge
from ..svg.ticks import to_days


def create_figure(width: Optional[float], plot_height: float) -> Chart:
    """New empty chart; every render function draws on the chart it is given."""
    return Chart(width=width, plot_height=plot_height)


def _hue_levels(df: pd.DataFrame, hue: str) -> List[Any]:
    """Hue values in data order; this is also the legend order."""
    return list(df[hue].dropna().unique())


def _set_legend(chart: Chart, colors: List[str], labels: List[Any]) -> None:
    chart.legend = [(color, str(label)) for color, label in zip(colors, labels)]


def _bar(
    chart: Chart, center: float, width: float, base: float, value: float, color: str, horizontal: bool, rounded: bool = False
) -> None:
    lo, hi = center - width / 2, center + width / 2
    if horizontal:
        chart.rects.append(Rect(base, base + value, lo, hi, color, rounded=rounded))
    else:
        chart.rects.append(Rect(lo, hi, base, base + value, color, rounded=rounded))


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
    n_columns = len(table.columns)
    width = FigureSize.BAR_GROUP_WIDTH / n_columns
    for i, (level, color) in enumerate(zip(table.columns, colors)):
        offset = (i - (n_columns - 1) / 2) * width
        for position, value in enumerate(table[level]):
            if pd.notna(value):
                _bar(chart, position + offset, width, 0, float(value), color, horizontal, rounded=True)
    _category_axis(chart, [str(category) for category in table.index], horizontal, top_down=True)
    if hue is not None:
        _set_legend(chart, colors, list(table.columns))
    return chart


def render_countplot(
    chart: Chart,
    df: pd.DataFrame,
    column: str,
    horizontal: bool,
    hue: Optional[str] = None,
    order: Optional[List[Any]] = None,
    color: Optional[str] = None,
    palette: Optional[Dict[Any, str]] = None,
) -> Chart:
    order = order if order is not None else list(df[column].dropna().unique())
    if hue is None:
        table = df[column].value_counts().reindex(order).to_frame()
        return _draw_categorical_bars(chart, table, [color], horizontal, hue)  # type: ignore[list-item]
    levels = _hue_levels(df, hue)
    table = pd.crosstab(df[column], df[hue]).reindex(index=order, columns=levels)
    return _draw_categorical_bars(chart, table, palette_colors(palette, levels), horizontal, hue)  # type: ignore[arg-type]


def render_barplot(
    chart: Chart,
    df: pd.DataFrame,
    column: str,
    value: str,
    horizontal: bool,
    hue: Optional[str] = None,
    order: Optional[List[Any]] = None,
    color: Optional[str] = None,
    palette: Optional[Dict[Any, str]] = None,
) -> Chart:
    """Bar length is the mean of value per category (and hue)."""
    order = order if order is not None else list(df[column].dropna().unique())
    if hue is None:
        table = df.groupby(column)[value].mean().reindex(order).to_frame()
        return _draw_categorical_bars(chart, table, [color], horizontal, hue)  # type: ignore[list-item]
    levels = _hue_levels(df, hue)
    table = df.groupby([column, hue])[value].mean().unstack().reindex(index=order, columns=levels)
    return _draw_categorical_bars(chart, table, palette_colors(palette, levels), horizontal, hue)  # type: ignore[arg-type]


def render_stacked_barplot(chart: Chart, df: pd.DataFrame, horizontal: bool, colors: List[str], width: float = 0.6) -> Chart:
    """One stacked bar per row of df, columns stacked in order; horizontal draws row 0 at the bottom."""
    base = np.zeros(len(df))
    for column, color in zip(df.columns, colors):
        values = df[column].to_numpy(dtype=float)
        for position, (start, value) in enumerate(zip(base, values)):
            _bar(chart, position, width, start, value, color, horizontal)
        base += values
    _category_axis(chart, [str(category) for category in df.index], horizontal, top_down=False)
    _set_legend(chart, colors, list(df.columns))
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
    if hue is None:
        groups, colors = [df[x]], [color]
    else:
        levels = _hue_levels(df, hue)
        groups = [df.loc[df[hue] == level, x] for level in levels]
        colors = palette_colors(palette, levels)  # type: ignore[arg-type]
        _set_legend(chart, colors, levels)  # type: ignore[arg-type]

    base = np.zeros(len(edges) - 1)
    for i, (values, group_color) in enumerate(zip(groups, colors)):
        counts = np.histogram(values, bins=edges)[0].astype(float)
        for left, right, start, count in zip(edges[:-1], edges[1:], base, counts):
            if stacked is False and hue is not None:
                step = (right - left) / len(groups)
                left, right, start = left + i * step, left + (i + 1) * step, 0
            chart.rects.append(Rect(left, right, start, start + count, group_color, stroke=TextColors.WHITE))  # type: ignore[arg-type]
        if stacked is not False:
            base += counts
    return chart


def _numeric_x(chart: Chart, values: pd.Series) -> pd.Series:
    """Positions on the x axis: numbers as is, dates as days, anything else as categories."""
    if pd.api.types.is_datetime64_any_dtype(values):
        chart.x.dates = True
        return to_days(values)
    if pd.api.types.is_numeric_dtype(values):
        return values.astype(float)
    categories = sorted(values.dropna().unique(), key=str)
    chart.x.ticks, chart.x.tick_labels = list(range(len(categories))), [str(c) for c in categories]
    return values.map({category: i for i, category in enumerate(categories)}).astype(float)


def render_lineplot(
    chart: Chart,
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    color: Optional[str] = None,
    palette: Optional[Dict[Any, str]] = None,
) -> Chart:
    """One line per hue value; duplicate x values are averaged."""
    df = df.assign(**{x: _numeric_x(chart, df[x])})
    if hue is None:
        groups, colors = [df], [color]
    else:
        levels = _hue_levels(df, hue)
        groups = [df[df[hue] == level] for level in levels]
        colors = palette_colors(palette, levels)  # type: ignore[arg-type]
        _set_legend(chart, colors, levels)  # type: ignore[arg-type]
    for group, group_color in zip(groups, colors):
        line = group.groupby(x)[y].mean()
        chart.lines.append(Line(list(line.index), list(line.values), group_color, marker_radius=2))  # type: ignore[arg-type]
    return chart


def render_scatterplot(
    chart: Chart,
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    palette: Optional[Dict[Any, str]] = None,
) -> Chart:
    """size scales marker area linearly between 18 and 72 square points over the numeric size column."""
    areas = pd.Series(36.0, index=df.index)
    if size is not None:
        values = df[size].astype(float)
        areas = pd.Series(np.interp(values, (values.min(), values.max()), (18, 72)), index=df.index)
    radii = np.sqrt(areas) / 2
    xs = _numeric_x(chart, df[x])

    if hue is None:
        chart.dots.append(Dots(list(xs), list(df[y]), list(radii), color, alpha=0.8))  # type: ignore[arg-type]
        return chart
    levels = _hue_levels(df, hue)
    colors = palette_colors(palette, levels)  # type: ignore[arg-type]
    for level, level_color in zip(levels, colors):
        rows = df[hue] == level
        chart.dots.append(Dots(list(xs[rows]), list(df.loc[rows, y]), list(radii[rows]), level_color, alpha=0.8))
    _set_legend(chart, colors, levels)
    return chart


def render_time_bars(chart: Chart, days: pd.Series, counts: pd.Series, color: str, width: float) -> Chart:
    chart.y.sticky = (0,)
    for day, count in zip(days, counts):
        _bar(chart, day, width, 0, float(count), color, horizontal=False)
    return chart


def render_time_line(chart: Chart, days: pd.Series, counts: pd.Series, color: str, show_markers: bool) -> Chart:
    chart.lines.append(Line(list(days), list(counts), color, width=2, marker_radius=1.5 if show_markers else 0, alpha=0.9))
    return chart


def render_piechart(
    chart: Chart,
    values: List[float],
    colors: List[str],
    donut: bool,
    n_after_comma: int,
    value_datalabel: int,
    pctdistance: float,
) -> List[Text]:
    """Draw the pie clockwise from 12 o'clock; returns one percentage text per slice ('' below value_datalabel)."""
    chart.x.lim = chart.y.lim = (-1, 1)
    chart.x.visible = chart.y.visible = False
    total = sum(values)
    texts: List[Text] = []
    start = 0.0
    for value, color in zip(values, colors):
        end = start + value / total
        chart.wedges.append(Wedge(start, end, color))
        percentage = value / total * 100
        angle = math.pi * (start + end)
        texts.append(Text(
            pctdistance * math.sin(angle),
            pctdistance * math.cos(angle),
            f'{percentage:.{n_after_comma}f}%' if percentage >= value_datalabel else '',
            TextColors.BLACK,
            FontSizes.TEXT,
        ))
        start = end
    if donut:
        chart.wedges.append(Wedge(0, 1, TextColors.WHITE, radius=0.6))
    chart.texts += texts
    return texts
