# %% [setup] Import your data.
from shirin.assets.data import df

# %% [setup] Create the plotter once and reuse it for every chart. Use palette to give values of a column a fixed color, and label_mapping to show them with a readable name. These settings apply to all charts you make with this plotter.
from shirin.plot import PlotGraphs

plot = PlotGraphs(
    palette={'is_ripe': {True: "#e9d0ff", False: "#6f2525"}},
    label_mapping={'is_ripe': {True: 'Ripe', False: 'Unripe'}},
)

# %% Plain
plot.countplot(
    df,
    x='fruit',
)

# %% Title, axis label, top n, suffix
plot.countplot(
    df,
    y='fruit',
    title=['Fruit counts', 'Top 4 only'],
    y_axis_label='Fruit',
    top_n=4,
    suffix='pcs'
)

# %% Alphabetical, no data labels
plot.countplot(
    df,
    x='fruit',
    order_type='alphabetical',
    data_labels=False,
    title='Alphabetical',
)

# %% Normalized share of total
plot.countplot(
    df,
    y='fruit',
    normalized=True,
    title='Share of total',
)

# %% Grouped by hue
plot.countplot(
    df,
    x='fruit',
    hue='is_ripe',
    legend=True,
    title='Grouped by ripeness',
)

# %% 100% stacked by hue
plot.countplot(
    df,
    y='fruit',
    hue='is_ripe',
    normalized=True,
    legend=True,
    title=['Normalized', 'Share ripe per fruit'],
)
