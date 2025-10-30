import matplotlib.pyplot as plt
from typing import Optional, Dict, Tuple
from ..config import TextColors, FontSizes

plt.rcParams['legend.fontsize'] = FontSizes.LEGEND

def format_legend(
    label_map: Optional[Dict[str, str]], 
    ncol: int = 2, 
    bbox_to_anchor: Tuple[float, float] = (0, 1.08)
) -> None:

    # Set legend labels based on label_map, or leave it empty if label_map is None
    legend_labels = [label_map[key] for key in label_map] if label_map else None

    # Configure the legend
    legend = plt.legend(
        legend_labels, 
        title='', 
        bbox_to_anchor=bbox_to_anchor, 
        loc='upper left', 
        ncol=ncol,
        handletextpad=0.5, 
        framealpha=0.0, 
        fontsize=FontSizes.LEGEND
    )

    # Apply dark grey color to all legend text
    for text in legend.get_texts():
        text.set_color(TextColors.DARK_GREY)

def format_optional_legend(
    plot: object, 
    hue: Optional[str], 
    plot_legend: bool, 
    label_map: Optional[Dict[str, str]], 
    ncol: int, 
    legend_offset: float
) -> None:
    if hue is not None:
        if plot_legend:
            format_legend(label_map, ncol=ncol, bbox_to_anchor=(-0.01, legend_offset))
        else:
            plot.get_legend().remove()