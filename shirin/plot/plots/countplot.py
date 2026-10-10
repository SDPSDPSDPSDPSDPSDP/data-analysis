import pandas as pd

from ..core.categorical_options import CountPlotOptions
from ..common.data_conversion import ensure_column_is_string, filter_top_n_categories
from .categorical import StackableCategoricalPlot


class CountPlot(StackableCategoricalPlot):
    options: CountPlotOptions

    def preprocess(self) -> pd.DataFrame:
        df = ensure_column_is_string(self.options.df, self.options.axis_column)
        if self.options.top_n is not None:
            df = filter_top_n_categories(df, self.options.axis_column, self.options.top_n)
        return df

    def _datalabel_formatting(self) -> str:
        return 'percentage' if self.options.normalized and self.options.hue is None else 'totals'
