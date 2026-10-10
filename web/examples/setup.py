# %% [setup] Import your data.
from shirin.assets.data import df

# %% [setup] Create the plotter once and reuse it for every chart. Use palette to give values of a column a fixed color, and label_mapping to show them with a readable name. These settings apply to all charts you make with this plotter.
from shirin.plot import PlotGraphs

plot = PlotGraphs(
    palette={
        'is_ripe': {True: "#e9d0ff", False: "#6f2525"},
        'fruit': {
            'Apple': "#8db600",
            'Banana': "#ffe135",
            'Cherry': "#9b111e",
            'Date': "#8b5a2b",
            'Fig': "#6c3461",
            'Mango': "#ffa62b",
        },
    },
    label_mapping={'is_ripe': {True: 'Ripe', False: 'Unripe'}},
)
