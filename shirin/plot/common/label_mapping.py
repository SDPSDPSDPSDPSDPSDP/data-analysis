from typing import Any, Dict, Optional


def create_label_map(
    label_map: Optional[Dict[Any, str]],
    values: Any
) -> Dict[Any, str]:
    if label_map is None:
        return {key: str(key) for key in values}
    return label_map