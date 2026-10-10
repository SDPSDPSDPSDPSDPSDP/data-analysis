from typing import Optional

import matplotlib.pyplot as plt

from .config.matplotlib import build_rc
from .core import AbstractPlot, PlotExporter
from .config.palettes import Palette, LabelMapping
from .graphs.bar import BarPlotsMixin
from .graphs.count import CountPlotsMixin
from .graphs.numeric import NumericPlotsMixin
from .graphs.specialized import SpecializedPlotsMixin


class PlotGraphs(CountPlotsMixin, BarPlotsMixin, NumericPlotsMixin, SpecializedPlotsMixin):
    """A comprehensive plotting interface for creating and exporting data visualizations.

    This class provides methods for creating various types of plots including **count plots**,
    **bar plots**, **histograms**, **line plots**, and **pie charts**. All plots can be automatically
    exported to files with customizable settings.

    Args:
        export: Whether to automatically export plots to files. *Default: `False`*.
        output_dir: Directory where exported plots will be saved. *Default: `'./plot_output/'`*.
        prefix: Optional prefix to add to all exported filenames. *Default: `None`*.
        format: File format for exported plots. **Options:** `'png'`, `'svg'`. *Default: `'png'`*.
        font: Font to use for all text. **Options:** `'satoshi'`, `None` (matplotlib default).
            *Default: `None`*. Styling (font, sizes, grid) only applies while this instance
            draws; matplotlib's global ``rcParams`` stay untouched.
        show: Whether to call ``plt.show()`` after each plot. *Default: `True`*.
        palette: A :class:`Palette` subclass with column-name attributes. When a plot uses
            `hue=col`, the matching palette is resolved automatically.
        label_mapping: A :class:`LabelMapping` subclass. Same resolution logic as `palette`.

    Example:
        >>> plot = PlotGraphs(export=True, output_dir='./charts/', prefix='analysis')
        >>> plot.countplot_x(df, x='category', output_name='category_counts')

        >>> plot = PlotGraphs(font='satoshi')
        >>> plot.countplot_x(df, x='category', output_name='category_counts')
    """

    def __init__(
        self,
        export: bool = False,
        output_dir: str = "./plot_output/",
        prefix: Optional[str] = None,
        format: str = 'png',
        font: Optional[str] = None,
        palette: Optional[type[Palette]] = None,
        label_mapping: Optional[type[LabelMapping]] = None,
        show: bool = True,
    ) -> None:
        self._rc = build_rc(font=font)

        self._exporter = PlotExporter(
            enabled=export,
            output_dir=output_dir,
            prefix=prefix,
            format=format,
            auto_show=show,
        )
        self._palette = palette
        self._label_mapping = label_mapping

    def _render(self, plot: AbstractPlot, output_name: str) -> None:
        with plt.rc_context(self._rc):
            plot.render()
            self._exporter.export_and_show(plot.ax.figure, output_name)  # type: ignore[union-attr]
