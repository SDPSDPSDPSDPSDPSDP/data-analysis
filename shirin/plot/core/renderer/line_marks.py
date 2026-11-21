"""Marks on a line plot: dots on flagged rows and their x/y labels."""

from typing import Optional

import numpy as np
import pandas as pd

from ....number_format import format_fraction_percentage, format_thousands
from ...config import FontSizes, Layout, Marks
from ...svg import Chart, Dots, Text


def slopes(line: pd.Series) -> pd.Series:
    if len(line) < 2:
        return pd.Series(0.0, index=line.index)
    xs, ys = line.index.values.astype(float), line.values.astype(float)
    return pd.Series(np.gradient(ys, xs), index=line.index)


def mark_texts(
    xs: pd.Series,
    ys: pd.Series,
    mark_labels: Optional[str],
    percentage_x: bool,
    percentage_y: bool,
) -> pd.Series:
    x_text = xs.map(format_fraction_percentage if percentage_x else format_thousands)
    y_text = ys.map(format_fraction_percentage if percentage_y else format_thousands)
    if mark_labels == "x":
        return x_text
    if mark_labels == "y":
        return y_text
    if mark_labels == "both":
        return x_text + "\n" + y_text
    return pd.Series("", index=xs.index)


def add_marks(
    chart: Chart,
    rows: pd.DataFrame,
    x: str,
    y: str,
    texts: pd.Series,
    titles: tuple[str, ...],
    color: str,
    slopes: pd.Series,
) -> None:
    """Dot plus text right of every row; the text sits below the line, or above where it falls (see place_point_labels)."""
    if rows.empty:
        return
    chart.dots.append(Dots(list(rows[x]), list(rows[y]), [Marks.POINT_LABEL_DOT_RADIUS] * len(rows), color))
    gap = Layout.POINT_LABEL_GAP
    for px, py, text in zip(rows[x], rows[y], texts[rows.index]):
        chart.texts.append(
            Text(
                px,
                py,
                text,
                color,
                FontSizes.POINT_LABELS,
                "left",
                "top",
                dx=gap,
                dy=-gap,
                slope=float(slopes[px]),
                keep_color=True,
                line_titles=titles,
            )
        )
