from dataclasses import dataclass
from typing import ClassVar, Optional

from ..config import PaletteInput, Sort, SortInput
from ..config.colors import BACKGROUND_COLOR
from .base_options import (
    VALID_ORIENTATIONS,
    VALID_SORTS,
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
    compact_labels: bool = True
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

    def validate(self) -> None:
        super().validate()
        if not self.hue:
            raise ValueError("hue must be specified for normalized plots")
        if self.palette is not None and not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary (or None) for normalized plots")


@dataclass
class RemainderPlotOptions(NormalizedPlotOptions):
    """Bars of the fractions in `value`, each filled up to 100% with a lighter remainder segment.

    `palette` and `label_map` belong to the `value` column (a color, or {value or remainder level: color}).
    With `hue` equal to `axis_column`, each bar gets its own color from `category_palette` instead.
    """

    value: str = ''  # type: ignore[assignment]
    category_palette: Optional[PaletteInput] = None
    background: str = BACKGROUND_COLOR  # remainder tint blends toward this, so it matches the dark mode background

    def validate(self) -> None:
        # Skips NormalizedPlotOptions.validate: hue and palette describe the user's columns here,
        # RemainderPlot turns them into the normalized hue split.
        CategoricalPlotOptions.validate(self)
        if not self.value:
            raise ValueError("value column must be specified")
        if self.hue is not None and self.hue != self.axis_column:
            raise ValueError(f"With remainder, hue must be the category column {self.axis_column!r} or None.")
        if self.hue is not None and self.legend:
            raise ValueError("legend is not supported when bars are colored by category")
