"""Integration tests for pie chart data-label text color contrast."""
import pandas as pd

from shirin.plot.core import PiePlotOptions
from shirin.plot.plots import PieChart
from shirin.plot.config.colors import Colors, TextColors
from shirin.plot.common.formatting.text_contrast import get_text_color_for_background


class TestPieChartTextColors:
    """Integration tests for pie chart text color contrast."""
    
    def test_pie_chart_boolean_palette_text_colors(self):
        """Test that pie chart correctly applies text colors with boolean palette keys."""
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
        
        plot = PieChart(options)
        plot.render()
        
        assert plot._colors is not None
        assert len(plot._colors) == 2
        
        for bg_color, autotext in zip(plot._colors, plot._autotexts):
            expected_text_color = get_text_color_for_background(bg_color)
            actual_text_color = autotext.color
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
        
        plot = PieChart(options)
        plot.render()
        
        for bg_color, autotext in zip(plot._colors, plot._autotexts):
            expected_text_color = get_text_color_for_background(bg_color)
            actual_text_color = autotext.color
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
        
        plot = PieChart(options)
        plot.render()
        
        assert plot._autotexts[0].color == TextColors.WHITE
    
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
        
        plot = PieChart(options)
        plot.render()
        
        assert plot._autotexts[0].color == TextColors.BLACK


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
        
        plot = PieChart(options)
        plot.render()
        
        for bg_color, autotext in zip(plot._colors, plot._autotexts):
            expected_text_color = get_text_color_for_background(bg_color)
            actual_text_color = autotext.color
            assert actual_text_color == expected_text_color
