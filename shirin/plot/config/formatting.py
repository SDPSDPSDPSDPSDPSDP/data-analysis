class FontSizes:
    TEXT = 10
    TITLE = 15
    TICKS = 8
    DATALABELS = 8
    XYLABEL = 10
    LEGEND = 8


class FigureSize:
    """Inches. Figure height is the plot area plus whatever rows (title, legend, labels) are present."""
    WIDTH = 8.4
    PLOT_HEIGHT = 3.2
    CATEGORY_SLOT = 0.8  # plot width per category for vertical bars
    BAR_ROW = 0.4  # plot height per category for horizontal bars
    PIE = 3.2


class Layout:
    """Points, measured from the figure edges."""
    PAD = 12
    ROW_GAP = 6
    PLOT_GAP = 12
    TICK_GAP = 6
    LABEL_GAP = 8
    DATALABEL_GAP = 3
    SWATCH = 8
    SWATCH_GAP = 4
    LEGEND_ITEM_GAP = 14
