import dataclasses
from typing import Any, Generic, Optional, TypeVar, Union

import pandas as pd

from ..common.colors import resolve_palette
from ..common.data_conversion import ensure_column_is_string
from ..common.formatting import format_optional_legend
from ..config import Colors, FigureSize, TitleInput
from ..svg import Chart
from .base_options import BasePlotOptions

PlotPalette = Optional[Union[dict[Any, str], str]]
# What transform() hands to draw() and format_plot(): a DataFrame, or a plot's own dataclass.
DataT = TypeVar("DataT")


def split_title(title: Optional[TitleInput], name: str = "title") -> tuple[str, str]:
    """A str is the text alone; a [text, subtext] list adds a grey second line. name is the argument, for errors."""
    if title is None:
        return "", ""
    if isinstance(title, str):
        return title, ""
    if isinstance(title, (list, tuple)) and len(title) == 2 and all(isinstance(t, str) for t in title):
        return title[0], title[1]
    raise ValueError(f"{name} must be a str or a [text, subtext] list of two str, got {title!r}")


def split_palette(palette: PlotPalette) -> tuple[Optional[str], Optional[dict[Any, str]]]:
    """Return (single color, per-hue palette): a dict maps hue values, a str is one color."""
    if isinstance(palette, dict):
        return None, palette
    if isinstance(palette, str):
        return palette, None
    return Colors.GREY, None


class AbstractPlot(Generic[DataT]):
    def __init__(self, options: BasePlotOptions):
        self.options = options
        self.chart: Optional[Chart] = None
        self._color: Optional[str] = None
        self._palette: Optional[dict[Any, str]] = None

    def render(self) -> Chart:
        # Work on a copy: validate() normalizes fields, the caller's options stay untouched.
        self.options = dataclasses.replace(self.options)
        self.options.validate()

        data = self.transform(self.preprocess())
        chart = self.draw(data)
        self.format_plot(chart, data)
        return chart

    def preprocess(self) -> pd.DataFrame:
        raise NotImplementedError

    def transform(self, df: pd.DataFrame) -> DataT:
        raise NotImplementedError

    def draw(self, data: DataT) -> Chart:
        raise NotImplementedError

    def format_plot(self, plot: Chart, data: DataT) -> None:
        raise NotImplementedError

    def _new_chart(self, width: Optional[float], plot_height: float) -> Chart:
        """width None makes the plot area square (pie)."""
        self.chart = Chart(width=width, plot_height=plot_height)
        self.chart.title, self.chart.subtitle = split_title(self.options.title)
        return self.chart

    def _standard_chart(self) -> Chart:
        return self._new_chart(FigureSize.WIDTH, FigureSize.PLOT_HEIGHT)

    def _format_labels_and_legend(self, plot: Any) -> None:
        options = self.options
        plot.x.label, plot.x.sublabel = split_title(options.x_axis_label, "x_axis_label")
        plot.y.label, plot.y.sublabel = split_title(options.y_axis_label, "y_axis_label")
        format_optional_legend(plot, options.hue, options.legend, options.label_map)

    def _resolve_hue_palette(self, df: pd.DataFrame, no_hue_color: Optional[str] = None) -> pd.DataFrame:
        """Set _color/_palette and stringify hue so it matches the (stringified) palette keys.

        With hue, _palette always maps every hue value to a color: a single palette color
        becomes shades of that color, no palette uses the default color cycle.
        """
        self._color, self._palette = split_palette(self.options.palette)
        if self.options.hue is None:
            if no_hue_color is not None and self.options.palette is None:
                self._color = no_hue_color
            return df
        df = ensure_column_is_string(df, self.options.hue)
        self._palette = resolve_palette(self.options.palette, df[self.options.hue])
        self._color = None
        return df
