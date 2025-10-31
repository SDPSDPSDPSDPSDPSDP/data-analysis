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
    np.random.seed(42)
    
    start_year = 2000
    end_year = 2023
    years = range(start_year, end_year)
    
    min_docs_per_year = 50
    max_docs_per_year = 150
    random_doc_counts = np.random.randint(min_docs_per_year, max_docs_per_year, size=len(years))
    cumulative_docs = np.cumsum(random_doc_counts)
    
    df_documents = pd.DataFrame({
        'year': years,
        'cumul_total_docs': cumulative_docs
    })
    
    cutoff_year = 2010
    df_documents['hue'] = df_documents['year'] < cutoff_year
    
    return df_documents


def generate_fake_data() -> tuple[DataFrame, DataFrame]:
    df = _create_base_dataframe()
    df = _expand_dataframe(df)
    df["values"] = _generate_middle_weighted_values(len(df))
    df = _add_category_columns(df)
    
    df_documents_by_year = _create_documents_by_year_dataframe()
    
    return df, df_documents_by_year


df, df_documents_by_year = generate_fake_data()