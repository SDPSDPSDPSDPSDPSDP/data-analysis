import pandas as pd
from typing import Any, Dict, Optional

from ..config import OrderTypeInput


def sort_by_frequency(df_pivot: pd.DataFrame, ascending: bool = False) -> pd.DataFrame:
    df_pivot['_order'] = df_pivot.sum(axis=1)
    df_sorted = df_pivot.sort_values(by='_order', ascending=ascending)
    return df_sorted.drop(columns=['_order'])


def sort_alphabetically(df_pivot: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
    index_values = df_pivot.index.tolist()
    
    try:
        numeric_index = pd.Series([float(v) for v in index_values], index=df_pivot.index)
        sorted_index = numeric_index.sort_values(ascending=ascending).index
        return df_pivot.loc[sorted_index]
    except (ValueError, TypeError):
        return df_pivot.sort_index(ascending=ascending)


def sort_pivot_table(df_pivot: pd.DataFrame, order_type: OrderTypeInput, ascending: bool = False) -> pd.DataFrame:
    if order_type == 'frequency':
        return sort_by_frequency(df_pivot, ascending=ascending)
    if order_type == 'alphabetical':
        return sort_alphabetically(df_pivot, ascending=True)
    return df_pivot


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
