import pytest

from shirin.plot.common.formatting.text_contrast import get_luminance, get_text_color_for_background
from shirin.plot.config.colors import Colors, TextColors


class TestGetLuminance:
    """Tests for luminance calculation."""
    
    def test_black_has_zero_luminance(self):
        assert get_luminance('#000000') == 0.0
    
    def test_white_has_max_luminance(self):
        assert get_luminance('#FFFFFF') == 1.0
    
    def test_works_without_hash(self):
        assert get_luminance('000000') == 0.0
        assert get_luminance('FFFFFF') == 1.0
    
    def test_red_luminance(self):
        # Pure red has luminance based on 0.2126 coefficient
        luminance = get_luminance('#FF0000')
        assert 0.2 < luminance < 0.25
    
    def test_green_luminance(self):
        # Pure green has luminance based on 0.7152 coefficient (brightest)
        luminance = get_luminance('#00FF00')
        assert 0.7 < luminance < 0.75
    
    def test_blue_luminance(self):
        # Pure blue has luminance based on 0.0722 coefficient (dimmest)
        luminance = get_luminance('#0000FF')
        assert 0.05 < luminance < 0.1


class TestGetTextColorForBackground:
    """Tests for automatic text color selection based on background."""
    
    def test_dark_background_returns_white_text(self):
        # Dark colors should get white text
        assert get_text_color_for_background('#000000') == TextColors.WHITE
        assert get_text_color_for_background('#1a1a1a') == TextColors.WHITE
        assert get_text_color_for_background('#333333') == TextColors.WHITE
    
    def test_light_background_returns_black_text(self):
        # Light colors should get black text
        assert get_text_color_for_background('#FFFFFF') == TextColors.BLACK
        assert get_text_color_for_background('#f0f0f0') == TextColors.BLACK
        assert get_text_color_for_background('#cccccc') == TextColors.BLACK
    
    def test_app_colors_bad_red_gets_white_text(self):
        # BAD_RED is dark, should get white text
        result = get_text_color_for_background(Colors.BAD_RED)
        assert result == TextColors.WHITE
    
    def test_app_colors_good_green_gets_black_text(self):
        # GOOD_GREEN is light, should get black text
        result = get_text_color_for_background(Colors.GOOD_GREEN)
        assert result == TextColors.BLACK
    
    def test_mid_grey_threshold(self):
        # Test around the WCAG threshold (0.179 luminance)
        # A grey with ~46% brightness is around the threshold
        dark_grey = '#555555'  # Below threshold
        light_grey = '#777777'  # Above threshold
        
        assert get_text_color_for_background(dark_grey) == TextColors.WHITE
        assert get_text_color_for_background(light_grey) == TextColors.BLACK
