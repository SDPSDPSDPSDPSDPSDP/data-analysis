import pandas as pd
import pytest

from shirin.plot.core.options import BarPlotOptions, InvalidOrderTypeError


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
