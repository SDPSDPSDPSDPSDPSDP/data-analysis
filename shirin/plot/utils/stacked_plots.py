import pandas as pd
from typing import Optional

from ..config import OrderTypeInput
from .sorting import sort_pivot_table


def prepare_stacked_data(
    df: pd.DataFrame,
    hue: str,
    category_col: str,
    order_type: OrderTypeInput,
    value_col: Optional[str] = None
) -> pd.DataFrame:
    if value_col:
        # For barplots: pivot with explicit values
        df_pivot = df.pivot(index=category_col, columns=hue, values=value_col).fillna(0)
    else:
        # For countplots: count occurrences
        df_subset = df[[hue, category_col]].copy()
        value_counts = df_subset.value_counts()
        value_counts_frame = value_counts.to_frame(name="count").reset_index()
        df_pivot = value_counts_frame.pivot(index=category_col, columns=hue, values="count").fillna(0).astype(int)
    
    # For frequency, use descending; for alphabetical, use ascending
    ascending = False if order_type == 'frequency' else True
    return sort_pivot_table(df_pivot, order_type, ascending=ascending)
