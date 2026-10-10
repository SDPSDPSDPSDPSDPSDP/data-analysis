# %%
import numpy as np
import pandas as pd

from shirin.plot import LabelMapping, Palette, PlotGraphs

rng = np.random.default_rng(0)
df = pd.DataFrame({
    'fruit': rng.choice(['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry', 'Fig'], 300, p=[.3, .25, .2, .12, .08, .05]),
    'ripe': rng.choice([True, False], 300),
})


class MyPalette(Palette):
    ripe = {True: '#57ccff', False: '#e3c2ff'}


class MyLabels(LabelMapping):
    ripe = {True: 'Ripe', False: 'Unripe'}


plot = PlotGraphs(palette=MyPalette, label_mapping=MyLabels)

# %% plain
plot.countplot_x(df, x='fruit')

# %% title + subtitle, axis labels, top_n
plot.countplot_x(df, x='fruit', title=['Fruit counts', 'Top 4 only'], x_axis_label='Fruit', top_n=4)

# %% alphabetical, no labels
plot.countplot_x(df, x='fruit', order_type='alphabetical', data_labels=False, title='Alphabetical')

# %% normalized without hue: labels show share of total
plot.countplot_x(df, x='fruit', normalized=True, title='Share of total')

# %% hue, grouped bars, legend
plot.countplot_x(df, x='fruit', hue='ripe', legend=True, title='Grouped by ripeness')

# %% hue, stacked
plot.countplot_x(df, x='fruit', hue='ripe', stacked=True, legend=True, title='Stacked')

# %% hue, normalized (100% stacked)
plot.countplot_x(df, x='fruit', hue='ripe', normalized=True, legend=True, title=['Normalized', 'Share ripe per fruit'])

# %% suffix
plot.countplot_x(df, x='fruit', suffix='pcs', title='With suffix')
