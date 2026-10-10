from typing import Optional

from ...svg import Chart


def format_xy_labels(chart: Chart, x_axis_label: Optional[str], y_axis_label: Optional[str]) -> None:
    chart.x.label = x_axis_label
    chart.y.label = y_axis_label
