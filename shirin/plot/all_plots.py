import os
from typing import Any, Dict, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd

from .plots import countplot_y, countplot_y_normalized, histogram, lineplot, pie_base

def _calculate_value_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Calculate value counts for a column and return as dataframe."""
    df_value_counts = df[col].value_counts().to_frame().reset_index()
    df_value_counts.columns = [col, "count"]
    return df_value_counts

class PlotGraphs:
    """Main plotting class for creating and exporting various chart types."""

    def __init__(
        self, 
        export: bool = True, 
        output_dir: str = os.path.expanduser("./plot_output/"), 
        prefix: Optional[str] = None, 
        format: str = 'png'
    ) -> None:
        """Initialize the PlotGraphs class.
        
        Args:
            export: Whether to export plots to files
            output_dir: Directory to save exported plots
            prefix: Prefix for exported filenames
            format: File format for exports ('png' or 'svg')
        """
        self.config = {
            "export": export,
            "output_dir": output_dir,
            "prefix": prefix,
        }
        if self.config["export"]:
            os.makedirs(self.config["output_dir"], exist_ok=True)
        self.format = format.lower()

    def _export_graph(self, output_name: str) -> None:
        """Export the current plot to file if export is enabled."""
        supported_formats = ['png', 'svg']

        if self.format not in supported_formats:
            raise ValueError(
                f"Unsupported format '{self.format}'. "
                f"Supported formats are {supported_formats}."
            )
        
        if self.config["export"]:
            if self.config["prefix"]:
                filepath = os.path.join(
                    self.config["output_dir"],
                    f"{self.config['prefix']}_{output_name}.{self.format}"
                )
            else:
                filepath = os.path.join(
                    self.config["output_dir"], 
                    f"{output_name}.{self.format}"
                )
            
            plt.savefig(filepath, bbox_inches="tight", dpi=300, format=self.format)
        plt.show()

    def countplot_y(
        self, 
        df: pd.DataFrame, 
        y: str, 
        output_name: str = 'countplot_y', 
        **kwargs
    ) -> None:
        """Create and export a horizontal count plot."""
        countplot_y(df, y, **kwargs)
        self._export_graph(output_name)

    def countplot_y_normalized(
        self, 
        df: pd.DataFrame, 
        y: str, 
        hue: str, 
        output_name: str = 'countplot_y_normalized', 
        **kwargs
    ) -> None:
        """Create and export a normalized horizontal count plot."""
        countplot_y_normalized(df, y, hue, **kwargs)
        self._export_graph(output_name)

    def histogram(
        self, 
        df: pd.DataFrame, 
        x: str, 
        output_name: str = 'histogram', 
        **kwargs
    ) -> None:
        """Create and export a histogram."""
        histogram(df, x, **kwargs)
        self._export_graph(output_name)

    def pie(
        self,
        df: pd.DataFrame, 
        col: str, 
        palette: Dict[Any, str], 
        output_name: str = 'pie_value_counts',
        **kwargs
    ) -> None:
        """Create and export a pie chart from value counts."""
        df_value_counts = _calculate_value_counts(df, col)
        pie_base(df=df_value_counts, value="count", label=col, palette=palette, **kwargs)
        self._export_graph(output_name)


    def lineplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        output_name: str = 'lineplot',
        **kwargs
    ) -> None:
        """Create and export a line plot."""
        lineplot(df, x, y, **kwargs)
        self._export_graph(output_name)