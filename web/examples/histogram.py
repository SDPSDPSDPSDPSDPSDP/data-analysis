# %% Plain
plot.histogram(
    df,
    x='weight',
)

# %% Title, axis labels, fewer bins
plot.histogram(
    df,
    x='weight',
    title=['Fruit weight', '20 bins'],
    x_axis_label='Weight (g)',
    y_axis_label='Fruits',
    bins=20,
)

# %% Upper limit
plot.histogram(
    df,
    x='weight',
    xlimit=100,
    title=['Light fruit', 'Weight up to 100 g'],
)

# %% Stacked by hue
plot.histogram(
    df,
    x='weight',
    hue='is_ripe',
    bins=30,
    legend=True,
    title='Stacked by ripeness',
)

# %% Dodged by hue
plot.histogram(
    df,
    x='weight',
    hue='is_ripe',
    bins=30,
    stacked=False,
    legend=True,
    title='Side by side',
)
