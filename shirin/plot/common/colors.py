import re
from typing import Tuple

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
