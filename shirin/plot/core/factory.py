from typing import Dict, Type, Optional

from .base_plot import AbstractPlot
from .options import BasePlotOptions
from .renderer import PlotRenderer, SeabornRenderer


class PlotRegistry:
    def __init__(self):
        self._registry: Dict[str, Type[AbstractPlot]] = {}
    
    def register(self, plot_type: str, plot_class: Type[AbstractPlot]) -> None:
        self._registry[plot_type] = plot_class
    
    def get(self, plot_type: str) -> Optional[Type[AbstractPlot]]:
        return self._registry.get(plot_type)
    
    def list_types(self) -> list[str]:
        return list(self._registry.keys())


class PlotFactory:
    def __init__(self, registry: Optional[PlotRegistry] = None):
        self.registry = registry or PlotRegistry()
        self._default_renderer: Optional[PlotRenderer] = None
    
    def set_default_renderer(self, renderer: PlotRenderer) -> None:
        self._default_renderer = renderer
    
    def create_plot(
        self,
        plot_type: str,
        options: BasePlotOptions,
        renderer: Optional[PlotRenderer] = None
    ) -> AbstractPlot:
        plot_class = self.registry.get(plot_type)
        if plot_class is None:
            raise ValueError(
                f"Unknown plot type '{plot_type}'. "
                f"Available types: {self.registry.list_types()}"
            )
        
        renderer = renderer or self._default_renderer or SeabornRenderer()
        return plot_class(options, renderer)


_global_registry = PlotRegistry()
_global_factory = PlotFactory(_global_registry)


def register_plot(plot_type: str, plot_class: Type[AbstractPlot]) -> None:
    _global_registry.register(plot_type, plot_class)


def create_plot(
    plot_type: str,
    options: BasePlotOptions,
    renderer: Optional[PlotRenderer] = None
) -> AbstractPlot:
    return _global_factory.create_plot(plot_type, options, renderer)


def get_factory() -> PlotFactory:
    return _global_factory
