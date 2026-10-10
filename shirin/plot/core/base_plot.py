from abc import ABC, abstractmethod
from typing import Any, Optional

import pandas as pd

from .options import BasePlotOptions
from ..common.data_conversion import ensure_column_is_string, prepare_legend_label_map
from ..common.formatting import format_optional_legend, format_xy_labels
from ..common.sorting import create_default_label_map
from ..common.strategies.palette import get_palette_strategy
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

    def _create_standard_figure(self) -> None:
        from ..config import FigureSize
        self.renderer.create_figure((FigureSize.WIDTH, FigureSize.STANDARD_HEIGHT))

    def _format_labels_and_legend(self, plot: Any) -> None:
        """Axis labels plus hue legend; builds a default label_map from the data when missing."""
        options = self.options
        if options.label_map is None and options.plot_legend and options.hue is not None:
            options.label_map = create_default_label_map(
                self._preprocessed_df,  # type: ignore[arg-type]
                options.hue,
            )
        self._label_map_legend = prepare_legend_label_map(options.label_map)

        format_xy_labels(plot, xlabel=options.xlabel, ylabel=options.ylabel)
        format_optional_legend(
            plot,
            options.hue,
            options.plot_legend,
            self._label_map_legend,
            options.ncol,
            options.legend_offset,
        )

    def _resolve_hue_palette(self, df: pd.DataFrame) -> pd.DataFrame:
        """Stringify hue (to match palette keys) and set _color/_palette; black when no hue."""
        hue = getattr(self.options, 'hue', None)
        self._color, self._palette = get_palette_strategy(self.options.palette).get_palette()  # type: ignore[attr-defined]
        if hue is None:
            self._color = 'black'
            return df
        return ensure_column_is_string(df, hue)
