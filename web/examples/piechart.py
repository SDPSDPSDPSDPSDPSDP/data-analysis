# %% Plain
plot.pie(
    df,
    col='fruit',
)

# %% Title and subtitle
plot.pie(
    df,
    col='fruit',
    title=['Fruit basket', 'Share per fruit'],
)

# %% Donut
plot.pie(
    df,
    col='fruit',
    donut=True,
    n_after_comma=1,
    value_datalabel=10,
    title=['Donut', 'One decimal, labels from 10%'],
)

# %% Palette and label mapping
plot.pie(
    df,
    col='is_ripe',
    donut=True,
    title='Ripeness',
)
