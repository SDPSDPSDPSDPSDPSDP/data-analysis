import base64
import functools
import json
from pathlib import Path
from typing import Any, Dict, Optional

FONTS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"
# em; Satoshi reads cramped at chart sizes without extra tracking.
LETTER_SPACING = 0.05
BOLD_LETTER_SPACING = 0.02
FONT_FILES = {500: "Satoshi-Medium.woff2", 700: "Satoshi-Bold.woff2"}


@functools.lru_cache(maxsize=None)
def _metrics() -> Dict[str, Any]:
    path = FONTS_DIR / "satoshi_metrics.json"
    if not path.exists():
        raise FileNotFoundError(f"Font metrics not found at {path}; reinstall the package.")
    return json.loads(path.read_text())


def text_width(text: str, size: float, bold: bool = False) -> float:
    """Width in points. Always measured with Satoshi, so with font=None it is an estimate."""
    metrics = _metrics()['bold' if bold else 'regular']
    widths, default = metrics['widths'], metrics['default']
    return size * (sum(widths.get(str(ord(char)), default) for char in text) + (BOLD_LETTER_SPACING if bold else LETTER_SPACING) * len(text))


def cap_height(size: float) -> float:
    return size * _metrics()['regular']['cap_height']


@functools.lru_cache(maxsize=None)
def _font_face(weight: int) -> str:
    data = base64.b64encode((FONTS_DIR / FONT_FILES[weight]).read_bytes()).decode()
    return (
        f"@font-face{{font-family:Satoshi;font-weight:{weight};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


def font_css(font: Optional[str], bold_used: bool) -> str:
    """Style block for the SVG; Satoshi is embedded so the chart renders the same everywhere."""
    if font is None:
        return "text{font-family:Helvetica,Arial,sans-serif}.b{font-weight:700}"
    faces = _font_face(500) + (_font_face(700) if bold_used else '')
    return f"{faces}text{{font-family:Satoshi;font-weight:500;letter-spacing:{LETTER_SPACING}em}}.b{{font-weight:700;letter-spacing:{BOLD_LETTER_SPACING}em}}"
