from typing import Optional

from .core import AbstractPlot
from .config.palettes import Palette, LabelMapping
from .graphs.bar import BarPlotsMixin
from .graphs.count import CountPlotsMixin
from .graphs.numeric import NumericPlotsMixin
from .graphs.specialized import SpecializedPlotsMixin
from .svg import to_svg


def show(svg: str) -> None:
    """Display one chart in the notebook; the web playground replaces this to collect the SVG."""
    from IPython.display import SVG, display

    display(SVG(svg))


class PlotGraphs(CountPlotsMixin, BarPlotsMixin, NumericPlotsMixin, SpecializedPlotsMixin):
    """A comprehensive plotting interface for creating data visualizations in a notebook.

    This class provides methods for creating various types of plots including **count plots**,
    **bar plots**, **histograms**, **line plots**, and **pie charts**. Each plot is shown
    inline as an SVG.

    Args:
        font: Font to use for all text. **Options:** `'satoshi'` (embedded in the SVG),
            `None` (the viewer's sans-serif). *Default: `None`*.
        palette: A :class:`Palette` subclass with column-name attributes. When a plot uses
            `hue=col`, the matching palette is resolved automatically.
        label_mapping: A :class:`LabelMapping` subclass. Same resolution logic as `palette`.

    Example:
        >>> plot = PlotGraphs(font='satoshi')
        >>> plot.countplot_x(df, x='category')
    """

    def __init__(
        self,
        font: Optional[str] = None,
        palette: Optional[type[Palette]] = None,
        label_mapping: Optional[type[LabelMapping]] = None,
    ) -> None:
        if font is not None and font.lower() != 'satoshi':
            raise ValueError(f"Unknown font {font!r}. Supported values: 'satoshi', None.")
        self._font = font
        self._palette = palette
        self._label_mapping = label_mapping

    def _render(self, plot: AbstractPlot) -> None:
        show(to_svg(plot.render(), font=self._font))
