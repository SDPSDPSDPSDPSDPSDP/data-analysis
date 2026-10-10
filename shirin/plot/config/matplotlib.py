import functools
from pathlib import Path
from typing import Optional

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

from .formatting import FontSizes, FigureSize

FONT_FAMILY_SATOSHI = "Satoshi Shirin"


@functools.lru_cache(maxsize=None)
def _register_fonts() -> None:
    """Register bundled Satoshi Shirin fonts with matplotlib's font manager (once)."""
    fonts_dir = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts" / "patched"
    if not fonts_dir.exists():
        raise FileNotFoundError(f"Bundled fonts not found at {fonts_dir}; reinstall the package.")
    for font_path in fonts_dir.glob("*.ttf"):
        fm.fontManager.addfont(str(font_path))


def configure_matplotlib(font: Optional[str] = None) -> None:
    """Configure matplotlib defaults.

    Args:
        font: Font to use for all text. Pass ``'satoshi'`` to use the bundled
            Satoshi Shirin font. ``None`` keeps the matplotlib default.
    """
    if font is not None:
        if font.lower() != "satoshi":
            raise ValueError(f"Unknown font {font!r}. Supported values: 'satoshi', None.")
        _register_fonts()
        plt.rcParams['font.family'] = FONT_FAMILY_SATOSHI

    plt.rcParams.update({
        'figure.figsize': [FigureSize.WIDTH, FigureSize.HEIGHT],
        'axes.grid': False,
        'grid.color': 'lightgrey',
        'grid.linestyle': 'dotted',
        'grid.linewidth': 0.5,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.bottom': False,
        'axes.spines.left': False,
        'axes.edgecolor': 'black',
        'axes.linewidth': 0.5,
        'legend.framealpha': 0.0,
        'font.size': FontSizes.TEXT,
        'axes.titlesize': FontSizes.TITLE,
        'xtick.labelsize': FontSizes.TICKS,
        'ytick.labelsize': FontSizes.TICKS,
        'axes.labelsize': FontSizes.XYLABEL,
        'legend.fontsize': FontSizes.LEGEND,
    })
