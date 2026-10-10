from shirin.plot import PlotGraphs
from shirin.assets.fake_data import df

plot = PlotGraphs(font='satoshi')
plot.countplot_x(df, x='label', hue='example_hue_1')
