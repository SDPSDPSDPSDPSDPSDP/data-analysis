from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

import pandas as pd

from ..config import OrderTypeInput, StackedLabelTypeInput, FigureSizeInput, FillMissingValuesInput, TimeGroupByInput
from ..common.data_conversion import convert_dict_keys_to_string


@dataclass
class BasePlotOptions:
    df: pd.DataFrame
    palette: Optional[Union[Dict[Any, str], str]] = None
    label_map: Optional[Dict[Any, str]] = None
    xlabel: str = ''
    ylabel: str = ''
    plot_legend: bool = True
    legend_offset: float = 1.13
    ncol: int = 2
    hue: Optional[str] = None
    
    def validate(self) -> None:
        if self.df is None or self.df.empty:
            raise ValueError("DataFrame cannot be None or empty")
        
        # Normalize dictionary keys to strings to ensure consistency
        if isinstance(self.palette, dict):
            self.palette = convert_dict_keys_to_string(self.palette)
        if isinstance(self.label_map, dict):
            self.label_map = convert_dict_keys_to_string(self.label_map)


@dataclass
class CategoricalPlotOptions(BasePlotOptions):
    axis_column: str = ''
    orientation: str = 'vertical'
    figsize: FigureSizeInput = 'dynamic'
    stacked: bool = False
    stacked_labels: StackedLabelTypeInput = None
    order_type: OrderTypeInput = 'frequency'

    def validate(self) -> None:
        super().validate()
        if not self.axis_column:
            raise ValueError("axis_column must be specified")
        if self.orientation not in ('vertical', 'horizontal'):
            raise ValueError("orientation must be 'vertical' or 'horizontal'")
        if self.stacked and self.hue is None:
            raise ValueError("hue must be provided when stacked=True")


@dataclass
class CountPlotOptions(CategoricalPlotOptions):
    top_n: Optional[int] = None
    normalized: bool = False
    show_labels: bool = True
    
    def validate(self) -> None:
        super().validate()
        if self.normalized:
            if self.hue is None:
                raise ValueError("hue must be provided when normalized=True")
            if not isinstance(self.palette, dict):
                raise ValueError("palette must be a dictionary when normalized=True")


@dataclass
class BarPlotOptions(CategoricalPlotOptions):
    value: str = ''
    percentage_labels: bool = False
    
    def validate(self) -> None:
        super().validate()
        if not self.value:
            raise ValueError("value column must be specified")


@dataclass
class HistogramOptions(BasePlotOptions):
    x: str = ''
    xlimit: Optional[Union[float, int]] = None
    bins: int = 100
    stacked: Optional[bool] = None
    
    def validate(self) -> None:
        super().validate()
        if not self.x:
            raise ValueError("x column must be specified")
        if self.bins <= 0:
            raise ValueError("bins must be positive")


@dataclass
class LinePlotOptions(BasePlotOptions):
    x: str = ''
    y: str = ''
    rotation: int = 0
    fill_missing_values: FillMissingValuesInput = None
    
    def validate(self) -> None:
        super().validate()
        if not self.x:
            raise ValueError("x column must be specified")
        if not self.y:
            raise ValueError("y column must be specified")


@dataclass
class PiePlotOptions(BasePlotOptions):
    col: str = ''
    n_after_comma: int = 0
    value_datalabel: int = 5
    donut: bool = False
    palette: Optional[Union[Dict[Any, str], str]] = field(default_factory=dict)
    
    def validate(self) -> None:
        super().validate()
        if not self.col:
            raise ValueError("col must be specified")
        if not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary for pie charts")


@dataclass
class NormalizedCountPlotOptions(CategoricalPlotOptions):
    top_n: Optional[int] = None
    show_labels: bool = True
    palette: Optional[Union[Dict[Any, str], str]] = field(default_factory=dict)
    ylabel: str = 'Percentage'
    
    def validate(self) -> None:
        super().validate()
        if not self.hue:
            raise ValueError("hue must be specified for normalized plots")
        if not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary for normalized plots")


@dataclass
class TimePlotOptions(BasePlotOptions):
    x: str = ''
    group_by: TimeGroupByInput = 'day'
    ylabel: str = 'Total'
    
    def validate(self) -> None:
        super().validate()
        if not self.x:
            raise ValueError("x column must be specified")
        if self.group_by not in ('year', 'month', 'day'):
            raise ValueError("group_by must be 'year', 'month', or 'day'")
