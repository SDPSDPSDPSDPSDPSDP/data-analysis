import dataclasses
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Union

import pandas as pd

from .base_options import BasePlotOptions
from .renderer import SeabornRenderer
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


class AbstractPlot(ABC):
    def __init__(self, options: BasePlotOptions):
        self.options = options
        self.renderer = SeabornRenderer()
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

    def _create_standard_figure(self) -> None:
        self.renderer.create_figure((FigureSize.WIDTH, FigureSize.STANDARD_HEIGHT))

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
        """Set _color/_palette and stringify hue so it matches the (stringified) palette keys."""
        self._color, self._palette = split_palette(self.options.palette)
        if self.options.hue is None:
            if no_hue_color is not None:
                self._color = no_hue_color
            return df
        if self._palette is None:
            # seaborn deprecated color= with hue: a single color becomes a gradient palette,
            # no palette falls back to seaborn's default categorical colors.
            if isinstance(self.options.palette, str):
                self._palette = f'dark:{self.options.palette}'  # type: ignore[assignment]
            self._color = None
        return ensure_column_is_string(df, self.options.hue)
