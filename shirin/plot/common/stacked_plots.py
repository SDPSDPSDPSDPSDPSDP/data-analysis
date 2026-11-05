from typing import Optional

import pandas as pd

from ..config import SortInput
from .data_conversion import aggregate
from .sorting import sort_pivot_table


def sort_stacked_pivot(df_pivot: pd.DataFrame, sort: Optional[SortInput], orientation: str) -> pd.DataFrame:
    ascending = sort != 'frequency'
    # Horizontal stacks run from the bottom up, so reverse the order to list the first category on top.
    if orientation == 'horizontal':
        ascending = not ascending
    return sort_pivot_table(df_pivot, sort, ascending=ascending)


def prepare_stacked_data(
    df: pd.DataFrame,
    hue: str,
    category_col: str,
    sort: Optional[SortInput],
    value_col: Optional[str] = None,
    orientation: str = 'vertical'
) -> pd.DataFrame:
    return sort_stacked_pivot(aggregate(df, category_col, value_col, hue).fillna(0), sort, orientation)
