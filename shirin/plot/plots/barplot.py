from typing import Any, Optional

import pandas as pd

from ..core.options import BarPlotOptions
from ..common.strategies.ordering import get_ordering_strategy
from ..common.data_conversion import ensure_column_is_string
from .categorical import StackableCategoricalPlot


class BarPlot(StackableCategoricalPlot):
    options: BarPlotOptions

    @property
    def value_column(self) -> Optional[str]:  # type: ignore[override]
        return self.options.value

    def preprocess(self) -> pd.DataFrame:
        df = ensure_column_is_string(self.options.df.copy(), self.options.axis_column)
        if self.options.hue is not None:
            df = ensure_column_is_string(df, self.options.hue)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self._order = get_ordering_strategy(self.options.order_type).get_order(
            df,
            self.options.axis_column,
            value_column=self.options.value,
        )
        self._resolve_palette()
        return df

    def _draw_unstacked(self, data: pd.DataFrame) -> Any:
        x, y = self.options.axis_column, self.options.value
        if self.options.orientation != 'vertical':
            x, y = y, x
        return self.renderer.render_barplot(
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
