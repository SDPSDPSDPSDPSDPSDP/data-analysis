from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

from .formatting import FontSizes, FigureSize

FONT_FAMILY = "Satoshi Shirin"


def _register_fonts() -> None:
    """Register bundled Satoshi Shirin fonts with matplotlib's font manager."""
    fonts_dir = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts" / "patched"
    if not fonts_dir.exists():
        return
    for font_path in fonts_dir.glob("*.ttf"):
        fm.fontManager.addfont(str(font_path))


def configure_matplotlib():
    _register_fonts()
    plt.rcParams['font.family'] = FONT_FAMILY

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
