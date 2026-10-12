# %% [hidden]
import numpy as np
import pandas as pd
rng = np.random.default_rng(0)
df = df.sample(300, random_state=0)
df['weight'] = (100 + df['sweetness'] * 8 + rng.normal(0, 20, len(df))).round(1)
df['days_on_tree'] = rng.integers(10, 60, len(df))
trend = (df['weight'] - df['weight'].mean()) / df['weight'].std() + (df['sweetness'] - df['sweetness'].mean()) / df['sweetness'].std()
df['fruit'] = pd.qcut(trend, 6, labels=['Cherry', 'Fig', 'Date', 'Apple', 'Orange', 'Banana']).astype(str)

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
