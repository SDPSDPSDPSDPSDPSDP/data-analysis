from typing import Union


Number = Union[int, float]


def format_thousands(value: Number) -> str:
    """Format numbers with a dot as thousands separator and no decimals."""
    return f"{value:,.0f}".replace(",", ".")
