import functools
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame


def _create_fruit_dataframe(rng: np.random.Generator, num_rows: int = 300) -> DataFrame:
    fruit_share = {'Apple': .15, 'Banana': .08, 'Cherry': .3, 'Date': .05, 'Mango': .25, 'Fig': .17}
    ripe_share = {'Apple': .8, 'Banana': .25, 'Cherry': .6, 'Date': .4, 'Mango': .9, 'Fig': .15}
    mean_weight = {'Apple': 180, 'Banana': 120, 'Cherry': 8, 'Date': 7, 'Mango': 300, 'Fig': 50}
    fruit = rng.choice(list(fruit_share), num_rows, p=list(fruit_share.values()))
    is_ripe = rng.random(num_rows) < pd.Series(fruit).map(ripe_share).to_numpy()
    mean = pd.Series(fruit).map(mean_weight).to_numpy()
    return pd.DataFrame({
        'fruit': fruit,
        'is_ripe': is_ripe,
        'weight': np.round(rng.normal(mean, mean * 0.15)).clip(1),
    })


def _count_fruit(df: DataFrame) -> DataFrame:
    """Pre-aggregated fruit data: one row per fruit and ripeness, with count."""
    return df.groupby(['fruit', 'is_ripe']).size().reset_index(name='count')


def _create_documents_by_year_dataframe(rng: np.random.Generator) -> DataFrame:
    """Creates dataframe with 2 rows per year (one for each type: True/False)."""
    
    start_year = 2000
    end_year = 2023
    years = range(start_year, end_year)
    
    cutoff_year = 2010
    
    rows = []
    cumul_true = 0
    cumul_false = 0
    
    for year in years:
        hue_value = year < cutoff_year
        
        count_true = int(rng.integers(80, 150))
        count_false = int(rng.integers(20, 60))
        
        cumul_true += count_true
        cumul_false += count_false
        
        rows.append({
            'year': year,
            'cumul_total_docs': cumul_true,
            'example_hue_4': hue_value,
            'example_hue_3': True
        })
        rows.append({
            'year': year,
            'cumul_total_docs': cumul_false,
            'example_hue_4': hue_value,
            'example_hue_3': False
        })
    
    return pd.DataFrame(rows)


def generate_demo_data(seed: int = 0) -> tuple[DataFrame, DataFrame]:
    rng = np.random.default_rng(seed)
    df = _create_fruit_dataframe(rng)

    df_documents_by_year = _create_documents_by_year_dataframe(rng)
    
    return df, df_documents_by_year


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
        if n_days == 0:
            continue

        base_year_events = int(max(1, round(avg_events_per_day * n_days)))

        min_increment = max(1, int(round(base_year_events * yearly_growth)))
        noise = int(rng.normal(loc=0, scale=max(1, base_year_events * 0.05)))
        target_total = max(prev_total + min_increment, base_year_events + noise)

        probs = np.ones(n_days) / n_days
        daily_counts = rng.multinomial(target_total, probs)
        dates.append(days.repeat(daily_counts))

        prev_total = target_total

    all_dates = dates[0].append(dates[1:]) if dates else pd.DatetimeIndex([])
    hues = rng.choice(["category_1", "category_2"], size=len(all_dates))
    return pd.DataFrame({"date": all_dates, "hue": hues})


@functools.lru_cache(maxsize=None)
def _build_lazy_frames() -> dict:
    df, df_documents_by_year = generate_demo_data()
    return {
        'df': df,
        'df_documents_by_year': df_documents_by_year,
        'df_fruit_counts': _count_fruit(df),
        # Larger yearly_growth produces more extreme increasing totals.
        'df_time': generate_time_series(yearly_growth=0.5),
        'df_accuracy': pd.DataFrame({
            'run_name': ['medium', 'nano', 'small'],
            'accuracy': [0.99, 0.71, 0.85],
        }),
    }


def __getattr__(name: str) -> DataFrame:
    """Build the demo frames on first access; each access gets its own copy."""
    frames = _build_lazy_frames() if name in ('df', 'df_documents_by_year', 'df_fruit_counts', 'df_time', 'df_accuracy') else {}
    if name in frames:
        return frames[name].copy()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")