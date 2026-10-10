import pandas as pd
from typing import Optional


def convert_dict_keys_to_string(d: Optional[dict]) -> Optional[dict]:
    if isinstance(d, dict):
        return {str(key): value for key, value in d.items()}
    return d


def ensure_column_is_string(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = df[col].astype(str)
    return df


def filter_top_n_categories(df: pd.DataFrame, col: str, top_n: int) -> pd.DataFrame:
    top_categories = df[col].value_counts().nlargest(top_n).index
    return df[df[col].isin(top_categories)].copy()


def calculate_value_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df_value_counts = df[col].value_counts().to_frame().reset_index()
    df_value_counts.columns = [col, "count"]
    return df_value_counts


def fill_missing_values_in_data(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str],
    fill_method: str
) -> pd.DataFrame:
    fills = {
        'shift': lambda s: s.interpolate(method='linear', limit_direction='forward'),
        'zero': lambda s: s.fillna(0),
    }
    df = df.copy()
    fill = fills.get(fill_method)
    if fill is not None:
        df[y] = df.groupby(hue)[y].transform(fill) if hue is not None else fill(df[y])
    return df
