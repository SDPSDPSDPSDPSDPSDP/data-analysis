"""What a chart contains, in data coordinates. render.py turns it into an SVG."""

from dataclasses import dataclass, field
from typing import Callable, Optional, Union


def plain_number(value: float) -> str:
    return f"{value:g}"


@dataclass
class Rect:
    x0: float
    x1: float
    y0: float
    y1: float
    color: str
    rounded: bool = False  # pill shape; off for stacked/adjacent rects where round ends leave gaps
    clip: Optional["Rect"] = None  # shared outline, e.g. a rounded stack that its segments are cut to
    fade_to: Optional[str] = None  # color the end (y1, or x1 when horizontal) blends into, e.g. the next stack segment
    horizontal: bool = False
    # Rounded pill drawn behind another pill from the same base that ends at this value: starts under that pill's cap.
    tuck: Optional[float] = None

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
    ha: str = "center"  # left | center | right
    va: str = "center"  # bottom | center | top
    dx: float = 0
    dy: float = 0
    short_text: Optional[str] = None  # shown instead when side-by-side labels leave too little room
    # Data slope of the line at a point label: layout moves the label above the line where it falls to the right.
    slope: Optional[float] = None
    alpha: float = 1
    # Dark theme leaves the color alone: text on a bar or wedge already contrasts with that fill, and a point
    # label shares its line's data color, which theming would turn into the background.
    keep_color: bool = False
    # Smaller, faded text before each line of text (one per line), e.g. the axis name before a mark's value.
    line_titles: tuple[str, ...] = ()
    # Layout wraps each line to this width in points; newlines already in text stay.
    wrap_width: Optional[float] = None
    # Text this one stacks on top of: layout centers the pair on their shared point, e.g. a pie headline over
    # its percentage. Must also be in the chart's texts.
    above: Optional["Text"] = None


@dataclass
class Line:
    xs: list[float]
    ys: list[float]
    color: str
    fill: bool = False  # gradient area from the line down to the plot bottom


@dataclass
class Dots:
    xs: list[float]
    ys: list[float]
    radii: list[float]
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


@dataclass
class Chart:
    width: Optional[float]  # inches; None makes the plot area square (pie)
    plot_height: float  # inches
    x: Axis = field(default_factory=Axis)
    y: Axis = field(default_factory=Axis)
    rects: list[Rect] = field(default_factory=list)
    lines: list[Line] = field(default_factory=list)
    dots: list[Dots] = field(default_factory=list)
    wedges: list[Wedge] = field(default_factory=list)
    texts: list[Text] = field(default_factory=list)
    donut_hole: float = 0  # radius of the background-colored pie center; 0 = full pie
    legend: list[tuple[str, str, str]] = field(
        default_factory=list
    )  # (color, label, value shown lighter after the label)
    title: str = ""
    subtitle: str = ""

    def data_values(self, axis: str) -> list[float]:
        """Every data coordinate on one axis; texts are excluded so labels never stretch the axis."""
        values: list[float] = []
        for rect in self.rects:
            values += [rect.x0, rect.x1] if axis == "x" else [rect.y0, rect.y1]
        all_series: list[Union[Line, Dots]] = [*self.lines, *self.dots]
        for series in all_series:
            values += list(series.xs if axis == "x" else series.ys)
        return values
