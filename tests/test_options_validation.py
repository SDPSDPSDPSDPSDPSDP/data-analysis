import pandas as pd
import pytest

from shirin.plot.core.options import BarPlotOptions, InvalidOrderTypeError, LinePlotOptions, TimePlotOptions


def test_order_type_typo_alpabetical_raises() -> None:
    df = pd.DataFrame({"n_prediction": ["10", "2", "1"], "count": [1, 2, 3]})
    options = BarPlotOptions(df=df, axis_column="n_prediction", value="count", order_type="alpabetical")

    with pytest.raises(InvalidOrderTypeError, match="Invalid order_type"):
        options.validate()


def test_order_type_invalid_value_raises() -> None:
    df = pd.DataFrame({"n_prediction": ["10", "2", "1"], "count": [1, 2, 3]})
    options = BarPlotOptions(df=df, axis_column="n_prediction", value="count", order_type="random")

    with pytest.raises(InvalidOrderTypeError, match="Valid options"):
        options.validate()


def test_order_type_uppercase_is_not_normalized_and_raises() -> None:
    df = pd.DataFrame({"n_prediction": ["10", "2", "1"], "count": [1, 2, 3]})
    options = BarPlotOptions(df=df, axis_column="n_prediction", value="count", order_type="Alphabetical")

    with pytest.raises(InvalidOrderTypeError, match="Valid options"):
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
    options = LinePlotOptions(df=df, x="x", y="y", fill_missing_values="median")

    with pytest.raises(ValueError, match="Valid options"):
        options.validate()


def test_timeplot_group_by_invalid_value_shows_valid_options() -> None:
    df = pd.DataFrame({"x": ["2024-01-01"], "y": [1]})
    options = TimePlotOptions(df=df, x="x", group_by="week")

    with pytest.raises(ValueError, match="Valid options"):
        options.validate()
