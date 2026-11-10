"""Axis limits, scales and tick selection for the SVG layout."""
from typing import List, Optional, Tuple

from ..config import FontSizes, Layout, TextColors
from .chart import Axis
from .fonts import text_width, wrap_text
from .marks import Scale
from .ticks import date_ticks, nice_ticks

Ticks = List[Tuple[float, str]]


def limits(axis: Axis, values: List[float]) -> Tuple[float, float]:
    if axis.lim is not None:
        return axis.lim
    values = [v for v in values if v == v]
    if not values:
        raise ValueError("Chart has no data to scale the axis on")
    lo, hi = min(values), max(values)
    if lo == hi:
        lo, hi = lo - 0.5, hi + 0.5
    pad = (hi - lo) * Layout.AXIS_MARGIN
    if lo not in axis.sticky:
        lo -= pad
    if hi not in axis.sticky:
        hi += pad
    return (lo, hi)


def ticks(axis: Axis, lo: float, hi: float) -> Ticks:
    if not axis.visible:
        return []
    if axis.ticks is not None:
        labels = axis.tick_labels if axis.tick_labels is not None else [axis.formatter(t) for t in axis.ticks]
        if len(labels) != len(axis.ticks):
            raise ValueError(f"Axis has {len(axis.ticks)} ticks but {len(labels)} tick labels")
        ticks = list(zip(axis.ticks, labels))
    elif axis.dates:
        ticks = list(zip(*date_ticks(lo, hi, fmt=axis.date_format)))
    else:
        ticks = [(t, axis.formatter(t)) for t in nice_ticks(lo, hi)]
    low, high = min(lo, hi) - 1e-9, max(lo, hi) + 1e-9
    return [(t, label) for t, label in ticks if low <= t <= high]


def tick_color(axis: Axis, other: Axis) -> str:
    """Value ticks opposite category labels are lighter, so the categories lead."""
    is_value_axis = axis.tick_labels is None and other.tick_labels is not None
    return TextColors.LIGHT_GREY if is_value_axis else TextColors.DARK_GREY


def description_lines(axis: Axis, position: float, sx: Optional[Scale] = None) -> List[str]:
    """The description under the tick at position, wrapped; empty when it has none.

    Pass the x scale for an x-axis: its descriptions also wrap to the space between ticks, so neighbours do not overlap.
    """
    max_width = float(Layout.DESCRIPTION_MAX_WIDTH)
    if sx is not None and axis.ticks is not None and len(axis.ticks) > 1:
        tick_spacing = abs(sx(axis.ticks[1]) - sx(axis.ticks[0]))
        max_width = min(max_width, tick_spacing - Layout.TICK_LABEL_MIN_SPACE)
    return wrap_text(dict(axis.descriptions).get(position, ''), FontSizes.DESCRIPTION, max_width)


def tick_label_width(axis: Axis, position: float, label: str, sx: Optional[Scale] = None) -> float:
    """Widest of the tick label and its description lines; sx as in description_lines."""
    lines = description_lines(axis, position, sx)
    return max([text_width(label, FontSizes.TICKS)] + [text_width(line, FontSizes.DESCRIPTION) for line in lines])


def scale(lo: float, hi: float, start: float, end: float) -> Scale:
    if lo == hi:
        raise ValueError(f"Axis limits are equal ({lo}), so there is no range to scale on")
    return lambda v: start + (v - lo) / (hi - lo) * (end - start)


def _x_labels_overlap(axis: Axis, ticks: Ticks, sx: Scale) -> bool:
    widths = [(t, tick_label_width(axis, t, label, sx)) for t, label in ticks if label]
    # Sorted on screen position: a flipped axis (x_limits=(1, 0)) lists its ticks right to left.
    spans = sorted((sx(t) - w / 2, sx(t) + w / 2) for t, w in widths)
    return any(right[0] - left[1] < Layout.TICK_LABEL_MIN_SPACE for left, right in zip(spans, spans[1:]))


def fit_x_ticks(axis: Axis, ticks: Ticks, sx: Scale) -> Ticks:
    """Short labels when the full ones overlap, then only every nth label; unlabelled ticks keep their grid line."""
    if axis.rotation or not _x_labels_overlap(axis, ticks, sx):
        return ticks
    if axis.short_formatter is not None and axis.tick_labels is None and not axis.dates:
        ticks = [(t, axis.short_formatter(t)) for t, _ in ticks]
    step = 1
    thinned = ticks
    while _x_labels_overlap(axis, thinned, sx) and step < len(ticks):
        step += 1
        thinned = [(t, label if i % step == 0 else '') for i, (t, label) in enumerate(ticks)]
    return thinned
