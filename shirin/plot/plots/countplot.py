from typing import Any

import pandas as pd

from ..core.categorical_options import CountPlotOptions
from ..common.data_conversion import ensure_column_is_string, filter_top_n_categories
from ..common.sorting import get_order
from .categorical import StackableCategoricalPlot


class CountPlot(StackableCategoricalPlot):
    options: CountPlotOptions

    def preprocess(self) -> pd.DataFrame:
        df = ensure_column_is_string(self.options.df, self.options.axis_column)
        if self.options.top_n is not None:
            df = filter_top_n_categories(df, self.options.axis_column, self.options.top_n)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self._order = get_order(self.options.order_type, df, self.options.axis_column)
        return self._resolve_hue_palette(df)

    def _draw_unstacked(self, data: pd.DataFrame) -> Any:
        axis = 'x' if self.options.orientation == 'vertical' else 'y'
        return self.renderer.render_countplot(
            df=data,
            hue=self.options.hue,
            order=self._order,
            color=self._color,
            palette=self._palette,
            **{axis: self.options.axis_column},
        )

    def _datalabel_formatting(self) -> str:
        return 'percentage' if self.options.normalized and self.options.hue is None else 'totals'
