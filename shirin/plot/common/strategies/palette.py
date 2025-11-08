from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union


class PaletteStrategy(ABC):
    @abstractmethod
    def get_palette(
        self
    ) -> tuple[Optional[str], Optional[Union[Dict[Any, str], str]]]:
        pass


class DictPaletteStrategy(PaletteStrategy):
    def __init__(self, palette: Dict[Any, str]):
        self.palette = palette
    
    def get_palette(
        self
    ) -> tuple[Optional[str], Optional[Union[Dict[Any, str], str]]]:
        return (None, self.palette)


class NamedPaletteStrategy(PaletteStrategy):
    def __init__(self, palette_name: str):
        self.palette_name = palette_name
    
    def get_palette(
        self
    ) -> tuple[Optional[str], Optional[Union[Dict[Any, str], str]]]:
        return (self.palette_name, None)


class DefaultPaletteStrategy(PaletteStrategy):
    def get_palette(
        self
    ) -> tuple[Optional[str], Optional[Union[Dict[Any, str], str]]]:
        from ...config import Colors
        return (Colors.GREY, None)


def get_palette_strategy(
    palette: Optional[Union[Dict[Any, str], str]]
) -> PaletteStrategy:
    if isinstance(palette, dict):
        return DictPaletteStrategy(palette)
    elif isinstance(palette, str):
        return NamedPaletteStrategy(palette)
    else:
        return DefaultPaletteStrategy()
