from typing import Any, Optional

import pandas as pd

from ..core import renderer
from ..svg import Chart
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
            self.options.sort, df, self.options.axis_column, value_column=self.options.value
        )
        return self._resolve_hue_palette(df)

    def _draw_unstacked(self, chart: Chart, data: pd.DataFrame) -> Any:
        return renderer.render_barplot(
            chart,
            df=data,
            column=self.options.axis_column,
            value=self.options.value,
            horizontal=self.options.orientation == 'horizontal',
            hue=self.options.hue,
            order=self._order,
            color=self._color,
            palette=self._palette,
        )

    def _datalabel_formatting(self) -> str:
        return 'percentage' if self.options.normalized else 'totals'
