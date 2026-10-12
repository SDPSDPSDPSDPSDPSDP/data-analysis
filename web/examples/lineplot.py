# %% [hidden]
from shirin.assets.data import df_documents_by_year
df = df_documents_by_year.rename(columns={'cumul_total_docs': 'harvest', 'example_hue_3': 'is_ripe'})
df = df.groupby('year', as_index=False)['harvest'].sum()

# %% Plain
plot.lineplot(
    df,
    x='year',
    y='harvest',
)

# %% [hidden]
df = df_documents_by_year.rename(columns={'cumul_total_docs': 'harvest', 'example_hue_3': 'is_ripe'})

# %% One line per hue, title, axis labels, legend, rotated ticks
plot.lineplot(
    df,
    x='year',
    y='harvest',
    hue='is_ripe',
    title=['Fruit harvest', 'Cumulative per year'],
    x_axis_label='Year',
    y_axis_label='Fruits harvested',
    rotation=45,
    legend=True,
)
