from pathlib import Path
from typing import Optional

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

from .formatting import FontSizes, FigureSize

FONT_FAMILY_SATOSHI = "Satoshi Shirin"

_fonts_registered = False


def _register_fonts() -> None:
    """Register bundled Satoshi Shirin fonts with matplotlib's font manager."""
    global _fonts_registered
    if _fonts_registered:
        return
    fonts_dir = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts" / "patched"
    if not fonts_dir.exists():
        return
    for font_path in fonts_dir.glob("*.ttf"):
        fm.fontManager.addfont(str(font_path))
    _fonts_registered = True


def configure_matplotlib(font: Optional[str] = None) -> None:
    """Configure matplotlib defaults.

    Args:
        font: Font to use for all text. Pass ``'satoshi'`` to use the bundled
            Satoshi Shirin font. ``None`` keeps the matplotlib default.
    """
    if font is not None:
        font_lower = font.lower()
        if font_lower == "satoshi":
            _register_fonts()
            plt.rcParams['font.family'] = FONT_FAMILY_SATOSHI
        else:
            raise ValueError(
                f"Unknown font {font!r}. Supported values: 'satoshi', None."
            )

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
