from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


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


class SeabornRenderer(PlotRenderer):
    def create_figure(self, figsize: tuple[float, float]) -> Any:
        return plt.figure(figsize=figsize)
    
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
        return sns.countplot(
            data=df,
            x=x,
            y=y,
            hue=hue,
            order=order,
            color=color,
            palette=palette,
            alpha=1,
            edgecolor='none',
            saturation=1
        )
    
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
        return sns.barplot(
            data=df,
            x=x,
            y=y,
            hue=hue,
            order=order,
            color=color,
            palette=palette,
            alpha=1,
            edgecolor='none',
            saturation=1,
            errorbar=None
        )
    
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
        multiple = 'stack'
        if hue is None:
            multiple = 'stack'
        elif stacked is True:
            multiple = 'stack'
        elif stacked is False:
            multiple = 'dodge'
        else:
            multiple = 'stack'
        
        return sns.histplot(
            data=df,
            x=x,
            bins=bins,
            hue=hue,
            color=color,
            palette=palette,
            multiple=multiple,  # type: ignore
            edgecolor='white',
            alpha=1
        )
    
    def render_lineplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        hue: Optional[str] = None,
        color: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None
    ) -> Any:
        return sns.lineplot(
            data=df,
            x=x,
            y=y,
            hue=hue,
            color=color,
            palette=palette,
            marker='o',
            markersize=4,
            alpha=1
        )
    
    def render_stacked_barplot(
        self,
        df: pd.DataFrame,
        kind: str,
        colors: list[str],
        width: float = 0.6
    ) -> Any:
        return df.plot(
            kind=kind,
            stacked=True,
            color=colors,
            edgecolor='none',
            ax=plt.gca(),
            alpha=1,
            width=width
        )
    
    def render_piechart(
        self,
        values: list[float],
        colors: list[str],
        donut: bool,
        n_after_comma: int,
        value_datalabel: int,
        pctdistance: float
    ) -> Any:
        ax = plt.gca()
        wedgeprops = dict(edgecolor='none', width=0.6 if donut else 1.0)
        result = ax.pie(
            values,
            colors=colors,
            autopct=lambda p: f'{p:.{n_after_comma}f}%' if p >= value_datalabel else '',
            wedgeprops=wedgeprops,
            textprops={'fontsize': 10},
            pctdistance=pctdistance,
        )
        if donut:
            from matplotlib.patches import Circle
            center_circle = Circle((0, 0), 0.6, color='white', fc='white', linewidth=0)
            ax.add_artist(center_circle)
        ax.axis('equal')
        return result

    def get_current_axes(self) -> Any:
        return plt.gca()
