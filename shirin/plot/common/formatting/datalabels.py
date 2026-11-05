from typing import Optional

from ....number_format import format_compact, format_percentage, format_thousands
from ...config import FontSizes, Layout, TextColors
from ...svg import Chart, Rect, Text


def _length(rect: Rect, orientation: str) -> float:
    return rect.height if orientation == 'vertical' else rect.width


def _add_text(chart: Chart, rect: Rect, text: str, orientation: str, short_text: Optional[str] = None) -> None:
    """Label just past the bar's end: above/right of positive bars, below/left of negative ones."""
    sign = 1 if _length(rect, orientation) >= 0 else -1
    gap = Layout.DATALABEL_GAP * sign
    if orientation == 'vertical':
        va = 'bottom' if sign > 0 else 'top'
        label = Text((rect.x0 + rect.x1) / 2, rect.y1, text, TextColors.FAINT_GREY, FontSizes.DATALABELS, 'center', va, dy=gap, short_text=short_text)
    else:
        # No short_text: crowding is only checked between side-by-side (vertical) labels.
        ha = 'left' if sign > 0 else 'right'
        label = Text(rect.x1, (rect.y0 + rect.y1) / 2, text, TextColors.FAINT_GREY, FontSizes.DATALABELS, ha, 'center', dx=gap)
    chart.texts.append(label)


def format_datalabels(
    chart: Chart,
    formatting: str = 'totals',
    orientation: str = 'vertical',
    suffix: Optional[str] = None,
    compact: bool = False,
) -> None:
    rects = chart.rects
    lengths = [_length(r, orientation) for r in rects]
    total = sum(lengths)

    for rect, length in zip(rects, lengths):
        if length == 0:
            continue
        if formatting == 'percentage':
            share = length / total * 100 if total > 0 else 0
            _add_text(chart, rect, percentage_label(share, 1, suffix), orientation)
        elif compact:
            _add_text(chart, rect, with_suffix(format_compact(length), suffix), orientation)
        else:
            full = with_suffix(format_thousands(length), suffix)
            short = with_suffix(format_compact(length), suffix)
            _add_text(chart, rect, full, orientation, short)


def with_suffix(text: str, suffix: Optional[str]) -> str:
    return f'{text} {suffix.strip()}' if suffix and suffix.strip() else text


def percentage_label(percentage: float, decimals: int, suffix: Optional[str]) -> str:
    """A suffix replaces the '%' sign; an empty suffix drops it."""
    if suffix is None:
        return format_percentage(percentage, decimals)
    return with_suffix(format_thousands(percentage, decimals), suffix)
