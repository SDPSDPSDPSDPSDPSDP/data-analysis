# %% Plain
plot.pie(
    df,
    col='fruit',
)

# %% Donut [no-home]
plot.pie(
    df,
    col='fruit',
    donut=True,
    n_after_comma=1,
    value_datalabel=10,
    title=['Fruit basket', 'Share per fruit'],
)

# %% Pie [home-only]
plot.pie(
    df,
    col='fruit',
    n_after_comma=1,
    value_datalabel=10,
    title=['Fruit basket', 'Share per fruit'],
)

# %% Palette and label mapping
plot.pie(
    df,
    col='is_ripe',
    donut=True,
    title='Ripe vs unripe fruit',
)
