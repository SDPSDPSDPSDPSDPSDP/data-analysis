from typing import Optional

import pandas as pd

from ..config import SortInput
from .sorting import sort_pivot_table


def largest_hue_first(df_pivot: pd.DataFrame) -> pd.DataFrame:
    """Hue columns (stack segments, legend entries) ordered by total, largest first; ties keep data order."""
    return df_pivot[df_pivot.sum().sort_values(ascending=False, kind='stable').index]


def sort_stacked_pivot(df_pivot: pd.DataFrame, sort: Optional[SortInput], orientation: str) -> pd.DataFrame:
    ascending = sort != 'frequency'
    # Horizontal stacks run from the bottom up, so reverse the order to list the first category on top.
    if orientation == 'horizontal':
        ascending = not ascending
    return sort_pivot_table(df_pivot, sort, ascending=ascending)

