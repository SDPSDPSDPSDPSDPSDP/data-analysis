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
    CATEGORY_SLOT = 0.75  # plot width per category for vertical bars; sets the figure width
    BAR_ROW = 0.4  # plot height per category for horizontal bars
    BAR_GROUP_WIDTH = 0.65  # share of a category slot covered by its bars (dodged bars split it)
    DODGE_GAP = 0.06  # share of a category slot left between dodged bars
    PIE = 3.2


class Layout:
    """Points, measured from the figure edges."""
    PAD = 12
    ROW_GAP = 6
    PLOT_GAP = 12
    TICK_GAP = 6
    LABEL_GAP = 14
    DATALABEL_GAP = 6
    SWATCH = 8
    SWATCH_GAP = 4
    LEGEND_ITEM_GAP = 14
    LEGEND_GAP = 2  # extra space between title/subtitle and legend
    STACKED_LABEL_MIN_SHARE = 0.15  # smaller stack segments (share of tallest stack) get no label; rounded ends leave no room
