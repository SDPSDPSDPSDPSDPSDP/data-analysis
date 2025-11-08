from abc import ABC, abstractmethod
from typing import Any, Optional

import pandas as pd

from ...config import OrderTypeInput
from .utils.sorting import sort_alphabetically


class OrderingStrategy(ABC):
    @abstractmethod
    def get_order(
        self,
        df: pd.DataFrame,
        column: str,
        value_column: Optional[str] = None
    ) -> Optional[Any]:
        pass


class FrequencyOrderingStrategy(OrderingStrategy):
    def get_order(
        self,
        df: pd.DataFrame,
        column: str,
        value_column: Optional[str] = None
    ) -> Optional[Any]:
        if value_column:
            return df.groupby(column)[value_column].sum().sort_values(ascending=False).index  # type: ignore
        else:
            return df[column].value_counts().sort_values(ascending=False).index


class AlphabeticalOrderingStrategy(OrderingStrategy):
    def get_order(
        self,
        df: pd.DataFrame,
        column: str,
        value_column: Optional[str] = None
    ) -> Optional[Any]:
        return sort_alphabetically(df[column].unique())


class NoOrderingStrategy(OrderingStrategy):
    def get_order(
        self,
        df: pd.DataFrame,
        column: str,
        value_column: Optional[str] = None
    ) -> Optional[Any]:
        return None


def get_ordering_strategy(order_type: OrderTypeInput) -> OrderingStrategy:
    if order_type == 'frequency':
        return FrequencyOrderingStrategy()
    elif order_type == 'alphabetical':
        return AlphabeticalOrderingStrategy()
    else:
        return NoOrderingStrategy()
