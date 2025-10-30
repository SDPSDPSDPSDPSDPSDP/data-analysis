import pandas as pd
from typing import Optional, Union, Dict
from ..config import Colors

def filter_top_n_categories(data: pd.DataFrame, y: str, top_n: int) -> pd.DataFrame:

    top_categories = data[y].value_counts().nlargest(top_n).index
    return data[data[y].isin(top_categories)]

def handle_palette(palette: Optional[Union[Dict[str, str], str]] = None, color: Optional[str] = None) -> tuple:
    if isinstance(palette, (dict, list)):
        color = None
    elif palette is not None and not isinstance(palette, (dict, list)):
        color = palette
        palette = None
    else:
        color = Colors.GREY
        palette = None
    return color, palette