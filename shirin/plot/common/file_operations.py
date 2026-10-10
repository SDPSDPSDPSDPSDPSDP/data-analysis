import pandas as pd


def calculate_value_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df_value_counts = df[col].value_counts().to_frame().reset_index()
    df_value_counts.columns = [col, "count"]
    return df_value_counts

