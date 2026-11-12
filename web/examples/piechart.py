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
    legend_percentages=True,
    title='Ripe vs unripe fruit',
)

# %% Slice labels
from shirin.number_format import format_thousands

sweetness = df.loc[df['is_ripe'], 'sweetness'].mean()
plot.pie(
    df,
    col='is_ripe',
    slice_labels={True: f'Sweetness: {format_thousands(sweetness, decimals=1)}'},
    title=['Ripe vs unripe fruit', 'Average sweetness of the ripe fruit'],
)
