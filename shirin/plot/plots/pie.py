from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd

from ..config import FigureSize, FontSizes, TextColors

VALUE_DATALABEL = 5

def _extract_values_and_labels(
    df: pd.DataFrame, value: str, label: str
) -> Tuple[List[float], List[str]]:
    """Extract and prepare values and labels from dataframe for pie chart."""
    df = df.copy()
    df[value] = df[value].fillna(0).astype(float)
    values = df[value].tolist()
    labels = df[label].tolist()
    return values, labels

def _map_pie_labels(
    label_map: Optional[Dict[str, str]],
    original_labels: List[str],
    palette: Dict[str, str],
    values: List[float]
) -> Tuple[List[str], List[str]]:
    """Map labels and create formatted legend entries with values."""
    mapped_labels = [
        label_map[label] if label_map and label in label_map else label
        for label in original_labels
    ]
    mapped_colors = [palette[label] for label in original_labels]

    legend_labels = [
        f'{mapped_label}: {value:,.0f}'.replace(",", ".")
        for mapped_label, value in zip(mapped_labels, values)
    ]

    return mapped_colors, legend_labels

def _format_pie_labels(
    white_text_labels: Optional[Union[str, List[str]]],
    original_labels: List[str],
    autotexts: List[Any],
) -> None:
    """Set text color to white for specified labels."""
    if not white_text_labels:
        return
    
    if not isinstance(white_text_labels, list):
        white_text_labels = [white_text_labels]
    
    for label, autotext in zip(original_labels, autotexts):
        if label in white_text_labels:
            autotext.set_color('white')

def _format_pie_legend_with_totals(legend_labels: List[str]) -> None:
    """Create and format legend with value totals."""
    legend = plt.legend(
        legend_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.98),
        fontsize=FontSizes.LEGEND,
        framealpha=0.0,
        ncol=1,
    )
    for text in legend.get_texts():
        text.set_color(TextColors.DARK_GREY)


def pie_base(
    df: pd.DataFrame,
    value: str,
    label: str,
    palette: Dict[str, str],
    label_map: Optional[Dict[str, str]] = None,
    white_text_labels: Optional[Union[str, List[str]]] = None,
    n_after_comma: int = 0,
    value_datalabel: int = VALUE_DATALABEL,
    donut: bool = False
) -> None:
    """Create a pie or donut chart with customization.
    
    Args:
        df: DataFrame with value and label columns
        value: Column name for values
        label: Column name for labels
        palette: Dictionary mapping labels to colors
        label_map: Dictionary mapping labels to display names
        white_text_labels: Labels to display in white text
        n_after_comma: Decimal places for percentages
        value_datalabel: Minimum percentage to show data label
        donut: Whether to create donut chart (default: pie)
    """
    values, original_labels = _extract_values_and_labels(df, value, label)
    mapped_colors, legend_labels = _map_pie_labels(
        label_map, original_labels, palette, values
    )

    plt.figure(figsize=(FigureSize.PIE, FigureSize.PIE))
    result = plt.pie(
        values,
        colors=mapped_colors,
        autopct=lambda p: f'{p:.{n_after_comma}f}%' if p >= value_datalabel else '',
        wedgeprops=dict(edgecolor='none', width=0.6 if donut else 1.0),
        textprops={'fontsize': FontSizes.XYLABEL},
        pctdistance=0.775 if donut else 0.6,
    )
    
    autotexts = result[2] if len(result) == 3 else []

    if donut:
        from matplotlib.patches import Circle
        center_circle = Circle((0, 0), 0.6, color='white', fc='white', linewidth=0)
        plt.gcf().gca().add_artist(center_circle)
    
    plt.axis('equal')

    _format_pie_legend_with_totals(legend_labels)
    _format_pie_labels(white_text_labels, original_labels, autotexts)