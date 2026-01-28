import pandas as pd
from typing import Any, Dict, Optional

from ..config import OrderTypeInput


def is_all_numeric(values: list) -> tuple[bool, list[float]]:
    numeric_values = []
    for v in values:
        try:
            numeric_values.append(float(str(v)))
        except (ValueError, TypeError):
            return False, []
    return True, numeric_values


def sort_alphabetically(values: Any, ascending: bool = True) -> list:
    values_list = list(values)
    is_numeric, numeric_vals = is_all_numeric(values_list)
    
    if is_numeric:
        sorted_pairs = sorted(zip(numeric_vals, values_list), key=lambda x: x[0], reverse=not ascending)
        return [original_val for _, original_val in sorted_pairs]
    else:
        return sorted(values_list, reverse=not ascending)


def _sort_dataframe_alphabetically(df_pivot: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
    sorted_index = sort_alphabetically(df_pivot.index, ascending=ascending)
    return df_pivot.loc[sorted_index]


def sort_by_frequency(df_pivot: pd.DataFrame, ascending: bool = False) -> pd.DataFrame:
    df_pivot['_order'] = df_pivot.sum(axis=1)
    df_sorted = df_pivot.sort_values(by='_order', ascending=ascending)
    return df_sorted.drop(columns=['_order'])


def sort_pivot_table(df_pivot: pd.DataFrame, order_type: OrderTypeInput, ascending: bool = False) -> pd.DataFrame:
    if order_type == 'frequency':
        return sort_by_frequency(df_pivot, ascending=ascending)
    if order_type == 'alphabetical':
        return _sort_dataframe_alphabetically(df_pivot, ascending=ascending)
    return df_pivot


def apply_label_mapping(df: pd.DataFrame, label_map: Optional[Dict[Any, str]]) -> pd.DataFrame:
    if not label_map:
        return df
    df = df.copy()
    # Convert column names to strings for consistent lookup
    df.columns = [str(col) for col in df.columns]
    df.columns = [label_map.get(col, col) for col in df.columns]
    return df


def create_colors_list(df: pd.DataFrame, palette: Dict[Any, str]) -> list[str]:
    colors = []
    for col in df.columns:
        # Convert column name to string for consistent lookup
        str_col = str(col)
        if str_col in palette:
            colors.append(palette[str_col])
        else:
            raise KeyError(f"Column '{col}' not found in palette. Available keys: {list(palette.keys())}")
    return colors


def create_default_label_map(df: pd.DataFrame, hue: str) -> Dict[Any, Any]:
    return {str(key): str(key) for key in df[hue].unique()}
