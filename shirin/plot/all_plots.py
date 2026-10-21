from typing import Any, Dict, Optional

from .config.colors import DARK_MODE_DEFAULT_COLOR
from .config.palettes import (
    DEFAULT_LABEL_MAPPING,
    DEFAULT_PALETTE,
    LabelMappingInput,
    PaletteInput,
    merge_column_config,
)
from .core import AbstractPlot
from .graphs.bar import BarPlotsMixin
from .graphs.numeric import NumericPlotsMixin
from .graphs.specialized import SpecializedPlotsMixin
from .svg import to_svg


def show(svg: str) -> None:
    """Display one chart in the notebook; the web playground replaces this to collect the SVG."""
    from IPython.display import SVG, display

    display(SVG(svg))


class PlotGraphs(BarPlotsMixin, NumericPlotsMixin, SpecializedPlotsMixin):
    """A comprehensive plotting interface for creating data visualizations in a notebook.

    This class provides methods for creating various types of plots including
    **bar plots**, **histograms**, **line plots**, and **pie charts**. Each plot is shown
    inline as an SVG.

    Args:
        font: Font to use for all text. **Options:** `'satoshi'` (embedded in the SVG),
            `None` (the viewer's sans-serif). *Default: `'satoshi'`*.
        palette: Dict of `{column: {value: color}}` (or `{column: color}`). When a plot uses
            `hue=col`, the matching palette is resolved automatically. Built-in entries
            (`is_correct`) apply unless overridden.
        label_mapping: Dict of `{column: {value: label}}`. Same resolution logic as `palette`.
        dark_mode: Dark grey background with white text, white instead of grey for charts without hue. *Default: `False`*.

    Example:
        >>> plot = PlotGraphs(
        ...     palette={'is_ripe': {True: '#e9d0ff', False: '#6f2525'}},
        ...     label_mapping={'is_ripe': {True: 'Ripe', False: 'Unripe'}},
        ... )
        >>> plot.bar(df, x='fruit', hue='is_ripe')
    """

    def __init__(
        self,
        font: Optional[str] = 'satoshi',
        palette: Optional[PaletteInput] = None,
        label_mapping: Optional[LabelMappingInput] = None,
        dark_mode: bool = False,
    ) -> None:
        if font is not None and font.lower() != 'satoshi':
            raise ValueError(f"Unknown font {font!r}. Supported values: 'satoshi', None.")
        self._font = font
        self._dark_mode = dark_mode
        self._palette = merge_column_config('palette', DEFAULT_PALETTE, palette, (dict, str))
        self._label_mapping = merge_column_config('label_mapping', DEFAULT_LABEL_MAPPING, label_mapping, (dict,))

    def _column_config(self, column: Optional[str]) -> Dict[str, Any]:
        """palette and label_map configured for a hue (or pie col) column."""
        if column is None:
            return {'palette': DARK_MODE_DEFAULT_COLOR if self._dark_mode else None, 'label_map': None}
        return {'palette': self._palette.get(column), 'label_map': self._label_mapping.get(column)}

    def _render(self, plot: AbstractPlot) -> None:
        show(to_svg(plot.render(), font=self._font, dark_mode=self._dark_mode))
