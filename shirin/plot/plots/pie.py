import matplotlib.pyplot as plt
from ..config import FigureSize, FontSizes, TextColors
import pandas as pd
from typing import Optional, Union, Tuple, Dict, List

VALUE_DATALABEL = 5

def _extract_values_and_labels(
    df: pd.DataFrame, value: str, label: str
) -> Tuple[List[float], List[str]]:

    # Extract values and labels from the dataframe
    df = df.copy()
    df[value] = df[value].fillna(0).astype(float)
    values = df[value].tolist()
    original_labels = df[label].tolist()  # Keep original labels for mapping when needed

    return values, original_labels

def _map_pie_labels(
    label_map: Optional[Dict[str, str]], original_labels: List[str], palette: Dict[str, str], values: List[float]
) -> Tuple[List[str], List[str]]:

    # Map labels and colors consistently
    if label_map:
        mapped_labels = [label_map[label] for label in original_labels]
    else:
        mapped_labels = original_labels
    mapped_colors = [palette[label] for label in original_labels]

    # Combine mapped labels with values for the legend
    legend_labels = [
        f'{mapped_label}: {value:,.0f}'.replace(",", ".")
        for mapped_label, value in zip(mapped_labels, values)
    ]

    return mapped_colors, legend_labels

def _format_pie_labels(
    white_text_labels: Optional[Union[str, List[str]]],
    original_labels: List[str],
    autotexts: List[plt.Text],
) -> None:
    if white_text_labels:
        if not isinstance(white_text_labels, list):
            white_text_labels = [white_text_labels]
        for label, autotext in zip(original_labels, autotexts):
            if label in white_text_labels:
                autotext.set_color('white')

def _format_pie_legend_with_totals(legend_labels: List[str]) -> None:
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
    df: pd.DataFrame,  # DataFrame with two columns
    value: str,  # Column name for values
    label: str,  # Column name for labels
    palette: Dict[str, str],  # Dictionary mapping label categories to colors
    label_map: Optional[Dict[str, str]] = None,  # Dictionary mapping label categories to display names
    white_text_labels: Optional[Union[str, List[str]]] = None,  # Single label or list of labels to apply white text
    n_after_comma: int = 0,  # Number of decimal places in percentage text
    value_datalabel: int = VALUE_DATALABEL,  # Minimum percentage value to display data label
    donut: bool = False  # default is False for a regular pie
) -> None:

    values, original_labels = _extract_values_and_labels(df, value, label)
    mapped_colors, legend_labels = _map_pie_labels(label_map, original_labels, palette, values)

    # Create the pie chart (or donut chart if "donut" is True)
    plt.figure(figsize=(FigureSize.PIE, FigureSize.PIE))
    wedges, texts, autotexts = plt.pie(
        values,
        colors=mapped_colors,
        autopct=lambda p: f'{p:.{n_after_comma}f}%' if p >= value_datalabel else '',
        wedgeprops=dict(edgecolor='none', width=0.6 if donut else 1.0),  # Adjust width for donut
        textprops={'fontsize': FontSizes.XYLABEL},
        pctdistance=0.775 if donut else 0.6,  # Move percentages closer to edges for donut
    )

    if donut:
        # Add a white circle in the center for the donut appearance
        center_circle = plt.Circle((0, 0), 0.6, color='white', fc='white', linewidth=0)
        plt.gcf().gca().add_artist(center_circle)
    
    plt.axis('equal')

    # Formatting
    _format_pie_legend_with_totals(legend_labels)
    _format_pie_labels(white_text_labels, original_labels, autotexts)