import pandas as pd
from typing import Optional

REMAINDER_SHARE_COL = '__share__'


def convert_dict_keys_to_string(d: Optional[dict]) -> Optional[dict]:
    if isinstance(d, dict):
        return {str(key): value for key, value in d.items()}
    return d


def ensure_column_is_string(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = df[col].astype(str)
    return df


def filter_top_n_categories(df: pd.DataFrame, col: str, top_n: int) -> pd.DataFrame:
    top_categories = df[col].value_counts().nlargest(top_n).index
    return df[df[col].isin(top_categories)].copy()


def fill_missing_values_in_data(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str],
    fill_method: str
) -> pd.DataFrame:
    fills = {
        'shift': lambda s: s.interpolate(method='linear', limit_direction='forward'),
        'zero': lambda s: s.fillna(0),
    }
    # 'shift' interpolates between neighbours along x, so rows must be in x order.
    df = df.sort_values(x)
    fill = fills.get(fill_method)
    if fill is not None:
        df[y] = df.groupby(hue)[y].transform(fill) if hue is not None else fill(df[y])
    return df


def fill_remainder(df: pd.DataFrame, category_col: str, value_col: str, remainder: str) -> pd.DataFrame:
    """Long format: per category one `value_col` row (the fraction) and one `remainder` row (1 - fraction).

    The segment labels go in a column named `value_col`, the shares in REMAINDER_SHARE_COL.
    """
    if df[category_col].duplicated().any():
        raise ValueError(f"{category_col!r} must have one row per category when remainder is set")
    fractions = df[value_col].astype(float)
    if not fractions.between(0, 1).all():
        raise ValueError(f"{value_col!r} must hold fractions in [0, 1] when remainder is set")
    return pd.concat([
        pd.DataFrame({category_col: df[category_col], value_col: value_col, REMAINDER_SHARE_COL: fractions}),
        pd.DataFrame({category_col: df[category_col], value_col: remainder, REMAINDER_SHARE_COL: 1 - fractions}),
    ], ignore_index=True)
