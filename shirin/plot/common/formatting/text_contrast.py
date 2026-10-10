import re

from matplotlib.colors import to_rgb

from ...config import TextColors


def get_luminance(color: str) -> float:
    """WCAG relative luminance of any matplotlib color (hex with or without '#', named)."""
    if re.fullmatch(r'[0-9a-fA-F]{6}', color):
        color = f'#{color}'
    r, g, b = to_rgb(color)

    def adjust(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = adjust(r), adjust(g), adjust(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_text_color_for_background(bg_color: str) -> str:
    luminance = get_luminance(bg_color)
    # 0.179 is the WCAG contrast threshold between black and white text.
    return TextColors.WHITE if luminance < 0.179 else TextColors.BLACK
