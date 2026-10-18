A reusable package to create data visualizations quickly, efficiently and uniformly, plus helpers for repetitive data tasks:

- `shirin.plot`: SVG charts (bar, histogram, time, scatter, pie) with its own renderer.
- `shirin.stats`: descriptive statistics on a pandas Series.
- `shirin.number_format`: Dutch number formatting.
- `shirin.sql`: DB2 query helpers (optional `sql` extra).

### Install

```powershell
uv add "shirin @ git+https://github.com/SDPSDPSDPSDPSDPSDP/data-analysis.git"
# with DB2 helpers:
uv add "shirin[sql] @ git+https://github.com/SDPSDPSDPSDPSDPSDP/data-analysis.git"
```

### Example Usage

Runnable examples for every chart and module are on the website: https://shirins-data-analysis.vercel.app

### Documentation

The [`docs/`](./docs/) folder has a developer guide with setup steps and an overview of the package layout, and the coding standards.

### Claude Code skill

A skill that teaches Claude how to use this package ships as a plugin in [`shirin-charts/`](./shirin-charts/). Install it with:

```
/plugin marketplace add SDPSDPSDPSDPSDPSDP/data-analysis
/plugin install shirin-charts@shirin-charts
```

### Website

Write Python on the left and see the chart on the right. Python runs in the browser with Pyodide. To run it locally:

```powershell
cd web; npm run dev
```

Then open http://localhost:6817.

---

WIP: This package is and always will be a work in progress.
