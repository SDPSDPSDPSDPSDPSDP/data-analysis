# %%
from shirin.assets.data import df
from shirin.plot import PlotGraphs

plot = PlotGraphs(
    palette={'ripe': {True: "#e9d0ff", False: "#6f2525"}},
    label_mapping={'ripe': {True: 'Ripe', False: 'Unripe'}},
)

# %% plain
plot.countplot(df, y='fruit')

# %% title + subtitle, axis labels, top_n
plot.countplot(df, y='fruit', title=['Fruit counts', 'Top 4 only'], y_axis_label='Fruit', top_n=4)

# %% alphabetical, no labels
plot.countplot(df, y='fruit', order_type='alphabetical', data_labels=False, title='Alphabetical')

# %% hidden x axis label
plot.countplot(df, y='fruit', x_axis_label='', title='No x axis label')

# %% normalized without hue: labels show share of total
plot.countplot(df, y='fruit', normalized=True, title='Share of total')

# %% hue, grouped bars, legend
plot.countplot(df, y='fruit', hue='ripe', legend=True, title='Grouped by ripeness')

# %% hue, stacked
plot.countplot(df, y='fruit', hue='ripe', stacked=True, legend=True, title='Stacked')

# %% hue, normalized (100% stacked)
plot.countplot(df, y='fruit', hue='ripe', normalized=True, legend=True, title=['Normalized', 'Share ripe per fruit'])

# %% suffix
plot.countplot(df, y='fruit', suffix='pcs', title='With suffix')
