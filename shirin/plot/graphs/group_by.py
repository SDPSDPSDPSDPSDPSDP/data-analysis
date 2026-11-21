from typing import Optional

import pandas as pd

from ..common.data_conversion import COUNT_COL, period_totals
from ..config import SortInput, TimeGroupBy, TimeGroupByInput
from ..core.base_options import VALID_TIME_GROUP_BY, validate_str_or_enum_option


def _check_group_by(
    group_by: TimeGroupByInput, vertical: bool, sort: Optional[SortInput], top_n: Optional[int], remainder: bool
) -> None:
    validate_str_or_enum_option(
        option_name="group_by",
        value=group_by,
        valid_options=VALID_TIME_GROUP_BY,
        enum_type=TimeGroupBy,
    )
    if not vertical:
        raise ValueError("group_by needs x: periods run along the x-axis.")
    if sort is not None or top_n is not None or remainder:
        raise ValueError("group_by does not work with sort, top_n or remainder.")


def group_periods(
    df: pd.DataFrame,
    x: str,
    value: Optional[str],
    hue: Optional[str],
    group_by: TimeGroupByInput,
    vertical: bool,
    sort: Optional[SortInput],
    top_n: Optional[int],
    remainder: bool,
) -> tuple[pd.DataFrame, str, str, SortInput]:
    """Totals per period, counted up front so the bars sum COUNT_COL like any value column.

    Returns df, value column, period and the sort that keeps periods in time order.
    Raises ValueError for options group_by does not work with.
    """
    _check_group_by(group_by, vertical, sort, top_n, remainder)
    period = TimeGroupBy(group_by).value
    return period_totals(df, x, value, hue, period), value or COUNT_COL, period, "alphabetical"
