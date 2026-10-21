import functools

import numpy as np
import pandas as pd
from pandas import DataFrame


def _create_fruit_dataframe(rng: np.random.Generator, num_rows: int = 60000) -> DataFrame:
    fruit_share = {'Apple': .15, 'Banana': .08, 'Cherry': .3, 'Date': .05, 'Orange': .25, 'Fig': .17}
    ripe_share = {'Apple': .8, 'Banana': .25, 'Cherry': .6, 'Date': .4, 'Orange': .9, 'Fig': .15}
    fruit = rng.choice(list(fruit_share), num_rows, p=list(fruit_share.values()))
    is_ripe = rng.random(num_rows) < pd.Series(fruit).map(ripe_share).to_numpy()
    return pd.DataFrame({
        'fruit': fruit,
        'is_ripe': is_ripe,
        'sweetness': np.round(rng.normal(np.where(is_ripe, 14, 11), 2.5), 2),
    })


def _count_fruit(df: DataFrame) -> DataFrame:
    """Pre-aggregated fruit data: one row per fruit and ripeness, with count and the fruit's share sold."""
    sold_share = {'Apple': .92, 'Banana': .7, 'Cherry': .85, 'Date': .55, 'Orange': .97, 'Fig': .6}
    counts = df.groupby(['fruit', 'is_ripe']).size().reset_index(name='count')
    counts['sold_share'] = counts['fruit'].map(sold_share)
    return counts


def _create_harvest_by_year_dataframe(rng: np.random.Generator) -> DataFrame:
    """Two rows per year 2000-2022 (is_ripe True/False) with cumulative harvest counts."""
    rows = []
    cumul = {True: 0, False: 0}
    for year in range(2000, 2023):
        cumul[True] += int(rng.integers(80, 150))
        cumul[False] += int(rng.integers(20, 60))
        for is_ripe in (True, False):
            rows.append({'year': year, 'n_harvested': cumul[is_ripe], 'is_ripe': is_ripe})
    return pd.DataFrame(rows)


def generate_demo_data(seed: int = 0) -> tuple[DataFrame, DataFrame]:
    rng = np.random.default_rng(seed)
    return _create_fruit_dataframe(rng), _create_harvest_by_year_dataframe(rng)


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
        days = pd.date_range(start=year_start, end=year_end, freq='D')
        n_days = len(days)
        base_year_events = int(max(1, round(avg_events_per_day * n_days)))

        min_increment = max(1, int(round(base_year_events * yearly_growth)))
        noise = int(rng.normal(loc=0, scale=max(1, base_year_events * 0.05)))
        target_total = max(prev_total + min_increment, base_year_events + noise)

        probs = np.ones(n_days) / n_days
        daily_counts = rng.multinomial(target_total, probs)
        dates.append(days.repeat(daily_counts))

        prev_total = target_total

    if not dates:
        raise ValueError(f"start_date {start_date} is after end_date {end_date}")
    return pd.DataFrame({"date": dates[0].append(dates[1:])})


@functools.lru_cache(maxsize=None)
def _build_lazy_frames() -> dict:
    df, df_harvest_by_year = generate_demo_data()
    return {
        'df': df,
        'df_harvest_by_year': df_harvest_by_year,
        'df_fruit_counts': _count_fruit(df),
        'df_time': generate_time_series(),
    }


def __getattr__(name: str) -> DataFrame:
    """Build the demo frames on first access; each access gets its own copy."""
    if name not in ('df', 'df_harvest_by_year', 'df_fruit_counts', 'df_time'):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return _build_lazy_frames()[name].copy()