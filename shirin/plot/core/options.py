from dataclasses import dataclass
from typing import Any, ClassVar, Optional, Union

import pandas as pd

from .base_options import (
    BasePlotOptions,
)

MARK_LABELS = ("x", "y", "both", None)


@dataclass
class HistogramOptions(BasePlotOptions):
    column_fields: ClassVar[tuple[str, ...]] = ("hue", "x")

    x: str = ""
    xlimit: Optional[Union[float, int]] = None
    bins: int = 100
    stacked: Optional[bool] = None
    suffix: Optional[str] = None

    def validate(self) -> None:
        super().validate()
        if not self.x:
            raise ValueError("x column must be specified")
        if self.bins <= 0:
            raise ValueError("bins must be positive")


@dataclass
class ScatterPlotOptions(BasePlotOptions):
    column_fields: ClassVar[tuple[str, ...]] = ("hue", "x", "y", "size")

    x: str = ""
    y: str = ""
    size: Optional[str] = None

    def validate(self) -> None:
        super().validate()
        if not self.x:
            raise ValueError("x column must be specified")
        if not self.y:
            raise ValueError("y column must be specified")


def _validate_limits(name: str, limits: Optional[tuple[float, float]]) -> None:
    if limits is None:
        return
    if len(limits) != 2 or limits[0] == limits[1]:
        raise ValueError(f"{name} must be two different numbers (low, high), got {limits!r}")


@dataclass
class LinePlotOptions(BasePlotOptions):
    column_fields: ClassVar[tuple[str, ...]] = ("hue", "x", "y", "marks")

    x: str = ""
    y: str = ""
    marks: Optional[str] = None
    mark_labels: Optional[str] = "y"
    percentage_x: bool = False
    percentage_y: bool = False
    x_limits: Optional[tuple[float, float]] = None
    y_limits: Optional[tuple[float, float]] = None

    def validate(self) -> None:
        super().validate()
        for name in ("x", "y"):
            column = getattr(self, name)
            if not column:
                raise ValueError(f"{name} column must be specified")
            if not pd.api.types.is_numeric_dtype(self.df[column]):
                raise ValueError(
                    f"{name}={column!r} must be numeric, got dtype {self.df[column].dtype}; use time() for dates"
                )
        _validate_limits("x_limits", self.x_limits)
        _validate_limits("y_limits", self.y_limits)
        if self.marks is not None:
            marks = self.df[self.marks]
            if not pd.api.types.is_bool_dtype(marks) or marks.isna().any():
                raise ValueError(
                    f"marks={self.marks!r} must be a boolean column without missing values, got dtype {marks.dtype}"
                )
        if self.mark_labels not in MARK_LABELS:
            raise ValueError(f"mark_labels must be one of {MARK_LABELS}, got {self.mark_labels!r}")


@dataclass
class PiePlotOptions(BasePlotOptions):
    column_fields: ClassVar[tuple[str, ...]] = ("col",)

    col: str = ""
    n_after_comma: int = 0
    value_datalabel: int = 5
    donut: bool = False
    legend_percentages: bool = False
    slice_labels: Optional[dict[Any, str]] = None  # {slice value: headline drawn above its percentage}

    def validate(self) -> None:
        super().validate()
        if not self.col:
            raise ValueError("col must be specified")
