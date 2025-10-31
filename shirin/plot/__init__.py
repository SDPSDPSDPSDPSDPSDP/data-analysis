from .all_plots import PlotGraphs
from .config import FontSizes, FigureSize, Colors
import matplotlib.pyplot as plt
# import seaborn as sns
# from matplotlib import font_manager

# Use a font with naturally wider letter spacing
# Options: 'Segoe UI', 'Calibri', 'Century Gothic'
plt.rcParams['font.family'] = 'Arial'

# plt.rcParams['savefig.dpi'] = 300
# plt.rcParams['savefig.format'] = 'png'
plt.rcParams['figure.figsize'] = [FigureSize.WIDTH, FigureSize.HEIGHT]

linestyle_grid = 'dotted'
color_grid = 'lightgrey'
linewidth_grid = 0.5

plt.rcParams['axes.grid'] = False
plt.rcParams['grid.color'] = color_grid
plt.rcParams['grid.linestyle'] = linestyle_grid
plt.rcParams['grid.linewidth'] = linewidth_grid

color_axis = 'black'
linewidth_axis = 0.5

plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.bottom'] = False
plt.rcParams['axes.spines.left'] = False
plt.rcParams['axes.edgecolor'] = color_axis
plt.rcParams['axes.linewidth'] = linewidth_axis

plt.rcParams['legend.framealpha'] = 0.0

plt.rcParams['font.size'] = FontSizes.TEXT
plt.rcParams['axes.titlesize'] = FontSizes.TITLE
plt.rcParams['xtick.labelsize'] = FontSizes.TICKS
plt.rcParams['ytick.labelsize'] = FontSizes.TICKS

__all__ = ['PlotGraphs', 'Colors']