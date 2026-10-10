from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from ..common.sorting import palette_colors


def create_figure(figsize: tuple[float, float]) -> Axes:
    """New figure with one axes; every render function draws on the axes it is given."""
    _, ax = plt.subplots(figsize=figsize)
    return ax


def _hue_levels(df: pd.DataFrame, hue: str) -> List[Any]:
    """Hue values in data order; this is also the legend order."""
    return list(df[hue].dropna().unique())


def _draw_categorical_bars(
    ax: Axes, table: pd.DataFrame, colors: List[Optional[str]], horizontal: bool, hue: Optional[str]
) -> Axes:
    """One bar group per row of table, one dodged bar per column; NaN cells are not drawn."""
    n_columns = len(table.columns)
    width = 0.8 / n_columns
    positions = np.arange(len(table))
    draw = ax.barh if horizontal else ax.bar
    for i, (level, color) in enumerate(zip(table.columns, colors)):
        values = table[level]
        drawn = values.notna().to_numpy()
        offset = (i - (n_columns - 1) / 2) * width
        draw(positions[drawn] + offset, values[drawn], width, color=color, edgecolor='none', label=level)

    labels = [str(category) for category in table.index]
    if horizontal:
        ax.set_yticks(positions, labels)
        ax.set_ylim(len(table) - 0.5, -0.5)  # first category on top
    else:
        ax.set_xticks(positions, labels)
        ax.set_xlim(-0.5, len(table) - 0.5)
    if hue is not None:
        ax.legend(title=hue)
    return ax


def render_countplot(
    ax: Axes,
    df: pd.DataFrame,
    column: str,
    horizontal: bool,
    hue: Optional[str] = None,
    order: Optional[List[Any]] = None,
    color: Optional[str] = None,
    palette: Optional[Dict[Any, str]] = None,
) -> Axes:
    order = order if order is not None else list(df[column].dropna().unique())
    if hue is None:
        table = df[column].value_counts().reindex(order).to_frame()
        return _draw_categorical_bars(ax, table, [color], horizontal, hue)
    levels = _hue_levels(df, hue)
    table = pd.crosstab(df[column], df[hue]).reindex(index=order, columns=levels)
    return _draw_categorical_bars(ax, table, palette_colors(palette, levels), horizontal, hue)  # type: ignore[arg-type]


def render_barplot(
    ax: Axes,
    df: pd.DataFrame,
    column: str,
    value: str,
    horizontal: bool,
    hue: Optional[str] = None,
    order: Optional[List[Any]] = None,
    color: Optional[str] = None,
    palette: Optional[Dict[Any, str]] = None,
) -> Axes:
    """Bar length is the mean of value per category (and hue)."""
    order = order if order is not None else list(df[column].dropna().unique())
    if hue is None:
        table = df.groupby(column)[value].mean().reindex(order).to_frame()
        return _draw_categorical_bars(ax, table, [color], horizontal, hue)
    levels = _hue_levels(df, hue)
    table = df.groupby([column, hue])[value].mean().unstack().reindex(index=order, columns=levels)
    return _draw_categorical_bars(ax, table, palette_colors(palette, levels), horizontal, hue)  # type: ignore[arg-type]


def render_histogram(
    ax: Axes,
    df: pd.DataFrame,
    x: str,
    bins: int,
    hue: Optional[str] = None,
    color: Optional[str] = None,
    palette: Optional[Dict[Any, str]] = None,
    stacked: Optional[bool] = None,
) -> Axes:
    """With hue, groups stack unless stacked is False, then they are drawn side by side."""
    edges = np.histogram_bin_edges(df[x], bins=bins)
    if hue is None:
        ax.hist(df[x], bins=edges, color=color, edgecolor='white')
        return ax
    levels = _hue_levels(df, hue)
    ax.hist(
        [df.loc[df[hue] == level, x] for level in levels],
        bins=edges,
        stacked=stacked is not False,
        color=palette_colors(palette, levels),  # type: ignore[arg-type]
        label=levels,
        edgecolor='white',
    )
    ax.legend(title=hue)
    return ax


def render_lineplot(
    ax: Axes,
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    color: Optional[str] = None,
    palette: Optional[Dict[Any, str]] = None,
) -> Axes:
    """One line per hue value; duplicate x values are averaged."""
    if hue is None:
        line = df.groupby(x)[y].mean()
        ax.plot(line.index, line.values, color=color, marker='o', markersize=4)
        return ax
    levels = _hue_levels(df, hue)
    for level, level_color in zip(levels, palette_colors(palette, levels)):  # type: ignore[arg-type]
        line = df[df[hue] == level].groupby(x)[y].mean()
        ax.plot(line.index, line.values, color=level_color, marker='o', markersize=4, label=level)
    ax.legend(title=hue)
    return ax


def render_scatterplot(
    ax: Axes,
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    palette: Optional[Dict[Any, str]] = None,
) -> Axes:
    """size scales marker area linearly between 18 and 72 over the numeric size column."""
    areas = pd.Series(36.0, index=df.index)
    if size is not None:
        values = df[size].astype(float)
        areas = pd.Series(np.interp(values, (values.min(), values.max()), (18, 72)), index=df.index)

    if hue is None:
        ax.scatter(df[x], df[y], s=areas, color=color, alpha=0.8, edgecolors='none')
        return ax
    levels = _hue_levels(df, hue)
    for level, level_color in zip(levels, palette_colors(palette, levels)):  # type: ignore[arg-type]
        rows = df[hue] == level
        ax.scatter(df.loc[rows, x], df.loc[rows, y], s=areas[rows], color=level_color, alpha=0.8, edgecolors='none', label=level)
    ax.legend(title=hue)
    return ax


def render_stacked_barplot(ax: Axes, df: pd.DataFrame, kind: str, colors: list[str], width: float = 0.6) -> Axes:
    return df.plot(kind=kind, stacked=True, color=colors, edgecolor='none', ax=ax, alpha=1, width=width)


def render_time_bars(ax: Axes, dates: pd.Series, counts: pd.Series, color: Optional[str], width: float) -> Axes:
    ax.bar(dates, counts, color=color, edgecolor='none', alpha=1, width=width)
    return ax


def render_time_line(ax: Axes, dates: pd.Series, counts: pd.Series, color: Optional[str], show_markers: bool) -> Axes:
    ax.plot(
        dates,
        counts,
        color=color,
        linewidth=2,
        marker='o' if show_markers else None,
        markersize=3 if show_markers else 0,
        markerfacecolor=color,
        markeredgecolor=color,
        markeredgewidth=0,
        alpha=0.9,
    )
    return ax


def render_piechart(
    ax: Axes,
    values: list[float],
    colors: list[str],
    donut: bool,
    n_after_comma: int,
    value_datalabel: int,
    pctdistance: float,
) -> list:
    """Draw the pie on ax; returns the percentage text artists."""
    wedgeprops = dict(edgecolor='none', width=0.6 if donut else 1.0)
    result = ax.pie(
        values,
        colors=colors,
        autopct=lambda p: f'{p:.{n_after_comma}f}%' if p >= value_datalabel else '',
        wedgeprops=wedgeprops,
        textprops={'fontsize': 10},
        pctdistance=pctdistance,
    )
    if donut:
        ax.add_artist(Circle((0, 0), 0.6, color='white', fc='white', linewidth=0))
    ax.axis('equal')
    return result[2] if len(result) > 2 else []
