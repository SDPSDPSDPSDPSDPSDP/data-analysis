"""
Copy the Satoshi fonts the charts embed into the package and write their glyph widths.

The SVG renderer measures text without a font engine, so it needs every character's
advance width up front. Widths are stored as fractions of the em size.

Usage:
    uv run python scripts/build_font_metrics.py
"""

import json
import shutil
from pathlib import Path

from fontTools.ttLib import TTFont

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "scripts" / "fonts" / "Satoshi_Complete" / "WEB" / "fonts"
OUTPUT_DIR = REPO_ROOT / "shirin" / "assets" / "fonts"

# Medium reads as the regular chart weight.
WEIGHTS = {"regular": "Satoshi-Medium", "bold": "Satoshi-Bold"}


def glyph_metrics(ttf_path: Path) -> dict:
    font = TTFont(ttf_path)
    units = font["head"].unitsPerEm
    hmtx = font["hmtx"]
    # Charts render digits with tnum, which swaps in the ".tf" glyphs.
    widths = {
        str(code): hmtx[f"{name}.tf" if f"{name}.tf" in hmtx.metrics else name][0] / units
        for code, name in font.getBestCmap().items()
    }
    return {
        "widths": widths,
        "cap_height": font["OS/2"].sCapHeight / units,
        # Characters missing from the font are measured as an average glyph.
        "default": sum(widths.values()) / len(widths),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = {}
    for weight, name in WEIGHTS.items():
        metrics[weight] = glyph_metrics(SOURCE_DIR / f"{name}.ttf")
        shutil.copyfile(SOURCE_DIR / f"{name}.woff2", OUTPUT_DIR / f"{name}.woff2")
    (OUTPUT_DIR / "satoshi_metrics.json").write_text(json.dumps(metrics, separators=(",", ":")))
    print(f"Wrote metrics and fonts to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
