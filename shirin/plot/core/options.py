from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from ..config import FillMissingValues, FillMissingValuesInput, TimeGroupBy, TimeGroupByInput
from .base_options import (
    VALID_FILL_MISSING_VALUES,
    VALID_TIME_GROUP_BY,
    VALID_TIME_PLOT_TYPES,
    BasePlotOptions,
    InvalidOptionError,
    InvalidOrderTypeError,
    validate_str_or_enum_option,
)
from .categorical_options import (
    AccuracyPlotOptions,
    BarPlotOptions,
    CategoricalPlotOptions,
    CountPlotOptions,
    NormalizedCountPlotOptions,
)


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

        validate_str_or_enum_option(
            option_name='fill_missing_values',
            value=self.fill_missing_values,
            valid_options=VALID_FILL_MISSING_VALUES,
            enum_type=FillMissingValues,
            allow_none=True,
        )


@dataclass
class ScatterPlotOptions(BasePlotOptions):
    x: str = ''
    y: str = ''
    size: Optional[str] = None

    def validate(self) -> None:
        super().validate()
        if not self.x:
            raise ValueError("x column must be specified")
        if not self.y:
            raise ValueError("y column must be specified")


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

        validate_str_or_enum_option(
            option_name='group_by',
            value=self.group_by,
            valid_options=VALID_TIME_GROUP_BY,
            enum_type=TimeGroupBy,
        )
        validate_str_or_enum_option(
            option_name='plot_type',
            value=self.plot_type,
            valid_options=VALID_TIME_PLOT_TYPES,
        )
