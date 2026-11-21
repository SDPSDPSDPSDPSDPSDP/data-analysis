from typing import Any, Optional

from ..config.theme import Theme
from ..core import AbstractPlot


class PlotHost:
    """What the plot mixins use from PlotGraphs, declared so each mixin type-checks on its own."""

    _theme: Theme

    def _column_config(self, column: Optional[str]) -> dict[str, Any]:
        raise NotImplementedError

    def _render(self, plot: AbstractPlot) -> None:
        raise NotImplementedError
