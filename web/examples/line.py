# %% [hidden]
from shirin.assets.data import df_threshold_curve as df

# %% Marks from a column: rows with a value in marked get a dot and that value
plot.line(
    df,
    x='coverage',
    y='accuracy',
    labels='marked',
)

# %% Marks from a list, percentages, reversed x axis, axis labels
plot.line(
    df,
    x='coverage',
    y='accuracy',
    labels='threshold',
    label_values=[0.5, 0.9, 0.95, 0.98],
    percentage_x=True,
    percentage_y=True,
    x_limits=(1, 0),
    y_limits=(0.5, 1),
    title=['Ripeness detector', 'Pick a threshold: higher means fewer fruits, but more of them right'],
    x_axis_label=['Coverage', 'share of fruits at or above the threshold'],
    y_axis_label='Accuracy above the threshold',
)
