"""Type definitions for plot configuration."""

from enum import Enum
from typing import Union


class OrderType(str, Enum):
    """Order type for sorting plot categories.
    
    Options:
        FREQUENCY: Sort by frequency (most common first)
        ALPHABETICAL: Sort alphabetically
    """
    FREQUENCY = 'frequency'
    ALPHABETICAL = 'alphabetical'


class StackedLabelType(str, Enum):
    """Label type for stacked plots.
    
    Options:
        STANDARD: Show standard count labels
        PERCENTAGE: Show percentage labels
    """
    STANDARD = 'standard'
    PERCENTAGE = 'percentage'


class FigureSize(str, Enum):
    """Figure size options.
    
    Options:
        DYNAMIC: Automatically calculate based on data
        STANDARD: Use standard fixed size
    """
    DYNAMIC = 'dynamic'
    STANDARD = 'standard'


class FillMissingValues(str, Enum):
    """Strategy for filling missing values in lineplot.
    
    Options:
        SHIFT: Forward fill (use previous value)
        ZERO: Fill with zeros
    """
    SHIFT = 'shift'
    ZERO = 'zero'


# Type aliases that accept both Enum and string
OrderTypeInput = Union[OrderType, str]
StackedLabelTypeInput = Union[StackedLabelType, str, None]
FigureSizeInput = Union[FigureSize, str, float]
FillMissingValuesInput = Union[FillMissingValues, str, None]
