# Migrating old shirin code to 4.x

4.0 replaced matplotlib/seaborn with an own SVG renderer and merged the per-orientation methods into one `bar`. Rewrite old calls with the tables below. Check the installed version first: `importlib.metadata.version('shirin')`.

How to spot the version of old code:
- `Palette` / `LabelMapping` subclasses, `@resolve_palette`: 3.x.
- `palette=` passed per plot call, `font=` on `PlotGraphs`: 2.6 - 2.9.
- `accuracy_plot(...)`: 2.8. `accuracy(...)`: 2.9 - 3.x.
- `countplot_y_normalized`, `print_stats`, `**kwargs` plot methods: 2.0 - 2.1.
- Anything with `export=`, `output_name=`, `xlabel=`, `plot_legend=`, `figsize_*`, `order_type=`: pre-4.0.

## Removed outright

| Old | 4.x |
|-----|-----|
| `PlotGraphs(export=, output_dir=, prefix=, format=)` | Removed. Charts display inline only. |
| `output_name=` on every plot method | Remove. |
| `legend_offset=`, `ncol=` | Remove. Layout is automatic. |
| `figsize_width=`, `figsize_height=` | Remove. Size is automatic. |
| `plt.title(...)`, `plt.savefig(...)`, any `plt.*` after a plot | Remove. Use `title=`. There is no matplotlib figure anymore. |
| `configure_matplotlib()` | Remove. |
| `pd.set_option('display.max_colwidth' / 'display.width')` side effect of `import shirin.plot` | Gone. Set it yourself if the notebook relied on it. |
| seaborn palette names (`palette='viridis'`) | Not supported. A string palette is now one hex color, values get shades of it. |

Saving to a file was the point of `export=True`. 4.x has no API for it; tell the user. Workaround, same hook the web playground uses:

```python
import shirin.plot.all_plots as ap
ap.show = lambda svg: open('chart.svg', 'w', encoding='utf-8').write(svg)
```

## PlotGraphs constructor

| Old | 4.x |
|-----|-----|
| `font=None` default (matplotlib font) | `font='satoshi'` default. Pass `font=None` for the viewer's sans-serif. |
| `palette=MyPalettes` (`Palette` subclass, 3.x) | `palette={'col': {...}, ...}` plain dict. One key per class attribute. |
| `label_mapping=MyLabels` (`LabelMapping` subclass, 3.x) | `label_mapping={'col': {...}}` plain dict. |
| `from shirin.plot import Palette, LabelMapping` | Remove import. Built-in `is_correct` entries still apply. |

```python
# 3.x
class MyPalettes(Palette):
    fruit = {'Apple': Colors.RED, 'Pear': Colors.GREEN}
    is_correct = Palette.is_correct
plot = PlotGraphs(palette=MyPalettes, label_mapping=MyLabels, export=True)

# 4.x
plot = PlotGraphs(
    palette={'fruit': {'Apple': Colors.RED, 'Pear': Colors.GREEN}},
    label_mapping={...},
)
```

2.x passed `palette=` per call. In 4.x move it to the constructor, keyed by the `hue` column (pie: the `col` column):

```python
# 2.x
plot.countplot_x(df, x='fruit', hue='ripe', palette={True: Colors.GREEN, False: Colors.RED})
# 4.x
plot = PlotGraphs(palette={'ripe': {True: Colors.GREEN, False: Colors.RED}})
plot.bar(df, x='fruit', hue='ripe')
```

If the same hue column needs different colors in different charts, make a second `PlotGraphs` instance.

## Shared argument renames (all methods)

| Old | 4.x |
|-----|-----|
| `xlabel=` | `x_axis_label=` |
| `ylabel=` | `y_axis_label=` |
| `plot_legend=True` (default was `True`) | `legend=` (default now `False`). Pass `legend=True` where a hue legend was shown. |
| `show_labels=` | `data_labels=` |
| `order_type=` | `sort=` (same options `'frequency'`, `'alphabetical'`) |
| no title argument | `title='...'` or `['title', 'subtitle']` |

