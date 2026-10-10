from ...config import TextColors
from ..colors import to_rgb


def get_luminance(color: str) -> float:
    """WCAG relative luminance of a hex color (with or without '#')."""
    r, g, b = to_rgb(color)

    def adjust(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = adjust(r), adjust(g), adjust(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_text_color_for_background(bg_color: str) -> str:
    luminance = get_luminance(bg_color)
    # 0.179 is the WCAG contrast threshold between black and white text.
    return TextColors.WHITE if luminance < 0.179 else TextColors.BLACK
