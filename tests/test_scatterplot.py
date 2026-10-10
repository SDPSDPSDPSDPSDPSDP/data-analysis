import pandas as pd
import pytest

from shirin.plot.core import ScatterPlotOptions
from shirin.plot.plots import ScatterPlot


class TestScatterPlotOptionsValidation:
    def test_missing_x_raises(self) -> None:
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        options = ScatterPlotOptions(df=df, x="", y="y")

        with pytest.raises(ValueError, match="x column must be specified"):
            options.validate()

    def test_missing_y_raises(self) -> None:
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        options = ScatterPlotOptions(df=df, x="x", y="")

        with pytest.raises(ValueError, match="y column must be specified"):
            options.validate()

    def test_empty_dataframe_raises(self) -> None:
        df = pd.DataFrame({"x": [], "y": []})
        options = ScatterPlotOptions(df=df, x="x", y="y")

        with pytest.raises(ValueError, match="DataFrame cannot be None or empty"):
            options.validate()


def _render(group=None, **options):
    data = {"height": [150, 160, 170, 180], "weight": [50, 60, 70, 80]}
    if group is not None:
        data["group"] = group
    return ScatterPlot(ScatterPlotOptions(df=pd.DataFrame(data), x="height", y="weight", **options)).render()


class TestScatterPlotRender:
    def test_render_returns_chart_with_expected_labels(self) -> None:
        chart = _render(x_axis_label="Height", y_axis_label="Weight")

        assert chart.x.label == "Height"
        assert chart.y.label == "Weight"
        assert len(chart.dots) > 0

    def test_render_with_hue_creates_legend(self) -> None:
        chart = _render(group=["A", "A", "B", "B"], hue="group", legend=True)

        assert [label for _, label, _ in chart.legend] == ["A", "B"]

    def test_render_without_hue_hides_legend(self) -> None:
        chart = _render()

        assert chart.legend == []
