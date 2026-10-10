from typing import Any, Dict, Optional

from ...svg import Chart


def format_optional_legend(
    chart: Chart,
    hue: Optional[str],
    plot_legend: bool,
    label_map: Optional[Dict[Any, str]],
) -> None:
    if hue is None:
        return
    if not plot_legend:
        chart.legend = []
    elif label_map:
        chart.legend = [(color, label_map.get(label, label)) for color, label in chart.legend]
