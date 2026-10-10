from ...svg import Chart


def format_xy_labels(chart: Chart, x_axis_label: str = 'Count', y_axis_label: str = 'Count') -> None:
    chart.x.label = x_axis_label
    chart.y.label = y_axis_label
