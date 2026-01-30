from .factory import register_plot
from ..plots import CountPlot, BarPlot, Histogram, LinePlot, PieChart, NormalizedCountPlot, TimePlot


def register_all_plots() -> None:
    register_plot('count', CountPlot)
    register_plot('bar', BarPlot)
    register_plot('histogram', Histogram)
    register_plot('line', LinePlot)
    register_plot('pie', PieChart)
    register_plot('normalized_count', NormalizedCountPlot)
    register_plot('time', TimePlot)


register_all_plots()
