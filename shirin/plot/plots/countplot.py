from typing import Optional

import pandas as pd

from ..common.data_conversion import COUNT_COL, ensure_column_is_string, filter_top_n_categories
from ..core.categorical_options import CountPlotOptions
from .categorical import StackableCategoricalPlot
from .categorical_layout import period_rows


class CountPlot(StackableCategoricalPlot):
    options: CountPlotOptions

    def _value_column(self) -> Optional[str]:
        # group_by counts rows per period up front, so the bars sum COUNT_COL.
        return COUNT_COL if self.options.group_by is not None else None

    def preprocess(self) -> pd.DataFrame:
        if self.options.group_by is not None:
            return period_rows(self.options, None)
        df = ensure_column_is_string(self.options.df, self.options.axis_column)
        if self.options.top_n is not None:
            df = filter_top_n_categories(df, self.options.axis_column, self.options.top_n)
        return df

    def _datalabel_formatting(self) -> str:
        return "percentage" if self.options.normalized and self.options.hue is None else "totals"
