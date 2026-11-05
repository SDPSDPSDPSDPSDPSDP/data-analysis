# Reads preview SVG paths as JSON on stdin and composes them into a 1200x630 Open Graph PNG at argv[1].
import json
import re
import sys

import resvg_py

from shirin.plot.svg.fonts import TTF_FILES

WIDTH, HEIGHT = 1200, 630
COLUMNS, ROWS = 5, 3
COLUMN_CENTERS = [216 + 192 * i for i in range(COLUMNS)]
ROW_CENTERS = [124, 316, 509]
CARD_MAX_WIDTH, CARD_MAX_HEIGHT = 146, 166
# Site tokens scaled to the image: --radius-home-chart and --shadow-home-chart at ~0.7x.
CARD_RADIUS = 7
SHADOW = '<feDropShadow dx="0" dy="1.4" stdDeviation="4.2" flood-color="#000" flood-opacity="0.06"/>'
# A shade darker than --color-bg-home, so the white cards stand out at thumbnail size.
BACKGROUND = "#f2f4f7"

paths = json.load(sys.stdin)
if len(paths) != COLUMNS * ROWS:
    raise ValueError(f"Expected {COLUMNS * ROWS} charts for the grid, got {len(paths)}")

clips, cards = [], []
font_style = ""
for i, path in enumerate(paths):
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    # Every preview embeds the same Satoshi @font-face; keep one copy at the top level.
    font_style = re.search(r"<style>.*?</style>", svg, re.S).group(0)
    svg = re.sub(r"<style>.*?</style>", "", svg, count=1, flags=re.S)
    view_box = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    scale = min(CARD_MAX_WIDTH / view_box[2], CARD_MAX_HEIGHT / view_box[3])
    w, h = view_box[2] * scale, view_box[3] * scale
    x, y = COLUMN_CENTERS[i % COLUMNS] - w / 2, ROW_CENTERS[i // COLUMNS] - h / 2
    box = f'x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}"'
    svg = re.sub(r"^<svg [^>]*>", f'<svg {box} viewBox="{" ".join(map(str, view_box))}">', svg)
    clips.append(f'<clipPath id="card{i}"><rect {box} rx="{CARD_RADIUS}"/></clipPath>')
    cards.append(f'<rect {box} rx="{CARD_RADIUS}" fill="#fff" filter="url(#shadow)"/>')
    cards.append(f'<g clip-path="url(#card{i})">{svg}</g>')

page = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">'
    f'{font_style}<defs><filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">{SHADOW}</filter>'
    f'{"".join(clips)}</defs><rect width="{WIDTH}" height="{HEIGHT}" fill="{BACKGROUND}"/>{"".join(cards)}</svg>'
)
with open(sys.argv[1], "wb") as f:
    f.write(resvg_py.svg_to_bytes(svg_string=page, font_files=TTF_FILES))
