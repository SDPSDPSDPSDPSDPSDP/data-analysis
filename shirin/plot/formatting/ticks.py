from matplotlib.ticker import FuncFormatter
from matplotlib.axes import Axes
from ..config import TextColors

def _configure_grid(plot: Axes, x_grid: bool = False, y_grid: bool = False) -> None:
    """Configures the grid for both X and Y axes."""
    plot.set_axisbelow(True)  # Ensure the grid renders below elements
    if y_grid:
        plot.yaxis.grid(y_grid, zorder=1)
    if x_grid:
        plot.xaxis.grid(x_grid, zorder=1)

def _set_ticks(plot: Axes, numeric_x: bool = False, numeric_y: bool = False, percentage_x: bool = False, percentage_y: bool = False) -> None:
    """Formats the tick labels for numerical data (e.g., 100.000) or percentages."""
    def format_numeric(tick_val: float, pos: int) -> str:
        return "{:,.0f}".format(tick_val).replace(",", ".")

    def format_percentage(tick_val: float, pos: int) -> str:
        return f"{tick_val * 100:.0f}%"  # Scale tick values as percentages

    if numeric_x and percentage_x:
        raise ValueError("Cannot format ticks as both 'numeric' and 'percentage'. Choose one.")
    if numeric_y and percentage_y:
        raise ValueError("Cannot format ticks as both 'numeric' and 'percentage'. Choose one.")

    if numeric_x:
        plot.xaxis.set_major_formatter(FuncFormatter(format_numeric))
    elif percentage_x:
        plot.xaxis.set_major_formatter(FuncFormatter(format_percentage))

    if numeric_y:
        plot.yaxis.set_major_formatter(FuncFormatter(format_numeric))
    elif percentage_y:
        plot.yaxis.set_major_formatter(FuncFormatter(format_percentage))

def _customize_ticks(plot: Axes, rotation: int) -> None:
    """Customizes the colors (and optionally the visibility) of tick labels."""
    plot.tick_params(axis='x', colors=TextColors.DARK_GREY, which='both', color='white', rotation=rotation)
    plot.tick_params(axis='y', colors=TextColors.DARK_GREY, which='both', color='white')

def format_ticks(
    plot: Axes,
    x_grid: bool = False,
    y_grid: bool = False,
    numeric_x: bool = False,
    numeric_y: bool = False,
    percentage_x: bool = False,
    percentage_y: bool = False,
    rotation: int = 0,
) -> None:
    """Configures grid, formats ticks, and applies customizations."""
    _configure_grid(plot, x_grid, y_grid)
    _set_ticks(plot, numeric_x, numeric_y, percentage_x, percentage_y)
    _customize_ticks(plot, rotation=rotation)