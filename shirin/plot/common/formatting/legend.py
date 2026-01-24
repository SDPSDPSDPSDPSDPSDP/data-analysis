import matplotlib.pyplot as plt
from typing import Any, Optional, Dict, Tuple, TYPE_CHECKING

from ...config import TextColors, FontSizes


if TYPE_CHECKING:
    from matplotlib.axes import Axes


plt.rcParams['legend.fontsize'] = FontSizes.LEGEND


def format_legend(
    label_map: Optional[Dict[Any, str]], 
    ncol: int = 2, 
    bbox_to_anchor: Tuple[float, float] = (0, 1.08)
) -> None:

    # Get the current legend to access its handles and texts
    current_legend = plt.gca().get_legend()
    if current_legend is None:
        return
    
    handles = current_legend.legend_handles
    
    # Map existing legend labels using label_map
    if label_map:
        legend_labels = [label_map.get(text.get_text(), text.get_text()) for text in current_legend.get_texts()]
    else:
        legend_labels = None

    # Configure the legend
    legend = plt.legend(
        handles,
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
    plot: Any, 
    hue: Optional[str], 
    plot_legend: bool, 
    label_map: Optional[Dict[Any, str]], 
    ncol: int, 
    legend_offset: float
) -> None:
    if hue is not None:
        if plot_legend:
            format_legend(label_map, ncol=ncol, bbox_to_anchor=(-0.01, legend_offset))
        else:
            legend = plot.get_legend()
            if legend is not None:
                legend.remove()