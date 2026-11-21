"""Picks the bar plot class for a PlotGraphs.bar call and renders it."""

from dataclasses import dataclass
from typing import Any, Optional

from ..config import TitleInput
from ..core import BarPlotOptions, CountPlotOptions, NormalizedPlotOptions, RemainderPlotOptions
from ..plots import BarPlot, CountPlot, NormalizedPlot, RemainderPlot
from .host import PlotHost


@dataclass(frozen=True)
class BarModes:
    """The bar() flags that pick the plot class."""

    top_n: Optional[int]
    remainder: bool
    normalized: bool
    stacked: bool


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


class BarDispatchMixin(PlotHost):
    """`common` holds the options every bar plot shares, including hue and axis_column."""

    def _render_counted_bar(self, common: dict[str, Any], modes: BarModes) -> None:
        """Raises ValueError for options that need a value column."""
        if modes.remainder:
            raise ValueError("remainder needs value.")
        if modes.normalized and common["hue"] is not None:
            self._render(NormalizedPlot(NormalizedPlotOptions(**common, top_n=modes.top_n)))
            return
        options = CountPlotOptions(**common, top_n=modes.top_n, stacked=modes.stacked, normalized=modes.normalized)
        self._render(CountPlot(options))

    def _render_summed_bar(self, common: dict[str, Any], value: str, modes: BarModes) -> None:
        """Raises ValueError for options that only work on counted bars."""
        if modes.top_n is not None:
            raise ValueError("top_n only works without value.")
        if modes.remainder:
            self._render_remainder_bar(common, value, modes.normalized)
            return
        hue = common["hue"]
        if modes.normalized and hue is not None and hue != common["axis_column"]:
            self._render(NormalizedPlot(NormalizedPlotOptions(**common, value=value)))
            return
        options = BarPlotOptions(**common, value=value, stacked=modes.stacked, normalized=modes.normalized)
        self._render(BarPlot(options))

    def _render_remainder_bar(self, common: dict[str, Any], value: str, normalized: bool) -> None:
        if not normalized:
            raise ValueError("remainder needs normalized=True.")
        hue = common["hue"]
        options = RemainderPlotOptions(
            **{**common, **self._column_config(value)},
            value=value,
            category_palette=self._column_config(hue)["palette"] if hue is not None else None,
            background=self._theme.background,
        )
        self._render(RemainderPlot(options))
