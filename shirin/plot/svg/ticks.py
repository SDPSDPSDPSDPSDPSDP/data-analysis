import math
from typing import List, Tuple

import pandas as pd

_EPOCH = pd.Timestamp(0)
_DAY = pd.Timedelta(days=1)

# (pandas frequency, label format), finest first; the first one that fits is used.
_DATE_STEPS = (
    ('D', '%Y-%m-%d'), ('2D', '%Y-%m-%d'), ('7D', '%Y-%m-%d'), ('14D', '%Y-%m-%d'),
    ('MS', '%b %Y'), ('2MS', '%b %Y'), ('3MS', '%b %Y'), ('6MS', '%b %Y'),
    ('YS', '%Y'), ('2YS', '%Y'), ('5YS', '%Y'), ('10YS', '%Y'), ('20YS', '%Y'), ('50YS', '%Y'), ('100YS', '%Y'),
)


def to_days(dates: pd.Series) -> pd.Series:
    """Datetimes as float days since 1970, so a time axis is an ordinary linear axis."""
    return (pd.to_datetime(dates) - _EPOCH) / _DAY


def from_days(days: float) -> pd.Timestamp:
    return _EPOCH + days * _DAY


def nice_ticks(lo: float, hi: float, count: int = 5) -> List[float]:
    """Round tick values (steps of 1, 2, 2.5 or 5 times a power of ten) inside [lo, hi]."""
    lo, hi = min(lo, hi), max(lo, hi)
    if hi == lo:
        return [lo]
    raw = (hi - lo) / count
    magnitude = 10 ** math.floor(math.log10(raw))
    step = next(m * magnitude for m in (1, 2, 2.5, 5, 10) if raw <= m * magnitude)
    first, last = math.ceil(lo / step - 1e-9), math.floor(hi / step + 1e-9)
    return [round(i * step, 12) for i in range(first, last + 1)]


def date_ticks(lo: float, hi: float, max_ticks: int = 8, fmt: str = '') -> Tuple[List[float], List[str]]:
    """Day/month/year ticks between two day numbers; fmt overrides the step's own format."""
    lo, hi = min(lo, hi), max(lo, hi)
    start, end = from_days(lo).ceil('D'), from_days(hi)
    for freq, step_fmt in _DATE_STEPS:
        dates = pd.date_range(start, end, freq=freq)
        if len(dates) <= max_ticks:
            return list(to_days(pd.Series(dates))), [d.strftime(fmt or step_fmt) for d in dates]
    raise ValueError(f"Date range {start} - {end} is too long for date ticks")

