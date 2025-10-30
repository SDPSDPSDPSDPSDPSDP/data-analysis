
import pandas as pd


def filter_top_n_categories(df: pd.DataFrame, y: str, top_n: int) -> pd.DataFrame:
    top_categories = df[y].value_counts().nlargest(top_n).index
    return df[df[y].isin(top_categories)]
