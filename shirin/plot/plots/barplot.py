from typing import Optional

import pandas as pd

from ..core.categorical_options import BarPlotOptions
from ..common.data_conversion import ensure_column_is_string
from .categorical import StackableCategoricalPlot


class BarPlot(StackableCategoricalPlot):
    options: BarPlotOptions

    def _value_column(self) -> Optional[str]:
        return self.options.value

    def preprocess(self) -> pd.DataFrame:
        return ensure_column_is_string(self.options.df, self.options.axis_column)

    def _datalabel_formatting(self) -> str:
        return 'percentage' if self.options.normalized else 'totals'
