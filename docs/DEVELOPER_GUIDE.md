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
python -m pytest
```

## Architecture

```
shirin/
  plot/
    all_plots.py   PlotGraphs: public entry point, composed of the graphs/ mixins
    graphs/        public methods (countplot_x, pie, ...): build an Options object, pick the plot class
    core/          Options dataclasses + validation, AbstractPlot, renderer (seaborn/matplotlib calls), exporter
    plots/         one class per chart: preprocess -> transform -> draw -> format_plot
    common/        shared helpers: data conversion, sorting, palettes, formatting (ticks, labels, legend)
    config/        colors, font sizes, palette/label-mapping base classes, matplotlib rc settings
  number_format.py Dutch number formatting, shared by plot and stats
  stats/           descriptive statistics accessor
  sql/             DB2 query helpers (optional `sql` extra)
  assets/          bundled fonts and demo data
```

Flow of one call: `PlotGraphs.countplot_x(...)` -> `CountPlotOptions` -> `CountPlot(options).render()`
(validates a copy of the options, draws on its own figure) -> `PlotExporter` saves/shows/closes that figure.
Styling is applied with `plt.rc_context`, so matplotlib's global `rcParams` are never changed.
