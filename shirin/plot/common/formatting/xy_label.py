from matplotlib.axes import Axes

from ...config import TextColors, FontSizes


def format_xy_labels(
    plot: Axes,
    xlabel: str = 'Count',
    x_labelpad: int = 10,
    ylabel: str = 'Count',
    y_offset: float = 0.5,
    y_labelpad: int = 20
) -> None:
    plot.set_xlabel(
        xlabel,
        ha='center',
        x=0.5,
        labelpad=x_labelpad,
        fontsize=FontSizes.XYLABEL,
        color=TextColors.BLACK
    )
    plot.set_ylabel(
        ylabel,
        y=y_offset,
        labelpad=y_labelpad,
        fontsize=FontSizes.XYLABEL,
        color=TextColors.BLACK
    )
