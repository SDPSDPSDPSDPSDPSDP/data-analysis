import pandas as pd
from typing import Any, Dict, Optional

from ..config import OrderTypeInput


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
    order_type: OrderTypeInput,
    df: pd.DataFrame,
    column: str,
    value_column: Optional[str] = None,
) -> Optional[list]:
    """Category order for seaborn: by total (value sum or count), alphabetical, or None (data order)."""
    if order_type == 'frequency':
        totals = df.groupby(column)[value_column].sum() if value_column else df[column].value_counts()
        return list(totals.sort_values(ascending=False).index)
    if order_type == 'alphabetical':
        return sort_alphabetically(df[column].unique())
    return None


def _sort_dataframe_alphabetically(df_pivot: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
    sorted_index = sort_alphabetically(df_pivot.index, ascending=ascending)
    return df_pivot.loc[sorted_index]


def sort_by_frequency(df_pivot: pd.DataFrame, ascending: bool = False) -> pd.DataFrame:
    df_pivot['_order'] = df_pivot.sum(axis=1)
    df_sorted = df_pivot.sort_values(by='_order', ascending=ascending)
    return df_sorted.drop(columns=['_order'])


def sort_pivot_table(df_pivot: pd.DataFrame, order_type: Optional[OrderTypeInput], ascending: bool = False) -> pd.DataFrame:
    if order_type == 'frequency':
        return sort_by_frequency(df_pivot, ascending=ascending)
    if order_type == 'alphabetical':
        return _sort_dataframe_alphabetically(df_pivot, ascending=ascending)
    return df_pivot


def apply_label_mapping(df: pd.DataFrame, label_map: Optional[Dict[Any, str]]) -> pd.DataFrame:
    if not label_map:
        return df
    df = df.copy()
    df.columns = [label_map.get(str(col), str(col)) for col in df.columns]
    return df


def create_colors_list(df: pd.DataFrame, palette: Dict[Any, str]) -> list[str]:
    missing = [col for col in df.columns if str(col) not in palette]
    if missing:
        raise KeyError(f"Column '{missing[0]}' not found in palette. Available keys: {list(palette.keys())}")
    return [palette[str(col)] for col in df.columns]


def create_default_label_map(df: pd.DataFrame, hue: str) -> Dict[Any, Any]:
    return {str(key): str(key) for key in df[hue].unique()}
