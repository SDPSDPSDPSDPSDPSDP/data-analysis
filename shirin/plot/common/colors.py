import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from ..config.colors import DEFAULT_CYCLE, SHADE_BASE, SHADE_DARKEST_MIX

RGB = Tuple[float, float, float]


def to_rgb(color: str) -> RGB:
    """RGB in [0, 1] of a hex color ('#1a2b3c', '1a2b3c' or '#abc')."""
    digits = color.lstrip('#')
    if len(digits) == 3:
        digits = ''.join(c * 2 for c in digits)
    if not re.fullmatch(r'[0-9a-fA-F]{6}', digits):
        raise ValueError(f"Color {color!r} must be a hex string like '#1a2b3c'")
    return tuple(int(digits[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def blend(start: str, end: str, t: float) -> str:
    """Hex color t of the way from start to end."""
    mixed = [a + (b - a) * t for a, b in zip(to_rgb(start), to_rgb(end))]
    return '#' + ''.join(f'{round(c * 255):02x}' for c in mixed)


def palette_colors(palette: Dict[Any, str], keys: Iterable[Any]) -> List[str]:
    """Color per key; every plot raises the same KeyError when the palette misses a key."""
    keys = [str(key) for key in keys]
    missing = [key for key in keys if key not in palette]
    if missing:
        raise KeyError(f"Palette missing keys: {missing}. Available keys: {list(palette.keys())}")
    return [palette[key] for key in keys]


def default_colors(n: int) -> List[str]:
    """First n colors of the default color cycle, repeating when n is larger."""
    return [DEFAULT_CYCLE[i % len(DEFAULT_CYCLE)] for i in range(n)]


def default_palette(values: pd.Series, color: Optional[str] = None) -> Dict[str, str]:
    """Color per sorted value: shades of color when given, else the default color cycle."""
    keys = sorted(values.astype(str).unique())
    if color is None:
        return dict(zip(keys, default_colors(len(keys))))
    return {key: blend(SHADE_BASE, color, t) for key, t in zip(keys, np.linspace(1, SHADE_DARKEST_MIX, len(keys)))}
