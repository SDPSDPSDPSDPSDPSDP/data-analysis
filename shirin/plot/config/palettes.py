from typing import Any, Dict, Optional, Tuple, Union

from .colors import Colors

PaletteInput = Dict[str, Union[Dict[Any, str], str]]
LabelMappingInput = Dict[str, Dict[Any, str]]

# Plain dicts instead of user subclasses: class-level dicts trip linters (Ruff RUF012) in user code.
DEFAULT_PALETTE: PaletteInput = {
    'is_correct': {True: Colors.GOOD_GREEN, False: Colors.BAD_RED},
}

DEFAULT_LABEL_MAPPING: LabelMappingInput = {
    'is_correct': {True: 'Correct', False: 'Incorrect'},
}


def merge_column_config(name: str, defaults: Dict[str, Any], user: Optional[Dict[str, Any]], allowed: Tuple[type, ...]) -> Dict[str, Any]:
    """Validate a ``{column: mapping}`` dict and layer it over the built-in defaults."""
    if user is None:
        return dict(defaults)
    if not isinstance(user, dict):
        raise TypeError(f"{name} must be a dict of {{column: mapping}}, got {type(user).__name__}")
    for column, value in user.items():
        if not isinstance(value, allowed):
            expected = ' or '.join(t.__name__ for t in allowed)
            raise TypeError(f"{name}[{column!r}] must be a {expected}, got {type(value).__name__}")
    return {**defaults, **user}
