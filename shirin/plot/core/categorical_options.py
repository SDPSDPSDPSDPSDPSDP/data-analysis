from dataclasses import dataclass
from typing import Any, ClassVar, Optional, Union

from ..config import Sort, SortInput, StackSplit, StackSplitInput, TimeGroupBy, TimeGroupByInput
from ..config.colors import BACKGROUND_COLOR
from .base_options import (
    VALID_ORIENTATIONS,
    VALID_SORTS,
    VALID_STACK_SPLITS,
    VALID_TIME_GROUP_BY,
    BasePlotOptions,
    validate_str_or_enum_option,
)

GROUP_BY_CONFLICT = "group_by does not work with sort, top_n or remainder."


@dataclass
class CategoricalPlotOptions(BasePlotOptions):
    column_fields: ClassVar[tuple[str, ...]] = ("hue", "axis_column")

    axis_column: str = ""
    orientation: str = "vertical"
    stacked: bool = False
    split: StackSplitInput = "rounded"  # how stacked segments meet
    sort: Optional[SortInput] = None  # None: 'frequency', or time order with group_by
    data_labels: bool = True
    compact_labels: bool = True
    suffix: Optional[str] = None
    # axis_column holds dates, drawn as one bar per period; 'month' gets month ticks with a year row.
    group_by: Optional[TimeGroupByInput] = None
    descriptions: Optional[dict[str, str]] = None  # {category: grey line under its tick label}

    def validate(self) -> None:
        super().validate()
        if not self.axis_column:
            raise ValueError("axis_column must be specified")

        validate_str_or_enum_option(
            option_name="orientation",
            value=self.orientation,
            valid_options=VALID_ORIENTATIONS,
        )

        validate_str_or_enum_option(
            option_name="sort",
            value=self.sort,
            valid_options=VALID_SORTS,
            enum_type=Sort,
            allow_none=True,
        )

        validate_str_or_enum_option(
            option_name="split",
            value=self.split,
            valid_options=VALID_STACK_SPLITS,
            enum_type=StackSplit,
        )

        if self.group_by is not None:
            self._validate_group_by()

        if self.descriptions and self.group_by is not None:
            raise ValueError("descriptions do not work with group_by")
        if self.stacked and self.hue is None:
            raise ValueError("hue must be provided when stacked=True")
        if self.stacked and self.palette is not None and not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary (or None) when stacked=True")

    def resolved_sort(self) -> SortInput:
        if self.sort is not None:
            return self.sort
        # ISO period labels sort alphabetically in time order.
        return "alphabetical" if self.group_by is not None else "frequency"

    def _validate_group_by(self) -> None:
        validate_str_or_enum_option(
            option_name="group_by",
            value=self.group_by,
            valid_options=VALID_TIME_GROUP_BY,
            enum_type=TimeGroupBy,
        )
        self.group_by = TimeGroupBy(self.group_by).value
        if self.orientation != "vertical":
            raise ValueError("group_by needs x: periods run along the x-axis.")
        if self.sort is not None:
            raise ValueError(GROUP_BY_CONFLICT)


@dataclass
class CountPlotOptions(CategoricalPlotOptions):
    top_n: Optional[int] = None
    normalized: bool = False

    def validate(self) -> None:
        super().validate()
        if self.group_by is not None and self.top_n is not None:
            raise ValueError(GROUP_BY_CONFLICT)


@dataclass
class BarPlotOptions(CategoricalPlotOptions):
    column_fields: ClassVar[tuple[str, ...]] = ("hue", "axis_column", "value")

    value: str = ""
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

    column_fields: ClassVar[tuple[str, ...]] = ("hue", "axis_column", "value")

    top_n: Optional[int] = None
    value: Optional[str] = None

    def validate(self) -> None:
        super().validate()
        if not self.hue:
            raise ValueError("hue must be specified for normalized plots")
        if self.palette is not None and not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary (or None) for normalized plots")
        if self.group_by is not None and self.top_n is not None:
            raise ValueError(GROUP_BY_CONFLICT)


@dataclass
class RemainderPlotOptions(NormalizedPlotOptions):
    """Bars of the fractions in `value`, each filled up to 100% with a lighter remainder segment.

    `palette` and `label_map` belong to the `value` column (a color, or {value or remainder level: color}).
    With `hue` equal to `axis_column`, each bar gets its own color from `category_palette` instead.
    """

    value: str = ""
    category_palette: Optional[Union[dict[Any, str], str]] = None
    background: str = BACKGROUND_COLOR  # remainder tint blends toward this, so it matches the dark mode background

    def validate(self) -> None:
        # Skips NormalizedPlotOptions.validate: hue and palette describe the user's columns here,
        # RemainderPlot turns them into the normalized hue split.
        CategoricalPlotOptions.validate(self)
        if self.group_by is not None:
            raise ValueError(GROUP_BY_CONFLICT)
        if not self.value:
            raise ValueError("value column must be specified")
        if self.hue is not None and self.hue != self.axis_column:
            raise ValueError(f"With remainder, hue must be the category column {self.axis_column!r} or None.")
        if self.hue is not None and self.legend:
            raise ValueError("legend is not supported when bars are colored by category")
