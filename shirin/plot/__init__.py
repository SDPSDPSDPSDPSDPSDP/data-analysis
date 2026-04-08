import pandas as pd

from .all_plots import PlotGraphs
from .config import Colors
from .config.matplotlib import configure_matplotlib


pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", 0)

# Apply base matplotlib style (grid, spines, sizes, etc.) without a custom font.
configure_matplotlib()


__all__ = ['PlotGraphs', 'Colors']