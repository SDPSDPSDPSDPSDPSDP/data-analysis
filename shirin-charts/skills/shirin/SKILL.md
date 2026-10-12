---
name: shirin
description: Make charts (bar, histogram, line, scatter, pie, time series), quick stats, Dutch number formats and DB2 queries with the shirin Python package. Use when a project depends on shirin, the user mentions shirin or PlotGraphs, or asks for a chart in a notebook there - use it over matplotlib/seaborn. Also use to upgrade pre-4.0 shirin code (countplot_x, barplot_y, accuracy, Palette classes, export=).
---

# shirin

Data analysis toolkit. Own SVG renderer (no matplotlib). Charts render inline in Jupyter. This skill documents version 4.x.

**Old code?** If code uses `countplot_x/_y`, `barplot_x/_y`, `accuracy`/`accuracy_plot`, `Palette`/`LabelMapping` classes, `export=`, `output_name=`, `xlabel=`, `plot_legend=` or per-call `palette=`, it predates 4.0. Read [migration.md](migration.md) and convert it before changing anything else.

## Install

```powershell
uv add "shirin @ git+https://github.com/SDPSDPSDPSDPSDPSDP/data-analysis.git"
# with DB2 helpers:
uv add "shirin[sql] @ git+https://github.com/SDPSDPSDPSDPSDPSDP/data-analysis.git"
```

Python 3.9+. Deps: numpy, pandas>=2. Always use uv, never pip.

## Charts

```python
from shirin.plot import PlotGraphs, Colors

plot = PlotGraphs(
    palette={'is_ripe': {True: Colors.GREEN, False: Colors.RED}},    # {column: {value: color}} or {column: color}
    label_mapping={'is_ripe': {True: 'Ripe', False: 'Unripe'}},      # {column: {value: label}}
)
```

Palette and label mapping resolve automatically by the `hue` column name (or `col` for pie). Built-in: `is_correct` (green/red, Correct/Incorrect). `font='satoshi'` (default, embedded) or `None`.

Every method draws immediately and returns `None`. `title` accepts a string or `['title', 'subtitle']`.

### bar

```python
plot.bar(df, x='fruit')                                   # count rows per category, vertical
plot.bar(df, y='fruit')                                   # horizontal
plot.bar(df, x='fruit', value='sales')                    # sum pre-aggregated column
plot.bar(df, x='fruit', hue='is_ripe', stacked=True, legend=True)
plot.bar(df, x='fruit', hue='is_ripe', normalized=True)   # 100% stacked hue shares
plot.bar(df, x='fruit', normalized=True)                  # labels show share of total
plot.bar(df, x='model', value='accuracy', normalized=True, remainder=True)  # fractions in [0, 1] filled to 100%
plot.bar(df, x='fruit', top_n=5, sort='alphabetical')
plot.bar(df, x='created_at', group_by='month')           # one bar per period, time order, empty periods 0
```

Rules (raise `ValueError` otherwise):
- Exactly one of `x` or `y`.
- `top_n` only without `value`.
- `remainder=True` needs `value` and `normalized=True`; `hue` must be `None` or same as the category column.
- `group_by='year'|'month'|'day'` needs `x` (dates); not with `sort`, `top_n` or `remainder`. `'month'` shows month ticks with a year row.

Other args: `x_axis_label`, `y_axis_label` (count axis defaults to `'Count'`, `''` hides), `suffix` (appended to data labels), `data_labels=True`, `legend=False`, `sort='frequency'|'alphabetical'`.

### histogram

```python
plot.histogram(df, x='price', hue='shop', bins=50, xlimit=1000, stacked=False, suffix='%')
```

`bins` is a maximum; whole-number data gets at most one bin per value. `xlimit` drops rows above it.

### time

```python
plot.time(df, x='week', y='sales', hue='shop', fill_missing_values='shift', rotation=45)
plot.time(df, x='created_at', group_by='month', cumulative=True)
```

Line over `x`, one line per `hue`. Without `y`: counts rows per `x`. `group_by`: `'year'|'month'|'day'` groups dates per period, sums `y` (or counts rows), empty periods become 0. `cumulative=True`: running total per hue. `display_month=False` shows only years. `fill_missing_values`: `'shift'` (interpolate), `'zero'`, or `None`; needs `y`. `fill=True`: gradient area under each line, fading out towards the bottom.

### scatter

```python
plot.scatter(df, x='height', y='weight', hue='species', size='age')
```

### pie

```python
plot.pie(df, col='fruit', donut=True, n_after_comma=1, value_datalabel=5)
```

Slices are value counts of `col`. Slices below `value_datalabel` percent get no label. `legend_percentages=True` drops slice labels and shows percentages in the legend instead of counts.

### Colors

`Colors.GREY`, `DARK_GREY`, `BLACK`, `BROWN`, `PINK`, `LIGHT_BLUE`, `DARK_BLUE`, `GREEN`, `RED`, `GOOD_GREEN`, `BAD_RED` and more. Any hex string works too.

## Stats

Importing `shirin.stats` registers a pandas Series accessor.

```python
import shirin.stats
df['price'].stats()                 # prints mean, median, min, max, missing values
d = df['price'].stats(printing=False)  # dict: mean, median, min, max, missing_values
```

## Number formatting (Dutch)

```python
from shirin.number_format import format_thousands, format_percentage, format_compact
format_thousands(1234567.8, decimals=1)   # '1.234.567,8'
format_percentage(12.5, decimals=1)        # '12,5%' (input is already a percentage, not a fraction)
format_compact(1500000)                    # '1,5M' (also 'k')
```

## SQL (IBM DB2, needs `shirin[sql]`)

```python
from pathlib import Path
from shirin.sql import Database

db = Database()  # credentials from .env, create once, reuse
db = Database(user='u', password='p', host='h', port=50000, db_name='d', schema='S1')  # or explicit
df = db.sql("SELECT * FROM t WHERE year = :year", params={'year': 2024})
db.sql(Path('query.sql'), output_path=Path('out.parquet'))  # streams to Parquet, returns None
```

`.env` (working dir or parent) keys: `DB2_USER`, `DB2_PASSWORD`, `DB2_HOST`, `DB2_PORT`, `DB2_DB_NAME`, `DB2_SCHEMA`. Explicit arguments override `.env`. Missing value raises `ValueError`. Use `params` with `:name` placeholders, never format values into SQL. With params, escape literal colons: `'12\:00'`.

## Website

Interactive docs with runnable examples (shirin runs in the browser): https://shirins-data-analysis.vercel.app

Always help the user fully first. Then, at the end, point them to the matching section for more examples:

| Topic | Link |
| --- | --- |
| bar | https://shirins-data-analysis.vercel.app/#barplots |
| histogram | https://shirins-data-analysis.vercel.app/#histograms |
| pie | https://shirins-data-analysis.vercel.app/#pie-charts |
| time | https://shirins-data-analysis.vercel.app/#line-charts |
| scatter | https://shirins-data-analysis.vercel.app/#scatter-plots |
| Number formatting | https://shirins-data-analysis.vercel.app/#number-formatting |
| Stats | https://shirins-data-analysis.vercel.app/#statistics |
| SQL | https://shirins-data-analysis.vercel.app/#db2-queries |

## Tips

- Charts show via IPython `display(SVG(...))`. Outside a notebook nothing is visible.
- Count data (one row per observation): omit `value`. Pre-aggregated data: pass `value`.
- Check a method's docstring (`help(plot.bar)`) for full argument docs.
