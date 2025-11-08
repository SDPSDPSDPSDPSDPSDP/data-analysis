from .factory import register_plot
from .plots import CountPlot, BarPlot


def register_all_plots() -> None:
    register_plot('count', CountPlot)
    register_plot('bar', BarPlot)


register_all_plots()
