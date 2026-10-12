import pandas as pd
import pytest

from shirin.plot.core import BarPlotOptions, InvalidOptionError, TimePlotOptions


@pytest.mark.parametrize(
    "sort, match",
    [
        ("alpabetical", "Invalid sort"),  # typo
        ("random", "Valid options"),
        ("Alphabetical", "Valid options"),  # uppercase is not normalized
    ],
)
def test_sort_invalid_raises(sort: str, match: str) -> None:
    df = pd.DataFrame({"n_prediction": ["10", "2", "1"], "count": [1, 2, 3]})
    options = BarPlotOptions(df=df, axis_column="n_prediction", value="count", sort=sort)

    with pytest.raises(InvalidOptionError, match=match):
        options.validate()


def test_orientation_invalid_value_shows_valid_options() -> None:
    df = pd.DataFrame({"n_prediction": ["10", "2", "1"], "count": [1, 2, 3]})
    options = BarPlotOptions(
        df=df,
        axis_column="n_prediction",
        value="count",
        orientation="diag",
    )

    with pytest.raises(ValueError, match="Valid options"):
        options.validate()


def test_fill_missing_values_invalid_value_shows_valid_options() -> None:
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    options = TimePlotOptions(df=df, x="x", y="y", fill_missing_values="median")

    with pytest.raises(ValueError, match="Valid options"):
        options.validate()


def test_timeplot_group_by_invalid_value_shows_valid_options() -> None:
    df = pd.DataFrame({"x": ["2024-01-01"], "y": [1]})
    options = TimePlotOptions(df=df, x="x", group_by="week")

    with pytest.raises(ValueError, match="Valid options"):
        options.validate()
