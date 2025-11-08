from typing import Any, Dict, Optional


def create_label_map(
    label_map: Optional[Dict[Any, str]],
    values: Any
) -> Dict[str, str]:
    if label_map is None:
        return {str(key): str(key) for key in values}
    return {str(key): str(value) for key, value in label_map.items()}