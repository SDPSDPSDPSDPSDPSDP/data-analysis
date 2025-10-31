from enum import Enum
from typing import Optional, Union


class OrderType(str, Enum):
    FREQUENCY = 'frequency'
    ALPHABETICAL = 'alphabetical'


class StackedLabelType(str, Enum):
    STANDARD = 'standard'
    PERCENTAGE = 'percentage'


class FigureSize(str, Enum):
    DYNAMIC = 'dynamic'
    STANDARD = 'standard'


class FillMissingValues(str, Enum):
    SHIFT = 'shift'
    ZERO = 'zero'


OrderTypeInput = Union[OrderType, str]
StackedLabelTypeInput = Optional[Union[StackedLabelType, str]]
FigureSizeInput = Union[FigureSize, str, float]
FillMissingValuesInput = Optional[Union[FillMissingValues, str]]
