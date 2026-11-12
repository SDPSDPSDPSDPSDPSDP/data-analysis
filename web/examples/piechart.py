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
from shirin.number_format import format_percentage

sweet_share = (df.loc[df['is_ripe'], 'sweetness'] >= 12).mean() * 100
plot.pie(
    df,
    col='is_ripe',
    slice_labels={True: f'Sweetness: {format_percentage(sweet_share)}'},
    title=['Ripe vs unripe fruit', 'Share of ripe fruit with sweetness 12 or more'],
)
