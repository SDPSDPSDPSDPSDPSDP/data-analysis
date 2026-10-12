# %% [hidden]
import numpy as np
rng = np.random.default_rng(0)
df = df.sample(300, random_state=0)
centers = {'Cherry': (60, 9), 'Date': (100, 15), 'Fig': (140, 12), 'Apple': (180, 14), 'Orange': (225, 11), 'Banana': (265, 17)}
weight_center, sweetness_center = zip(*df['fruit'].map(centers))
ripe_shift = np.where(df['is_ripe'], 1.2, -1.2)
df['weight'] = (np.array(weight_center) + ripe_shift * 6 + rng.normal(0, 12, len(df))).round(1)
df['sweetness'] = (np.array(sweetness_center) + ripe_shift + rng.normal(0, 1, len(df))).round(2)
df['days_on_tree'] = rng.integers(10, 60, len(df))

# %% Plain
plot.scatterplot(
    df,
    x='weight',
    y='sweetness',
)

# %% Color by hue, title, axis labels, legend
plot.scatterplot(
    df,
    x='weight',
    y='sweetness',
    hue='is_ripe',
    title=['Heavier fruit is sweeter', '300 fruits'],
    x_axis_label='Weight (g)',
    y_axis_label='Sugar (%)',
    legend=True,
)

# %% Point size by column
plot.scatterplot(
    df,
    x='weight',
    y='sweetness',
    hue='fruit',
    size='days_on_tree',
    title='Point size: days on the tree',
    legend=True,
)
