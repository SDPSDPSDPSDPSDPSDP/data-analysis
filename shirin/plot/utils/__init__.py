from typing import Any, Dict, Optional, Union

import pandas as pd

from ..config import Colors

def filter_top_n_categories(df: pd.DataFrame, y: str, top_n: int) -> pd.DataFrame:
    top_categories = df[y].value_counts().nlargest(top_n).index
    return df[df[y].isin(top_categories)]

def _is_dict_or_list(palette: Any) -> bool:
    return isinstance(palette, dict)

def handle_palette(
    palette: Optional[Union[Dict[Any, str], str]] = None,
    color: Optional[str] = None
) -> tuple[Optional[str], Optional[Union[Dict[Any, str], str]]]:
    if _is_dict_or_list(palette):
        return None, palette
    if palette is not None:
        return palette, None
    return Colors.GREY, None


__all__ = ['filter_top_n_categories', 'handle_palette']