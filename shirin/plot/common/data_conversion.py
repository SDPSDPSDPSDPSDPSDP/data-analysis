from typing import Optional

import pandas as pd

REMAINDER_SHARE_COL = '__share__'
REMAINDER_LABEL = 'Remainder'
# Reserved name: a user column called 'count' must not collide with the row counts.
COUNT_COL = '__count__'
_PERIODS = {'year': 'Y', 'month': 'M', 'day': 'D'}
_PERIOD_STARTS = {'year': 'YS', 'month': 'MS', 'day': 'D'}


def convert_dict_keys_to_string(d: Optional[dict]) -> Optional[dict]:
    if isinstance(d, dict):
        return {str(key): value for key, value in d.items()}
    return d


def ensure_column_is_string(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = df[col].astype(str)
    return df


def filter_top_n_categories(df: pd.DataFrame, col: str, top_n: int) -> pd.DataFrame:
    if top_n < 1:
        raise ValueError(f"top_n must be at least 1, got {top_n}")
    top_categories = df[col].value_counts().nlargest(top_n).index
    return df[df[col].isin(top_categories)].copy()


def to_period_start(dates: pd.Series, group_by: str) -> pd.Series:
    return pd.to_datetime(dates).dt.to_period(_PERIODS[group_by]).dt.to_timestamp()


def totals_per_x(df: pd.DataFrame, x: str, y: Optional[str], hue: Optional[str], group_by: Optional[str]) -> pd.Series:
    """Sum of y (or the row count when y is None) per x (and hue).

    With group_by, x is bucketed per period and empty periods count as zero, so lines and bars stay continuous.
    """
    if group_by is not None:
        df = df.assign(**{x: to_period_start(df[x], group_by)})
    keys = [x] + ([hue] if hue else [])
    grouped = df.groupby(keys)
    values = grouped.size() if y is None else grouped[y].sum()
    if group_by is None:
        return values
    periods = pd.date_range(values.index.get_level_values(0).min(), values.index.get_level_values(0).max(), freq=_PERIOD_STARTS[group_by])
    if hue:
        index = pd.MultiIndex.from_product([periods, values.index.levels[1]], names=keys)
    else:
        index = pd.Index(periods, name=x)
    return values.reindex(index, fill_value=0)


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
    fill = fills[fill_method]
    df[y] = df.groupby(hue)[y].transform(fill) if hue is not None else fill(df[y])
    return df


def fill_remainder(df: pd.DataFrame, category_col: str, value_col: str, remainder: str) -> pd.DataFrame:
    """Long format: per category one `value_col` row (the fraction) and one `remainder` row (1 - fraction).

    A category may span several rows (e.g. one per hue level) as long as they repeat the same fraction.
    The segment labels go in a column named `value_col`, the shares in REMAINDER_SHARE_COL.
    """
    per_category = df.groupby(category_col, sort=False)[value_col]
    conflicting = per_category.nunique() > 1
    if conflicting.any():
        raise ValueError(
            f"{value_col!r} must be the same on every row of a category when remainder is set; "
            f"differs for {list(conflicting[conflicting].index)}"
        )
    fractions = per_category.first().astype(float)
    if not fractions.between(0, 1).all():
        raise ValueError(f"{value_col!r} must hold fractions in [0, 1] when remainder is set")
    return pd.concat([
        pd.DataFrame({category_col: fractions.index, value_col: value_col, REMAINDER_SHARE_COL: fractions.to_numpy()}),
        pd.DataFrame({category_col: fractions.index, value_col: remainder, REMAINDER_SHARE_COL: 1 - fractions.to_numpy()}),
    ], ignore_index=True)
