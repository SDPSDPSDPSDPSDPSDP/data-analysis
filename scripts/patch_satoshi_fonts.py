"""
Patch Satoshi fonts to add extra letter-spacing for matplotlib compatibility.

matplotlib has no letter-spacing property, so we bake the spacing directly
into the font by increasing every glyph's advance width. The result is saved
as "Satoshi Shirin" — a spaced variant that renders cleanly in matplotlib's
Agg backend.

Usage:
    python scripts/patch_satoshi_fonts.py
    python scripts/patch_satoshi_fonts.py --spacing 65
"""

import argparse
import shutil
from pathlib import Path

from fontTools.ttLib import TTFont


SOURCE_DIR = Path("shirin/assets/Satoshi_Complete/WEB/fonts")
OUTPUT_DIR = Path("shirin/assets/fonts/patched")

FONTS_TO_PATCH = [
    "Satoshi-Medium.ttf",
    "Satoshi-Bold.ttf",
    # "Satoshi-Regular.ttf",
    # "Satoshi-Light.ttf",
    # "Satoshi-Italic.ttf",
    # "Satoshi-MediumItalic.ttf",
    # "Satoshi-BoldItalic.ttf",
    # "Satoshi-LightItalic.ttf",
]

NEW_FAMILY_NAME = "Satoshi Shirin"

# Mapping from original style substring to name record style.
# Medium is promoted to "Regular" so matplotlib uses it as the default weight.
STYLE_MAP = {
    "BoldItalic": ("Bold Italic", "Satoshi Shirin Bold Italic"),
    "MediumItalic": ("Medium Italic", "Satoshi Shirin Medium Italic"),
    "LightItalic": ("Light Italic", "Satoshi Shirin Light Italic"),
    "Bold": ("Bold", "Satoshi Shirin Bold"),
    "Medium": ("Regular", "Satoshi Shirin"),
    "Light": ("Light", "Satoshi Shirin Light"),
    "Italic": ("Italic", "Satoshi Shirin Italic"),
    "Regular": ("Regular", "Satoshi Shirin"),
}


def get_style_info(filename: str) -> tuple[str, str]:
    """Extract style and full name from filename."""
    for key, (style, full_name) in STYLE_MAP.items():
        if key in filename:
            return style, full_name
    return "Regular", "Satoshi Shirin"


def patch_font(input_path: Path, output_path: Path, extra_spacing: int) -> None:
    """Add extra_spacing units to every glyph's advance width and rename the font."""
    font = TTFont(input_path)
    hmtx = font["hmtx"]

    # Increase advance width for every glyph
    for glyph_name in hmtx.metrics:
        width, lsb = hmtx[glyph_name]
        hmtx[glyph_name] = (width + extra_spacing, lsb)

    # Rename the font family so matplotlib sees it as a distinct font.
    # We patch nameIDs 1, 2, 4, 6, 16, 17 to ensure matplotlib (which prefers
    # nameID 16/17 when present) always resolves the correct family + style.
    style, full_name = get_style_info(input_path.name)
    ps_name = full_name.replace(" ", "-")
    name_table = font["name"]
    for record in name_table.names:
        if record.nameID == 1:  # Font Family
            record.string = NEW_FAMILY_NAME
        elif record.nameID == 2:  # Font Subfamily (style)
            record.string = style
        elif record.nameID == 4:  # Full Name
            record.string = full_name
        elif record.nameID == 6:  # PostScript Name
            record.string = ps_name
        elif record.nameID == 16:  # Typographic Family Name
            record.string = NEW_FAMILY_NAME
        elif record.nameID == 17:  # Typographic Subfamily Name
            record.string = style

    # If Medium is promoted to Regular, update OS/2 weight class so
    # matplotlib's font matching treats it as the normal (400) weight.
    if style == "Regular":
        font["OS/2"].usWeightClass = 400

    font.save(str(output_path))
    font.close()
    print(f"  {input_path.name} -> {output_path.name}  (+{extra_spacing} units)")


def main():
    parser = argparse.ArgumentParser(description="Patch Satoshi fonts with extra spacing")
    parser.add_argument(
        "--spacing",
        type=int,
        default=50,
        help="Extra advance width in font units (1000 UPM). Default: 50",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Patching Satoshi fonts with +{args.spacing} spacing units (1000 UPM)")
    print(f"Output: {OUTPUT_DIR}/\n")

    patched_count = 0
    for font_file in FONTS_TO_PATCH:
        source = SOURCE_DIR / font_file
        if not source.exists():
            print(f"  SKIP {font_file} (not found)")
            continue

        # Derive output filename; Medium becomes Regular in the output
        output_name = font_file.replace("Satoshi-", "SatoshiShirin-")
        if "Medium" in font_file and "Italic" not in font_file:
            output_name = "SatoshiShirin-Regular.ttf"
        output_path = OUTPUT_DIR / output_name

        patch_font(source, output_path, args.spacing)
        patched_count += 1

    print(f"\nDone. Patched {patched_count} fonts.")


if __name__ == "__main__":
    main()
