import pandas as pd
from typing import Any, Dict, Optional


def convert_dict_keys_to_string(d: Optional[dict]) -> Optional[dict]:
    if isinstance(d, dict):
        return {str(key): value for key, value in d.items()}
    return d


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
