from abc import ABC, abstractmethod

import pandas as pd

from ..config import FigureSize, FigureSizeInput


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
