from typing import Optional

from ..config import SortInput, TimeGroupBy, TimeGroupByInput
from ..core.base_options import VALID_TIME_GROUP_BY, validate_str_or_enum_option


def check_group_by(
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
