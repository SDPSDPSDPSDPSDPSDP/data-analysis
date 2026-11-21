from typing import Any, Optional

import pandas as pd

from ..common.data_conversion import COUNT_COL
from ..config import TitleInput
from ..core import PiePlotOptions
from ..plots import PieChart
from .host import PlotHost


class SpecializedPlotsMixin(PlotHost):
    """Pie chart: slices instead of axes, so its own layout."""

    def pie(
        self,
        df: pd.DataFrame,
        col: str,
        title: Optional[TitleInput] = None,
        n_after_comma: int = 0,
        value_datalabel: int = 5,
        donut: bool = False,
        legend_percentages: bool = False,
        slice_labels: Optional[dict[Any, str]] = None,
    ) -> None:
        """Create a **pie chart** of the value counts in a column.

        Input:
            df: DataFrame containing the data to plot.
            col: Column whose value counts become the slices.

        Text:
            title: Chart title above the plot. Pass `['title', 'subtitle']` to add a grey
                subtitle line. *Optional*.
            n_after_comma: Decimals in the percentage labels. *Default: `0`*.
            value_datalabel: Slices below this percentage get no label. *Default: `5`*.
            legend_percentages: Show percentages in the legend instead of counts, and no
                labels on the slices. *Default: `False`*.
            slice_labels: `{value: text}` headlines drawn large on the slice of that value in
                `col`, above its percentage (centered when the slice has no percentage label).
                Long text wraps on spaces; `\\n` forces a break. Unknown values raise
                `ValueError`. *Optional*.

        Layout:
            donut: Whether to draw a donut instead of a full pie. *Default: `False`*.

        Example:
            >>> plot = PlotGraphs()
            >>> plot.pie(df, col='over_threshold', slice_labels={True: 'Accuracy: 96,4%'})
        """
        if col not in df.columns:
            raise ValueError(f"col={col!r} is not a column. Available columns: {list(df.columns)}")
        counts = df[col].value_counts()
        if counts.empty:
            raise ValueError(f"col={col!r} has no non-null values to count.")
        options = PiePlotOptions(
            df=counts.rename(COUNT_COL).to_frame(),
            col=COUNT_COL,
            **self._column_config(col),
            title=title,
            n_after_comma=n_after_comma,
            value_datalabel=value_datalabel,
            donut=donut,
            legend_percentages=legend_percentages,
            slice_labels=slice_labels,
        )
        self._render(PieChart(options))
