from typing import Any, Optional

import pandas as pd
from matplotlib.axes import Axes

from ..core import renderer
from ..core.categorical_options import BarPlotOptions
from ..common.data_conversion import ensure_column_is_string
from ..common.sorting import get_order
from .categorical import StackableCategoricalPlot


class BarPlot(StackableCategoricalPlot):
    options: BarPlotOptions

    def _value_column(self) -> Optional[str]:
        return self.options.value

    def preprocess(self) -> pd.DataFrame:
        return ensure_column_is_string(self.options.df, self.options.axis_column)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self._order = get_order(
            self.options.order_type, df, self.options.axis_column, value_column=self.options.value
        )
        return self._resolve_hue_palette(df, require_dict=self.options.stacked)

    def _draw_unstacked(self, ax: Axes, data: pd.DataFrame) -> Any:
        x, y = self.options.axis_column, self.options.value
        if self.options.orientation != 'vertical':
            x, y = y, x
        return renderer.render_barplot(
            ax,
            df=data,
            x=x,
            y=y,
            hue=self.options.hue,
            order=self._order,
            color=self._color,
            palette=self._palette,
        )

    def _datalabel_formatting(self) -> str:
        return 'percentage' if self.options.percentage_labels else 'totals'
