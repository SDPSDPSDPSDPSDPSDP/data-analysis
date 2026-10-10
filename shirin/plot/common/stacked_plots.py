import pandas as pd
from typing import Optional

from ..config import SortInput
from .sorting import sort_pivot_table


def sort_stacked_pivot(df_pivot: pd.DataFrame, sort: Optional[SortInput], orientation: str) -> pd.DataFrame:
    ascending = sort != 'frequency'
    # barh draws bottom-to-top, so reverse the order.
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
    if value_col:
        df_pivot = df.pivot_table(index=category_col, columns=hue, values=value_col, aggfunc='sum', fill_value=0)
    else:
        df_pivot = pd.crosstab(df[category_col], df[hue])
    df_pivot.columns.name = hue
    return sort_stacked_pivot(df_pivot, sort, orientation)
