import pandas as pd

from shirin.plot.core import PiePlotOptions
from shirin.plot.plots import PieChart


class TestPieChartRender:
    def test_render_returns_axes(self) -> None:
        df = pd.DataFrame({"count": [10, 20, 30]}, index=["A", "B", "C"])
        options = PiePlotOptions(
            df=df,
            col="count",
            palette={"A": "#111111", "B": "#222222", "C": "#333333"},
        )

        plot = PieChart(options)
        ax = plot.render()

        assert len(ax.patches) == 3

    def test_render_donut(self) -> None:
        df = pd.DataFrame({"count": [1, 1]}, index=["A", "B"])
        options = PiePlotOptions(
            df=df,
            col="count",
            palette={"A": "#111111", "B": "#222222"},
            donut=True,
        )

        plot = PieChart(options)
        ax = plot.render()

        assert len(ax.patches) >= 2

    def test_render_sets_autotext_colors_for_all_slices(self) -> None:
        # Regression test: matplotlib's Axes.pie() can return either a plain
        # tuple (patches, texts, autotexts) or, on newer matplotlib versions,
        # a PieContainer that supports indexing but not len(). The plot must
        # render and color every slice's autotext regardless of which one
        # matplotlib hands back.
        df = pd.DataFrame({"count": [70, 30]}, index=["Decided", "Undecided"])
        options = PiePlotOptions(
            df=df,
            col="count",
            palette={"Decided": "#2b2b2b", "Undecided": "#d9d9d9"},
            value_datalabel=0,
        )

        plot = PieChart(options)
        plot.render()
        plot.format_plot(plot.plot_object)

        assert len(plot._autotexts) == 2
        for autotext in plot._autotexts:
            assert autotext.get_color() is not None

    def test_render_with_no_labels_above_threshold(self) -> None:
        # value_datalabel higher than any slice's percentage means autopct
        # returns '' for every wedge; must not raise.
        df = pd.DataFrame({"count": [1, 1, 1]}, index=["A", "B", "C"])
        options = PiePlotOptions(
            df=df,
            col="count",
            palette={"A": "#111111", "B": "#222222", "C": "#333333"},
            value_datalabel=101,
        )

        plot = PieChart(options)
        plot.render()
        plot.format_plot(plot.plot_object)

        assert len(plot._autotexts) == 3
