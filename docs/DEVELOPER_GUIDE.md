# Developer Guide

## Setup

This project uses `uv` for dependency management. Make sure you have `uv` installed.

### Initial Setup

1. Clone the repository
2. Install dependencies using `uv`:
   ```powershell
   uv sync
   ```

This will create a virtual environment and install all project dependencies.

## Running Tests

To run the test suite locally, use:

```powershell
uv run python -m pytest
```

## Architecture

```
shirin/
  plot/
    all_plots.py   PlotGraphs: public entry point, composed of the graphs/ mixins
    graphs/        public methods (bar, pie, ...): build an Options object, pick the plot class
    core/          Options dataclasses + validation, AbstractPlot, renderer/ (fills a Chart with marks)
    plots/         one class per chart: preprocess -> transform -> draw -> format_plot
    common/        shared helpers: data conversion, sorting, palettes, formatting (ticks, labels, legend)
    config/        colors, font sizes, layout sizes, palette/label-mapping base classes
    svg/           Chart data model, nice/date ticks, font metrics, layout + SVG writer
  number_format.py Dutch number formatting, shared by plot and stats
  stats/           descriptive statistics accessor
  sql/             DB2 query helpers (optional `sql` extra): engine.py config + pooled engine, helpers.py queries, parquet.py streaming export
  assets/          bundled fonts and demo data
```

Flow of one call: `PlotGraphs.bar(...)` -> `CountPlotOptions` (no `value`), `BarPlotOptions`, or `NormalizedPlotOptions`
(`normalized=True` with `hue`, or `remainder=True`) -> `CountPlot` / `BarPlot` / `NormalizedPlot(options).render()`
(validates a copy of the options, fills a `Chart` in data coordinates) -> `svg.to_svg` lays it out and writes
the SVG -> `all_plots.show` displays it in the notebook (the web worker replaces `show` to collect the SVG).

Text is measured with Satoshi glyph widths from `assets/fonts/satoshi_metrics.json`. After changing the fonts, run
`uv run python scripts/build_font_metrics.py`.
