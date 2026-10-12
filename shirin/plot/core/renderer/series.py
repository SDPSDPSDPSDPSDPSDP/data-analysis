"""Point marks: lines and dots on a numeric, date or categorical x axis."""
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from ...config import Marks
from ...svg import Chart, Dots, Line
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
) -> Chart:
    """One line per hue value; duplicate x values are averaged."""
    df = df.assign(**{x: _numeric_x(chart, df[x])})
    masks, colors = hue_groups(chart, df, hue, color, palette)
    for group, group_color in zip((df[mask] for mask in masks), colors):
        line = group.groupby(x)[y].mean()
        chart.lines.append(Line(list(line.index), list(line.values), group_color))  # type: ignore[arg-type]
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
    areas = pd.Series(Marks.DOT_AREA, index=df.index)
    if size is not None:
        values = df[size].astype(float)
        areas = pd.Series(np.interp(values, (values.min(), values.max()), Marks.DOT_AREA_RANGE), index=df.index)
    radii = np.sqrt(areas) / 2
    xs = _numeric_x(chart, df[x])
    for rows, level_color in zip(*hue_groups(chart, df, hue, color, palette)):
        chart.dots.append(Dots(list(xs[rows]), list(df.loc[rows, y]), list(radii[rows]), level_color, alpha=Marks.DOT_ALPHA))
    return chart

