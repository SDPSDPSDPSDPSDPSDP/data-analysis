from typing import Any, Dict, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.patches import Circle

PaletteArg = Optional[Union[Dict[Any, str], str]]


def create_figure(figsize: tuple[float, float]) -> Axes:
    """New figure with one axes; every render function draws on the axes it is given."""
    _, ax = plt.subplots(figsize=figsize)
    return ax


def render_countplot(
    ax: Axes,
    df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    order: Optional[Any] = None,
    color: Optional[str] = None,
    palette: PaletteArg = None,
) -> Axes:
    return sns.countplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        order=order,
        color=color,
        palette=palette,
        alpha=1,
        edgecolor='none',
        saturation=1,
        ax=ax,
    )


def render_barplot(
    ax: Axes,
    df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    hue: Optional[str] = None,
    order: Optional[Any] = None,
    color: Optional[str] = None,
    palette: PaletteArg = None,
) -> Axes:
    return sns.barplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        order=order,
        color=color,
        palette=palette,
        alpha=1,
        edgecolor='none',
        saturation=1,
        errorbar=None,
        ax=ax,
    )


def render_histogram(
    ax: Axes,
    df: pd.DataFrame,
    x: str,
    bins: int,
    hue: Optional[str] = None,
    color: Optional[str] = None,
    palette: PaletteArg = None,
    stacked: Optional[bool] = None,
) -> Axes:
    multiple = 'dodge' if hue is not None and stacked is False else 'stack'
    return sns.histplot(
        data=df,
        x=x,
        bins=bins,
        hue=hue,
        color=color,
        palette=palette,
        multiple=multiple,  # type: ignore
        edgecolor='white',
        alpha=1,
        ax=ax,
    )


def render_lineplot(
    ax: Axes,
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    color: Optional[str] = None,
    palette: PaletteArg = None,
) -> Axes:
    return sns.lineplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        color=color,
        palette=palette,
        marker='o',
        markersize=4,
        alpha=1,
        ax=ax,
    )


def render_scatterplot(
    ax: Axes,
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    palette: PaletteArg = None,
) -> Axes:
    return sns.scatterplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        size=size,
        color=color,
        palette=palette,
        alpha=0.8,
        edgecolor='none',
        ax=ax,
    )


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
