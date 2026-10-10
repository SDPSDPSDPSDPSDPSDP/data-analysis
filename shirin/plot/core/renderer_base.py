from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

import pandas as pd


class PlotRenderer(ABC):
    @abstractmethod
    def create_figure(self, figsize: tuple[float, float]) -> Any:
        pass
    
    @abstractmethod
    def render_countplot(
        self,
        df: pd.DataFrame,
        x: Optional[str] = None,
        y: Optional[str] = None,
        hue: Optional[str] = None,
        order: Optional[Any] = None,
        color: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None
    ) -> Any:
        pass
    
    @abstractmethod
    def render_barplot(
        self,
        df: pd.DataFrame,
        x: Optional[str] = None,
        y: Optional[str] = None,
        hue: Optional[str] = None,
        order: Optional[Any] = None,
        color: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None
    ) -> Any:
        pass
    
    @abstractmethod
    def render_histogram(
        self,
        df: pd.DataFrame,
        x: str,
        bins: int,
        hue: Optional[str] = None,
        color: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None,
        stacked: Optional[bool] = None
    ) -> Any:
        pass
    
    @abstractmethod
    def render_lineplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        hue: Optional[str] = None,
        color: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None
    ) -> Any:
        pass
    
    @abstractmethod
    def render_scatterplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        hue: Optional[str] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None
    ) -> Any:
        pass

    @abstractmethod
    def render_stacked_barplot(
        self,
        df: pd.DataFrame,
        kind: str,
        colors: list[str],
        width: float = 0.6
    ) -> Any:
        pass
    
    @abstractmethod
    def render_piechart(
        self,
        values: list[float],
        colors: list[str],
        donut: bool,
        n_after_comma: int,
        value_datalabel: int,
        pctdistance: float
    ) -> Any:
        pass

    @abstractmethod
    def get_current_axes(self) -> Any:
        pass
