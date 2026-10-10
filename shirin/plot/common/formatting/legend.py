from typing import Any, Dict, Optional, Tuple

from matplotlib.axes import Axes

from ...config import TextColors, FontSizes


def format_legend(
    plot: Axes,
    label_map: Optional[Dict[Any, str]],
    ncol: int = 2,
    bbox_to_anchor: Tuple[float, float] = (0, 1.08)
) -> None:
    current_legend = plot.get_legend()
    if current_legend is None:
        return

    handles = current_legend.legend_handles
    texts = [text.get_text() for text in current_legend.get_texts()]
    legend_labels = [label_map.get(text, text) for text in texts] if label_map else texts

    legend = plot.legend(
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

    for text in legend.get_texts():
        text.set_color(TextColors.DARK_GREY)


def format_optional_legend(
    plot: Axes,
    hue: Optional[str],
    plot_legend: bool,
    label_map: Optional[Dict[Any, str]],
    ncol: int,
    legend_offset: float
) -> None:
    if hue is None:
        return
    if plot_legend:
        format_legend(plot, label_map, ncol=ncol, bbox_to_anchor=(-0.01, legend_offset))
    elif plot.get_legend() is not None:
        plot.get_legend().remove()
