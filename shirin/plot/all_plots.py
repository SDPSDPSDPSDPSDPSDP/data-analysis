from typing import Optional

import matplotlib.pyplot as plt

from .config.matplotlib import build_rc
from .core import AbstractPlot
from .config.palettes import Palette, LabelMapping
from .graphs.bar import BarPlotsMixin
from .graphs.count import CountPlotsMixin
from .graphs.numeric import NumericPlotsMixin
from .graphs.specialized import SpecializedPlotsMixin


class PlotGraphs(CountPlotsMixin, BarPlotsMixin, NumericPlotsMixin, SpecializedPlotsMixin):
    """A comprehensive plotting interface for creating data visualizations in a notebook.

    This class provides methods for creating various types of plots including **count plots**,
    **bar plots**, **histograms**, **line plots**, and **pie charts**. Each plot is shown
    inline and then closed; copy the image straight from the notebook.

    Args:
        font: Font to use for all text. **Options:** `'satoshi'`, `None` (matplotlib default).
            *Default: `None`*. Styling (font, sizes, grid) only applies while this instance
            draws; matplotlib's global ``rcParams`` stay untouched.
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
        self._rc = build_rc(font=font)
        self._palette = palette
        self._label_mapping = label_mapping

    def _render(self, plot: AbstractPlot) -> None:
        """Show this figure only, then close it; other open figures are left alone."""
        with plt.rc_context(self._rc):
            plot.render()
            figure = plot.ax.figure  # type: ignore[union-attr]
            plt.show()
        plt.close(figure)
