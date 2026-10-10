import pandas as pd
from typing import Any, Dict, Iterable, Optional

from ..config import SortInput


def _as_float(value: Any) -> float:
    return float(str(value))


def sort_alphabetically(values: Any, ascending: bool = True) -> list:
    """Sort numerically when every value parses as a number, otherwise as plain values."""
    values_list = list(values)
    try:
        return sorted(values_list, key=_as_float, reverse=not ascending)
    except (ValueError, TypeError):
        return sorted(values_list, reverse=not ascending)


def get_order(
    sort: SortInput,
    df: pd.DataFrame,
    column: str,
    value_column: Optional[str] = None,
) -> Optional[list]:
    """Category order: by total (value sum or count), alphabetical, or None (data order)."""
    if sort == 'frequency':
        totals = df.groupby(column)[value_column].sum() if value_column else df[column].value_counts()
        return list(totals.sort_values(ascending=False).index)
    if sort == 'alphabetical':
        return sort_alphabetically(df[column].unique())
    return None


def sort_by_frequency(df_pivot: pd.DataFrame, ascending: bool = False) -> pd.DataFrame:
    return df_pivot.loc[df_pivot.sum(axis=1).sort_values(ascending=ascending).index]


def sort_pivot_table(df_pivot: pd.DataFrame, sort: Optional[SortInput], ascending: bool = False) -> pd.DataFrame:
    if sort == 'frequency':
        return sort_by_frequency(df_pivot, ascending=ascending)
    if sort == 'alphabetical':
        return df_pivot.loc[sort_alphabetically(df_pivot.index, ascending=ascending)]
    return df_pivot


def palette_colors(palette: Dict[Any, str], keys: Iterable[Any]) -> list[str]:
    """Color per key; every plot raises the same KeyError when the palette misses a key."""
    keys = [str(key) for key in keys]
    missing = [key for key in keys if key not in palette]
    if missing:
        raise KeyError(f"Palette missing keys: {missing}. Available keys: {list(palette.keys())}")
    return [palette[key] for key in keys]

