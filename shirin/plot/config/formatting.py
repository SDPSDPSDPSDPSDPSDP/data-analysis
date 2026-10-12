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
    CATEGORY_MARGIN = 1  # approximates the margins around vertical bars; measure them if wide charts look off
    BAR_ROW = 0.6  # plot height per category for horizontal bars
    HORIZONTAL_WIDTH = 5  # figure width for horizontal bars
    BAR_GROUP_WIDTH = 0.65  # share of a category slot covered by its bars (dodged bars split it)
    DODGE_GAP = 0.06  # share of a category slot left between dodged bars
    PIE = 3.2


class Layout:
    """Points, measured from the figure edges."""
    PAD = 12
    CORNER_RADIUS = 6
    ROW_GAP = 6
    PLOT_GAP = 12
    TICK_GAP = 6
    LABEL_GAP = 14
    DATALABEL_GAP = 6
    DATALABEL_MIN_SPACE = 4  # whitespace between side-by-side data labels before they get shortened
    SWATCH = 8
    SWATCH_GAP = 4
    LEGEND_ITEM_GAP = 14
    LEGEND_GAP = 2  # extra space between title/subtitle and legend
    STACK_BLEND = 20  # gradient length across the boundary between stack segments
    WEDGE_SEAM = 1  # stroke in the slice's own color: anti-aliased edges of touching slices leave a white seam
    STACKED_LABEL_MIN_SHARE = 0.15  # smaller stack segments (share of tallest stack) get no label; rounded ends leave no room
    HAIRLINE = 0.5  # stroke width of grid lines and rect outlines
    AXIS_MARGIN = 0.05  # share of the data range padded on each side of an auto-scaled axis
    MAX_MONTH_TICKS = 24  # longer monthly axes label every 2nd, 3rd or 6th month; past that only years
    MONTH_TICK_STEPS = (1, 2, 3, 6)  # divide a year evenly so the labelled months repeat each year
    MONTH_TICK_ROTATION = 90
    MAX_DAY_TICKS = 12  # daily bar axes label every nth day so the dates do not overlap


class Marks:
    """Data-mark sizes. Bar widths are shares of a category slot, pie radii shares of the pie radius."""
    BAR_WIDTH = 0.6
    HORIZONTAL_BAR_WIDTH = 0.8
    HISTOGRAM_GAP = 0.15  # share of a bin left empty between neighbouring histogram bars
    PIE_LABEL_RADIUS = 0.6
    DONUT_LABEL_RADIUS = 0.8
    DONUT_HOLE_RADIUS = 0.6
    LINE_WIDTH = 1.5
    DOT_AREA = 36.0  # square points
    DOT_AREA_RANGE = (8, 200)  # square points, when sized by a column
    DOT_ALPHA = 0.8
