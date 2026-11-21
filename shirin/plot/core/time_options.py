"""Options for the time plot."""

from dataclasses import dataclass
from typing import ClassVar, Optional

from ..config import FillMissingValues, FillMissingValuesInput, TimeGroupBy, TimeGroupByInput
from .base_options import (
    VALID_FILL_MISSING_VALUES,
    VALID_TIME_GROUP_BY,
    BasePlotOptions,
    validate_str_or_enum_option,
)


@dataclass
class TimePlotOptions(BasePlotOptions):
    column_fields: ClassVar[tuple[str, ...]] = ("hue", "x", "y")

    x: str = ""
    y: Optional[str] = None
    group_by: Optional[TimeGroupByInput] = None
    cumulative: bool = False
    display_month: bool = True
    rotation: int = 0
    fill_missing_values: FillMissingValuesInput = None
    fill: bool = False

    def validate(self) -> None:
        super().validate()
        if not self.x:
            raise ValueError("x column must be specified")
        validate_str_or_enum_option(
            option_name="group_by",
            value=self.group_by,
            valid_options=VALID_TIME_GROUP_BY,
            enum_type=TimeGroupBy,
            allow_none=True,
        )
        validate_str_or_enum_option(
            option_name="fill_missing_values",
            value=self.fill_missing_values,
            valid_options=VALID_FILL_MISSING_VALUES,
            enum_type=FillMissingValues,
            allow_none=True,
        )
        if self.fill_missing_values is not None and self.y is None:
            raise ValueError("fill_missing_values needs y: without y the plot counts rows, which has no gaps")
