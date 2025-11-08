from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

import pandas as pd

from ..config import FigureSize, OrderTypeInput, FigureSizeInput
from ..utils.sorting import get_category_order as _get_category_order


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
        return _get_category_order(df, column, 'frequency', value_column)


class AlphabeticalOrderingStrategy(OrderingStrategy):
    def get_order(
        self,
        df: pd.DataFrame,
        column: str,
        value_column: Optional[str] = None
    ) -> Optional[Any]:
        return _get_category_order(df, column, 'alphabetical', value_column)


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


class FigureSizeStrategy(ABC):
    @abstractmethod
    def calculate_size(
        self,
        df: pd.DataFrame,
        column: str,
        orientation: str
    ) -> tuple[float, float]:
        pass


class DynamicSizeStrategy(FigureSizeStrategy):
    def calculate_size(
        self,
        df: pd.DataFrame,
        column: str,
        orientation: str
    ) -> tuple[float, float]:
        if orientation == 'vertical':
            n_categories = len(df[column].value_counts())
            width = (n_categories * 1) + 1
            height = FigureSize.STANDARD_HEIGHT
        else:
            n_categories = len(df[column].value_counts())
            width = FigureSize.WIDTH
            height = (n_categories / 2) + 1
        return (width, height)


class StandardSizeStrategy(FigureSizeStrategy):
    def calculate_size(
        self,
        df: pd.DataFrame,
        column: str,
        orientation: str
    ) -> tuple[float, float]:
        if orientation == 'vertical':
            return (FigureSize.WIDTH, FigureSize.STANDARD_HEIGHT)
        else:
            return (FigureSize.WIDTH, FigureSize.HEIGHT)


class FixedSizeStrategy(FigureSizeStrategy):
    def __init__(self, size: float, orientation: str):
        self.size = size
        self.orientation = orientation
    
    def calculate_size(
        self,
        df: pd.DataFrame,
        column: str,
        orientation: str
    ) -> tuple[float, float]:
        if orientation == 'vertical':
            return (float(self.size), FigureSize.STANDARD_HEIGHT)
        else:
            return (FigureSize.WIDTH, float(self.size))


def get_figure_size_strategy(
    figsize_input: FigureSizeInput,
    orientation: str
) -> FigureSizeStrategy:
    if figsize_input == 'dynamic':
        return DynamicSizeStrategy()
    elif figsize_input == 'standard':
        return StandardSizeStrategy()
    else:
        return FixedSizeStrategy(float(figsize_input), orientation)


class PaletteStrategy(ABC):
    @abstractmethod
    def get_palette(
        self
    ) -> tuple[Optional[str], Optional[Union[Dict[Any, str], str]]]:
        pass


class DictPaletteStrategy(PaletteStrategy):
    def __init__(self, palette: Dict[Any, str]):
        self.palette = palette
    
    def get_palette(
        self
    ) -> tuple[Optional[str], Optional[Union[Dict[Any, str], str]]]:
        return (None, self.palette)


class NamedPaletteStrategy(PaletteStrategy):
    def __init__(self, palette_name: str):
        self.palette_name = palette_name
    
    def get_palette(
        self
    ) -> tuple[Optional[str], Optional[Union[Dict[Any, str], str]]]:
        return (self.palette_name, None)


class DefaultPaletteStrategy(PaletteStrategy):
    def get_palette(
        self
    ) -> tuple[Optional[str], Optional[Union[Dict[Any, str], str]]]:
        from ..config import Colors
        return (Colors.GREY, None)


def get_palette_strategy(
    palette: Optional[Union[Dict[Any, str], str]]
) -> PaletteStrategy:
    if isinstance(palette, dict):
        return DictPaletteStrategy(palette)
    elif isinstance(palette, str):
        return NamedPaletteStrategy(palette)
    else:
        return DefaultPaletteStrategy()
