"""Integration tests for pie chart data-label text color contrast."""
import pandas as pd

from shirin.plot.common.formatting.text_contrast import get_text_color_for_background
from shirin.plot.config.colors import Colors, TextColors
from shirin.plot.core import PiePlotOptions
from shirin.plot.plots import PieChart


def _render_pie(counts, index, palette, label_map=None) -> PieChart:
    df = pd.DataFrame({'count': counts}, index=index)
    plot = PieChart(PiePlotOptions(df=df, col='count', palette=palette, label_map=label_map))
    plot.render()
    return plot


def _assert_contrasting_text(plot: PieChart) -> None:
    for bg_color, autotext in zip(plot._colors, plot._autotexts):
        expected_text_color = get_text_color_for_background(bg_color)
        assert autotext.color == expected_text_color, \
            f"Text color {autotext.color} doesn't match expected {expected_text_color} for background {bg_color}"


class TestPieChartTextColors:
    """Integration tests for pie chart text color contrast."""

    def test_pie_chart_boolean_palette_text_colors(self):
        """Test that pie chart correctly applies text colors with boolean palette keys."""
        plot = _render_pie(
            [30, 70], [True, False],
            palette={True: Colors.BAD_RED, False: Colors.GOOD_GREEN},
            label_map={True: "Bad", False: "Good"},
        )

        assert plot._colors is not None
        assert len(plot._colors) == 2
        _assert_contrasting_text(plot)

    def test_pie_chart_string_palette_text_colors(self):
        """Test that pie chart works with string palette keys."""
        plot = _render_pie(
            [40, 60], ['category_a', 'category_b'],
            palette={'category_a': Colors.BAD_RED, 'category_b': Colors.GOOD_GREEN},
        )

        _assert_contrasting_text(plot)

    def test_pie_chart_dark_background_gets_white_text(self):
        """Test that dark pie slices get white text."""
        plot = _render_pie([100], ['dark'], palette={'dark': '#1a1a1a'})

        assert plot._autotexts[0].color == TextColors.WHITE

    def test_pie_chart_light_background_gets_black_text(self):
        """Test that light pie slices get black text."""
        plot = _render_pie([100], ['light'], palette={'light': '#f0f0f0'})

        assert plot._autotexts[0].color == TextColors.BLACK


class TestIntegerPaletteKeys:
    """Integration tests for integer palette keys."""

    def test_pie_chart_integer_palette_keys(self):
        """Test that pie chart works with integer palette keys."""
        plot = _render_pie(
            [25, 75], [1, 2],
            palette={1: Colors.BAD_RED, 2: Colors.GOOD_GREEN},
            label_map={1: "Option 1", 2: "Option 2"},
        )

        _assert_contrasting_text(plot)


def test_legend_percentages_replaces_counts_and_hides_slice_labels():
    df = pd.DataFrame({'count': [25, 75]}, index=['a', 'b'])
    plot = PieChart(PiePlotOptions(df=df, col='count', legend_percentages=True))
    chart = plot.render()

    assert [value for _, _, value in chart.legend] == ['25%', '75%']
    assert not any(text in chart.texts for text in plot._autotexts)
