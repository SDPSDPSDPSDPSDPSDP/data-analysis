# %%
from shirin.assets.data import df
from shirin.plot import PlotGraphs

plot = PlotGraphs(
    palette={'ripe': {True: "#e9d0ff", False: "#6f2525"}},
    label_mapping={'ripe': {True: 'Ripe', False: 'Unripe'}},
)

totals = df.groupby('fruit').size().reset_index(name='count')
by_ripe = df.groupby(['fruit', 'ripe']).size().reset_index(name='count')
shares = totals.assign(share=totals['count'] / totals['count'].sum())

# %% plain, vertical
plot.barplot(totals, x='fruit', value='count')

# %% plain, horizontal
plot.barplot(totals, y='fruit', value='count')

# %% title + subtitle, axis labels
plot.barplot(totals, x='fruit', value='count', title=['Fruit counts', 'Pre-aggregated'], x_axis_label='Fruit', y_axis_label='Count')
plot.barplot(totals, y='fruit', value='count', title=['Fruit counts', 'Pre-aggregated'], x_axis_label='Count', y_axis_label='Fruit')

# %% alphabetical, no labels
plot.barplot(totals, x='fruit', value='count', order_type='alphabetical', data_labels=False, title='Alphabetical')
plot.barplot(totals, y='fruit', value='count', order_type='alphabetical', data_labels=False, title='Alphabetical')

# %% percentage labels
plot.barplot(shares, x='fruit', value='share', percentage_labels=True, title='Share of total')
plot.barplot(shares, y='fruit', value='share', percentage_labels=True, title='Share of total')

# %% hue, grouped bars, legend
plot.barplot(by_ripe, x='fruit', value='count', hue='ripe', legend=True, title='Grouped by ripeness')
plot.barplot(by_ripe, y='fruit', value='count', hue='ripe', legend=True, title='Grouped by ripeness')

# %% hue, stacked
plot.barplot(by_ripe, x='fruit', value='count', hue='ripe', stacked=True, legend=True, title='Stacked')
plot.barplot(by_ripe, y='fruit', value='count', hue='ripe', stacked=True, legend=True, title='Stacked')

# %% suffix
plot.barplot(totals, x='fruit', value='count', suffix='pcs', title='With suffix')
plot.barplot(totals, y='fruit', value='count', suffix='pcs', title='With suffix')
