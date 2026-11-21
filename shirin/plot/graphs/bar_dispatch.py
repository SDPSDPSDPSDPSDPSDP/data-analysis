"""Picks the bar plot class for a PlotGraphs.bar call and renders it."""

from typing import Any, Optional

from ..config import TitleInput
from ..core import BarPlotOptions, CountPlotOptions, NormalizedPlotOptions, RemainderPlotOptions
from ..plots import BarPlot, CountPlot, NormalizedPlot, RemainderPlot
from .host import PlotHost


def count_axis_labels(
    value: Optional[str], vertical: bool, x_axis_label: Optional[TitleInput], y_axis_label: Optional[TitleInput]
) -> tuple[Optional[TitleInput], Optional[TitleInput]]:
    """Counted bars (value None) label the count axis 'Count' unless the user passed a label ('' hides it)."""
    if value is not None:
        return x_axis_label, y_axis_label
    if vertical and y_axis_label is None:
        return x_axis_label, "Count"
    if not vertical and x_axis_label is None:
        return "Count", y_axis_label
    return x_axis_label, y_axis_label


def render_bar(
    host: PlotHost,
    common: dict[str, Any],
    value: Optional[str],
    hue: Optional[str],
    axis_column: Optional[str],
    top_n: Optional[int],
    remainder: bool,
    normalized: bool,
    stacked: bool,
) -> None:
    """Raises ValueError for option combinations the chosen plot does not support."""
    if value is None:
        if remainder:
            raise ValueError("remainder needs value.")
        common["top_n"] = top_n
        if normalized and hue is not None:
            host._render(NormalizedPlot(NormalizedPlotOptions(**common)))
        else:
            host._render(CountPlot(CountPlotOptions(**common, stacked=stacked, normalized=normalized)))
        return
    if top_n is not None:
        raise ValueError("top_n only works without value.")
    common["value"] = value
    if remainder:
        if not normalized:
            raise ValueError("remainder needs normalized=True.")
        category_palette = host._column_config(hue)["palette"] if hue is not None else None
        options = RemainderPlotOptions(
            **{**common, **host._column_config(value)},
            category_palette=category_palette,
            background=host._theme.background,
        )
        host._render(RemainderPlot(options))
        return
    hue_splits_bars = hue is not None and hue != axis_column
    if normalized and hue_splits_bars:
        host._render(NormalizedPlot(NormalizedPlotOptions(**common)))
    else:
        host._render(BarPlot(BarPlotOptions(**common, stacked=stacked, normalized=normalized)))
