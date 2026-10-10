from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from ..config import FigureSizeInput, OrderType, OrderTypeInput, StackedLabelType, StackedLabelTypeInput
from .base_options import (
    VALID_ORDER_TYPES,
    VALID_ORIENTATIONS,
    VALID_STACKED_LABEL_TYPES,
    BasePlotOptions,
    InvalidOrderTypeError,
    validate_str_or_enum_option,
)


@dataclass
class CategoricalPlotOptions(BasePlotOptions):
    axis_column: str = ''
    orientation: str = 'vertical'
    figsize: FigureSizeInput = 'dynamic'
    stacked: bool = False
    stacked_labels: StackedLabelTypeInput = None
    order_type: OrderTypeInput = 'frequency'

    def validate(self) -> None:
        super().validate()
        if not self.axis_column:
            raise ValueError("axis_column must be specified")

        validate_str_or_enum_option(
            option_name='orientation',
            value=self.orientation,
            valid_options=VALID_ORIENTATIONS,
        )

        if isinstance(self.order_type, OrderType):
            pass
        elif isinstance(self.order_type, str):
            if self.order_type not in VALID_ORDER_TYPES:
                raise InvalidOrderTypeError(self.order_type, VALID_ORDER_TYPES)
        else:
            raise InvalidOrderTypeError(self.order_type, VALID_ORDER_TYPES, type_error=True)

        validate_str_or_enum_option(
            option_name='stacked_labels',
            value=self.stacked_labels,
            valid_options=VALID_STACKED_LABEL_TYPES,
            enum_type=StackedLabelType,
            allow_none=True,
        )

        if self.stacked and self.hue is None:
            raise ValueError("hue must be provided when stacked=True")


@dataclass
class CountPlotOptions(CategoricalPlotOptions):
    top_n: Optional[int] = None
    normalized: bool = False
    show_labels: bool = True
    suffix: Optional[str] = None


    def validate(self) -> None:
        super().validate()
        if self.normalized and self.hue is not None and not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary when normalized=True with hue")


@dataclass
class BarPlotOptions(CategoricalPlotOptions):
    value: str = ''
    percentage_labels: bool = False
    suffix: Optional[str] = None


    def validate(self) -> None:
        super().validate()
        if not self.value:
            raise ValueError("value column must be specified")


@dataclass
class NormalizedCountPlotOptions(CategoricalPlotOptions):
    top_n: Optional[int] = None
    show_labels: bool = True
    suffix: Optional[str] = None
    palette: Optional[Union[Dict[Any, str], str]] = field(default_factory=dict)
    ylabel: str = 'Percentage'


    def validate(self) -> None:
        super().validate()
        if not self.hue:
            raise ValueError("hue must be specified for normalized plots")
        if not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary for normalized plots")


@dataclass
class AccuracyPlotOptions(CategoricalPlotOptions):
    value_column: str = ''
    suffix: Optional[str] = None
    reverse_order: bool = False

    def validate(self) -> None:
        if not self.value_column:
            raise ValueError("value_column must be specified")
        # These are fixed for accuracy plots – not exposed as user options.
        self.stacked = True
        self.hue = '__is_correct__'
        self.figsize = 'dynamic'
        self.stacked_labels = 'standard'
        if not isinstance(self.palette, dict):
            from ..config.colors import Colors
            self.palette = {
                'Correct': Colors.GOOD_GREEN,
                'Incorrect': Colors.BAD_RED,
            }
        super().validate()
