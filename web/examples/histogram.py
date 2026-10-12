# %% Plain
plot.histogram(
    df,
    x='sweetness',
)

# %% Title, axis labels, fewer bins
plot.histogram(
    df,
    x='sweetness',
    title=['Fruit sweetness', '20 bins'],
    x_axis_label='Sugar',
    suffix='%',
    y_axis_label='Number of fruits',
    bins=20,
)

# %% Upper limit
plot.histogram(
    df,
    x='sweetness',
    xlimit=10,
    title=['Sour fruit', 'Sugar up to 10%'],
)

# %% Stacked by hue [no-home]
plot.histogram(
    df,
    x='sweetness',
    hue='is_ripe',
    bins=30,
    legend=True,
    title='Sweetness by ripeness',
)

# %% Dodged by hue
plot.histogram(
    df,
    x='sweetness',
    hue='is_ripe',
    bins=30,
    stacked=False,
    legend=True,
    title='Sweetness, ripe vs unripe',
)
