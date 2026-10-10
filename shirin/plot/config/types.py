from enum import Enum
from typing import List, Optional, Union


class OrderType(str, Enum):
    FREQUENCY = 'frequency'
    ALPHABETICAL = 'alphabetical'


class FillMissingValues(str, Enum):
    SHIFT = 'shift'
    ZERO = 'zero'


class TimeGroupBy(str, Enum):
    YEAR = 'year'
    MONTH = 'month'
    DAY = 'day'


OrderTypeInput = Union[OrderType, str]
FillMissingValuesInput = Optional[Union[FillMissingValues, str]]
TimeGroupByInput = Union[TimeGroupBy, str]
TitleInput = Union[str, List[str]]
