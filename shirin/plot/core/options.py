from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

import pandas as pd

from ..common.data_conversion import convert_dict_keys_to_string
from ..config import (
    FigureSizeInput,
    FillMissingValues,
    FillMissingValuesInput,
    OrderType,
    OrderTypeInput,
    StackedLabelType,
    StackedLabelTypeInput,
    TimeGroupBy,
    TimeGroupByInput,
)


class InvalidOptionError(ValueError):
    """Raised when an unsupported option value/type is provided."""

    def __init__(
        self,
        option_name: str,
        received: Any,
        valid_options: tuple[str, ...],
        expected: str,
        type_error: bool = False,
    ) -> None:
        if type_error:
            message = (
                f"Invalid {option_name} type '{type(received).__name__}'. "
                f"Valid options are {expected}: {valid_options}."
            )
        else:
            message = f"Invalid {option_name} '{received}'. Valid options are: {valid_options}."
        super().__init__(message)


class InvalidOrderTypeError(InvalidOptionError):
    """Raised when an unsupported order_type is provided."""

    def __init__(self, received: Any, valid_options: tuple[str, ...], type_error: bool = False) -> None:
        super().__init__(
            option_name='order_type',
            received=received,
            valid_options=valid_options,
            expected='strings or OrderType enum values',
            type_error=type_error,
        )


VALID_ORDER_TYPES = tuple(order_type.value for order_type in OrderType)
VALID_ORIENTATIONS = ('vertical', 'horizontal')
VALID_STACKED_LABEL_TYPES = tuple(stacked_label.value for stacked_label in StackedLabelType)
VALID_TIME_GROUP_BY = tuple(time_group.value for time_group in TimeGroupBy)
VALID_TIME_PLOT_TYPES = ('bar', 'line')
VALID_FILL_MISSING_VALUES = tuple(fill_option.value for fill_option in FillMissingValues)


def _validate_str_or_enum_option(
    *,
    option_name: str,
    value: Any,
    valid_options: tuple[str, ...],
    enum_type: Optional[type] = None,
    allow_none: bool = False,
) -> None:
    if allow_none and value is None:
        return

    if enum_type is not None and isinstance(value, enum_type):
        return

    if isinstance(value, str):
        if value not in valid_options:
            raise InvalidOptionError(option_name, value, valid_options, 'strings')
        return

    expected = 'strings'
    if enum_type is not None:
        expected = f'strings or {enum_type.__name__} enum values'
    raise InvalidOptionError(option_name, value, valid_options, expected, type_error=True)


@dataclass
class BasePlotOptions:
    df: pd.DataFrame
    palette: Optional[Union[Dict[Any, str], str]] = None
    label_map: Optional[Dict[Any, str]] = None
    xlabel: str = ''
    ylabel: str = ''
    plot_legend: bool = True
    legend_offset: float = 1.13
    ncol: int = 2
    hue: Optional[str] = None

    def validate(self) -> None:
        if self.df is None or self.df.empty:
            raise ValueError("DataFrame cannot be None or empty")

        # Normalize dictionary keys to strings to ensure consistency
        if isinstance(self.palette, dict):
            self.palette = convert_dict_keys_to_string(self.palette)
        if isinstance(self.label_map, dict):
            self.label_map = convert_dict_keys_to_string(self.label_map)


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

        _validate_str_or_enum_option(
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

        _validate_str_or_enum_option(
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

    def validate(self) -> None:
        super().validate()
        if self.normalized:
            if self.hue is not None and not isinstance(self.palette, dict):
                raise ValueError("palette must be a dictionary when normalized=True with hue")


@dataclass
class BarPlotOptions(CategoricalPlotOptions):
    value: str = ''
    percentage_labels: bool = False

    def validate(self) -> None:
        super().validate()
        if not self.value:
            raise ValueError("value column must be specified")


@dataclass
class HistogramOptions(BasePlotOptions):
    x: str = ''
    xlimit: Optional[Union[float, int]] = None
    bins: int = 100
    stacked: Optional[bool] = None

    def validate(self) -> None:
        super().validate()
        if not self.x:
            raise ValueError("x column must be specified")
        if self.bins <= 0:
            raise ValueError("bins must be positive")


@dataclass
class LinePlotOptions(BasePlotOptions):
    x: str = ''
    y: str = ''
    rotation: int = 0
    fill_missing_values: FillMissingValuesInput = None

    def validate(self) -> None:
        super().validate()
        if not self.x:
            raise ValueError("x column must be specified")
        if not self.y:
            raise ValueError("y column must be specified")

        _validate_str_or_enum_option(
            option_name='fill_missing_values',
            value=self.fill_missing_values,
            valid_options=VALID_FILL_MISSING_VALUES,
            enum_type=FillMissingValues,
            allow_none=True,
        )


@dataclass
class PiePlotOptions(BasePlotOptions):
    col: str = ''
    n_after_comma: int = 0
    value_datalabel: int = 5
    donut: bool = False
    palette: Optional[Union[Dict[Any, str], str]] = field(default_factory=dict)

    def validate(self) -> None:
        super().validate()
        if not self.col:
            raise ValueError("col must be specified")
        if not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary for pie charts")


@dataclass
class NormalizedCountPlotOptions(CategoricalPlotOptions):
    top_n: Optional[int] = None
    show_labels: bool = True
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

    def validate(self) -> None:
        if not self.value_column:
            raise ValueError("value_column must be specified")
        # These are fixed for accuracy plots – not exposed as user options.
        self.stacked = True
        self.hue = '__is_correct__'
        self.figsize = 'dynamic'
        self.stacked_labels = 'standard'
        _validate_str_or_enum_option(
            option_name='orientation',
            value=self.orientation,
            valid_options=VALID_ORIENTATIONS,
        )
        super().validate()


@dataclass
class TimePlotOptions(BasePlotOptions):
    x: str = ''
    group_by: TimeGroupByInput = 'day'
    plot_type: str = 'bar'
    display_month: bool = True
    ylabel: str = 'Total'
    cumulative: bool = False
    rotation: int = 0

    def validate(self) -> None:
        super().validate()
        if not self.x:
            raise ValueError("x column must be specified")

        _validate_str_or_enum_option(
            option_name='group_by',
            value=self.group_by,
            valid_options=VALID_TIME_GROUP_BY,
            enum_type=TimeGroupBy,
        )
        _validate_str_or_enum_option(
            option_name='plot_type',
            value=self.plot_type,
            valid_options=VALID_TIME_PLOT_TYPES,
        )