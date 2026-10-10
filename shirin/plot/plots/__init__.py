from typing import Dict, Type

from ..core import AbstractPlot, BasePlotOptions
from .barplot import BarPlot
from .countplot import CountPlot
from .histogram import Histogram
from .lineplot import LinePlot
from .piechart import PieChart
from .normalized_countplot import NormalizedCountPlot
from .timeplot import TimePlot
from .accuracy import AccuracyPlot
from .scatterplot import ScatterPlot

PLOT_TYPES: Dict[str, Type[AbstractPlot]] = {
    'count': CountPlot,
    'bar': BarPlot,
    'histogram': Histogram,
    'line': LinePlot,
    'pie': PieChart,
    'normalized_count': NormalizedCountPlot,
    'time': TimePlot,
    'accuracy': AccuracyPlot,
    'scatter': ScatterPlot,
}


def create_plot(plot_type: str, options: BasePlotOptions) -> AbstractPlot:
    if plot_type not in PLOT_TYPES:
        raise ValueError(f"Unknown plot type '{plot_type}'. Available types: {list(PLOT_TYPES)}")
    return PLOT_TYPES[plot_type](options)


__all__ = [
    'CountPlot', 'BarPlot', 'Histogram', 'LinePlot', 'PieChart', 'NormalizedCountPlot', 'TimePlot',
    'AccuracyPlot', 'ScatterPlot', 'PLOT_TYPES', 'create_plot',
]
