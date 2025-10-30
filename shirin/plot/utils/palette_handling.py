
from typing import Any, Dict, Optional, Union

from ..config import Colors


def _is_dict_or_list(palette: Any) -> bool:
    return isinstance(palette, dict)


def handle_palette(
    palette: Optional[Union[Dict[Any, str], str]] = None,
    color: Optional[str] = None
) -> tuple[Optional[str], Optional[Union[Dict[Any, str], str]]]:
    if _is_dict_or_list(palette):
        return None, palette
    if palette is not None:
        return palette, None
    return Colors.GREY, None
