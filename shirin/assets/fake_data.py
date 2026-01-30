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
) -> DataFrame:
    """Generate a DataFrame of events with a `date` column for testing time plots.

    Each day between `start_date` and `end_date` will have a Poisson-distributed
    number of events (approx `avg_events_per_day`). The resulting DataFrame has
    one row per event with a `date` datetime column and a `hue` category.
    """
    np.random.seed(seed)
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    counts = np.random.poisson(lam=avg_events_per_day, size=len(dates))

    rows = []
    for date, count in zip(dates, counts):
        for _ in range(count):
            rows.append({"date": date, "hue": random.choice(["category_1", "category_2"])})

    return pd.DataFrame(rows)


# Existing fake datasets
df, df_documents_by_year = generate_fake_data()
# Time-series fake dataset for testing `timeplot` grouping by day/month/year
df_time = generate_time_series()