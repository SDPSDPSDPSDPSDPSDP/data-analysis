"""
Integration tests for text color contrast in plots.

These tests verify that when using boolean (or other non-string) keys in palettes,
the text colors on data labels are correctly determined based on background luminance.
"""
import pytest
import pandas as pd
import matplotlib.pyplot as plt

from shirin.plot.core import create_plot, PiePlotOptions, CountPlotOptions, BarPlotOptions
from shirin.plot.config.colors import Colors, TextColors
from shirin.plot.common.formatting.text_contrast import get_text_color_for_background


@pytest.fixture(autouse=True)
def close_plots():
    """Close all matplotlib figures after each test."""
    yield
    plt.close('all')


class TestPieChartTextColors:
    """Integration tests for pie chart text color contrast."""
    
    def test_pie_chart_boolean_palette_text_colors(self):
        """Test that pie chart correctly applies text colors with boolean palette keys."""
        # Create test data with boolean index
        df = pd.DataFrame({
            'count': [30, 70]
        }, index=[True, False])
        
        palette = {True: Colors.BAD_RED, False: Colors.GOOD_GREEN}
        label_map = {True: "Bad", False: "Good"}
        
        options = PiePlotOptions(
            df=df,
            col='count',
            palette=palette,
            label_map=label_map
        )
        
        plot = create_plot('pie', options)
        plot.render()
        
        # Verify the colors were set correctly
        assert plot._colors is not None
        assert len(plot._colors) == 2
        
        # Verify text colors match expected contrast
        for bg_color, autotext in zip(plot._colors, plot._autotexts):
            expected_text_color = get_text_color_for_background(bg_color)
            actual_text_color = autotext.get_color()
            assert actual_text_color == expected_text_color, \
                f"Text color {actual_text_color} doesn't match expected {expected_text_color} for background {bg_color}"
    
    def test_pie_chart_string_palette_text_colors(self):
        """Test that pie chart works with string palette keys."""
        df = pd.DataFrame({
            'count': [40, 60]
        }, index=['category_a', 'category_b'])
        
        palette = {'category_a': Colors.BAD_RED, 'category_b': Colors.GOOD_GREEN}
        
        options = PiePlotOptions(
            df=df,
            col='count',
            palette=palette
        )
        
        plot = create_plot('pie', options)
        plot.render()
        
        # Verify text colors are correctly applied
        for bg_color, autotext in zip(plot._colors, plot._autotexts):
            expected_text_color = get_text_color_for_background(bg_color)
            actual_text_color = autotext.get_color()
            assert actual_text_color == expected_text_color
    
    def test_pie_chart_dark_background_gets_white_text(self):
        """Test that dark pie slices get white text."""
        df = pd.DataFrame({
            'count': [100]
        }, index=['dark'])
        
        dark_color = '#1a1a1a'
        palette = {'dark': dark_color}
        
        options = PiePlotOptions(
            df=df,
            col='count',
            palette=palette
        )
        
        plot = create_plot('pie', options)
        plot.render()
        
        assert plot._autotexts[0].get_color() == TextColors.WHITE
    
    def test_pie_chart_light_background_gets_black_text(self):
        """Test that light pie slices get black text."""
        df = pd.DataFrame({
            'count': [100]
        }, index=['light'])
        
        light_color = '#f0f0f0'
        palette = {'light': light_color}
        
        options = PiePlotOptions(
            df=df,
            col='count',
            palette=palette
        )
        
        plot = create_plot('pie', options)
        plot.render()
        
        assert plot._autotexts[0].get_color() == TextColors.BLACK


class TestStackedCountPlotTextColors:
    """Integration tests for stacked count plot text color contrast."""
    
    def test_stacked_countplot_boolean_palette_colors_applied(self):
        """Test that stacked countplot correctly uses boolean palette for bar colors."""
        df = pd.DataFrame({
            'category': ['A', 'A', 'A', 'B', 'B', 'B'],
            'status': [True, True, False, True, False, False]
        })
        
        palette = {True: Colors.BAD_RED, False: Colors.GOOD_GREEN}
        
        options = CountPlotOptions(
            df=df,
            axis_column='category',
            orientation='horizontal',
            hue='status',
            palette=palette,
            stacked=True,
            stacked_labels='percentage'
        )
        
        plot = create_plot('count', options)
        plot.render()
        
        # Verify the plot was created with correct palette
        assert plot._original_palette is not None
        assert True in plot._original_palette or 'True' in plot._original_palette


class TestStackedBarPlotTextColors:
    """Integration tests for stacked bar plot text color contrast."""
    
    def test_stacked_barplot_boolean_palette_colors_applied(self):
        """Test that stacked barplot correctly uses boolean palette."""
        df = pd.DataFrame({
            'category': ['A', 'A', 'B', 'B'],
            'status': [True, False, True, False],
            'value': [10, 20, 15, 25]
        })
        
        palette = {True: Colors.BAD_RED, False: Colors.GOOD_GREEN}
        
        options = BarPlotOptions(
            df=df,
            axis_column='category',
            value='value',
            orientation='horizontal',
            hue='status',
            palette=palette,
            stacked=True,
            stacked_labels='percentage'
        )
        
        plot = create_plot('bar', options)
        plot.render()
        
        # Verify the plot was created with correct palette
        assert plot._original_palette is not None


class TestIntegerPaletteKeys:
    """Integration tests for integer palette keys."""
    
    def test_pie_chart_integer_palette_keys(self):
        """Test that pie chart works with integer palette keys."""
        df = pd.DataFrame({
            'count': [25, 75]
        }, index=[1, 2])
        
        palette = {1: Colors.BAD_RED, 2: Colors.GOOD_GREEN}
        label_map = {1: "Option 1", 2: "Option 2"}
        
        options = PiePlotOptions(
            df=df,
            col='count',
            palette=palette,
            label_map=label_map
        )
        
        plot = create_plot('pie', options)
        plot.render()
        
        # Verify text colors are correctly applied
        for bg_color, autotext in zip(plot._colors, plot._autotexts):
            expected_text_color = get_text_color_for_background(bg_color)
            actual_text_color = autotext.get_color()
            assert actual_text_color == expected_text_color
