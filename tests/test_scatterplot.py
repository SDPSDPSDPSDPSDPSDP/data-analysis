import pandas as pd
import pytest

from shirin.plot.core import ScatterPlotOptions
from shirin.plot.plots import create_plot


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


class TestScatterPlotRender:
    def test_render_returns_axes_with_expected_labels(self) -> None:
        df = pd.DataFrame({
            "height": [150, 160, 170, 180],
            "weight": [50, 60, 70, 80],
        })

        options = ScatterPlotOptions(
            df=df,
            x="height",
            y="weight",
            xlabel="Height",
            ylabel="Weight",
        )

        plot = create_plot('scatter', options)
        ax = plot.render()

        assert ax.get_xlabel() == "Height"
        assert ax.get_ylabel() == "Weight"
        assert len(ax.collections) > 0

    def test_render_with_hue_creates_legend(self) -> None:
        df = pd.DataFrame({
            "height": [150, 160, 170, 180],
            "weight": [50, 60, 70, 80],
            "group": ["A", "A", "B", "B"],
        })

        options = ScatterPlotOptions(
            df=df,
            x="height",
            y="weight",
            hue="group",
            plot_legend=True,
        )

        plot = create_plot('scatter', options)
        ax = plot.render()

        assert ax.get_legend() is not None

    def test_render_without_hue_hides_legend(self) -> None:
        df = pd.DataFrame({
            "height": [150, 160, 170, 180],
            "weight": [50, 60, 70, 80],
        })

        options = ScatterPlotOptions(
            df=df,
            x="height",
            y="weight",
        )

        plot = create_plot('scatter', options)
        ax = plot.render()

        assert ax.get_legend() is None
