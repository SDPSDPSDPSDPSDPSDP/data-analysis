from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

import pandas as pd

from ..config import OrderTypeInput, StackedLabelTypeInput, FigureSizeInput, FillMissingValuesInput


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


@dataclass
class CountPlotOptions(BasePlotOptions):
    axis_column: str = ''
    orientation: str = 'vertical'
    top_n: Optional[int] = None
    figsize: FigureSizeInput = 'dynamic'
    stacked: bool = False
    stacked_labels: StackedLabelTypeInput = None
    order_type: OrderTypeInput = 'frequency'
    normalized: bool = False
    show_labels: bool = True
    
    def validate(self) -> None:
        super().validate()
        if not self.axis_column:
            raise ValueError("axis_column must be specified")
        if self.orientation not in ('vertical', 'horizontal'):
            raise ValueError("orientation must be 'vertical' or 'horizontal'")
        if self.normalized:
            if self.hue is None:
                raise ValueError("hue must be provided when normalized=True")
            if not isinstance(self.palette, dict):
                raise ValueError("palette must be a dictionary when normalized=True")
        if self.stacked and self.hue is None:
            raise ValueError("hue must be provided when stacked=True")


@dataclass
class BarPlotOptions(BasePlotOptions):
    axis_column: str = ''
    value: str = ''
    orientation: str = 'vertical'
    figsize: FigureSizeInput = 'dynamic'
    stacked: bool = False
    stacked_labels: StackedLabelTypeInput = None
    order_type: OrderTypeInput = 'frequency'
    percentage_labels: bool = False
    
    def validate(self) -> None:
        super().validate()
        if not self.axis_column:
            raise ValueError("axis_column must be specified")
        if not self.value:
            raise ValueError("value column must be specified")
        if self.orientation not in ('vertical', 'horizontal'):
            raise ValueError("orientation must be 'vertical' or 'horizontal'")
        if self.stacked and self.hue is None:
            raise ValueError("hue must be provided when stacked=True")


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
    palette: Dict[Any, str] = field(default_factory=dict)
    label_map: Optional[Dict[Any, str]] = None
    
    def validate(self) -> None:
        super().validate()
        if not self.col:
            raise ValueError("col must be specified")
        if not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary for pie charts")


@dataclass
class NormalizedCountPlotOptions(BasePlotOptions):
    axis_column: str = ''
    orientation: str = 'vertical'
    top_n: Optional[int] = None
    figsize: FigureSizeInput = 'dynamic'
    order_type: OrderTypeInput = 'frequency'
    show_labels: bool = True
    palette: Dict[Any, str] = field(default_factory=dict)
    label_map: Optional[Dict[Any, str]] = None
    hue: str = ''
    xlabel: str = ''
    ylabel: str = 'Percentage'
    plot_legend: bool = True
    legend_offset: float = 1.13
    ncol: int = 2
    
    def validate(self) -> None:
        super().validate()
        if not self.axis_column:
            raise ValueError("axis_column must be specified")
        if not self.hue:
            raise ValueError("hue must be specified for normalized plots")
        if self.orientation not in ('vertical', 'horizontal'):
            raise ValueError("orientation must be 'vertical' or 'horizontal'")
        if not isinstance(self.palette, dict):
            raise ValueError("palette must be a dictionary for normalized plots")
