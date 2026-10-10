from typing import Optional, Union


Number = Union[int, float]
_DUTCH_SEPARATORS = str.maketrans({',': '.', '.': ','})


def format_thousands(value: Number, decimals: Optional[int] = None) -> str:
    """Format with '.' as thousands separator and ',' as decimal separator.

    ``decimals=None`` picks automatically: none for whole numbers or values >= 10,
    one below 10, two below 1 (so fractional axis ticks don't all read "0").
    """
    if decimals is None:
        magnitude = abs(value)
        if float(value).is_integer() or magnitude >= 10:
            decimals = 0
        else:
            decimals = 1 if magnitude >= 1 else 2
    return f"{value:,.{decimals}f}".translate(_DUTCH_SEPARATORS)
