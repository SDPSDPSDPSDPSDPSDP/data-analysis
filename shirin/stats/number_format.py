from typing import Optional, Union


Number = Union[int, float]
_DUTCH_SEPARATORS = str.maketrans({',': '.', '.': ','})


def format_thousands(value: Number, decimals: Optional[int] = None) -> str:
    """Format with '.' as thousands separator and ',' as decimal separator.

    ``decimals=None`` picks automatically: whole numbers and values >= 10 get none,
    smaller values get up to two (trailing zeros dropped), so 1.25 -> "1,25", 1.5 -> "1,5".
    """
    if decimals is None:
        if float(value).is_integer() or abs(value) >= 10:
            decimals = 0
        else:
            return f"{value:.2f}".rstrip('0').rstrip('.').translate(_DUTCH_SEPARATORS)
    return f"{value:,.{decimals}f}".translate(_DUTCH_SEPARATORS)
