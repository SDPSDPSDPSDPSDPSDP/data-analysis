from dataclasses import dataclass
from typing import ClassVar, Optional

from ..config.colors import Colors
from ..config import Sort, SortInput
from .base_options import (
    VALID_SORTS,
    VALID_ORIENTATIONS,
    BasePlotOptions,
    validate_str_or_enum_option,
)


@dataclass
class CategoricalPlotOptions(BasePlotOptions):
    column_fields: ClassVar[tuple[str, ...]] = ('hue', 'axis_column')

    axis_column: str = ''
    orientation: str = 'vertical'
    stacked: bool = False
    sort: SortInput = 'frequency'
    data_labels: bool = True
    suffix: Optional[str] = None

    def validate(self) -> None:
        super().validate()
        if not self.axis_column:
            raise ValueError("axis_column must be specified")

        validate_str_or_enum_option(
            option_name='orientation',
            value=self.orientation,
            valid_options=VALID_ORIENTATIONS,
        )

        validate_str_or_enum_option(
            option_name='sort',
            value=self.sort,
            valid_options=VALID_SORTS,
            enum_type=Sort,
        )

        if self.stacked and self.hue is None:
            raise ValueError("hue must be provided when stacked=True")
        if self.stacked and self.palette is not None and not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary (or None) when stacked=True")


@dataclass
class CountPlotOptions(CategoricalPlotOptions):
    top_n: Optional[int] = None
    normalized: bool = False


@dataclass
class BarPlotOptions(CategoricalPlotOptions):
    column_fields: ClassVar[tuple[str, ...]] = ('hue', 'axis_column', 'value')

    value: str = ''
    normalized: bool = False

    def validate(self) -> None:
        super().validate()
        if not self.value:
            raise ValueError("value column must be specified")


@dataclass
class NormalizedPlotOptions(CategoricalPlotOptions):
    """Always a 100%-stacked plot of hue shares; `stacked` is ignored.

    Shares are of row counts, or of the summed `value` column when set.
    """

    column_fields: ClassVar[tuple[str, ...]] = ('hue', 'axis_column', 'value')

    top_n: Optional[int] = None
    value: Optional[str] = None

    def validate(self) -> None:
        super().validate()
        if not self.hue:
            raise ValueError("hue must be specified for normalized plots")
        if self.palette is not None and not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary (or None) for normalized plots")


@dataclass
class AccuracyPlotOptions(CategoricalPlotOptions):
    """`stacked`, `hue` and `sort` are fixed for accuracy plots."""

    # hue is a synthetic column added in transform, so it is not checked against df.
    column_fields: ClassVar[tuple[str, ...]] = ('axis_column', 'value_column')

    value_column: str = ''
    reverse_order: bool = False

    def __post_init__(self) -> None:
        self.stacked = True
        self.hue = '__is_correct__'
        if not isinstance(self.palette, dict):
            self.palette = {'Correct': Colors.GOOD_GREEN, 'Incorrect': Colors.BAD_RED}

    def validate(self) -> None:
        if not self.value_column:
            raise ValueError("value_column must be specified")
        super().validate()
        accuracy = self.df[self.value_column].astype(float)
        if not accuracy.between(0, 1).all():
            raise ValueError(f"{self.value_column!r} must hold fractions in [0, 1]")
