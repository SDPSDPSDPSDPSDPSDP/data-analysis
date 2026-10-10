# %% [setup] Import your data.
from shirin.assets.data import df

# %% [setup] Create the plotter once and reuse it for every chart. Use palette to give values of a column a fixed color, and label_mapping to show them with a readable name. These settings apply to all charts you make with this plotter.
from shirin.plot import PlotGraphs

plot = PlotGraphs(
    palette={'ripe': {True: "#e9d0ff", False: "#6f2525"}},
    label_mapping={'ripe': {True: 'Ripe', False: 'Unripe'}},
)

# %% Plain
plot.countplot_x(
    df,
    x='fruit',
)

# %% Title, axis label, top n, suffix
plot.countplot_x(
    df,
    x='fruit',
    title=['Fruit counts', 'Top 4 only'],
    x_axis_label='Fruit',
    top_n=4,
    suffix='pcs'
)

# %% Alphabetical, no data labels
plot.countplot_x(
    df,
    x='fruit',
    order_type='alphabetical',
    data_labels=False,
    title='Alphabetical',
)

# %% Normalized share of total
plot.countplot_x(
    df,
    x='fruit',
    normalized=True,
    title='Share of total',
)

# %% Grouped by hue
plot.countplot_x(
    df,
    x='fruit',
    hue='ripe',
    legend=True,
    title='Grouped by ripeness',
)

# %% 100% stacked by hue
plot.countplot_x(
    df,
    x='fruit',
    hue='ripe',
    normalized=True,
    legend=True,
    title=['Normalized', 'Share ripe per fruit'],
)
