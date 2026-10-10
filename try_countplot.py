# %%
import numpy as np
import pandas as pd

from shirin.plot import PlotGraphs

rng = np.random.default_rng(0)
fruit_share = {'Apple': .15, 'Banana': .08, 'Cherry': .3, 'Date': .05, 'Mango': .25, 'Fig': .17}
ripe_share = {'Apple': .8, 'Banana': .25, 'Cherry': .6, 'Date': .4, 'Mango': .9, 'Fig': .15}
fruit = rng.choice(list(fruit_share), 300, p=list(fruit_share.values()))
df = pd.DataFrame({
    'fruit': fruit,
    'ripe': rng.random(300) < pd.Series(fruit).map(ripe_share).to_numpy(),
})


plot = PlotGraphs(
    palette={'ripe': {True: "#e9d0ff", False: "#6f2525"}},
    label_mapping={'ripe': {True: 'Ripe', False: 'Unripe'}},
)

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
