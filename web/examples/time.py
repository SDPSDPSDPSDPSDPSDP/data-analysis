# %% [hidden]
from shirin.assets.data import df_documents_by_year, df_time
df = df_documents_by_year.rename(columns={'cumul_total_docs': 'n_harvested', 'example_hue_3': 'is_ripe'})
df = df.groupby('year', as_index=False)['n_harvested'].sum()

# %% Plain
plot.time(
    df,
    x='year',
    y='n_harvested',
)

# %% [hidden]
df = df_time.drop(columns='hue')

# %% Without y: count rows per month
plot.time(
    df,
    x='date',
    group_by='month',
    title='Fruits picked per month',
)

# %% [hidden]
df = df_documents_by_year.rename(columns={'cumul_total_docs': 'n_harvested', 'example_hue_3': 'is_ripe'})

# %% One line per hue, title, axis labels, legend, rotated ticks
plot.time(
    df,
    x='year',
    y='n_harvested',
    hue='is_ripe',
    title=['Fruit harvest', 'Cumulative per year'],
    x_axis_label='Year',
    y_axis_label='Fruits harvested',
    rotation=45,
    legend=True,
)

# %% [hidden]
df = df_time.drop(columns='hue')

# %% Cumulative, years only
plot.time(
    df,
    x='date',
    group_by='month',
    cumulative=True,
    display_month=False,
    title='Fruits picked so far',
)
