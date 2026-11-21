"""Axis model: ticks, limits and labels of one chart axis."""

from dataclasses import dataclass, field
from typing import Callable, Optional


def plain_number(value: float) -> str:
    return f"{value:g}"


@dataclass
class Axis:
    lim: Optional[tuple[float, float]] = None  # (lo, hi); hi < lo flips the axis
    ticks: Optional[list[float]] = None
    tick_labels: Optional[list[str]] = None
    formatter: Callable[[float], str] = plain_number
    short_formatter: Optional[Callable[[float], str]] = None  # used when formatter's tick labels overlap
    dates: bool = False
    date_format: str = ""
    sticky: tuple[float, ...] = ()  # data limits that get no margin, like the bar baseline
    grid: bool = False
    visible: bool = True
    rotation: float = 0
    label: Optional[str] = None
    sublabel: str = ""  # grey second line under (x) or beside (y) the axis label
    sub_labels: list[tuple[float, str]] = field(default_factory=list)  # a second tick row, e.g. years
    descriptions: list[tuple[float, str]] = field(
        default_factory=list
    )  # grey line under the tick label at that position
