import os
import matplotlib.pyplot as plt
from .plots import countplot_y, histogram, pie_base, lineplot, countplot_y_normalized
import pandas as pd
# from .config import Colors
from typing import Dict

def _calculate_value_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df_value_counts = df[col].value_counts().to_frame().reset_index()
    df_value_counts.columns = [col, "count"]
    return df_value_counts

class PlotGraphs:

    def __init__(
        self, 
        export: bool = True, 
        output_dir: str = os.path.expanduser("./plot_output/"), 
        prefix: str = None, 
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

        # Check if the format is supported
        supported_formats = ['png', 'svg']

        if self.format not in supported_formats:
            raise ValueError(f"Unsupported format '{self.format}'. Supported formats are {supported_formats}.")
        
        # Create the output file path
        if self.config["export"]:
            if self.config["prefix"]:
                filepath = os.path.join(
                    self.config["output_dir"],
                    f"{self.config['prefix']}_{output_name}.{self.format}"
                )
            else:
                filepath = os.path.join(self.config["output_dir"], f"{output_name}.{self.format}")
            
            # Save the graph in the specified format, if export is True
            plt.savefig(filepath, bbox_inches="tight", dpi=300, format=self.format)
        plt.show()

    def countplot_y(
            self, 
            df: pd.DataFrame, 
            y: str, 
            output_name: str='countplot_y', 
            **kwargs
            ) -> None:
        
        countplot_y(df, y, **kwargs)
        self._export_graph(output_name)

    def countplot_y_normalized(
        self, 
        df: pd.DataFrame, 
        y: str, 
        hue: str, 
        output_name: str='countplot_y_normalized', 
        **kwargs
        ) -> None:
    
        countplot_y_normalized(df, y, hue, **kwargs)
        self._export_graph(output_name)

    def histogram(
            self, 
            df: pd.DataFrame, 
            x: str, 
            output_name: str='histogram', 
            **kwargs
            ) -> None:
        
        histogram(df, x, **kwargs)
        self._export_graph(output_name)

    # def pie_TO_DO(
    #         self, 
    #         df: pd.DataFrame, 
    #         value: float,
    #         label: str, 
    #         palette: dict[str, str],
    #         output_name: str='pie', 
    #         **kwargs
    #         ) -> None:
        
    #     pie_base(df, value, label, palette, **kwargs)
    #     self._export_graph(output_name)

    # def pie_binary(self, 
    #         input: Dict[bool, int],
    #         palette: Dict[bool, str] = {True: Colors.GREEN, False: Colors.RED},
    #         output_name: str='pie_binary',
    #         **kwargs
    #     ) -> None:
    #     """Wrapper function for binary pie chart"""

    #     df_binary = pd.DataFrame({
    #         'key': input.keys(),
    #         'value': input.values()
    #     })

    #     pie_base(df=df_binary, value="value", label="key", palette=palette, label_map=None, **kwargs)
    #     self._export_graph(output_name)

    # def pie_missing_values(
    #     self,
    #     df: pd.DataFrame, 
    #     col: str,
    #     color_missing: str = Colors.RED, 
    #     color_non_missing: str = Colors.GREEN, 
    #     output_name: str='pie_missing_values',
    #     **kwargs
    # ) -> None:
    #     """Wrapper function for pie chart generation for missing values."""

    #     # Count missing and non-missing values
    #     missing_count = df[col].isna().sum()
    #     non_missing_count = len(df) - missing_count
        
    #     # Create a new DataFrame to hold counts
    #     df_missing_values = pd.DataFrame({
    #         col: ["Missing Values", "Non-Missing Values"],
    #         "count": [missing_count, non_missing_count]
    #     })
    #     palette={"Missing Values": color_missing, "Non-Missing Values": color_non_missing}

    #     pie_base(df=df_missing_values, value="count", label=col, palette=palette, label_map=None, **kwargs)
    #     self._export_graph(output_name)

    def pie(
        self,
        df: pd.DataFrame, 
        col: str, 
        palette: Dict[str, str], 
        output_name: str='pie_value_counts',
        **kwargs
    ) -> None:
        
        """Wrapper function for pie chart generation."""
        df_value_counts = _calculate_value_counts(df, col)
        pie_base(df=df_value_counts, value="count", label=col, palette=palette, **kwargs)
        self._export_graph(output_name)


    def lineplot(
        self,
        df: pd.DataFrame,
        x: str,
        y: str,
        output_name: str='lineplot',
        **kwargs
    ) -> None:

        lineplot(df, x, y, **kwargs)
        self._export_graph(output_name)