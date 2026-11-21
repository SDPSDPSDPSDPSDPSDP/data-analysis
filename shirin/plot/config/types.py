from enum import Enum
from typing import Optional, Union


class Sort(str, Enum):
    FREQUENCY = "frequency"
    ALPHABETICAL = "alphabetical"


class FillMissingValues(str, Enum):
    SHIFT = "shift"
    ZERO = "zero"


class TimeGroupBy(str, Enum):
    YEAR = "year"
    MONTH = "month"
    DAY = "day"


class StackSplit(str, Enum):
    ROUNDED = "rounded"
    FLAT = "flat"


SortInput = Union[Sort, str]
StackSplitInput = Union[StackSplit, str]
FillMissingValuesInput = Optional[Union[FillMissingValues, str]]
TimeGroupByInput = Union[TimeGroupBy, str]
TitleInput = Union[str, list[str]]
