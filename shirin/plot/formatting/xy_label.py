import matplotlib.pyplot as plt
from ..config import TextColors, FontSizes
from matplotlib.axes import Axes

plt.rcParams['axes.labelsize'] = FontSizes.XYLABEL

def format_xy_labels(
    plot: Axes, 
    xlabel: str = 'Count', 
    x_labelpad: int = 10, 
    ylabel: str = 'Count', 
    y_offset: float = 0.5, 
    y_labelpad: int = 20
) -> None:
    """Sets the X and Y labels along with their customization."""
    plt.xlabel(
        xlabel, 
        ha='center', 
        x=0.5, 
        labelpad=x_labelpad, 
        fontsize=FontSizes.XYLABEL, 
        color=TextColors.BLACK
    )
    plt.ylabel(
        ylabel, 
        y=y_offset, 
        labelpad=y_labelpad, 
        fontsize=FontSizes.XYLABEL, 
        color=TextColors.BLACK
    )