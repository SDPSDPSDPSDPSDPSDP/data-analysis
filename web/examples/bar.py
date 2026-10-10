# %% Count rows per category
plot.bar(
    df,
    x='fruit',
)

# %% Title, axis label, top n, suffix
plot.bar(
    df,
    y='fruit',
    title=['Fruit counts', 'Top 4 only'],
    y_axis_label='Fruit',
    top_n=4,
    suffix='pcs',
)

# %% Counts grouped by hue
plot.bar(
    df,
    x='fruit',
    hue='is_ripe',
    legend=True,
    title='Grouped by ripeness',
)

# %% [hidden]
from shirin.assets.data import df_fruit_counts as df

# %% Alphabetical, no data labels
plot.bar(
    df,
    x='fruit',
    value='count',
    hue='fruit',
    sort='alphabetical',
    data_labels=False,
    title='Alphabetical',
)

# %% Percentage labels
plot.bar(
    df,
    y='fruit',
    value='count',
    normalized=True,
    title='Share of total',
)

# %% Stacked by hue
plot.bar(
    df,
    y='fruit',
    value='count',
    hue='is_ripe',
    legend=True,
    stacked=True,
    title='Stacked',
)

# %% Share: fill each bar up to 100% with the remainder
plot.bar(
    df,
    x='fruit',
    value='sold_share',
    remainder=True,
    normalized=True,
    data_labels=False,
    title='Share sold',
)

# %% Share, colored per fruit
plot.bar(
    df,
    y='fruit',
    value='sold_share',
    hue='fruit',
    remainder=True,
    normalized=True,
    title='Share sold per fruit',
)
