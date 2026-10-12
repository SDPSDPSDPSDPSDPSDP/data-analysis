# Reads [{path, code}] as JSON on stdin and writes the chart each code draws to its path as SVG.
import json
import sys

import shirin.plot.all_plots as all_plots

images = []
all_plots.show = images.append

for chart in json.load(sys.stdin):
    images.clear()
    exec(chart["code"], {"__name__": "__main__"})
    if len(images) != 1:
        raise ValueError(f"Expected 1 chart, got {len(images)} for {chart['path']}:\n{chart['code']}")
    with open(chart["path"], "w", encoding="utf-8") as f:
        f.write(images[0])
