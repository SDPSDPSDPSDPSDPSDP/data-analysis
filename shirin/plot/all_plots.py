from typing import Any, Dict, Optional

from .common.colors import to_rgb
from .config.palettes import (
    DEFAULT_LABEL_MAPPING,
    DEFAULT_PALETTE,
    LabelMappingInput,
    PaletteInput,
    merge_column_config,
)
from .config.theme import Theme
from .core import AbstractPlot
from .graphs.bar import BarPlotsMixin
from .graphs.numeric import NumericPlotsMixin
from .graphs.specialized import SpecializedPlotsMixin
from .svg import to_png, to_svg


def show(svg: str) -> None:
    """Display one chart in the notebook; the web playground replaces this to collect the SVG.

    Sends SVG and PNG in one bundle: notebooks render the SVG, VS Code's copy button needs the PNG.
    """
    from IPython.display import display

    display({'image/svg+xml': svg, 'image/png': to_png(svg)}, raw=True)


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
        dark_mode: Dark grey background with white text. Charts without hue, and palette entries
            set to `Colors.GREY`, are drawn white instead of grey. *Default: `False`*.

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
        self._theme = Theme(dark_mode)
        self._palette = merge_column_config('palette', DEFAULT_PALETTE, palette, (dict, str))
        # Hex only: contrast, blending and shades all need RGB, so a named color would fail on some charts only.
        for column, mapping in self._palette.items():
            for color in mapping.values() if isinstance(mapping, dict) else [mapping]:
                try:
                    to_rgb(color)
                except (ValueError, AttributeError) as e:
                    raise ValueError(f"palette[{column!r}]: color {color!r} must be a hex string like '#1a2b3c'") from e
        self._label_mapping = merge_column_config('label_mapping', DEFAULT_LABEL_MAPPING, label_mapping, (dict,))

    def _column_config(self, column: Optional[str]) -> Dict[str, Any]:
        """palette and label_map configured for a hue (or pie col) column."""
        if column is None:
            return {'palette': self._theme.no_hue_palette, 'label_map': None}
        return {'palette': self._theme.palette(self._palette.get(column)), 'label_map': self._label_mapping.get(column)}

    def _render(self, plot: AbstractPlot, gradient: bool = True) -> None:
        show(to_svg(plot.render(), font=self._font, dark_mode=self._theme.dark, gradient=gradient))
