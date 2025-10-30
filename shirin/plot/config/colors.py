from dataclasses import dataclass

@dataclass
class Colors:
    # greys
    GREY: str = '#d6dde6'
    DARK_GREY: str = '#B0B1B4'
    LIGHT_GREY_WARM: str = '#EAECF0'
    DARK_GREY_WARM: str = '#B0B1B4'
    LIGHT_GREY_COOL: str = '#E5E9F1'
    DARK_GREY_COOL: str = '#B4C0D5'
    BLACK: str = '#000000'

    # colors
    BROWN: str = '#723746'
    PINK: str = '#FFD5FF'
    LIGHT_BLUE: str = '#c9e1ff'
    DARK_BLUE: str = '#8C9EBB'
    GREEN: str = '#dcffee'
    RED: str = '#A52B5A'

    # good/bad
    GOOD_GREEN: str = '#dcffee'
    BAD_RED: str = '#A52B5A'
    GOOD_DARK_GREEN: str = '#89BCA3'
    BAD_PINK: str = '#FDE0FD'


@dataclass
class TextColors:
    DARK_GREY = '#444444'
    # LIGHT_GREY = '#888888'
    LIGHT_GREY = '#777777'
    BLACK = '#000000'
    WHITE = '#FFFFFF'