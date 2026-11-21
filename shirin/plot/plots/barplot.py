from typing import Optional

import pandas as pd

from ..common.data_conversion import ensure_column_is_string
from ..core.categorical_options import BarPlotOptions
from .categorical import StackableCategoricalPlot
from .categorical_layout import period_rows


class BarPlot(StackableCategoricalPlot):
    options: BarPlotOptions

    def _value_column(self) -> Optional[str]:
        return self.options.value

    def preprocess(self) -> pd.DataFrame:
        if self.options.group_by is not None:
            return period_rows(self.options, self.options.value)
        return ensure_column_is_string(self.options.df, self.options.axis_column)

    def _datalabel_formatting(self) -> str:
        return "percentage" if self.options.normalized else "totals"
