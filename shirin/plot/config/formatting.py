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


class Marks:
    """Data-mark sizes. Bar widths are shares of a category slot, pie radii shares of the pie radius."""
    BAR_WIDTH = 0.6
    HORIZONTAL_BAR_WIDTH = 0.8
    HISTOGRAM_GAP = 0.15  # share of a bin left empty between neighbouring histogram bars
    TIME_BAR_DAYS = {'year': 300, 'month': 25, 'day': 0.8}  # bar width in days per time grouping
    PIE_LABEL_RADIUS = 0.6
    DONUT_LABEL_RADIUS = 0.8
    DONUT_HOLE_RADIUS = 0.6
    LINE_WIDTH = 1.5
    TIME_LINE_WIDTH = 2
    LINE_MARKER_RADIUS = 2
    TIME_LINE_MARKER_RADIUS = 1.5
    TIME_LINE_ALPHA = 0.9
    TIME_LINE_MAX_MARKED_DAYS = 25  # longer daily lines drop markers
    DOT_AREA = 36.0  # square points
    DOT_AREA_RANGE = (18, 72)  # square points, when sized by a column
    DOT_ALPHA = 0.8
