from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd

from ..config import FigureSize, FontSizes, TextColors
from ..formatting.text_contrast import get_text_color_for_background

VALUE_DATALABEL = 5

def _extract_values_and_labels(
    df: pd.DataFrame,
    value: str,
    label: str
) -> Tuple[List[float], List[str]]:
    df = df.copy()
    df[value] = df[value].fillna(0).astype(float)
    values = df[value].tolist()
    labels = df[label].tolist()
    return values, labels

def _apply_label_map_to_labels(
    original_labels: List[str],
    label_map: Optional[Dict[Any, str]]
) -> List[str]:
    if not label_map:
        return original_labels
    return [label_map.get(label, label) for label in original_labels]

def _create_colors_from_palette(
    original_labels: List[str],
    palette: Dict[Any, str]
) -> List[str]:
    return [palette[label] for label in original_labels]

def _format_legend_labels(
    mapped_labels: List[str],
    values: List[float]
) -> List[str]:
    return [
        f'{mapped_label}: {value:,.0f}'.replace(",", ".")
        for mapped_label, value in zip(mapped_labels, values)
    ]

def _prepare_pie_colors_and_labels(
    label_map: Optional[Dict[Any, str]],
    original_labels: List[str],
    palette: Dict[Any, str],
    values: List[float]
) -> Tuple[List[str], List[str]]:
    mapped_labels = _apply_label_map_to_labels(original_labels, label_map)
    mapped_colors = _create_colors_from_palette(original_labels, palette)
    legend_labels = _format_legend_labels(mapped_labels, values)
    return mapped_colors, legend_labels

def _apply_automatic_text_colors(
    autotexts: List[Any],
    palette: Dict[Any, str],
    original_labels: List[str]
) -> None:
    """Apply automatic text color based on background color luminance."""
    for label, autotext in zip(original_labels, autotexts):
        bg_color = palette.get(label, '#000000')
        text_color = get_text_color_for_background(bg_color)
        autotext.set_color(text_color)

def _create_pie_legend(legend_labels: List[str]) -> None:
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

def _create_donut_center() -> None:
    from matplotlib.patches import Circle
    center_circle = Circle((0, 0), 0.6, color='white', fc='white', linewidth=0)
    plt.gcf().gca().add_artist(center_circle)


def pie_base(
    df: pd.DataFrame,
    value: str,
    label: str,
    palette: Dict[Any, str],
    label_map: Optional[Dict[Any, str]] = None,
    n_after_comma: int = 0,
    value_datalabel: int = VALUE_DATALABEL,
    donut: bool = False
) -> None:
    values, original_labels = _extract_values_and_labels(df, value, label)
    mapped_colors, legend_labels = _prepare_pie_colors_and_labels(
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
        _create_donut_center()
    
    plt.axis('equal')

    _create_pie_legend(legend_labels)
    _apply_automatic_text_colors(autotexts, palette, original_labels)