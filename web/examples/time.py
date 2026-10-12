# %% [hidden]
from shirin.assets.data import df_harvest_by_year, df_time
df = df_harvest_by_year.groupby('year', as_index=False)['n_harvested'].sum()

# %% Plain
plot.time(
    df,
    x='year',
    y='n_harvested',
)

# %% [hidden]
df = df_time

# %% Without y: count rows per month
plot.time(
    df,
    x='date',
    group_by='month',
    title='Fruits picked per month',
)

# %% [hidden]
df = df_harvest_by_year

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
df = df_time

# %% Cumulative, years only
plot.time(
    df,
    x='date',
    group_by='month',
    cumulative=True,
    display_month=False,
    title='Fruits picked so far',
)
