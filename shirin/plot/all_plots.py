import os
from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import pandas as pd

from .plots import countplot_y, countplot_y_normalized, histogram, lineplot, pie_base

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

def _create_filepath(output_dir: str, prefix: Optional[str], output_name: str, format: str) -> str:
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

    def countplot_y(self, df: pd.DataFrame, y: str, output_name: str = 'countplot_y', **kwargs) -> None:
        countplot_y(df, y, **kwargs)
        self._export_graph(output_name)

    def countplot_y_normalized(self, df: pd.DataFrame, y: str, hue: str, output_name: str = 'countplot_y_normalized', **kwargs) -> None:
        countplot_y_normalized(df, y, hue, **kwargs)
        self._export_graph(output_name)

    def histogram(self, df: pd.DataFrame, x: str, output_name: str = 'histogram', **kwargs) -> None:
        histogram(df, x, **kwargs)
        self._export_graph(output_name)

    def pie(self, df: pd.DataFrame, col: str, palette: Dict[Any, str], output_name: str = 'pie_value_counts', **kwargs) -> None:
        df_value_counts = _calculate_value_counts(df, col)
        pie_base(df=df_value_counts, value="count", label=col, palette=palette, **kwargs)
        self._export_graph(output_name)


    def lineplot(self, df: pd.DataFrame, x: str, y: str, output_name: str = 'lineplot', **kwargs) -> None:
        lineplot(df, x, y, **kwargs)
        self._export_graph(output_name)