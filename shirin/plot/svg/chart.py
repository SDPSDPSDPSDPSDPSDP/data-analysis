"""What a chart contains, in data coordinates. render.py turns it into an SVG."""
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple


def plain_number(value: float) -> str:
    return f'{value:g}'


@dataclass
class Rect:
    x0: float
    x1: float
    y0: float
    y1: float
    color: str
    stroke: Optional[str] = None
    rounded: bool = False  # pill shape; off for stacked/adjacent rects where round ends leave gaps
    clip: Optional['Rect'] = None  # shared outline, e.g. a rounded stack that its segments are cut to
    fade_to: Optional[str] = None  # color the end (y1, or x1 when horizontal) blends into, e.g. the next stack segment
    horizontal: bool = False

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0


@dataclass
class Text:
    """dx/dy shift the text in points (dy up), so labels keep a fixed gap from their bar."""
    x: float
    y: float
    text: str
    color: str
    size: float
    ha: str = 'center'  # left | center | right
    va: str = 'center'  # bottom | center | top
    dx: float = 0
    dy: float = 0


@dataclass
class Line:
    xs: List[float]
    ys: List[float]
    color: str
    width: float = 1.5
    marker_radius: float = 0
    alpha: float = 1


@dataclass
class Dots:
    xs: List[float]
    ys: List[float]
    radii: List[float]
    color: str
    alpha: float = 1


@dataclass
class Wedge:
    """Pie slice centered on (0, 0); start/end are fractions of a turn, clockwise from 12 o'clock."""
    start: float
    end: float
    color: str
    radius: float = 1


@dataclass
class Axis:
    lim: Optional[Tuple[float, float]] = None  # (lo, hi); hi < lo flips the axis
    ticks: Optional[List[float]] = None
    tick_labels: Optional[List[str]] = None
    formatter: Callable[[float], str] = plain_number
    dates: bool = False
    date_format: str = ''
    sticky: Tuple[float, ...] = ()  # data limits that get no margin, like the bar baseline
    grid: bool = False
    show_tick_labels: bool = True
    visible: bool = True
    rotation: float = 0
    label: Optional[str] = None
    sub_labels: List[Tuple[float, str]] = field(default_factory=list)  # a second tick row, e.g. years


@dataclass
class Chart:
    width: Optional[float]  # inches; None makes the plot area square (pie)
    plot_height: float  # inches
    x: Axis = field(default_factory=Axis)
    y: Axis = field(default_factory=Axis)
    rects: List[Rect] = field(default_factory=list)
    lines: List[Line] = field(default_factory=list)
    dots: List[Dots] = field(default_factory=list)
    wedges: List[Wedge] = field(default_factory=list)
    texts: List[Text] = field(default_factory=list)
    legend: List[Tuple[str, str]] = field(default_factory=list)  # (color, label)
    title: str = ''
    subtitle: str = ''

    def data_values(self, axis: str) -> List[float]:
        """Every data coordinate on one axis; texts are excluded so labels never stretch the axis."""
        values: List[float] = []
        for rect in self.rects:
            values += [rect.x0, rect.x1] if axis == 'x' else [rect.y0, rect.y1]
        for series in [*self.lines, *self.dots]:
            values += list(series.xs if axis == 'x' else series.ys)
        return values
