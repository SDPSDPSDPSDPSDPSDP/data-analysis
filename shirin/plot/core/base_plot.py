from abc import ABC, abstractmethod
from typing import Any, Optional

import pandas as pd

from .options import BasePlotOptions
from .renderer import PlotRenderer, SeabornRenderer


class AbstractPlot(ABC):
    def __init__(
        self,
        options: BasePlotOptions,
        renderer: Optional[PlotRenderer] = None
    ):
        self.options = options
        self.renderer = renderer or SeabornRenderer()
        self.plot_object: Optional[Any] = None
        self._preprocessed_df: Optional[pd.DataFrame] = None
    
    def render(self) -> Any:
        self.options.validate()
        
        self._preprocessed_df = self.preprocess()
        transformed_data = self.transform(self._preprocessed_df)
        self.plot_object = self.draw(transformed_data)
        self.format_plot(self.plot_object)
        self.finalize(self.plot_object)
        
        return self.plot_object
    
    @abstractmethod
    def preprocess(self) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def transform(self, df: pd.DataFrame) -> Any:
        pass
    
    @abstractmethod
    def draw(self, data: Any) -> Any:
        pass
    
    @abstractmethod
    def format_plot(self, plot: Any) -> None:
        pass
    
    def finalize(self, plot: Any) -> None:
        pass
