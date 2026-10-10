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
    sort='alphabetical',
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
