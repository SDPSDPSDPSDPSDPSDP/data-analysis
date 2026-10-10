from typing import Any, Dict, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import Circle


class SeabornRenderer:
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
        multiple = 'dodge' if hue is not None and stacked is False else 'stack'
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
        return sns.scatterplot(
            data=df,
            x=x,
            y=y,
            hue=hue,
            size=size,
            color=color,
            palette=palette,
            alpha=0.8,
            edgecolor='none'
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
    
    def render_time_bars(self, dates: pd.Series, counts: pd.Series, color: Optional[str], width: float) -> Any:
        ax = plt.gca()
        ax.bar(dates, counts, color=color, edgecolor='none', alpha=1, width=width)
        return ax

    def render_time_line(self, dates: pd.Series, counts: pd.Series, color: str, show_markers: bool) -> Any:
        ax = plt.gca()
        ax.plot(
            dates,
            counts,
            color=color,
            linewidth=2,
            marker='o' if show_markers else None,
            markersize=3 if show_markers else 0,
            markerfacecolor=color,
            markeredgecolor=color,
            markeredgewidth=0,
            alpha=0.9,
        )
        return ax

    def render_piechart(
        self,
        values: list[float],
        colors: list[str],
        donut: bool,
        n_after_comma: int,
        value_datalabel: int,
        pctdistance: float
    ) -> tuple[Any, list]:
        """Draw on the current axes; returns (axes, percentage text artists)."""
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
            center_circle = Circle((0, 0), 0.6, color='white', fc='white', linewidth=0)
            ax.add_artist(center_circle)
        ax.axis('equal')
        autotexts = result[2] if len(result) > 2 else []
        return ax, autotexts
