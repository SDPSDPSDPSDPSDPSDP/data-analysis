import functools

import numpy as np
import pandas as pd
from pandas import DataFrame

FRUIT_DESCRIPTIONS = {
    'Apple': 'Crisp, keeps for months',
    'Banana': 'Ripens fast after picking',
    'Cherry': 'Short summer season',
    'Date': 'Dried, very sweet',
    'Orange': 'Winter citrus',
    'Fig': 'Soft, bruises easily',
}


def _create_fruit_dataframe(rng: np.random.Generator, num_rows: int = 60000) -> DataFrame:
    fruit_share = {'Apple': .15, 'Banana': .08, 'Cherry': .3, 'Date': .05, 'Orange': .25, 'Fig': .17}
    ripe_share = {'Apple': .8, 'Banana': .25, 'Cherry': .6, 'Date': .4, 'Orange': .9, 'Fig': .15}
    fruit = rng.choice(list(fruit_share), num_rows, p=list(fruit_share.values()))
    is_ripe = rng.random(num_rows) < pd.Series(fruit).map(ripe_share).to_numpy()
    return pd.DataFrame({
        'fruit': fruit,
        'is_ripe': is_ripe,
        'sweetness': np.round(rng.normal(np.where(is_ripe, 14, 11), 2.5), 2),
        'description': pd.Series(fruit).map(FRUIT_DESCRIPTIONS).to_numpy(),
    })


def _count_fruit(df: DataFrame) -> DataFrame:
    """Pre-aggregated fruit data: one row per fruit and ripeness, with count, the fruit's share sold and description."""
    sold_share = {'Apple': .92, 'Banana': .7, 'Cherry': .85, 'Date': .55, 'Orange': .97, 'Fig': .6}
    counts = df.groupby(['fruit', 'is_ripe']).size().reset_index(name='count')
    counts['sold_share'] = counts['fruit'].map(sold_share)
    counts['description'] = counts['fruit'].map(FRUIT_DESCRIPTIONS)
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


def _create_threshold_curve_dataframe(
    rng: np.random.Generator, num_fruits: int = 5000, sharpness: float = 20,
) -> DataFrame:
    """Ripeness detector: per probability threshold, the share of fruits it is that sure about and its accuracy on them.

    marked is True on a few highlighted thresholds. Lower sharpness = better detector: accuracy climbs sooner.
    """
    probability = rng.beta(5, 1.5, num_fruits)
    # Expected correctness instead of a random draw keeps the curve smooth where few fruits remain
    # High power makes accuracy stay flat until only the surest fruits remain: a clearly bent curve
    chance_correct = 0.5 + 0.5 * probability ** sharpness
    thresholds = np.round(np.arange(0, 1, 0.01), 2)
    above = probability[None, :] >= thresholds[:, None]
    df = pd.DataFrame({
        'threshold': thresholds,
        'coverage': above.mean(axis=1),
        'accuracy': (above * chance_correct).sum(axis=1) / above.sum(axis=1),
    })
    df['marked'] = df['threshold'].isin([0.5, 0.8, 0.9, 0.95])
    return df


def _create_threshold_curves_dataframe() -> DataFrame:
    """Threshold curves of two ripeness detectors stacked, told apart by the detector column."""
    detectors = {'Old detector': 20, 'New detector': 6}
    return pd.concat(
        [
            _create_threshold_curve_dataframe(np.random.default_rng(0), sharpness=sharpness).assign(detector=name)
            for name, sharpness in detectors.items()
        ],
        ignore_index=True,
    )


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
        'df_threshold_curve': _create_threshold_curve_dataframe(np.random.default_rng(0)),
        'df_threshold_curves': _create_threshold_curves_dataframe(),
    }


def __getattr__(name: str) -> DataFrame:
    """Build the demo frames on first access; each access gets its own copy."""
    if name not in _build_lazy_frames():
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return _build_lazy_frames()[name].copy()