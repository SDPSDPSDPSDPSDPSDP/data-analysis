class Colors:
    GREY: str = '#d6dde6'
    DARK_GREY: str = '#B0B1B4'
    LIGHT_GREY_WARM: str = '#EAECF0'
    DARK_GREY_WARM: str = '#B0B1B4'
    LIGHT_GREY_COOL: str = '#E5E9F1'
    DARK_GREY_COOL: str = '#B4C0D5'
    BLACK: str = '#000000'

    BROWN: str = '#723746'
    PINK: str = '#FFD5FF'
    LIGHT_BLUE: str = '#c9e1ff'
    DARK_BLUE: str = '#8C9EBB'
    GREEN: str = '#dcffee'
    RED: str = '#A52B5A'

    GOOD_GREEN: str = '#dcffee'
    BAD_RED: str = '#A52B5A'
    GOOD_DARK_GREEN: str = '#89BCA3'
    BAD_PINK: str = '#FDE0FD'


class TextColors:
    DARK_GREY = '#444444'
    LIGHT_GREY = '#777777'
    FAINT_GREY = '#aaaaaa'
    BLACK = '#000000'
    WHITE = '#FFFFFF'


GRID_COLOR = '#f4f4f4'
BACKGROUND_COLOR = '#ffffff'
DARK_MODE_COLORS = {
    BACKGROUND_COLOR: '#1e1e1e',
    GRID_COLOR: '#2e2e2e',
    TextColors.BLACK: TextColors.WHITE,
    TextColors.DARK_GREY: '#cccccc',
    TextColors.LIGHT_GREY: '#999999',
    TextColors.FAINT_GREY: '#777777',
}
DARK_MODE_DEFAULT_COLOR = '#ffffff'  # replaces Colors.GREY for charts without hue or palette
SHADE_BASE = '#333333'  # dark end when one color is spread over hue values
SHADE_DARKEST_MIX = 0.3  # share of the color in the darkest shade

# Colors for hue values without a palette (the tab10 cycle).
DEFAULT_CYCLE = (
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
)
REMAINDER_TINT = 0.78  # share of the way from the filled color to the background for a barplot remainder segment
