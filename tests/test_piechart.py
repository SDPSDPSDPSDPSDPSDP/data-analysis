import pandas as pd
import pytest

from shirin.plot.config import FontSizes
from shirin.plot.core import PiePlotOptions
from shirin.plot.plots import PieChart
from shirin.plot.svg.fonts import cap_height


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

        assert len(chart.wedges) == 2
        assert chart.donut_hole > 0

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

        assert len(plot._autotexts) == 3


class TestPieSliceLabels:
    def test_headline_sits_above_percentage_on_its_slice(self) -> None:
        df = pd.DataFrame({"count": [76, 24]}, index=[True, False])
        options = PiePlotOptions(
            df=df,
            col="count",
            palette={True: "#e0fff0", False: "#a62a5a"},
            slice_labels={True: "Accuracy: 96,4%"},
        )

        plot = PieChart(options)
        chart = plot.render()

        headline, percentage = plot._headline_texts[0], plot._autotexts[0]
        assert headline in chart.texts
        assert (headline.x, headline.y) == (percentage.x, percentage.y)
        assert headline.va == "bottom"
        # Pair centered on the label point: percentage pushed down, headline bottom above its top.
        assert percentage.dy < 0
        assert headline.dy > percentage.dy + cap_height(percentage.size) / 2
        assert headline.size > percentage.size
        assert headline.color == percentage.color
        # Every percentage shrinks and fades, not only the labelled slice's.
        assert percentage.size == plot._autotexts[1].size == FontSizes.DATALABELS
        assert percentage.alpha == plot._autotexts[1].alpha < headline.alpha

    def test_long_headline_wraps_and_keeps_explicit_newlines(self) -> None:
        df = pd.DataFrame({"count": [76, 24]}, index=["A", "B"])
        options = PiePlotOptions(
            df=df,
            col="count",
            palette={"A": "#111111", "B": "#222222"},
            slice_labels={"A": "Accuracy: 96,38%", "B": "Rest\n24"},
        )

        plot = PieChart(options)
        plot.render()

        assert [t.text for t in plot._headline_texts] == ["Accuracy:\n96,38%", "Rest\n24"]

    def test_headline_centered_when_slice_has_no_percentage(self) -> None:
        df = pd.DataFrame({"count": [76, 24]}, index=["A", "B"])
        options = PiePlotOptions(
            df=df,
            col="count",
            palette={"A": "#111111", "B": "#222222"},
            legend_percentages=True,
            slice_labels={"A": "Accuracy: 96%"},
        )

        chart = PieChart(options).render()

        assert [(t.text, t.va, t.dy) for t in chart.texts] == [("Accuracy:\n96%", "center", 0)]

    def test_unknown_slice_label_key_raises(self) -> None:
        df = pd.DataFrame({"count": [1, 1]}, index=["A", "B"])
        options = PiePlotOptions(
            df=df,
            col="count",
            palette={"A": "#111111", "B": "#222222"},
            slice_labels={"C": "Missing"},
        )

        with pytest.raises(ValueError, match="slice_labels keys \\['C'\\]"):
            PieChart(options).render()
