# %% [hidden]
from shirin.assets.data import df_threshold_curve as df

# %% Marks from a column: rows with a value in marked get a dot and that value
plot.line(
    df,
    x='coverage',
    y='accuracy',
    labels='marked',
    percentage_x=True,
    percentage_y=True,
    x_limits=(1, 0),
    y_limits=(0.85, 1),
    title='Ripeness detector: coverage vs accuracy per threshold',
    x_axis_label=['Coverage', 'share of fruits at or above the threshold'],
    y_axis_label='Accuracy above the threshold',
)

# %% Marks from a list: only these thresholds get a dot and label
plot.line(
    df,
    x='coverage',
    y='accuracy',
    labels='threshold',
    label_values=[0.5, 0.9, 0.95, 0.98],
    percentage_x=True,
    percentage_y=True,
    x_limits=(1, 0),
    y_limits=(0.85, 1),
    title=['Ripeness detector', 'Pick a threshold: higher means fewer fruits, but more of them right'],
    x_axis_label=['Coverage', 'share of fruits at or above the threshold'],
    y_axis_label='Accuracy above the threshold',
)
