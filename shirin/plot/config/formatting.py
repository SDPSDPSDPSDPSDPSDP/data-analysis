from dataclasses import dataclass


@dataclass
class FontSizes:
    TEXT = 10
    TITLE = 15
    TICKS = 8
    DATALABELS = 8
    XYLABEL = 10
    LEGEND = 8

@dataclass
class FigureSize:
    HEIGHT = 8 * 1.5
    WIDTH = 12 * 1.5 * 0.7
    STANDARD_HEIGHT = 4
    PIE = 4 * 1.2