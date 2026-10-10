from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import pandas as pd

from ..common.data_conversion import convert_dict_keys_to_string
from ..config import FillMissingValues, OrderType, StackedLabelType, TimeGroupBy


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


def validate_str_or_enum_option(
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

        if isinstance(self.palette, dict):
            self.palette = convert_dict_keys_to_string(self.palette)
        if isinstance(self.label_map, dict):
            self.label_map = convert_dict_keys_to_string(self.label_map)
