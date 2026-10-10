# Plan: own the chart layout, then maybe own the drawing

Goal: make `shirin` a cleaner, more predictable alternative to raw matplotlib. Every chart
should look the same, and labels, legends and margins should sit where they belong at
any figure size.

This package has one user, so it only needs to handle the cases that come up. Fix things
as they appear instead of solving every edge case up front.

## Why charts look messy today

The cause is mostly how this package places things, not matplotlib itself:

- Legends are placed with `bbox_to_anchor=(-0.01, legend_offset)`, where
  `legend_offset=1.13` is a fraction of the plot area's height. When the figure height
  changes, the legend drifts.
- Axis labels use fixed `labelpad` values (`10`, `20`, sometimes `0` in `accuracy.py`).
  Their distance from the plot area depends on the width of the tick labels.
- Margins are left to `bbox_inches="tight"`, `tight_layout()` and, in `timeplot.py`,
  a hard-coded `subplots_adjust(bottom=0.30)`.
- Figure sizes follow no single rule:
  - count and bar plots grow with the number of categories;
  - histograms are 8.4 x 8.4 inches;
  - line and scatter plots are 8.4 x 4 inches.
- There is no chart title option at all.

## Phase 1: own the layout, keep matplotlib for drawing

Give every part of the chart a fixed size and position, measured in points from the
figure edges rather than relative to the plot area. Matplotlib keeps doing what it is
good at: drawing shapes, measuring and rendering text, PNG output and date ticks.

### Layout spec (first draft, tune in the notebook)

The figure is split top to bottom into fixed rows:

```
+--------------------------------------------------+
| Title                          (optional, bold)  |  title row
| Subtitle                       (optional, grey)  |  subtitle row
| ■ x   ■ y   ■ z                (when hue)        |  legend row
|                                                  |
|  y-label   +----------------------------------+  |
|            |                                  |  |
|  ticks     |          plot area               |  |
|            |                                  |  |
|            +----------------------------------+  |
|                       ticks                      |
|                      x-label                     |
+--------------------------------------------------+
```

Rules:

- **Outer padding:** a fixed gap, for example 12 pt, on all sides.
- **Title, subtitle and legend:** left-aligned with the left edge of the plot area, not
  of the figure. This is how most modern chart styles align them.
- **Legend:** a single horizontal row of colored squares and labels. It wraps to a
  second row only when the row is wider than the plot area. `legend_offset` and `ncol`
  disappear.
- **Vertical gaps:** fixed point values between title, subtitle, legend and plot area.
  An empty row (for example no subtitle) takes no space.
- **Y-axis label:** horizontal above the y ticks, top-left of the plot area, instead of
  rotated 90°. Easier to read; decide in the notebook.
- **X-axis label:** centered under the x tick labels, with a fixed gap.
- **Left margin:** computed from the widest y tick label, measured with matplotlib's
  text renderer. No more `labelpad` guessing.
- **Bottom margin:** computed from the tick label height, including rotation for
  `timeplot`. This replaces `subplots_adjust(bottom=0.30)`.

### Figure size

- **Width:** one fixed default width for all charts, so pasted charts line up in a
  document. Count and bar plots keep growing with many categories, but by a clear rule:
  a fixed bar slot per category, with the default width as the minimum.
- **Height:** the plot area height is fixed per chart type. The full figure height is
  the plot area plus whatever rows are present (title, legend, x label). Adding a title
  never squeezes the plot.

### Implementation steps

1. Add a small layout module, for example `shirin/plot/core/layout.py`. Input: the
   figure size and the texts that are present (title, subtitle, legend items, axis
   labels). It measures the texts and returns the positions in figure coordinates of
   the plot area, title, legend and labels.
2. Create the figure first, then the axes at the computed position with
   `fig.add_axes([...])`. Place title, legend and labels with `fig.text(...)` and
   `fig.legend(...)`, not with axes-relative anchors.
3. Add `title` and `subtitle` parameters to the `PlotGraphs` methods.
4. Apply this to `countplot_x` first and check it in `example_notebook.ipynb`. Adjust
   the spec numbers until it looks right.
5. Port the other plots one by one: bar, histogram, line, scatter, timeplot, accuracy,
   pie. Delete `legend_offset`, `ncol`, the `labelpad` arguments, `tight_layout()` and
   `subplots_adjust()` as each plot moves over.
6. Replace `bbox_inches="tight"` thinking entirely: the computed figure size is the
   final size.

### Done when

- Every chart type uses the layout module.
- No magic offsets are left in the code (`1.13`, `labelpad=20`, `bottom=0.30`).
- Changing the figure size or adding a title does not move the legend or labels
  relative to each other.

## Phase 2 (optional): own the drawing, render SVG

Do this only if matplotlib still feels in the way after phase 1.

Swap the drawing part for a small SVG writer. The layout module from phase 1 carries over
unchanged, because it only produces numbers.

What it buys:

- Real `letter-spacing` and clean font handling via `@font-face`. The patched Satoshi
  font and `scripts/patch_satoshi_fonts.py` can go.
- Full control over every pixel, with no matplotlib defaults to fight.
- One fewer heavy dependency.

What has to be built (roughly 400–600 lines in total):

- Scales: linear, categorical (bands) and time.
- "Nice" tick values. Port the idea of matplotlib's `MaxNLocator`. The license is BSD,
  so keep its copyright notice when copying code.
- Date ticks for `timeplot`. Port the parts of `AutoDateLocator` that are needed:
  day, month and year.
- Text measurement from the font's glyph widths with `fontTools`, which is already a
  dev dependency.
- Shapes: rectangles, lines, markers and pie arcs as SVG elements.

Output in the notebook:

- First check whether copying an SVG output from a VS Code notebook works reliably. If
  it does not, render to PNG (for example with `resvg`, which has Windows wheels) and
  show it with `IPython.display.Image`.

Edge cases (negative values, NaN, a single category, very large numbers, overlapping
labels) are handled when they show up, not before.

## Order of work

1. Phase 1 on `countplot_x`, reviewed in the notebook.
2. Phase 1 on the remaining plots.
3. Use it for a while. Decide on phase 2 based on what still bothers you.
