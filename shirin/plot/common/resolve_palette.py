from typing import Any, Dict, Optional


def resolve_palette(graphs: Any, column: Optional[str]) -> Dict[str, Any]:
    """palette and label_map for a hue (or pie col) column, from the PlotGraphs config."""
    if column is None:
        return {'palette': None, 'label_map': None}
    return {'palette': graphs._palette.get(column), 'label_map': graphs._label_mapping.get(column)}
