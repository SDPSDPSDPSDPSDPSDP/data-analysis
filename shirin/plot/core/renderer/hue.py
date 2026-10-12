"""Hue grouping and legend shared by every renderer."""
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from ...common.colors import palette_colors
from ...svg import Chart


def hue_levels(df: pd.DataFrame, hue: str) -> List[Any]:
    """Hue values in data order; this is also the legend order."""
    return list(df[hue].dropna().unique())


def set_legend(chart: Chart, colors: List[str], labels: List[Any]) -> None:
    chart.legend = [(color, str(label), '') for color, label in zip(colors, labels)]


def hue_groups(
    chart: Chart, df: pd.DataFrame, hue: Optional[str], color: Optional[str], palette: Optional[Dict[Any, str]]
) -> Tuple[List[pd.Series], List[str]]:
    """(row masks, colors), one per hue value, and sets the legend; without hue one all-rows group in color."""
    if hue is None:
        return [pd.Series(True, index=df.index)], [color]  # type: ignore[list-item]
    levels = hue_levels(df, hue)
    colors = palette_colors(palette, levels)  # type: ignore[arg-type]
    set_legend(chart, colors, levels)
    return [df[hue] == level for level in levels], colors
