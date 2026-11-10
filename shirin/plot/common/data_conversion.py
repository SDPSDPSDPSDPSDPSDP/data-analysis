from typing import Any, Dict, Optional

import pandas as pd

REMAINDER_SHARE_COL = '__share__'
REMAINDER_LABEL = 'Remainder'
# Reserved name: a user column called 'count' must not collide with the row counts.
COUNT_COL = '__count__'
_PERIODS = {'year': 'Y', 'month': 'M', 'day': 'D'}
_PERIOD_STARTS = {'year': 'YS', 'month': 'MS', 'day': 'D'}
# ISO labels sort alphabetically in time order.
_PERIOD_LABELS = {'year': '%Y', 'month': '%Y-%m', 'day': '%Y-%m-%d'}


def convert_dict_keys_to_string(d: Optional[dict]) -> Optional[dict]:
    if isinstance(d, dict):
        return {str(key): value for key, value in d.items()}
    return d


def ensure_column_is_string(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = df[col].astype(str)
    return df


def category_descriptions(df: pd.DataFrame, category_col: str, description_col: str) -> Dict[str, str]:
    """{category: description}, keyed by str(category) like the tick labels. Categories without one are left out.

    Raises when a category has more than one distinct description.
    """
    if description_col not in df.columns:
        raise ValueError(f"description={description_col!r} is not a column. Available columns: {list(df.columns)}")
    described = df[[category_col, description_col]].dropna()
    conflicting = described.groupby(category_col)[description_col].nunique() > 1
    if conflicting.any():
        raise ValueError(
            f"{description_col!r} must be the same on every row of a category; "
            f"differs for {list(conflicting[conflicting].index)}"
        )
    return {str(category): str(text) for category, text in described.drop_duplicates(category_col).to_numpy()}


def filter_top_n_categories(df: pd.DataFrame, col: str, top_n: int) -> pd.DataFrame:
    if top_n < 1:
        raise ValueError(f"top_n must be at least 1, got {top_n}")
    top_categories = df[col].value_counts().nlargest(top_n).index
    return df[df[col].isin(top_categories)].copy()


def to_period_start(dates: pd.Series, group_by: str) -> pd.Series:
    return pd.to_datetime(dates).dt.to_period(_PERIODS[group_by]).dt.to_timestamp()


def aggregate(df: pd.DataFrame, column: str, value: Optional[str] = None, hue: Optional[str] = None) -> Any:
    """Sum of value (or the row count when value is None) per column value.

    Returns a Series, or with hue a table of categories x hue levels with NaN for missing pairs.
    """
    keys = [column] + ([hue] if hue else [])
    grouped = df.groupby(keys)
    totals = grouped[value].sum() if value else grouped.size()
    return totals.unstack() if hue else totals


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
    dates = values.index.get_level_values(0)
    periods = pd.date_range(dates.min(), dates.max(), freq=_PERIOD_STARTS[group_by])
    if hue:
        index = pd.MultiIndex.from_product([periods, values.index.levels[1]], names=keys)
    else:
        index = pd.Index(periods, name=x)
    return values.reindex(index, fill_value=0)


def period_totals(df: pd.DataFrame, x: str, y: Optional[str], hue: Optional[str], group_by: str) -> pd.DataFrame:
    """One row per period (and hue): the period's ISO label in x, its total in y (COUNT_COL when y is None)."""
    totals = totals_per_x(df, x, y, hue, group_by).rename(y or COUNT_COL).reset_index()
    totals[x] = totals[x].dt.strftime(_PERIOD_LABELS[group_by])
    return totals


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
    shares = fractions.to_numpy()
    return pd.concat([
        pd.DataFrame({category_col: fractions.index, value_col: value_col, REMAINDER_SHARE_COL: shares}),
        pd.DataFrame({category_col: fractions.index, value_col: remainder, REMAINDER_SHARE_COL: 1 - shares}),
    ], ignore_index=True)
