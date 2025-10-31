import pandas as pd
from typing import Any, Dict, Optional

from ..config import OrderTypeInput


def _is_all_numeric(values: list) -> tuple[bool, list[float]]:
    """Check if all values are numeric. Returns (is_numeric, numeric_values)."""
    numeric_values = []
    for v in values:
        try:
            numeric_values.append(float(str(v)))
        except (ValueError, TypeError):
            return False, []
    return True, numeric_values


def sort_alphabetically(values: Any, ascending: bool = True) -> list:
    """Sort values alphabetically with numeric awareness.
    
    If all values are numeric strings, sorts numerically (1, 2, 10).
    Otherwise, sorts alphabetically.
    """
    values_list = list(values)
    is_numeric, numeric_vals = _is_all_numeric(values_list)
    
    if is_numeric:
        # Sort numerically and return original values in that order
        sorted_pairs = sorted(zip(numeric_vals, values_list), key=lambda x: x[0], reverse=not ascending)
        return [original_val for _, original_val in sorted_pairs]
    else:
        return sorted(values_list, reverse=not ascending)


def _sort_dataframe_alphabetically(df_pivot: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
    """Sort DataFrame index alphabetically with numeric awareness."""
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


def get_category_order(
    df: pd.DataFrame,
    column: str,
    order_type: OrderTypeInput,
    value_column: Optional[str] = None
) -> Optional[Any]:
    if order_type == 'frequency':
        if value_column:
            # For barplots: sum values by category
            return df.groupby(column)[value_column].sum().sort_values(ascending=False).index #type: ignore
        else:
            # For countplots: count occurrences
            return df[column].value_counts().sort_values(ascending=False).index
    if order_type == 'alphabetical':
        return sort_alphabetically(df[column].unique())
    return None


def apply_label_mapping(df: pd.DataFrame, label_map: Optional[Dict[Any, str]]) -> pd.DataFrame:
    if not label_map:
        return df
    df = df.copy()
    df.columns = [label_map.get(col, col) for col in df.columns]
    return df


def create_colors_list(df: pd.DataFrame, palette: Dict[Any, str]) -> list[str]:
    return [palette[col] for col in df.columns]


def create_default_label_map(df: pd.DataFrame, hue: str) -> Dict[Any, Any]:
    return {key: key for key in df[hue].unique()}
