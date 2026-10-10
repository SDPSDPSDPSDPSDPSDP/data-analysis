import pandas as pd

from shirin.plot.core import PiePlotOptions
from shirin.plot.plots import PieChart


class TestPieChartRender:
    def test_render_returns_chart(self) -> None:
        df = pd.DataFrame({"count": [10, 20, 30]}, index=["A", "B", "C"])
        options = PiePlotOptions(
            df=df,
            col="count",
            palette={"A": "#111111", "B": "#222222", "C": "#333333"},
        )

        plot = PieChart(options)
        chart = plot.render()

        assert len(chart.wedges) == 3
        assert chart.wedges[-1].end == 1

    def test_render_donut(self) -> None:
        df = pd.DataFrame({"count": [1, 1]}, index=["A", "B"])
        options = PiePlotOptions(
            df=df,
            col="count",
            palette={"A": "#111111", "B": "#222222"},
            donut=True,
        )

        plot = PieChart(options)
        chart = plot.render()

        assert len(chart.wedges) == 3  # two slices plus the white center

    def test_render_sets_autotext_colors_for_all_slices(self) -> None:
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
            assert autotext.color is not None

    def test_render_with_no_labels_above_threshold(self) -> None:
        # value_datalabel higher than any slice's percentage leaves every label empty; must not raise.
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
