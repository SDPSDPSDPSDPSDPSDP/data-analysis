import dataclasses
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap, to_hex

from .base_options import BasePlotOptions
from . import renderer
from ..common.data_conversion import ensure_column_is_string
from ..common.formatting import format_optional_legend, format_xy_labels
from ..common.sorting import create_default_label_map
from ..config import Colors, FigureSize

PaletteInput = Optional[Union[Dict[Any, str], str]]


def split_palette(palette: PaletteInput) -> Tuple[Optional[str], Optional[Dict[Any, str]]]:
    """Return (single color, per-hue palette): a dict maps hue values, a str is one color."""
    if isinstance(palette, dict):
        return None, palette
    if isinstance(palette, str):
        return palette, None
    return Colors.GREY, None


def default_colors(n: int) -> List[str]:
    """First n colors of matplotlib's color cycle, repeating when n is larger."""
    cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    return [cycle[i % len(cycle)] for i in range(n)]


def default_palette(values: pd.Series, color: Optional[str] = None) -> Dict[str, str]:
    """Color per sorted value: shades of color when given, else the default color cycle."""
    keys = sorted(values.astype(str).unique())
    if color is None:
        return dict(zip(keys, default_colors(len(keys))))
    shades = LinearSegmentedColormap.from_list('', ['#333333', color])(np.linspace(1, 0.3, len(keys)))
    return dict(zip(keys, map(to_hex, shades)))


class AbstractPlot(ABC):
    def __init__(self, options: BasePlotOptions):
        self.options = options
        self.ax: Optional[Axes] = None
        self.plot_object: Optional[Any] = None
        self._preprocessed_df: Optional[pd.DataFrame] = None
        self._color: Optional[str] = None
        self._palette: Optional[Dict[Any, str]] = None
        self._label_map_legend: Optional[Dict[Any, str]] = None

    def render(self) -> Any:
        # Work on a copy: validate() normalizes fields, the caller's options stay untouched.
        self.options = dataclasses.replace(self.options)
        self.options.validate()

        self._preprocessed_df = self.preprocess()
        transformed_data = self.transform(self._preprocessed_df)
        self.plot_object = self.draw(transformed_data)
        self.format_plot(self.plot_object)

        return self.plot_object

    @abstractmethod
    def preprocess(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> Any:
        pass

    @abstractmethod
    def draw(self, data: Any) -> Any:
        pass

    @abstractmethod
    def format_plot(self, plot: Any) -> None:
        pass

    def _new_axes(self, figsize: Tuple[float, float]) -> Axes:
        self.ax = renderer.create_figure(figsize)
        return self.ax

    def _standard_axes(self) -> Axes:
        return self._new_axes((FigureSize.WIDTH, FigureSize.STANDARD_HEIGHT))

    def _format_labels_and_legend(self, plot: Any) -> None:
        """Axis labels plus hue legend; builds a default label_map from the data when missing."""
        options = self.options
        label_map = options.label_map
        if label_map is None and options.plot_legend and options.hue is not None:
            label_map = create_default_label_map(self._preprocessed_df, options.hue)  # type: ignore[arg-type]
        self._label_map_legend = label_map or None

        format_xy_labels(plot, xlabel=options.xlabel, ylabel=options.ylabel)
        format_optional_legend(
            plot,
            options.hue,
            options.plot_legend,
            self._label_map_legend,
            options.ncol,
            options.legend_offset,
        )

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
