# %% [setup] Import your data.
from shirin.assets.data import df

# %% [setup] Create the plotter once and reuse it for every chart. Use palette to give values of a column a fixed color, and label_mapping to show them with a readable name. These settings apply to all charts you make with this plotter.
from shirin.plot import PlotGraphs

palette = {
    'is_ripe': {True: "#e9d0ff", False: "#6f2525"},
    'fruit': {
        'Apple': "#c7ff0f",
        'Banana': "#e7ffb3",
        'Cherry': "#73304c",
        'Date': "#8b6f75",
        'Fig': "#9f5090",
        'Orange': "#ffb752",
    },
    'sold_share': "#d6dde6",
}
label_mapping = {'is_ripe': {True: 'Ripe', False: 'Unripe'}}

plot = PlotGraphs(palette=palette, label_mapping=label_mapping)
