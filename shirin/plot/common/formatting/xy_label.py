from ...svg import Chart


def format_xy_labels(chart: Chart, xlabel: str = 'Count', ylabel: str = 'Count') -> None:
    chart.x.label = xlabel
    chart.y.label = ylabel