## Method mapping

| Old | 4.x |
|-----|-----|
| `countplot_x(df, x=...)` | `bar(df, x=...)` |
| `countplot_y(df, y=...)` | `bar(df, y=...)` |
| `countplot_x/_y(..., hue=h, normalized=True)` | `bar(..., hue=h, normalized=True)`. No dict palette needed anymore. |
| `countplot_x/_y(..., normalized=True)` without hue | `bar(..., normalized=True)` |
| `countplot_y_normalized(df, y, hue)` (2.0) | `bar(df, y=y, hue=hue, normalized=True)` |
| `barplot_x(df, x=..., value=...)` | `bar(df, x=..., value=...)` |
| `barplot_y(df, y=..., value=...)` | `bar(df, y=..., value=...)` |
| `barplot_x/_y(..., percentage_labels=True)` | `bar(..., normalized=True)` (labels show share of total) |
| `stacked_labels='percentage'` | No equivalent. Closest: `normalized=True` with `hue` (100% stacked bars). Ask the user. |
| `stacked_labels='standard'` / `None` | Remove. Totals are labelled by default. |
| `accuracy(df, experiment=e, accuracy=a)` / `accuracy_plot(...)` | `bar(df, x=e, value=a, normalized=True, remainder=True)` |
| `accuracy(..., orientation='horizontal')` | `bar(df, y=e, value=a, normalized=True, remainder=True)` |
| `accuracy(..., experiment_label=, accuracy_label=)` | `x_axis_label=`, `y_axis_label=` (swap for horizontal) |
| `accuracy(..., color_correct=c)` | `PlotGraphs(palette={a: c})` (a = accuracy column name) |
| `accuracy(..., color_incorrect=, reverse=, reverse_order=)` | Remove. Remainder color and order are automatic. |
| `histogram(...)` | Same name. Rename shared args. `suffix=` now applies to x ticks. |
| `lineplot(...)` | Same name. Rename shared args. |
| `pie(df, col, palette=...)` | `pie(df, col)` with palette in the constructor under key `col`. |
| `timeplot(..., type='line')` | `timeplot(..., plot_type='line')` |
| `timeplot(..., palette='#hex')` | Remove. No color argument. |
| `timeplot` default `ylabel='Total'`, `histogram` default `ylabel='Count'` | No default y label anymore. Pass `y_axis_label='Total'` / `'Count'` to keep it. |
| - | New: `scatterplot(df, x, y, hue=, size=)` |

Accuracy charts: segments are now labelled with the value column name and `'Remainder'` instead of `'Correct'`/`'Incorrect'`. Rename the column (`df.rename(columns={'acc': 'Correct'})`) if the old label matters.

## Stats, number formatting, SQL

| Old | 4.x |
|-----|-----|
| `from shirin.stats import print_stats`; `print_stats(s)` (2.0) | `import shirin.stats`; `s.stats()` |
| `from shirin.stats.number_format import format_thousands` | `from shirin.number_format import format_thousands` (`from shirin.stats import format_thousands` still works) |
| `format_thousands(x)` always 0 decimals | Now picks decimals automatically for small values. Pass `decimals=0` for the old output. |
| `run_sql_query(sql, config, output_path)` | `from shirin.sql import Database`; `db = Database(user=..., password=..., host=..., port=..., db_name=..., schema=...)` once, then `db.sql(sql, params={...}, output_path=...)`. No JSON config: load your own file and pass `Database(**json.load(f))`. Replace f-string values in SQL with `params` (`:name` placeholders). |

## After converting

1. Grep the result for leftover old names: `countplot_|barplot_|accuracy|xlabel|ylabel|plot_legend|show_labels|order_type|output_name|figsize|legend_offset|ncol|stacked_labels|percentage_labels|export=|Palette|LabelMapping|plt\.`.
2. Run the notebook cells. Every `ValueError`/`TypeError` message names the bad argument.
3. Tell the user what changed visually: default legend off, Satoshi font, no file export, accuracy segment labels.
