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
    legend=True,
    stacked=True,
    title='Stacked',
)

# %% Accuracy: fill each run up to 100% with the remainder
from shirin.assets.data import df_accuracy

plot.barplot(
    df_accuracy,
    x='run_name',
    value='accuracy',
    remainder='Incorrect',
    normalized=True,
    title='Accuracy per run',
)
