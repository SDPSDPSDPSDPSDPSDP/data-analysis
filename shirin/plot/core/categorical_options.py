from dataclasses import dataclass
from typing import ClassVar, Dict, Optional

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
    group_by: Optional[str] = None  # categories are date periods; 'month' gets month ticks with a year row

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
    remainder: Optional[str] = None  # hue level drawn last, tinted from the other level unless the palette sets it
    category_palette: Optional[Dict[str, str]] = None  # with remainder: one color per bar instead of per hue level

    def validate(self) -> None:
        super().validate()
        if not self.hue:
            raise ValueError("hue must be specified for normalized plots")
        if self.palette is not None and not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary (or None) for normalized plots")
        if self.category_palette is not None and self.remainder is None:
            raise ValueError("category_palette needs remainder")
        if self.category_palette is not None and self.legend:
            raise ValueError("legend is not supported when bars are colored by category")
