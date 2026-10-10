# %%
from shirin.assets.data import df
from shirin.plot import PlotGraphs

plot = PlotGraphs(
    palette={'is_ripe': {True: "#e9d0ff", False: "#6f2525"}},
    label_mapping={'is_ripe': {True: 'Ripe', False: 'Unripe'}},
)

totals = df.groupby('fruit').size().reset_index(name='count')
by_ripe = df.groupby(['fruit', 'is_ripe']).size().reset_index(name='count')
shares = totals.assign(share=totals['count'] / totals['count'].sum())

# %% plain, vertical
plot.bar(totals, x='fruit', value='count')

# %% plain, horizontal
plot.bar(totals, y='fruit', value='count')

# %% title + subtitle, axis labels
plot.bar(totals, x='fruit', value='count', title=['Fruit counts', 'Pre-aggregated'], x_axis_label='Fruit', y_axis_label='Count')
plot.bar(totals, y='fruit', value='count', title=['Fruit counts', 'Pre-aggregated'], x_axis_label='Count', y_axis_label='Fruit')

# %% alphabetical, no labels
plot.bar(totals, x='fruit', value='count', sort='alphabetical', data_labels=False, title='Alphabetical')
plot.bar(totals, y='fruit', value='count', sort='alphabetical', data_labels=False, title='Alphabetical')

# %% percentage labels
plot.bar(shares, x='fruit', value='share', normalized=True, title='Share of total')
plot.bar(shares, y='fruit', value='share', normalized=True, title='Share of total')

# %% hue, grouped bars, legend
plot.bar(by_ripe, x='fruit', value='count', hue='is_ripe', legend=True, title='Grouped by ripeness')
plot.bar(by_ripe, y='fruit', value='count', hue='is_ripe', legend=True, title='Grouped by ripeness')

# %% hue, stacked
plot.bar(by_ripe, x='fruit', value='count', hue='is_ripe', stacked=True, legend=True, title='Stacked')
plot.bar(by_ripe, y='fruit', value='count', hue='is_ripe', stacked=True, legend=True, title='Stacked')

# %% suffix
plot.bar(totals, x='fruit', value='count', suffix='pcs', title='With suffix')
plot.bar(totals, y='fruit', value='count', suffix='pcs', title='With suffix')
