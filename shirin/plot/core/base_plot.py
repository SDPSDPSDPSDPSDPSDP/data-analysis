import dataclasses
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Union

import pandas as pd

from .base_options import BasePlotOptions
from ..common.colors import default_palette
from ..common.data_conversion import ensure_column_is_string
from ..common.formatting import format_optional_legend
from ..config import Colors, FigureSize, TitleInput
from ..svg import Chart

PlotPalette = Optional[Union[Dict[Any, str], str]]


def split_title(title: Optional[TitleInput]) -> Tuple[str, str]:
    """A str is the title alone; a [title, subtitle] list adds the grey subtitle line."""
    if title is None:
        return '', ''
    if isinstance(title, str):
        return title, ''
    if isinstance(title, (list, tuple)) and len(title) == 2 and all(isinstance(t, str) for t in title):
        return title[0], title[1]
    raise ValueError(f"title must be a str or a [title, subtitle] list of two str, got {title!r}")


def split_palette(palette: PlotPalette) -> Tuple[Optional[str], Optional[Dict[Any, str]]]:
    """Return (single color, per-hue palette): a dict maps hue values, a str is one color."""
    if isinstance(palette, dict):
        return None, palette
    if isinstance(palette, str):
        return palette, None
    return Colors.GREY, None


class AbstractPlot(ABC):
    def __init__(self, options: BasePlotOptions):
        self.options = options
        self.chart: Optional[Chart] = None
        self._color: Optional[str] = None
        self._palette: Optional[Dict[Any, str]] = None

    def render(self) -> Chart:
        # Work on a copy: validate() normalizes fields, the caller's options stay untouched.
        self.options = dataclasses.replace(self.options)
        self.options.validate()

        transformed_data = self.transform(self.preprocess())
        chart = self.draw(transformed_data)
        self.format_plot(chart)
        return chart

    @abstractmethod
    def preprocess(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> Any:
        pass

    @abstractmethod
    def draw(self, data: Any) -> Chart:
        pass

    @abstractmethod
    def format_plot(self, plot: Chart) -> None:
        pass

    def _new_chart(self, width: Optional[float], plot_height: float) -> Chart:
        """width None makes the plot area square (pie)."""
        self.chart = Chart(width=width, plot_height=plot_height)
        self.chart.title, self.chart.subtitle = split_title(self.options.title)
        return self.chart

    def _standard_chart(self) -> Chart:
        return self._new_chart(FigureSize.WIDTH, FigureSize.PLOT_HEIGHT)

    def _format_labels_and_legend(self, plot: Any) -> None:
        options = self.options
        plot.x.label, plot.y.label = options.x_axis_label, options.y_axis_label
        format_optional_legend(plot, options.hue, options.legend, options.label_map)

    def _resolve_hue_palette(self, df: pd.DataFrame, no_hue_color: Optional[str] = None) -> pd.DataFrame:
        """Set _color/_palette and stringify hue so it matches the (stringified) palette keys.

        With hue, _palette always maps every hue value to a color: a single palette color
        becomes shades of that color, no palette uses the default color cycle.
        """
        self._color, self._palette = split_palette(self.options.palette)
        if self.options.hue is None:
            if no_hue_color is not None:
                self._color = no_hue_color
            return df
        df = ensure_column_is_string(df, self.options.hue)
        if self._palette is None:
            single_color = self.options.palette if isinstance(self.options.palette, str) else None
            self._palette = default_palette(df[self.options.hue], single_color)
            self._color = None
        return df
