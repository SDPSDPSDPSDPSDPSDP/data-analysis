"""Point marks: lines and dots on a numeric, date or categorical x axis."""
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from ....number_format import format_fraction_percentage, format_thousands
from ...config import FontSizes, Layout, Marks
from ...svg import Chart, Dots, Line, Text
from ...svg.ticks import to_days
from .hue import hue_groups


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
    fill: bool = False,
    marks: Optional[str] = None,
    mark_labels: Optional[str] = 'y',
    percentage_x: bool = False,
    percentage_y: bool = False,
    axis_titles: Tuple[str, str] = ('', ''),
) -> Chart:
    """One line per hue value; duplicate x values are averaged.

    marks: boolean column, True rows get a dot. mark_labels: 'x', 'y', 'both' or None, the value(s) written
    next to each dot, formatted like their axis (percentage_x/percentage_y). 'both' writes x above y, each
    after its axis title from axis_titles.
    """
    df = df.assign(**{x: _numeric_x(chart, df[x])})
    masks, colors = hue_groups(chart, df, hue, color, palette)
    for group, group_color in zip((df[mask] for mask in masks), colors):
        line = group.groupby(x)[y].mean()
        chart.lines.append(Line(list(line.index), list(line.values), group_color, fill))  # type: ignore[arg-type]
        if marks is not None:
            texts = _mark_texts(group[x], group[y], mark_labels, percentage_x, percentage_y)
            titles = axis_titles if mark_labels == 'both' else ()
            _add_marks(chart, group[group[marks]], x, y, texts, titles, group_color, _slopes(line))
    return chart


def _slopes(line: pd.Series) -> pd.Series:
    if len(line) < 2:
        return pd.Series(0.0, index=line.index)
    xs, ys = line.index.values.astype(float), line.values.astype(float)
    return pd.Series(np.gradient(ys, xs), index=line.index)


def _mark_texts(
    xs: pd.Series, ys: pd.Series, mark_labels: Optional[str], percentage_x: bool, percentage_y: bool,
) -> pd.Series:
    x_text = xs.map(format_fraction_percentage if percentage_x else format_thousands)
    y_text = ys.map(format_fraction_percentage if percentage_y else format_thousands)
    if mark_labels == 'x':
        return x_text
    if mark_labels == 'y':
        return y_text
    if mark_labels == 'both':
        return x_text + '\n' + y_text
    return pd.Series('', index=xs.index)


def _add_marks(
    chart: Chart, rows: pd.DataFrame, x: str, y: str, texts: pd.Series, titles: Tuple[str, ...], color: str,
    slopes: pd.Series,
) -> None:
    """Dot plus text right of every row; the text sits below the line, or above where it falls (see place_point_labels)."""
    if rows.empty:
        return
    chart.dots.append(Dots(list(rows[x]), list(rows[y]), [Marks.POINT_LABEL_DOT_RADIUS] * len(rows), color))
    gap = Layout.POINT_LABEL_GAP
    for px, py, text in zip(rows[x], rows[y], texts[rows.index]):
        chart.texts.append(Text(
            px, py, text, color, FontSizes.POINT_LABELS, 'left', 'top', dx=gap, dy=-gap, slope=float(slopes[px]),
            keep_color=True, line_titles=titles,
        ))


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
    """size scales marker area linearly between Marks.DOT_AREA_RANGE square points over the numeric size column."""
    areas = pd.Series(Marks.DOT_AREA, index=df.index)
    if size is not None:
        values = df[size].astype(float)
        areas = pd.Series(np.interp(values, (values.min(), values.max()), Marks.DOT_AREA_RANGE), index=df.index)
    radii = np.sqrt(areas) / 2
    xs = _numeric_x(chart, df[x])
    for rows, level_color in zip(*hue_groups(chart, df, hue, color, palette)):
        chart.dots.append(Dots(list(xs[rows]), list(df.loc[rows, y]), list(radii[rows]), level_color, alpha=Marks.DOT_ALPHA))
    return chart

