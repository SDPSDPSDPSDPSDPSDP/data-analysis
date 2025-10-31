import pandas as pd
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Optional, Tuple

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
    
    mapped_labels = original_labels if not label_map else [label_map.get(label, label) for label in original_labels]
    mapped_colors = [palette[label] for label in original_labels]
    legend_labels = [
        f'{mapped_label}: {val:,.0f}'.replace(",", ".")
        for mapped_label, val in zip(mapped_labels, values)
    ]

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
        
    _apply_automatic_text_colors(autotexts, palette, original_labels)