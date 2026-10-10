# %% [hidden]
from shirin.assets.data import df_fruit_counts as df

# %% Plain
plot.barplot(
    df,
    x='fruit',
    value='count',
)

# %% Title, axis labels, suffix
plot.barplot(
    df,
    y='fruit',
    value='count',
    title=['Fruit counts', 'Pre-aggregated'],
    y_axis_label='Fruit',
    suffix='pcs',
)

# %% Alphabetical, no data labels
plot.barplot(
    df,
    x='fruit',
    value='count',
    sort='alphabetical',
    data_labels=False,
    title='Alphabetical',
)

# %% Percentage labels
plot.barplot(
    df,
    y='fruit',
    value='count',
    normalized=True,
    title='Share of total',
)

# %% Grouped by hue
plot.barplot(
    df,
    x='fruit',
    value='count',
    hue='is_ripe',
    legend=True,
    title='Grouped by ripeness',
)

# %% Stacked by hue
plot.barplot(
    df,
    y='fruit',
    value='count',
    hue='is_ripe',
    stacked=True,
    legend=True,
    title='Stacked',
)

# %% 100% stacked by hue
plot.barplot(
    df,
    y='fruit',
    value='count',
    hue='is_ripe',
    normalized=True,
    legend=True,
    title=['Normalized', 'Share ripe per fruit'],
)
