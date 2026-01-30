import random
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame


def _create_base_dataframe() -> DataFrame:
    initial_labels = ["A", "B", "A", "C", "B", "B", "C", "A", "A", "C", "D", "E", "F", "A", "B", "C"]
    initial_values = [5, 3, 8, 9, 4, 7, 6, 3, 2, 8, 1, 2, 3, 6, 5, 4]
    
    df = pd.DataFrame({
        "label": initial_labels,
        "values": initial_values,
    })
    
    df["label"] = "Label " + df["label"]
    
    return df


def _expand_dataframe(df: DataFrame, multiplier: int = 10000) -> DataFrame:
    return pd.concat([df] * multiplier, ignore_index=True)


def _generate_middle_weighted_values(num_rows: int, value_range: tuple[int, int] = (1, 101)) -> list[int]:
    min_val, max_val = value_range
    midpoint = (min_val + max_val) // 2
    
    weights = [100 - abs(midpoint - x) for x in range(min_val, max_val)]
    values = [random.choices(range(min_val, max_val), weights=weights)[0] for _ in range(num_rows)]
    
    return values


def _add_category_columns(df: DataFrame) -> DataFrame:
    df["hue"] = [random.choice(["category_1", "category_2"]) for _ in range(len(df))]
    df['hue2'] = df['hue'] == 'category_1'
    return df


def _create_documents_by_year_dataframe() -> DataFrame:
    """Creates dataframe with 2 rows per year (one for each type: True/False)."""
    np.random.seed(42)
    
    start_year = 2000
    end_year = 2023
    years = range(start_year, end_year)
    
    cutoff_year = 2010
    
    rows = []
    cumul_true = 0
    cumul_false = 0
    
    for year in years:
        hue_value = year < cutoff_year
        
        # Generate very different counts for each type
        count_true = np.random.randint(80, 150)
        count_false = np.random.randint(20, 60)
        
        cumul_true += count_true
        cumul_false += count_false
        
        rows.append({
            'year': year,
            'cumul_total_docs': cumul_true,
            'hue': hue_value,
            'type': True
        })
        rows.append({
            'year': year,
            'cumul_total_docs': cumul_false,
            'hue': hue_value,
            'type': False
        })
    
    return pd.DataFrame(rows)


def generate_fake_data() -> tuple[DataFrame, DataFrame]:
    df = _create_base_dataframe()
    df = _expand_dataframe(df)
    df["values"] = _generate_middle_weighted_values(len(df))
    df = _add_category_columns(df)
    
    df_documents_by_year = _create_documents_by_year_dataframe()
    
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
    np.random.seed(seed)

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    years = list(range(start.year, end.year + 1))

    rows = []
    prev_total = 0
    for year in years:
        # determine date range for this year within the global bounds
        year_start = max(start, pd.Timestamp(year=year, month=1, day=1))
        year_end = min(end, pd.Timestamp(year=year, month=12, day=31))
        days = pd.date_range(start=year_start, end=year_end, freq='D')
        n_days = len(days)
        if n_days == 0:
            continue

        # base expected events for the year (approx)
        base_year_events = int(max(1, round(avg_events_per_day * n_days)))

        # ensure strictly increasing yearly totals: choose an increment
        min_increment = max(1, int(round(base_year_events * yearly_growth)))
        noise = int(np.random.normal(loc=0, scale=max(1, base_year_events * 0.05)))
        target_total = max(prev_total + min_increment, base_year_events + noise)

        # distribute target_total across days randomly (multinomial)
        probs = np.ones(n_days) / n_days
        daily_counts = np.random.multinomial(target_total, probs)

        for date, count in zip(days, daily_counts):
            for _ in range(int(count)):
                rows.append({"date": date, "hue": random.choice(["category_1", "category_2"])})

        prev_total = target_total

    return pd.DataFrame(rows)


# Existing fake datasets
df, df_documents_by_year = generate_fake_data()
# Time-series fake dataset for testing `timeplot` grouping by day/month/year
# Use larger yearly_growth by default to produce more extreme increasing totals
df_time = generate_time_series(yearly_growth=0.5)