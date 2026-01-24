import pandas as pd
from typing import Any, Dict, Optional


def convert_dict_keys_to_string(d: Optional[dict]) -> Optional[dict]:
    if isinstance(d, dict):
        return {str(key): value for key, value in d.items()}
    return d


def prepare_legend_label_map(label_map: Optional[Dict[Any, str]]) -> Optional[Dict[str, str]]:
    """Convert label_map keys to strings for legend formatting."""
    return convert_dict_keys_to_string(label_map) if label_map else None


def convert_palette_to_strings(palette: Dict[Any, str]) -> Dict[str, str]:
    return {str(k): str(v) for k, v in palette.items()}


def ensure_column_is_string(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = df[col].astype(str)
    return df


def ensure_column_is_int(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = df[col].astype(int)
    return df


def fill_missing_values_in_data(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str],
    fill_method: str
) -> pd.DataFrame:
    df = df.copy()
    
    if fill_method == 'shift':
        if hue is not None:
            df[y] = df.groupby(hue)[y].transform(lambda group: group.interpolate(method='linear', limit_direction='forward'))
        else:
            df[y] = df[y].interpolate(method='linear', limit_direction='forward')
    elif fill_method == 'zero':
        if hue is not None:
            df[y] = df.groupby(hue)[y].transform(lambda group: group.fillna(0))
        else:
            df[y] = df[y].fillna(0)
    
    return df
