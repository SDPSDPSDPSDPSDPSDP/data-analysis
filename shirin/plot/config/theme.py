from dataclasses import dataclass
from typing import Any, Optional

from .colors import BACKGROUND_COLOR, DARK_MODE_COLORS, DARK_MODE_DEFAULT_COLOR, Colors


@dataclass(frozen=True)
class Theme:
    """Light or dark mode: every place that draws differently in dark mode asks this object."""

    dark: bool = False

    def color(self, color: str) -> str:
        """Chrome color (background, grid, text) as drawn in this theme. Data colors pass through."""
        return DARK_MODE_COLORS.get(color, color) if self.dark else color

    @property
    def background(self) -> str:
        return self.color(BACKGROUND_COLOR)

    @property
    def no_hue_palette(self) -> Optional[str]:
        """Palette for charts without hue; None lets each plot pick its light-mode default."""
        return DARK_MODE_DEFAULT_COLOR if self.dark else None

    def palette(self, palette: Any) -> Any:
        """Colors.GREY is the light-mode "no emphasis" color; on the dark background it reads as muddy."""
        if not self.dark:
            return palette

        def swap(color: str) -> str:
            return DARK_MODE_DEFAULT_COLOR if color.lower() == Colors.GREY else color

        if isinstance(palette, dict):
            return {value: swap(color) for value, color in palette.items()}
        return swap(palette) if isinstance(palette, str) else palette
