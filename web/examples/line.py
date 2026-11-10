# %% [hidden]
from shirin.assets.data import df_threshold_curve as df, df_threshold_curves

# %% Marks: rows where marked is True get a dot with their y value
plot.line(
    df,
    x='coverage',
    y='accuracy',
    marks='marked',
)

# %% Both values per mark, percentages, reversed x axis, axis labels
plot.line(
    df,
    x='coverage',
    y='accuracy',
    marks='marked',
    mark_labels='both',
    percentage_x=True,
    percentage_y=True,
    x_limits=(1, 0),
    y_limits=(0.4, 1),
    title=['Ripeness detector', 'Pick a threshold: higher means fewer fruits, but more of them right'],
    x_axis_label=['Coverage', 'Share of fruits at or above the threshold'],
    y_axis_label='Accuracy',
)

# %% One line per hue, legend
plot.line(
    df_threshold_curves,
    x='coverage',
    y='accuracy',
    hue='detector',
    marks='marked',
    percentage_x=True,
    percentage_y=True,
    x_limits=(1, 0),
    title='Old vs new detector',
    x_axis_label='Coverage',
    y_axis_label='Accuracy',
    legend=True,
)
