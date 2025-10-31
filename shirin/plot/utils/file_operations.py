import os
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


def calculate_value_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df_value_counts = df[col].value_counts().to_frame().reset_index()
    df_value_counts.columns = [col, "count"]
    return df_value_counts


def validate_format(format: str) -> None:
    supported_formats = ['png', 'svg']
    if format not in supported_formats:
        raise ValueError(
            f"Unsupported format '{format}'. "
            f"Supported formats are {supported_formats}."
        )


def create_filepath(
    output_dir: str,
    prefix: Optional[str],
    output_name: str,
    format: str
) -> str:
    if prefix:
        return os.path.join(output_dir, f"{prefix}_{output_name}.{format}")
    return os.path.join(output_dir, f"{output_name}.{format}")


def save_plot(filepath: str, format: str) -> None:
    plt.savefig(filepath, bbox_inches="tight", dpi=300, format=format)
