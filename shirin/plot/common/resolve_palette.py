from typing import Any, Dict, Optional


def resolve_palette(graphs: Any, column: Optional[str]) -> Dict[str, Any]:
    """palette and label_map for a hue (or pie col) column, from the PlotGraphs config."""
    resolved: Dict[str, Any] = {'palette': None, 'label_map': None}
    if column is None:
        return resolved
    sources = (
        ('palette', 'palette', 'Palette', graphs._palette),
        ('label_map', 'label_mapping', 'LabelMapping', graphs._label_mapping),
    )
    for arg, name, base, source in sources:
        if source is None:
            continue
        if not callable(getattr(source, 'get', None)):
            raise TypeError(f"{name} must be a {base} subclass, got {type(source).__name__}")
        resolved[arg] = source.get(column)
    return resolved
