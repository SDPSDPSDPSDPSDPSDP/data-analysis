"""Demo time series for the time plot examples."""

import numpy as np
import pandas as pd
from pandas import DataFrame


def generate_time_series(
    start_date: str = "2018-01-01",
    end_date: str = "2023-12-31",
    avg_events_per_day: float = 3.0,
    seed: int = 42,
    yearly_growth: float = 0.5,
) -> DataFrame:
    """Generate a DataFrame of events with a `date` column for testing time plots.

    This generator ensures that yearly totals increase each year. For each
    calendar year in the range, it computes a target number of events that is
    at least slightly larger than the previous year's total (controlled by
    `yearly_growth`), then randomly distributes those events across the days
    of that year.
    """
    rng = np.random.default_rng(seed)

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    years = list(range(start.year, end.year + 1))

    dates: list[pd.DatetimeIndex] = []
    prev_total = 0
    for year in years:
        year_start = max(start, pd.Timestamp(year=year, month=1, day=1))
        year_end = min(end, pd.Timestamp(year=year, month=12, day=31))
        days = pd.date_range(start=year_start, end=year_end, freq="D")
        n_days = len(days)
        base_year_events = int(max(1, round(avg_events_per_day * n_days)))

        min_increment = max(1, round(float(base_year_events * yearly_growth)))
        noise = int(rng.normal(loc=0, scale=max(1, base_year_events * 0.05)))
        target_total = max(prev_total + min_increment, base_year_events + noise)

        probs = np.ones(n_days) / n_days
        daily_counts = rng.multinomial(target_total, probs)
        dates.append(days.repeat(daily_counts))

        prev_total = target_total

    if not dates:
        raise ValueError(f"start_date {start_date} is after end_date {end_date}")
    return pd.DataFrame({"date": dates[0].append(dates[1:])})
