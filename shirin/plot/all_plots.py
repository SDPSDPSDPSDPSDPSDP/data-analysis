import os
from typing import Any, Dict, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd

from .config import OrderTypeInput, StackedLabelTypeInput, FigureSizeInput
from .plots import (
    countplot_x,
    countplot_x_normalized,
    countplot_y,
    countplot_y_normalized,
    histogram,
    lineplot,
    pie_base,
)

def _calculate_value_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df_value_counts = df[col].value_counts().to_frame().reset_index()
    df_value_counts.columns = [col, "count"]
    return df_value_counts

def _validate_format(format: str) -> None:
    supported_formats = ['png', 'svg']
    if format not in supported_formats:
        raise ValueError(
            f"Unsupported format '{format}'. "
            f"Supported formats are {supported_formats}."
        )

def _create_filepath(
    output_dir: str,
    prefix: Optional[str],
    output_name: str,
    format: str
) -> str:
    if prefix:
        return os.path.join(output_dir, f"{prefix}_{output_name}.{format}")
    return os.path.join(output_dir, f"{output_name}.{format}")

def _save_plot(filepath: str, format: str) -> None:
    plt.savefig(filepath, bbox_inches="tight", dpi=300, format=format)

class PlotGraphs:

    def __init__(
        self,
        export: bool = True,
        output_dir: str = os.path.expanduser("./plot_output/"),
        prefix: Optional[str] = None,
        format: str = 'png'
    ) -> None:
        self.config = {
            "export": export,
            "output_dir": output_dir,
            "prefix": prefix,
        }
        if self.config["export"]:
            os.makedirs(self.config["output_dir"], exist_ok=True)
        self.format = format.lower()

    def _export_graph(self, output_name: str) -> None:
        _validate_format(self.format)
        
        if self.config["export"]:
            filepath = _create_filepath(
                self.config["output_dir"],
                self.config["prefix"],
                output_name,
                self.format
            )
            _save_plot(filepath, self.format)
        plt.show()

    def countplot_x(
        self,
        df: pd.DataFrame,
        x: str,
        hue: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
        xlabel: str = '',
        ylabel: str = 'Count',
        plot_legend: bool = True,
        legend_offset: float = 1.13,
        ncol: int = 2,
        top_n: Optional[int] = None,
        figsize_width: FigureSizeInput = 'dynamic',
        stacked: bool = False,
        stacked_labels: StackedLabelTypeInput = None,
        order_type: OrderTypeInput = 'frequency',
        normalized: bool = False,
        show_labels: bool = True,
        output_name: str = 'countplot_x'
    ) -> None:
        if normalized:
            if hue is None:
                raise ValueError("hue must be provided when normalized=True")
            if not isinstance(palette, dict):
                raise ValueError("palette must be a dictionary when normalized=True")
            countplot_x_normalized(
                df=df, x=x, hue=hue, palette=palette, label_map=label_map,
                xlabel=xlabel, ylabel=ylabel, plot_legend=plot_legend,
                legend_offset=legend_offset, ncol=ncol, top_n=top_n,
                figsize_width=figsize_width, order_type=order_type,
                show_labels=show_labels
            )
        else:
            countplot_x(
                df=df, x=x, hue=hue, palette=palette, label_map=label_map,
                xlabel=xlabel, ylabel=ylabel, plot_legend=plot_legend,
                legend_offset=legend_offset, ncol=ncol, top_n=top_n,
                figsize_width=figsize_width, stacked=stacked,
                stacked_labels=stacked_labels, order_type=order_type
            )
        self._export_graph(output_name)

    def countplot_y(
        self,
        df: pd.DataFrame,
        y: str,
        hue: Optional[str] = None,
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
        xlabel: str = 'Count',
        ylabel: str = '',
        plot_legend: bool = True,
        legend_offset: float = 1.13,
        ncol: int = 2,
        top_n: Optional[int] = None,
        figsize_height: FigureSizeInput = 'dynamic',
        stacked: bool = False,
        stacked_labels: StackedLabelTypeInput = None,
        order_type: OrderTypeInput = 'frequency',
        normalized: bool = False,
        show_labels: bool = True,
        output_name: str = 'countplot_y'
    ) -> None:
        if normalized:
            if hue is None:
                raise ValueError("hue must be provided when normalized=True")
            if not isinstance(palette, dict):
                raise ValueError("palette must be a dictionary when normalized=True")
            countplot_y_normalized(
                df=df, y=y, hue=hue, palette=palette, label_map=label_map,
                xlabel=xlabel, ylabel=ylabel, plot_legend=plot_legend,
                legend_offset=legend_offset, ncol=ncol, top_n=top_n,
                figsize_height=figsize_height, order_type=order_type,
                show_labels=show_labels
            )
        else:
            countplot_y(
                df=df, y=y, hue=hue, palette=palette, label_map=label_map,
                xlabel=xlabel, ylabel=ylabel, plot_legend=plot_legend,
                legend_offset=legend_offset, ncol=ncol, top_n=top_n,
                figsize_height=figsize_height, stacked=stacked,
                stacked_labels=stacked_labels, order_type=order_type
            )
        self._export_graph(output_name)

    def histogram(
        self,
        df: pd.DataFrame,
        x: str,
        xlabel: str = '',
        ylabel: str = 'Count',
        xlimit: Optional[Union[float, int]] = None,
        bins: int = 100,
        palette: Optional[Union[Dict[Any, str], str]] = None,
        label_map: Optional[Dict[Any, str]] = None,
        hue: Optional[str] = None,
        stacked: Optional[bool] = None,
        plot_legend: bool = True,
        legend_offset: float = 1.13,
        ncol: int = 2,
        output_name: str = 'histogram'
    ) -> None:
        histogram(
            df=df, x=x, xlabel=xlabel, ylabel=ylabel, xlimit=xlimit,
            bins=bins, palette=palette, label_map=label_map, hue=hue,
            stacked=stacked, plot_legend=plot_legend,
            legend_offset=legend_offset, ncol=ncol
        )
        self._export_graph(output_name)

    def pie(
        self,
        df: pd.DataFrame,
        col: str,
        palette: Dict[Any, str],
        label_map: Optional[Dict[Any, str]] = None,
        n_after_comma: int = 0,
        value_datalabel: int = 5,
        donut: bool = False,
        output_name: str = 'pie_value_counts'
    ) -> None:
        df_value_counts = _calculate_value_counts(df, col)
        pie_base(
            df=df_value_counts,
            value="count",
            label=col,
            palette=palette,
            label_map=label_map,
            n_after_comma=n_after_comma,
            value_datalabel=value_datalabel,
            donut=donut
        )
        self._export_graph(output_name)


    def lineplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        xlabel: str = '',
        ylabel: str = '',
        rotation: int = 0,
        dynamic_x_ticks: Optional[int] = None,
        fill_missing_values: Optional[str] = None,
        output_name: str = 'lineplot'
    ) -> None:
        lineplot(
            df=df, x=x, y=y, xlabel=xlabel, ylabel=ylabel,
            rotation=rotation, dynamic_x_ticks=dynamic_x_ticks,
            fill_missing_values=fill_missing_values
        )
        self._export_graph(output_name)