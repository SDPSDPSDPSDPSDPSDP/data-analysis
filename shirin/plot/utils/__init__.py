from typing import Any, Dict, Optional, Union

import pandas as pd

from ..config import Colors

def filter_top_n_categories(df: pd.DataFrame, y: str, top_n: int) -> pd.DataFrame:
    """Filter dataframe to keep only top N most frequent categories."""
    top_categories = df[y].value_counts().nlargest(top_n).index
    return df[df[y].isin(top_categories)]

def handle_palette(
    palette: Optional[Union[Dict[Any, str], str]] = None, 
    color: Optional[str] = None
) -> tuple[Optional[str], Optional[Union[Dict[Any, str], str]]]:
    """Convert palette parameter into color and palette components.
    
    Returns:
        Tuple of (color, palette) where one is None based on input type.
    """
    if isinstance(palette, dict):
        return None, palette
    elif palette is not None:
        return palette, None
    else:
        return Colors.GREY, None


__all__ = ['filter_top_n_categories', 'handle_palette']